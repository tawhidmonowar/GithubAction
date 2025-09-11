import os
import json
import requests

def call_gemini_api(prompt: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
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


def format_hashtags(response):

    # Extract the text content from the response
    try:
        csv_text = api_response["candidates"][0]["content"]["parts"][0]["text"]
        csv_lines = csv_text.replace("```csv\n", "").replace("```\n", "").strip().split('\n')
    except (KeyError, IndexError):
        print("Error: Could not find the CSV content in the API response.")
        return None

    # Skip the header row
    data_lines = csv_lines[1:]

    # Parse each line and create a list of dictionaries
    hashtags_list = []
    for line in data_lines:
        if line.strip(): # Ensure line is not empty
            try:
                tag, uses_count = line.split(',')
                hashtags_list.append({
                    "tag": tag.strip(),
                    "uses_count": uses_count.strip()
                })
            except ValueError:
                print(f"Warning: Skipping malformed line: {line}")

    # so we'll use "Happiness" as the category key. You can change this as needed.
    category_name = "Happiness"

    formatted_data = {
        category_name: hashtags_list
    }
    return formatted_data


if __name__ == '__main__':
    # Example prompt
    custom_prompt = "Generate 15 hashtags related to travel, food, movie with uses count in short form output in CSV"
    api_response = call_gemini_api(custom_prompt)

    # Format the data
    formatted_output = format_hashtags(api_response)

    if formatted_output:
        # Save formatted output as JSON
        with open("hashtags.json", "w", encoding="utf-8") as f:
            json.dump(formatted_output, f, indent=4, ensure_ascii=False)
        print("Formatted data saved to formatted_hashtags.json")