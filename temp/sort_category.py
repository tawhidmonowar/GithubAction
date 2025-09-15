import os
import sys
import json
from collections import OrderedDict

# Define the filename of the JSON file to read
input_file_path = 'hashtags_category.json'
# Define the filename for the sorted JSON output
output_file_path = 'sorted_category.json'

try:
    # Check if the input file exists before attempting to open it.
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"The file '{input_file_path}' was not found.")

    # Open the JSON file for reading and load its content.
    with open(input_file_path, 'r') as f:
        data = json.load(f)

    # Get the dictionary containing the categories.
    categories = data["categories"]

    # Sort the category names alphabetically.
    sorted_category_names = sorted(categories.keys())

    # Create a new dictionary to hold the sorted categories.
    # An OrderedDict is used here to ensure the order is maintained.
    sorted_categories = OrderedDict()

    # Iterate through the sorted names and add the original category data
    # to the new dictionary in the correct order.
    for name in sorted_category_names:
        sorted_categories[name] = categories[name]

    # Update the original data with the sorted categories.
    data["categories"] = sorted_categories

    # Open the new file for writing and dump the sorted JSON into it.
    # The 'indent' parameter makes the output readable.
    with open(output_file_path, 'w') as f:
        json.dump(data, f, indent=2)

    # Print a success message to the console.
    print(f"Successfully sorted categories and saved to '{output_file_path}'")

except FileNotFoundError as e:
    print(f"Error: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON from '{input_file_path}': {e}")
except KeyError as e:
    print(f"Error: Missing key 'categories' in JSON data from '{input_file_path}': {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
