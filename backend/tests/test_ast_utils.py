import unittest
from app.utils.ast_utils import extract_imports, get_import_dependencies, ImportInfo


class TestAstUtils(unittest.TestCase):
    """Test cases for AST utility functions."""

    def test_extract_imports_simple_import(self):
        """Test extraction of simple import statements."""
        code = "import os\nimport sys"
        imports = extract_imports(code)
        self.assertIn("os", imports)
        self.assertIn("sys", imports)

    def test_extract_imports_from_import(self):
        """Test extraction of from-import statements."""
        code = "from pathlib import Path\nfrom typing import List"
        imports = extract_imports(code)
        self.assertIn("pathlib", imports)
        self.assertIn("typing", imports)

    def test_extract_imports_with_alias(self):
        """Test extraction of imports with aliases."""
        code = "import numpy as np\nfrom pandas import DataFrame as df"
        imports = extract_imports(code)
        self.assertIn("numpy", imports)
        self.assertIn("pandas", imports)

    def test_extract_imports_wildcard(self):
        """Test extraction of wildcard imports."""
        code = "from os import *"
        imports = extract_imports(code)
        self.assertIn("os", imports)

    def test_extract_imports_detailed(self):
        """Test extraction with detailed information."""
        code = "import os\nfrom pathlib import Path as P"
        imports = extract_imports(code, include_details=True)
        
        self.assertEqual(len(imports), 2)
        self.assertIsInstance(imports[0], ImportInfo)
        
        # Check first import (import os)
        os_import = imports[0]
        self.assertEqual(os_import.module, "os")
        self.assertIsNone(os_import.name)
        self.assertFalse(os_import.is_from_import)
        
        # Check second import (from pathlib import Path as P)
        path_import = imports[1]
        self.assertEqual(path_import.module, "pathlib")
        self.assertEqual(path_import.name, "Path")
        self.assertEqual(path_import.alias, "P")
        self.assertTrue(path_import.is_from_import)

    def test_extract_imports_empty_content(self):
        """Test extraction from empty content."""
        imports = extract_imports("")
        self.assertEqual(imports, [])

    def test_extract_imports_no_imports(self):
        """Test extraction from code with no imports."""
        code = "def hello():\n    print('Hello, World!')"
        imports = extract_imports(code)
        self.assertEqual(imports, [])

    def test_extract_imports_syntax_error(self):
        """Test extraction from code with syntax errors."""
        code = "import os\ndef invalid_syntax(\n    pass"  # Missing closing parenthesis
        with self.assertRaises(SyntaxError):
            extract_imports(code)

    def test_extract_imports_complex_code(self):
        """Test extraction from complex code with multiple import types."""
        code = """
import os
import sys as system
from pathlib import Path
from typing import List, Dict
from collections import defaultdict as dd
from . import local_module
from ..parent import parent_module
"""
        imports = extract_imports(code)
        expected_imports = ["os", "sys", "pathlib", "typing", "collections"]
        
        for expected in expected_imports:
            self.assertIn(expected, imports)

    def test_get_import_dependencies_basic(self):
        """Test dependency extraction for basic imports."""
        code = """
import custom_module
from my_package import something
import os  # This should be filtered out as standard library
"""
        dependencies = get_import_dependencies(code)
        self.assertIn("custom_module", dependencies)
        self.assertIn("my_package", dependencies)
        self.assertNotIn("os", dependencies)  # Standard library should be filtered

    def test_get_import_dependencies_no_duplicates(self):
        """Test that dependencies don't contain duplicates."""
        code = """
import custom_module
from custom_module import something
import custom_module as cm
"""
        dependencies = get_import_dependencies(code)
        # Should only appear once despite multiple import statements
        self.assertEqual(dependencies.count("custom_module"), 1)

    def test_get_import_dependencies_syntax_error(self):
        """Test dependency extraction with syntax errors."""
        code = "import os\ndef invalid("  # Syntax error
        dependencies = get_import_dependencies(code)
        self.assertEqual(dependencies, [])  # Should return empty list on error

    def test_get_import_dependencies_empty_code(self):
        """Test dependency extraction from empty code."""
        dependencies = get_import_dependencies("")
        self.assertEqual(dependencies, [])

    def test_import_info_repr(self):
        """Test ImportInfo string representation."""
        info = ImportInfo(module="test_module", name="TestClass", alias="TC", line=5)
        repr_str = repr(info)
        self.assertIn("test_module", repr_str)
        self.assertIn("TestClass", repr_str)
        self.assertIn("TC", repr_str)
        self.assertIn("5", repr_str)

    def test_standard_library_filtering(self):
        """Test that standard library modules are properly filtered."""
        code = """
import os
import sys
import json
import custom_module
from pathlib import Path
from my_package import MyClass
"""
        dependencies = get_import_dependencies(code)
        
        # Standard library modules should be filtered out
        standard_modules = ["os", "sys", "json", "pathlib"]
        for module in standard_modules:
            self.assertNotIn(module, dependencies)
        
        # Custom modules should be included
        self.assertIn("custom_module", dependencies)
        self.assertIn("my_package", dependencies)

    def test_extract_imports_relative_imports(self):
        """Test extraction of relative imports."""
        code = """
from . import local_module
from ..parent import parent_module
from ...grandparent import gp_module
"""
        imports = extract_imports(code, include_details=True)
        
        self.assertEqual(len(imports), 3)
        
        # Check relative imports - AST parser returns None for relative imports without module
        local_import = imports[0]
        self.assertEqual(local_import.module, "")  # AST returns None, converted to empty string
        self.assertEqual(local_import.name, "local_module")
        self.assertTrue(local_import.is_from_import)
        
        # For relative imports with module names, AST returns the module name
        parent_import = imports[1]
        self.assertEqual(parent_import.module, "parent")  # AST returns "parent" for ..parent
        self.assertEqual(parent_import.name, "parent_module")
        
        gp_import = imports[2]
        self.assertEqual(gp_import.module, "grandparent")  # AST returns "grandparent" for ...grandparent
        self.assertEqual(gp_import.name, "gp_module")

    def test_extract_imports_multiple_names_from_import(self):
        """Test extraction of multiple names from single import statement."""
        code = "from typing import List, Dict, Optional, Union as U"
        imports = extract_imports(code, include_details=True)
        
        self.assertEqual(len(imports), 4)
        
        # Check all imports are from typing module
        for imp in imports:
            self.assertEqual(imp.module, "typing")
            self.assertTrue(imp.is_from_import)
        
        # Check specific names
        names = [imp.name for imp in imports]
        self.assertIn("List", names)
        self.assertIn("Dict", names)
        self.assertIn("Optional", names)
        self.assertIn("Union", names)
        
        # Check alias
        union_import = next(imp for imp in imports if imp.name == "Union")
        self.assertEqual(union_import.alias, "U")

    def test_extract_imports_mixed_import_styles(self):
        """Test extraction from code with mixed import styles."""
        code = """
import os, sys
from pathlib import Path, PurePath
import json as j
from typing import List as L, Dict
"""
        imports = extract_imports(code)
        
        expected_modules = ["os", "sys", "pathlib", "json", "typing"]
        for module in expected_modules:
            self.assertIn(module, imports)

    def test_extract_imports_with_comments_and_strings(self):
        """Test extraction ignores imports in comments and strings."""
        code = '''
import real_module
# import fake_module_in_comment
"""
This is a docstring with import fake_module_in_docstring
"""
def function():
    """Another docstring with from fake import something"""
    return "import fake_module_in_string"
'''
        imports = extract_imports(code)
        
        # Only real import should be extracted
        self.assertEqual(len(imports), 1)
        self.assertIn("real_module", imports)
        self.assertNotIn("fake_module_in_comment", imports)
        self.assertNotIn("fake_module_in_docstring", imports)
        self.assertNotIn("fake_module_in_string", imports)

    def test_extract_imports_value_error_handling(self):
        """Test handling of unexpected parsing errors."""
        # This should trigger the general exception handler
        # We'll mock ast.parse to raise an unexpected error
        import unittest.mock
        
        with unittest.mock.patch('ast.parse') as mock_parse:
            mock_parse.side_effect = ValueError("Unexpected error")
            
            with self.assertRaises(ValueError) as context:
                extract_imports("import os")
            
            self.assertIn("Failed to parse Python code", str(context.exception))

    def test_get_import_dependencies_with_duplicates_complex(self):
        """Test dependency extraction with complex duplicate scenarios."""
        code = """
import custom_module
from custom_module import something
from custom_module.submodule import other
import another_module
from another_module import func
"""
        dependencies = get_import_dependencies(code)
        
        # Should contain each module only once
        self.assertIn("custom_module", dependencies)
        self.assertIn("another_module", dependencies)
        
        # Count occurrences
        custom_count = dependencies.count("custom_module")
        another_count = dependencies.count("another_module")
        
        self.assertEqual(custom_count, 1)
        self.assertEqual(another_count, 1)

    def test_is_standard_library_module_edge_cases(self):
        """Test standard library module detection with edge cases."""
        from app.utils.ast_utils import _is_standard_library_module
        
        # Test standard modules
        self.assertTrue(_is_standard_library_module("os"))
        self.assertTrue(_is_standard_library_module("sys"))
        self.assertTrue(_is_standard_library_module("json"))
        
        # Test submodules of standard library
        self.assertTrue(_is_standard_library_module("os.path"))
        self.assertTrue(_is_standard_library_module("urllib.parse"))
        
        # Test custom modules
        self.assertFalse(_is_standard_library_module("custom_module"))
        self.assertFalse(_is_standard_library_module("my_package"))
        self.assertFalse(_is_standard_library_module("django"))


if __name__ == '__main__':
    unittest.main()