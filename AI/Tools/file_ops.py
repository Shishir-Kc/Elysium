import os
import subprocess
from pathlib import Path
from langchain.tools import tool


@tool
def read_file(file_path: str) -> str:
    """
    Read the contents of a file from the filesystem.

    Args:
        file_path: The absolute path to the file to read.

    Returns:
        The contents of the file as a string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"Successfully read file: {file_path}\n\n---FILE CONTENTS---\n{content}\n---END FILE---"
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file. Creates the file if it doesn't exist.

    Args:
        file_path: The absolute path to the file to write.
        content: The content to write to the file.

    Returns:
        Success or error message.
    """
    try:
        file_path = os.path.abspath(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to file: {file_path}\nFile size: {len(content)} characters"
    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"


@tool
def append_to_file(file_path: str, content: str) -> str:
    """
    Append content to a file. Creates the file if it doesn't exist.

    Args:
        file_path: The absolute path to the file to append to.
        content: The content to append to the file.

    Returns:
        Success or error message.
    """
    try:
        file_path = os.path.abspath(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully appended to file: {file_path}\nAppended {len(content)} characters"
    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error appending to file {file_path}: {str(e)}"


@tool
def list_directory(dir_path: str = ".") -> str:
    """
    List the contents of a directory.

    Args:
        dir_path: The path to the directory to list. Defaults to current directory.

    Returns:
        A formatted list of files and directories.
    """
    try:
        dir_path = os.path.abspath(dir_path)
        if not os.path.isdir(dir_path):
            return f"Error: Not a directory: {dir_path}"

        items = []
        for item in sorted(os.listdir(dir_path)):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                items.append(f"📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                items.append(f"📄 {item} ({size} bytes)")

        if not items:
            return f"Directory is empty: {dir_path}"

        return f"Contents of {dir_path}:\n" + "\n".join(items)
    except PermissionError:
        return f"Error: Permission denied: {dir_path}"
    except Exception as e:
        return f"Error listing directory {dir_path}: {str(e)}"


@tool
def get_file_info(file_path: str) -> str:
    """
    Get detailed information about a file or directory.

    Args:
        file_path: The path to the file or directory.

    Returns:
        File/directory information including size, modified time, etc.
    """
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            return f"Error: Path does not exist: {file_path}"

        stat = os.stat(file_path)
        file_type = "Directory" if os.path.isdir(file_path) else "File"

        info = f"""
Path: {file_path}
Type: {file_type}
Size: {stat.st_size} bytes
Created: {stat.st_ctime}
Modified: {stat.st_mtime}
Accessed: {stat.st_atime}
"""
        return info.strip()
    except Exception as e:
        return f"Error getting file info: {str(e)}"


@tool
def execute_command(command: str) -> str:
    """
    Execute a shell command and return the output.

    Args:
        command: The shell command to execute.

    Returns:
        The stdout/stderr output of the command.
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=60
        )

        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Exit code: {result.returncode}")

        if not output:
            return "Command executed successfully with no output"

        return "\n\n".join(output)
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool
def create_directory(dir_path: str) -> str:
    """
    Create a new directory.

    Args:
        dir_path: The path of the directory to create.

    Returns:
        Success or error message.
    """
    try:
        dir_path = os.path.abspath(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        return f"Successfully created directory: {dir_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


@tool
def delete_file(file_path: str) -> str:
    """
    Delete a file or empty directory.

    Args:
        file_path: The path to the file or directory to delete.

    Returns:
        Success or error message.
    """
    try:
        file_path = os.path.abspath(file_path)
        if os.path.isdir(file_path):
            os.rmdir(file_path)
            return f"Successfully deleted directory: {file_path}"
        else:
            os.remove(file_path)
            return f"Successfully deleted file: {file_path}"
    except Exception as e:
        return f"Error deleting: {str(e)}"


@tool
def search_files(directory: str, pattern: str) -> str:
    """
    Search for files matching a pattern in a directory.

    Args:
        directory: The directory to search in.
        pattern: The pattern to search for (substring match).

    Returns:
        List of matching file paths.
    """
    try:
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            return f"Error: Not a directory: {directory}"

        matches = []
        pattern_lower = pattern.lower()

        for root, dirs, files in os.walk(directory):
            for name in files + dirs:
                if pattern_lower in name.lower():
                    full_path = os.path.join(root, name)
                    matches.append(full_path)

        if not matches:
            return f"No files matching '{pattern}' found in {directory}"

        return f"Found {len(matches)} matches for '{pattern}':\n" + "\n".join(matches)
    except Exception as e:
        return f"Error searching files: {str(e)}"
