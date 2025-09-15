import json
import sys
from pathlib import Path

import google.generativeai as genai

# --- Constants and Configuration ---
DEFAULT_MODEL = "gemini-2.5-flash-lite"
API_KEY = "AIzaSyCSwvec77qav-c1MtU7_ltulngPUqyGNdA"

SYSTEM_PROMPT = """
You are a precise JSON editor. You will receive a JSON object and your task is to UPDATE ONLY the `hashtags` arrays. Do not add, remove, rename, or reorder any categories or subcategories.
Rules:
- Keep the exact category and subcategory structure.
- For every subcategory, produce 15-20 relevant hashtags.
- update all the subcategories.
- Each hashtag must be an object: { "tag": "#lowercase", "uses_count": "compact_count" }.
- Each hashtag must include a usage count.
- Do not duplicate the same hashtag within the same subcategory.
- I want all subcategories to expand
- Populate each subcategory with new, relevant hashtags (focus on Instagram, Facebook, X, Threads, and YouTube etc).
- Output ONE valid JSON object only (no prose, no markdown).
"""


# --- Helper Functions ---
def get_updated_hashtags(input_data: dict) -> dict | None:
    """
    Calls the Gemini API to update hashtags in the provided JSON data.
    Prints the API request and response for debugging, including token counts.
    """
    genai.configure(api_key=API_KEY)

    model = genai.GenerativeModel(
        model_name=DEFAULT_MODEL,
        system_instruction=SYSTEM_PROMPT
    )

    user_prompt = (
        "Update the hashtags in the following JSON while keeping the structure unchanged."
        "Return ONLY valid JSON. The JSON data to process is:\n\n"
        f"{json.dumps(input_data, indent=2)}"
    )

    # --- Count input tokens before sending the request ---
    try:
        input_token_count = model.count_tokens(user_prompt).total_tokens
        print("\n--- Token Count Details ---")
        print(f"Input Token Count (before API call): {input_token_count}")
        print("----------------------------\n")
    except Exception as e:
        print(f"Failed to count input tokens: {e}", file=sys.stderr)
        input_token_count = "N/A"

    # --- Print API Request ---
    print("\n--- API Request Details ---")
    print(f"Model: {DEFAULT_MODEL}")
    print(f"System Prompt:\n{SYSTEM_PROMPT}")
    print(f"User Prompt:\n{user_prompt}")
    print("---------------------------\n")

    try:
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )

        # --- Print API Response and Token Usage ---
        print("--- API Response Details ---")
        print(f"Response Text:\n{response.text}")

        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            print("\n--- Final Token Usage (from response) ---")
            print(f"Prompt Tokens: {usage.prompt_token_count}")
            print(f"Output Tokens: {usage.candidates_token_count}")
            print(f"Total Tokens: {usage.total_token_count}")
        else:
            print("\nUsage metadata not available in the response.")

        print("----------------------------\n")

        return json.loads(response.text)

    except Exception as e:
        print(f"An error occurred during the API call: {e}", file=sys.stderr)
        return None


# --- Main Logic ---
def main():
    """Main function to read, process, and write the JSON data."""
    input_file = Path("hashtags_expanded.json")
    output_file = Path("output.json")

    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        print(f"Reading from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        updated_data = get_updated_hashtags(input_data)

        if updated_data:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)
            print(f"Success! Updated JSON saved to {output_file}.")
        else:
            print("Failed to get a valid response from the API.", file=sys.stderr)

    except json.JSONDecodeError:
        print(f"Error: The file '{input_file}' is not a valid JSON file.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
