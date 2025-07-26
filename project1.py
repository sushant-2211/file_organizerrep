import shutil
import logging
from pathlib import Path
from datetime import datetime

# --- Configuration ---
LOG_FILE_NAME = 'file_organizer.log'

FILE_CATEGORIES = {
    "Images": {
        "JPG": [".jpg", ".jpeg"],
        "PNG": [".png"],
        "GIF": [".gif"],
        "Vector": [".svg"],
        "Other": [".bmp", ".tiff"],
    },
    "Documents": {
        "PDFs": [".pdf"],
        "Word": [".docx", ".doc"],
        "PowerPoint": [".pptx", ".ppt"],
        "Excel": [".xlsx", ".xls"],
        "Text": [".txt", ".odt", ".rtf"],
    },
    "Audio": {
        "MP3": [".mp3"],
        "Lossless": [".flac"],
        "Other": [".wav", ".aac", ".m4a"],
    },
    "Video": {
        "MP4": [".mp4"],
        "AVI": [".avi"],
        "Other": [".mov", ".mkv", ".wmv"],
    },
    "Archives": {
        "ZIP": [".zip"],
        "RAR": [".rar"],
        "Other": [".tar", ".gz", ".7z"],
    },
    "Code": {
        "Python": [".py"],
        "Web": [".js", ".html", ".css"],
        "C_and_C++": [".c", ".cpp", ".h"],
        "Other": [".java", ".json", ".xml"],
    },
    "Executables": {
        "Windows": [".exe", ".msi"],
    },
}

DEFAULT_CATEGORY = "Miscellaneous"

# --- Function Definitions ---

def setup_logging():
    """Configures the logging settings for the application."""
    logging.basicConfig(
        filename=LOG_FILE_NAME,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger().addHandler(logging.StreamHandler())

def get_folder_paths_for_extension(extension):
    """
    Finds the main and sub-category names for a given file extension.
    Returns a tuple: (main_category, sub_category).
    """
    ext_lower = extension.lower()
    for main_category, sub_categories in FILE_CATEGORIES.items():
        for sub_category, extensions in sub_categories.items():
            if ext_lower in extensions:
                return main_category, sub_category
    return DEFAULT_CATEGORY, None

def resolve_conflict(destination_path):
    """Generates a unique filename if the target path already exists."""
    if not destination_path.exists():
        return destination_path

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"{destination_path.stem}_{timestamp}{destination_path.suffix}"
    return destination_path.with_name(new_filename)

def process_single_file(file_path, base_dir):
    """
    Processes one file: determines its destination, creates folders, and moves it.
    Returns True on success, False on failure.
    """
    if file_path.is_dir():
        return False, "Skipped (is a directory)"

    extension = file_path.suffix
    if not extension:
        logging.warning(f"Skipping '{file_path.name}' (no file extension).")
        return False, "Skipped (no extension)"

    main_category, sub_category = get_folder_paths_for_extension(extension)

    destination_dir = base_dir / main_category
    if sub_category:
        destination_dir = destination_dir / sub_category

    destination_dir.mkdir(parents=True, exist_ok=True)

    target_path = resolve_conflict(destination_dir / file_path.name)
    log_path = Path(main_category, sub_category) if sub_category else Path(main_category)

    try:
        shutil.move(file_path, target_path)
        logging.info(f"Moved '{file_path.name}' to '{log_path}/'")
        return True, "Moved"
    except (shutil.Error, OSError) as e:
        logging.error(f"Failed to move '{file_path.name}'. Reason: {e}")
        return False, "Failed"

def main():
    """Main function to orchestrate the file organization process."""
    setup_logging()

    source_dir_str = input("Enter the folder path to organize: ").strip()
    source_dir = Path(source_dir_str)

    if not source_dir.is_dir():
        logging.error(f"Error: Path '{source_dir}' is not a valid directory.")
        return

    logging.info(f"--- Starting organization for '{source_dir}' ---")

    stats = {"moved": 0, "failed": 0, "skipped": 0}

    for item in source_dir.iterdir():
        # Avoid processing this script or log file
        if item.name == Path(__file__).name or item.name == LOG_FILE_NAME:
            continue
        if item.is_dir() and item.name in (list(FILE_CATEGORIES.keys()) + [DEFAULT_CATEGORY]):
            continue

        success, status = process_single_file(item, source_dir)
        if success:
            stats["moved"] += 1
        elif "Skipped" in status:
            stats["skipped"] += 1
        else:
            stats["failed"] += 1

    logging.info("--- Organization Complete ---")
    logging.info(f"Summary: {stats['moved']} files moved, {stats['failed']} failed, {stats['skipped']} skipped.")
    print("\n✅ File organization complete. Check 'file_organizer.log' for details.")

if __name__ == "__main__":
    main()
