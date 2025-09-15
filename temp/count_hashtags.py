import json

def calculate_counts(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

            total_categories = len(data.get('categories', {}))

            total_subcategories = 0
            total_hashtags = 0

            category = data.get('categories', {})
            for category_data in category.values():
                total_subcategories += len(category_data)
                for subcategory_data in category_data.values():
                    if 'hashtags' in subcategory_data and isinstance(subcategory_data['hashtags'], list):
                        total_hashtags += len(subcategory_data['hashtags'])

            return total_categories, total_subcategories, total_hashtags

    except FileNotFoundError:
        return "Error: The file was not found.", None, None
    except json.JSONDecodeError:
        return "Error: The file is not a valid JSON.", None, None
    except Exception as e:
        return f"An unexpected error occurred: {e}", None, None


json_file_name = 'hashtags_expanded.json'

categories, subcategories, hashtags = calculate_counts(json_file_name)

if categories is not None:
    print(f"Total categories: {categories}")
    print(f"Total subcategories: {subcategories}")
    print(f"Total hashtags: {hashtags}")