import os
from typing import Any
from python.helpers.files import VariablesPlugin
from python.helpers import files
from python.helpers.print_style import PrintStyle


class CallSubordinate(VariablesPlugin):
    def get_variables(self, file: str, backup_dirs: list[str] | None = None) -> dict[str, Any]:

        # collect all prompt folders in order of their priority
        folder = files.get_abs_path(os.path.dirname(file))
        folders = [folder]
        if backup_dirs:
            for backup_dir in backup_dirs:
                folders.append(files.get_abs_path(backup_dir))

        # Also search in subdirectories (like adversys/)
        # Get all subdirectories in the prompt folders
        all_folders = list(folders)
        for folder_path in folders:
            try:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isdir(item_path):
                        all_folders.append(item_path)
            except Exception:
                pass

        # collect all tool instruction files from all folders (including subdirectories)
        prompt_files = files.get_unique_filenames_in_dirs(all_folders, "agent.system.tool.*.md")
        
        # load tool instructions
        tools = []
        for prompt_file in prompt_files:
            try:
                tool = files.read_prompt_file(prompt_file)
                tools.append(tool)
            except Exception as e:
                PrintStyle().error(f"Error loading tool '{prompt_file}': {e}")

        return {"tools": "\n\n".join(tools)}
