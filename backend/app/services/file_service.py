import os
from app.core.config import settings
from app.utils.ast_utils import extract_imports
from app.core.logging import logger

def get_python_files(directory):
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                python_files.append(relative_path)
    return python_files

def get_files_info():
    try:
        files = get_python_files(settings.BACKEND_DIR)
        nodes = [{"id": f, "label": f} for f in files]
        edges = []

        for file in files:
            with open(os.path.join(settings.BACKEND_DIR, file), 'r') as f:
                content = f.read()
                imports = extract_imports(content)
                for imp in imports:
                    for target in files:
                        if target.replace('/', '.').replace('.py', '') == imp:
                            edges.append({"source": file, "target": target})
        files_info={"nodes": nodes, "edges": edges}
        print("files_info=",files_info)

        return files_info
    except Exception as e:
        logger.error(f"Error getting files: {str(e)}")
        raise

def get_file_content(file_path: str):
    try:
        full_path = os.path.join(settings.BACKEND_DIR, file_path)
        if not full_path.startswith(settings.BACKEND_DIR):
            raise PermissionError("Access denied")

        with open(full_path, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise