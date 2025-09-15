import glob
import json
import os
from datetime import datetime


def merge_json_files(input_folder, output_file):
    merged_hashtags = {"categories": {}}

    # Use glob to find all JSON files in the specified folder
    file_list = glob.glob(os.path.join(input_folder, "*.json"))

    # Iterate through each file
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # The data structure has one key (the main category) which we need to merge
                for main_category, sub_categories in data.items():
                    if main_category not in merged_hashtags["categories"]:
                        merged_hashtags["categories"][main_category] = {}

                    # Merge the sub-categories and their hashtags
                    for sub_category, details in sub_categories.items():
                        merged_hashtags["categories"][main_category][sub_category] = details
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred with file {file_path}: {e}")

    # Add the last_update timestamp
    merged_hashtags["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_hashtags, f, indent=2, ensure_ascii=False)
        print(f"Successfully merged {len(file_list)} files into {output_file}")
    except Exception as e:
        print(f"Error writing the merged file to {output_file}: {e}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder_path = os.path.join(script_dir, "updated_data_chunks")
    output_folder_path = os.path.join(script_dir, "..", "data")
    output_file_path = os.path.join(output_folder_path, "updated_hashtags.json")

    # Create the output data folder if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)

    # Run the merge function
    merge_json_files(input_folder_path, output_file_path)
