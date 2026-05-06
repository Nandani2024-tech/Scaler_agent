import os

def normalize_path(file_path: str) -> str:
    """
    Ensures all files are written ONLY inside /output directory.
    Fixes Windows/Linux path issues and prevents nested output folders.
    """
    if not file_path:
        return file_path

    # Normalize slashes
    file_path = file_path.replace("\\", "/")

    # Extract only filename if model sends weird paths
    file_name = os.path.basename(file_path)

    # Force into output directory
    normalized = os.path.join("output", file_name)
    
    print(f"\033[1;30m[DEBUG][PATH] Normalized path: {normalized}\033[0m")
    return normalized

def create_folder(folder_path: str) -> str:
    """Creates a folder at the given path."""
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Successfully created folder: {folder_path}"
    except Exception as e:
        return f"Error creating folder {folder_path}: {str(e)}"

def create_file(file_path: str = None, content: str = "", file_name: str = None) -> str:
    """
    Creates a new file with the given content. 
    Always overwrites if the file exists.
    """
    final_path = file_path if file_path else file_name
    if not final_path:
        return "Error: No file path provided."
        
    final_path = normalize_path(final_path)
        
    try:
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully created file: {final_path} ({len(content)} bytes written)"
    except Exception as e:
        return f"Error creating file {final_path}: {str(e)}"

def append_file(file_path: str, content: str) -> str:
    """
    Appends content to an existing file.
    Creates the file if it doesn't exist.
    """
    file_path = normalize_path(file_path)
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully appended to file: {file_path} ({len(content)} bytes added)"
    except Exception as e:
        return f"Error appending to file {file_path}: {str(e)}"
