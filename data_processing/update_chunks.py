import os
import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Optional

import google.generativeai as genai
from google.generativeai import types

DEFAULT_MODEL = "gemini-2.5-flash-lite"

SYSTEM_INSTRUCTION = (
    "You are a precise JSON editor. You will be given a JSON object or array.\n"
    "- Return ONLY valid JSON. No prose, no markdown, no code fences.\n"
    "- Keep the same top-level structure (object vs array) unless the content is clearly invalid.\n"
    "- Update hashtags with uses counts.\n"
    "- If something is missing, infer reasonable values, but remain consistent and realistic.\n"
    "- Do not add commentary."
)

# Configure logging
LOG_DIR = Path("update_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "run.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(console)


def _usage_to_dict(usage) -> dict:
    if not usage:
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    return {
        "input_tokens": getattr(usage, "prompt_token_count", 0) or 0,
        "output_tokens": getattr(usage, "candidates_token_count", 0) or 0,
        "total_tokens": getattr(usage, "total_token_count", 0) or 0,
    }


def _strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` fences if model returned them."""
    t = text.strip()
    if t.startswith("```"):
        # Remove opening fence
        t = t.split("\n", 1)[1] if "\n" in t else ""
        # Remove closing fence
        if "```" in t:
            t = t.rsplit("```", 1)[0]
    return t.strip()


def _safe_json_loads(s: str) -> Any:
    """Attempt to parse JSON, raising ValueError with context on failure."""
    try:
        return json.loads(s)
    except Exception as e:
        # Try a second pass after stripping common artifacts
        s2 = _strip_code_fences(s)
        if s2 != s:
            try:
                return json.loads(s2)
            except Exception as e2:
                raise ValueError(f"Failed to parse JSON after stripping fences: {e2}\nRaw start: {s[:500]}") from e2
        raise ValueError(f"Failed to parse JSON: {e}\nRaw start: {s[:500]}") from e


def _read_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_file(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _init_model(model_name: str) -> "genai.GenerativeModel":
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_INSTRUCTION
    )


def _call_gemini(model, input_json: Any, max_retries: int = 5, base_delay: float = 1.5) -> tuple[Any, dict]:
    prompt = (
        "Update and return only the JSON below (no explanations):\n"
        f"{json.dumps(input_json, ensure_ascii=False)}"
    )

    logging.info("[REQUEST] %s", prompt[:4000] + (" ...[truncated]" if len(prompt) > 4000 else ""))

    for attempt in range(1, max_retries + 1):
        try:
            resp = model.generate_content(prompt)
            if not hasattr(resp, "text") or not resp.text:
                raise RuntimeError("Empty response from model.")

            raw = resp.text.strip()
            logging.info("[RESPONSE raw] %s", raw[:4000] + (" ...[truncated]" if len(raw) > 4000 else ""))

            parsed = _safe_json_loads(raw)

            usage_dict = _usage_to_dict(getattr(resp, "usage_metadata", None))
            logging.info(
                "Tokens — Input: %s | Output: %s | Total: %s",
                usage_dict["input_tokens"], usage_dict["output_tokens"], usage_dict["total_tokens"]
            )

            return parsed, usage_dict
        except Exception as e:
            if attempt == max_retries:
                logging.error("Gemini call failed after %d attempts: %s", attempt, e)
                raise
            sleep_for = base_delay * (2 ** (attempt - 1))
            logging.warning("Gemini call error (attempt %d/%d): %s | retrying in %.1fs", attempt, max_retries, e,
                            sleep_for)
            time.sleep(sleep_for)

    raise RuntimeError("Exhausted retries without returning.")


def update_json_with_gemini(input_file_path: Path, output_folder_path: Path, model) -> Optional[tuple[Path, dict]]:
    try:
        if not input_file_path.exists():
            logging.error("Input file not found: %s", input_file_path)
            return None

        input_data = _read_json_file(input_file_path)
        updated_data, usage = _call_gemini(model, input_data)

        output_folder_path.mkdir(parents=True, exist_ok=True)
        output_path = output_folder_path / input_file_path.name
        _write_json_file(output_path, updated_data)

        logging.info(
            "✓ Updated '%s' -> '%s' | Tokens — In:%s Out:%s Total:%s",
            input_file_path.name,
            output_path,
            usage["input_tokens"], usage["output_tokens"], usage["total_tokens"]
        )
        return output_path, usage
    except Exception as e:
        logging.error("✗ Failed '%s': %s", input_file_path.name, e)
        return None


def process_files(input_dir: Path, output_dir: Path, model_name: str) -> None:
    model = _init_model(model_name)

    if not input_dir.exists() or not input_dir.is_dir():
        logging.error("Input directory not found: %s", input_dir)
        sys.exit(1)

    json_files = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".json"])

    if not json_files:
        logging.info("No .json files found in '%s'.", input_dir)
        return

    logging.info("Found %d JSON files in '%s'. Starting updates...", len(json_files), input_dir)

    successes = 0
    per_file_usage = []  # <— NEW
    total_in = total_out = total_all = 0  # <— NEW

    for idx, path in enumerate(json_files, start=1):
        logging.info("[%d/%d] Processing %s", idx, len(json_files), path.name)
        result = update_json_with_gemini(path, output_dir, model)
        if result:
            successes += 1
            out_path, usage = result
            per_file_usage.append({
                "file": path.name,
                "output_file": out_path.name,
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "total_tokens": usage["total_tokens"],
            })
            total_in += usage["input_tokens"]
            total_out += usage["output_tokens"]
            total_all += usage["total_tokens"]

    # --- Write JSON summary (NEW) ---
    summary = {
        "model": model_name,
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "files_processed": len(json_files),
        "files_succeeded": successes,
        "totals": {
            "input_tokens": total_in,
            "output_tokens": total_out,
            "total_tokens": total_all,
        },
        "files": per_file_usage,
    }
    summary_path = LOG_DIR / "token_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logging.info("Done. %d/%d files updated.", successes, len(json_files))
    logging.info("Token summary written to: %s", summary_path)
    print(f"Token summary: {summary_path}")  # also to console


def main():
    parser = argparse.ArgumentParser(description="Batch-update JSON files via Gemini.")
    parser.add_argument("--in", dest="input_folder", default="data_chunks", help="Input folder containing JSON files")
    parser.add_argument("--out", dest="output_folder", default="updated_data_chunks",
                        help="Destination folder for updated JSON files")
    parser.add_argument("--model", dest="model", default=DEFAULT_MODEL, help=f"Gemini model (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    process_files(Path(args.input_folder), Path(args.output_folder), args.model)


if __name__ == "__main__":
    main()
