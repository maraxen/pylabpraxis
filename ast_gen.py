import ast
import os
import json  # Import the json module


def generate_asts_for_folder(folder_path, exclude_folders=None):
  """Generate ASTs for all Python files in a given folder and its subfolders.

  Args:
      folder_path (str): The path to the folder containing Python files.
      exclude_folders (list, optional): List of folder names to exclude.

  Returns:
      dict: A dictionary where keys are file paths and values are their ASTs.

  """
  asts = {}
  for root, dirs, files in os.walk(folder_path):
    # Modify dirs in-place to exclude specified folders
    if exclude_folders:
      dirs[:] = [d for d in dirs if d not in exclude_folders]

    for file_name in files:
      if file_name.endswith(".py"):
        file_path = os.path.join(root, file_name)
        try:
          with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
          tree = ast.parse(source_code, filename=file_path)
          asts[file_path] = tree
        except SyntaxError as e:
          print(f"Error parsing {file_path}: {e}")
        except Exception as e:
          print(f"An unexpected error occurred with {file_path}: {e}")
  return asts


if __name__ == "__main__":
  folder_to_analyze = os.path.dirname(os.path.abspath(__file__))
  folders_to_exclude = [
    "__pycache__",
    ".git",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "tests",
    "frontend",
  ]
  python_asts = generate_asts_for_folder(
    folder_to_analyze, exclude_folders=folders_to_exclude
  )

  # Prepare data for JSON output
  output_data = {}
  for file_path, tree in python_asts.items():
    # ast.dump() converts the AST object to a string representation
    output_data[file_path] = ast.dump(tree, indent=4)

  output_file_name = "asts_output.json"
  output_file_path = os.path.join(folder_to_analyze, output_file_name)

  try:
    with open(output_file_path, "w", encoding="utf-8") as f:
      json.dump(output_data, f, indent=4)
    print(f"\nSuccessfully wrote ASTs to {output_file_path}")
  except Exception as e:
    print(f"Error writing ASTs to file: {e}")

  # You can still iterate and print if you want to see them in console as well
  # for file_path, tree_string in output_data.items():
  #   print(f"AST for: {file_path}")
  #   print(tree_string)
