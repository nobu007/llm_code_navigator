import os
from typing import List, Dict
from app.core.config import settings
from app.utils.ast_utils import extract_imports
from app.core.logging import logger
from app.models.file import FileNode, FileEdge, FileData, FilePath, FileContent
from pathlib import Path


def get_relationships(file_node_list: List[FileNode]) -> List[FileEdge]:
    relationships = []
    for file_node in file_node_list:
        if file_node.children:
            for child in file_node.children:
                relationships.append(FileEdge(source=file_node.name, target=child.name))
    return relationships


def get_file_data() -> FileData:
    try:
        files_info = get_files_info()
        relationships = get_relationships(files_info)
        return FileData(files=files_info, relationships=relationships)
    except FileNotFoundError as e:
        logger.error(f"File not found in get_file_data: {str(e)}")
        raise
    except PermissionError as e:
        logger.error(f"Permission error in get_file_data: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in get_file_data: {str(e)}")
        raise


def get_files_info() -> List[FileNode]:
    try:
        file_path_list = get_python_file_path_list(settings.BACKEND_DIR)
        file_node_list = []

        for i, file_path in enumerate(file_path_list):
            file_node = get_file_info(file_path, file_path_list, i)
            file_node_list.append(file_node)
        logger.info(f"File node list: {file_node_list}")
        return file_node_list
    except Exception as e:
        logger.error(f"Error getting files: {str(e)}")
        raise


def get_file_info(file_path: FilePath, all_file_path_list: List[FilePath], index: int) -> FileNode:
    try:
        imports = extract_imports(file_path.full)
        children = []
        for imp in imports:
            for other_file_path in all_file_path_list:
                if imp in other_file_path.relative:
                    children.append(FileNode(
                        id=str(len(all_file_path_list) + len(children)),
                        name=other_file_path.relative,
                        type='file',
                        children=[]
                    ))
                    break

        full_path = file_path.full
        if not os.path.isabs(full_path):
            full_path = os.path.join(settings.BACKEND_DIR, full_path)

        file_node = FileNode(
            id=str(index),
            name=full_path,
            type='file',
            children=children,
        )

        return file_node
    except Exception as e:
        logger.error(f"Error processing file {file_path.full}: {str(e)}")
        # Return a basic node even if processing fails
        return FileNode(
            id=str(index),
            name=file_path.full,
            type='file',
            children=[],
        )


def get_python_file_path_list(base_dir: str) -> List[FilePath]:
    """Get list of Python files in the specified directory."""
    python_files = []
    
    # Check if directory exists
    if not os.path.exists(base_dir):
        logger.warning(f"Directory does not exist: {base_dir}")
        return python_files
    
    if not os.path.isdir(base_dir):
        logger.warning(f"Path is not a directory: {base_dir}")
        return python_files
    
    try:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, base_dir)
                    python_files.append(FilePath(full=full_path, base=base_dir, relative=relative_path))
    except Exception as e:
        logger.error(f"Error walking directory {base_dir}: {str(e)}")
        
    return python_files


def get_file_content(full_path: str) -> FileContent:
    """
    Retrieve file content with secure path validation and proper encoding handling.
    
    Args:
        full_path: Path to the file to read
        
    Returns:
        FileContent: Object containing file content, path, and encoding information
        
    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If access is denied or path is outside allowed directory
        UnicodeDecodeError: If file encoding cannot be determined
        OSError: For other file system errors
    """
    try:
        # Validate and normalize the path
        validated_path = _validate_file_path(full_path)
        
        # Check if file exists and is accessible
        if not os.path.exists(validated_path):
            raise FileNotFoundError(f"File not found: {validated_path}")
        
        if not os.path.isfile(validated_path):
            raise PermissionError(f"Path is not a file: {validated_path}")
        
        # Check file size to prevent memory issues
        file_size = os.path.getsize(validated_path)
        if file_size > settings.MAX_FILE_SIZE:
            raise PermissionError(f"File too large: {file_size} bytes exceeds limit of {settings.MAX_FILE_SIZE} bytes")
        
        # Check file extension
        file_ext = os.path.splitext(validated_path)[1].lower()
        if file_ext not in settings.ALLOWED_FILE_EXTENSIONS:
            raise PermissionError(f"File extension {file_ext} not allowed")
        
        # Try to read file with different encodings
        content, encoding = _read_file_with_encoding(validated_path)
        
        logger.info(f"Successfully read file: {validated_path} (encoding: {encoding}, size: {file_size} bytes)")
        
        return FileContent(
            content=content,
            path=validated_path,
            encoding=encoding
        )
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise
    except PermissionError as e:
        logger.error(f"Permission error: {str(e)}")
        raise
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading file {full_path}: {str(e)}")
        raise
    except OSError as e:
        logger.error(f"OS error reading file {full_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading file {full_path}: {str(e)}")
        raise


def _validate_file_path(file_path: str) -> str:
    """
    Validate file path to ensure it's within the allowed directory and secure.
    
    Args:
        file_path: Path to validate
        
    Returns:
        str: Validated absolute path
        
    Raises:
        PermissionError: If path is outside allowed directory or contains suspicious patterns
    """
    if not file_path or not file_path.strip():
        raise PermissionError("File path cannot be empty")
    
    # Check for suspicious path patterns first (before any path resolution)
    suspicious_patterns = ['..', '~', '/etc/', '/root/', '/home/', 'C:\\', 'windows\\system32']
    for pattern in suspicious_patterns:
        if pattern in file_path:
            raise PermissionError(f"Suspicious path pattern detected: {pattern}")
    
    # Convert to absolute path and resolve any symbolic links
    try:
        # If it's already an absolute path outside our directory, reject it immediately
        if os.path.isabs(file_path):
            backend_dir = os.path.abspath(settings.BACKEND_DIR)
            if not file_path.startswith(backend_dir):
                raise PermissionError(f"Access denied: Absolute path outside allowed directory")
        
        # For relative paths, join with backend directory
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BACKEND_DIR, file_path)
        
        abs_path = os.path.abspath(file_path)
        resolved_path = os.path.realpath(abs_path)
    except Exception as e:
        raise PermissionError(f"Invalid file path: {str(e)}")
    
    # Ensure the resolved path is within the allowed backend directory
    backend_dir = os.path.abspath(settings.BACKEND_DIR)
    if not resolved_path.startswith(backend_dir):
        raise PermissionError(f"Access denied: Path outside allowed directory. Path: {resolved_path}, Allowed: {backend_dir}")
    
    return resolved_path


def _read_file_with_encoding(file_path: str) -> tuple[str, str]:
    """
    Read file content with automatic encoding detection.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        tuple: (content, encoding) where content is the file content and encoding is the detected encoding
        
    Raises:
        UnicodeDecodeError: If file cannot be decoded with any supported encoding
    """
    # List of encodings to try in order of preference
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except UnicodeDecodeError:
            continue
        except Exception as e:
            # For other errors (like permission errors), re-raise immediately
            raise
    
    # If all encodings failed, raise an error
    raise UnicodeDecodeError(
        'unknown', 
        b'', 
        0, 
        0, 
        f"Could not decode file {file_path} with any of the supported encodings: {encodings}"
    )


def main():
    # for test
    settings.BACKEND_DIR = "./"
    try:
        file_data = get_file_data()
        # ここでfile_dataを用いて何か処理を行う
        logger.info("File data retrieved successfully.")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main()