import os
from pathlib import Path

EXCLUDED_FILES = [
    ".DS_Store",
    ".gitignore",
    "package-lock.json",
    "postcss.config.js",
    "tailwind.config.js",
    "next.config.js",
    "playwright.config.js",
    "jsconfig.json",
    "components.json",
    "API_doc.md",
    "env.example",
]
EXCLUDED_DIRS = [
    "ui",
    "cypress",
    "node_modules",
    "migrations",
    ".next",
    "playwright-report",
    "test-results",
    "dist",
    "build",
    "coverage",
]
EXCLUDED_EXT = [
    ".ico",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tiff",
    ".webp",
]


def _should_exclude(root_path, path):
    """
    Check if a file or directory should be excluded based on the exclusions and depth.
    """
    for dir_name in EXCLUDED_DIRS:
        if os.path.commonpath(
            [path, os.path.join(root_path, dir_name)]
        ) == os.path.normpath(os.path.join(root_path, dir_name)):
            return True
    return False


def find_files(root_path, depth):
    """
    Recursively find files in the given directory up to a certain depth,
    excluding specified files, directories, and file extensions.
    """
    found_files = []

    for root, dirs, files in Path(root_path).walk():
        # Calculate current depth
        current_depth = root.relative_to(root_path).parts
        if len(current_depth) > depth:
            break
        for file in files:
            if file in EXCLUDED_FILES or any(
                file.endswith(ext) for ext in EXCLUDED_EXT
            ):
                continue
            file_path = root / file
            if not _should_exclude(root_path, file_path):
                found_files.append(str(file_path.relative_to(root_path)))

    return found_files
