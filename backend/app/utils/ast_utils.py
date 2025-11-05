import ast
from typing import List, Dict, Optional
from app.core.logging import logger


class ImportInfo:
    """Information about an import statement."""
    
    def __init__(self, module: str, name: Optional[str] = None, alias: Optional[str] = None, 
                 line: int = 0, is_from_import: bool = False):
        self.module = module
        self.name = name
        self.alias = alias
        self.line = line
        self.is_from_import = is_from_import
    
    def __repr__(self):
        return f"ImportInfo(module='{self.module}', name='{self.name}', alias='{self.alias}', line={self.line})"


def extract_imports(content: str, include_details: bool = False) -> List[str]:
    """
    Extract import statements from Python code using AST parsing.
    
    Args:
        content: Python source code as string
        include_details: If True, returns detailed import information
        
    Returns:
        List of imported module names or ImportInfo objects
        
    Raises:
        SyntaxError: When the Python code has syntax errors
    """
    if not content or not content.strip():
        logger.warning("Empty content provided to extract_imports")
        return []
    
    try:
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Handle: import module, import module as alias
                for alias in node.names:
                    if include_details:
                        imports.append(ImportInfo(
                            module=alias.name,
                            alias=alias.asname,
                            line=node.lineno,
                            is_from_import=False
                        ))
                    else:
                        imports.append(alias.name)
                        
            elif isinstance(node, ast.ImportFrom):
                # Handle: from module import name, from module import name as alias
                module = node.module if node.module else ''
                
                for alias in node.names:
                    if alias.name == '*':
                        # Handle wildcard imports: from module import *
                        if include_details:
                            imports.append(ImportInfo(
                                module=module,
                                name='*',
                                line=node.lineno,
                                is_from_import=True
                            ))
                        else:
                            imports.append(module)
                    else:
                        if include_details:
                            imports.append(ImportInfo(
                                module=module,
                                name=alias.name,
                                alias=alias.asname,
                                line=node.lineno,
                                is_from_import=True
                            ))
                        else:
                            # For dependency analysis, we care about the module being imported from
                            if module:
                                imports.append(module)
                            else:
                                # Relative imports
                                imports.append(alias.name)
        
        return imports
        
    except SyntaxError as e:
        logger.error(f"Syntax error in Python file at line {e.lineno}: {e.msg}")
        raise SyntaxError(f"Invalid Python syntax at line {e.lineno}: {e.msg}")
    except Exception as e:
        logger.error(f"Unexpected error parsing Python code: {str(e)}")
        raise ValueError(f"Failed to parse Python code: {str(e)}")


def get_import_dependencies(content: str) -> List[str]:
    """
    Extract module dependencies from Python code for dependency graph creation.
    
    Args:
        content: Python source code as string
        
    Returns:
        List of module names that this code depends on
    """
    try:
        imports = extract_imports(content, include_details=False)
        
        # Filter out standard library and built-in modules for cleaner dependency graphs
        # Focus on local/project imports
        dependencies = []
        for imp in imports:
            # Skip standard library modules (basic filtering)
            if not _is_standard_library_module(imp):
                dependencies.append(imp)
        
        return list(set(dependencies))  # Remove duplicates
        
    except (SyntaxError, ValueError):
        # Return empty list if parsing fails
        return []


def _is_standard_library_module(module_name: str) -> bool:
    """
    Basic check to identify standard library modules.
    This is a simplified approach - in production, you might want a more comprehensive list.
    """
    standard_modules = {
        'os', 'sys', 'json', 'ast', 'typing', 'pathlib', 'subprocess', 
        'logging', 'datetime', 'collections', 'itertools', 'functools',
        'urllib', 'http', 're', 'math', 'random', 'time', 'io'
    }
    
    # Check if it's a standard library module or starts with standard library prefix
    base_module = module_name.split('.')[0]
    return base_module in standard_modules
