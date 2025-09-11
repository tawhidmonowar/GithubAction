import os
import json
import requests

def fetch_gemini_data(prompt: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    response = requests.post(url, headers=headers, params=params, json=payload)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    # Example prompt
    custom_prompt = "Give me three fun facts about AI."
    data = fetch_gemini_data(custom_prompt)

    # Save output as JSON
    with open("gemini_output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Data saved to gemini_output.json")
