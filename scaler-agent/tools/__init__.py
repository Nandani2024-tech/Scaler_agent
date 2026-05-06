from .file_tools import create_folder, create_file, append_file
from .browser_tools import open_in_browser

tool_map = {
    "create_folder": create_folder,
    "create_file": create_file,
    "append_file": append_file,
    "open_in_browser": open_in_browser
}
