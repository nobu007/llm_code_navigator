import ast
from app.core.logging import logger

def extract_imports(content):
    try:
        tree = ast.parse(content)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports
    except SyntaxError:
        logger.error(f"Syntax error in Python file")
        return []