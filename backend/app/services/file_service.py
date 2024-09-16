import os
from typing import List, Dict
from app.core.config import settings
from app.utils.ast_utils import extract_imports
from app.core.logging import logger
from app.models.file import FileNode, FileEdge, FileData, FilePath
from pathlib import Path


def get_relationships(file_node_list: List[FileNode]) -> List[FileEdge]:
    relationships = []
    for file_node in file_node_list:
        if file_node.children:
            for child in file_node.children:
                relationships.append(FileEdge(source=file_node.name, target=child))
    return relationships


def get_file_data() -> FileData:
    try:
        files_info = get_files_info()
        relationships = get_relationships(files_info)
        return FileData(files=files_info, relationships=relationships)
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
        print("file_node_list=", file_node_list)
        return file_node_list
    except Exception as e:
        logger.error(f"Error getting files: {str(e)}")
        raise


def get_file_info(file_path: FilePath, all_file_path_list: List[FilePath], index: int) -> FileNode:
    # ファイルの基本情報を取得
    full_path = file_path.full
    path = Path(full_path)
    if not path.exists():
        raise FileNotFoundError(f"{full_path} does not exist.")

    # インポートを抽出する
    with open(full_path, 'r') as f:
        content = f.read()
        imports = extract_imports(content)  # ここでインポートを抽出

    # 絶対パスを取得
    children = []
    for imp in imports:
        # インポート文を絶対パスに変換
        normalized_import = imp.replace('.', '/').replace('_', '.')
        for target_file_path in all_file_path_list:
            target = target_file_path.full
            if normalized_import == target.replace('/', '.').replace('.py', ''):
                # 絶対パスを追加
                children.append(str(Path(full_path).parent / target))

    file_node = FileNode(
        id=str(index) + "_" + path.name,  # IDとしてファイルのパスを使用
        name=full_path,
        type='file',
        children=children,
    )

    return file_node


def get_python_file_path_list(base_dir: str) -> List[FilePath]:
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, base_dir)
                python_files.append(FilePath(full=full_path, base=base_dir, relative=relative_path))
    return python_files


def get_file_content(full_path: str) -> str:
    try:
        if not os.path.abspath(full_path).startswith(os.path.abspath(settings.BACKEND_DIR)):
            raise PermissionError("Access denied")

        with open(full_path, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except PermissionError as e:
        logger.error(f"Permission error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise


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
