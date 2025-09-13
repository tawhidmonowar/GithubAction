import json
import os
import subprocess
import sys
import random


def generate_hashtags(prompt):
    """
    Calls the Gemini CLI to generate hashtags based on a prompt.
    Returns the raw string output.
    """
    try:
        # Pass the prompt to the Gemini CLI. The output is captured.
        result = subprocess.run(
            ['gemini', 'generate', prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error calling Gemini CLI: {e.stderr}", file=sys.stderr)
        return ""


def generate_random_uses_count():
    """Generates a random uses count in a simplified format."""
    # Simplified logic for generating a random count
    value = random.randint(10, 200)
    unit = random.choice(["M", "B", "K"])
    return f"{value}{unit}"


def update_json_file(category, prompt):
    """Updates the hashtags.json file with new hashtags for a given category."""
    # Step 1: Generate hashtags from Gemini
    hashtags_str = generate_hashtags(prompt)
    if not hashtags_str:
        print("Failed to generate hashtags. Exiting.")
        return

    # Step 2: Parse the raw output into a list of strings
    # Clean up the output to handle potential extra commas or spaces
    hashtags_list = [tag.strip() for tag in hashtags_str.split(',') if tag.strip()]

    # Step 3: Format the list into the required JSON structure
    new_hashtags_data = [
        {
            "tag": hashtag,
            "uses_count": generate_random_uses_count()  # Placeholder count
        }
        for hashtag in hashtags_list
    ]

    # Step 4: Read the existing JSON file
    try:
        with open("hashtags.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("hashtags.json not found. Creating a new file.")
        data = {}
    except json.JSONDecodeError:
        print("Error decoding hashtags.json. Creating a new file.")
        data = {}

    # Step 5: Update the specific category with the new data
    data[category] = new_hashtags_data

    # Step 6: Write the updated data back to the file
    with open("hashtags.json", "w") as f:
        json.dump(data, f, indent=4)

    print(f"Successfully updated the '{category}' category with new hashtags.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_hashtags.py <category_name> <gemini_prompt>")
        sys.exit(1)

    category_name = sys.argv[1]
    gemini_prompt = sys.argv[2]
    update_json_file(category_name, gemini_prompt)