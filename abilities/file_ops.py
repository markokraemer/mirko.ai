import os
import json
import logger

excluded_files = ['.DS_Store', '.gitignore', 'package-lock.json', 'postcss.config.js', 'tailwind.config.js', 'next.config.js', 'playwright.config.js', 'jsconfig.json', 'components.json', 'API_doc.md', 'env.example']
excluded_dirs = ['cypress', 'cypress/downloads', 'node_modules', 'migrations', '.next', 'cypress/screenshots', 'playwright-report', 'test-results', 'dist', 'build', 'coverage' ] 
excluded_file_extensions = ['.ico', '.svg', '.png', '.jpg','.jpeg', '.gif', '.bmp', '.tiff', '.webp']


def read_directory(directory):
    """Reads all files in a given directory and returns a file tree and file contents, excluding certain files and directories."""
    # logger.info(f"Reading directory {directory}")
    file_tree = []
    file_contents = {}

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        files = [f for f in files if f not in excluded_files and not any(
            f.endswith(ext) for ext in excluded_file_extensions)]

        root_path = os.path.relpath(root, directory)
        file_tree.append({"directory": root_path, "files": files})

        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as file_content:
                    file_contents[file_path] = file_content.read()
            except UnicodeDecodeError:
                # logger.info(f"Skipping non-UTF-8 encoded file: {file_path}")
                continue

    return file_tree, file_contents

def read_file_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    # logger.info(f"Reading file content from {file_path}")
    return ""
    
def modify_file(file_path, new_content):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Create or overwrite the file with the new content
    with open(file_path, 'w') as file:
        file.write(new_content)
    logger.info(f"Writing new content to {file_path}")

def rename_file(file_path, new_name):
    new_file_path = os.path.join(os.path.dirname(file_path), new_name)
    os.rename(file_path, new_file_path)
    logger.info(f"Renamed file {file_path} to {new_file_path}")

def delete_file(file_path):
    os.remove(file_path)
    logger.info(f"Deleted file {file_path}")

def get_file_paths_by_name(file_name, directory):
    # Search for the file in the given directory and collect all matches
    matching_file_paths = []
    for root, dirs, files in os.walk(directory):
        if file_name in files:
            matching_file_paths.append(os.path.join(root, file_name))
    if not matching_file_paths:
        raise FileNotFoundError(f"File {file_name} not found in {directory}.")
    return matching_file_paths
