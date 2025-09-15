import os
import json

def split_hashtags(input_filepath, output_dir):
    with open(input_filepath) as input_file:
        input_data = json.load(input_file)

        main_categories = input_data["categories"]

        for category_name, category_content in main_categories.items():

            filename = category_name.replace(" ", "_").replace("&", "and").lower() + ".json"
            new_json_data = {
                category_name: category_content
            }

            os.makedirs(output_dir, exist_ok=True)
            output_filepath = os.path.join(output_dir, filename)

            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(new_json_data, f, indent=2)

            print(f"Successfully created: {filename}")

if __name__ == "__main__":

    input_file_path = os.path.join('..', 'data', 'hashtags.json')
    output_directory = 'data_chunks'

    if not os.path.exists(input_file_path):
        print(f"The file '{input_file_path}' was not found.")
        print("Please make sure you have created the file with your data.")
    else:
        split_hashtags(input_file_path, output_directory)
