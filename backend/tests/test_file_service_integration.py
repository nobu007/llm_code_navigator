#!/usr/bin/env python3
"""
Integration tests for file services.
Tests file scanning, dependency extraction, and security path validation.
Requirements: 1.5, 5.2
"""

import os
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.file_service import (
    get_file_data, 
    get_files_info, 
    get_file_content,
    get_python_file_path_list,
    _validate_file_path
)
from app.models.file import FileData, FileNode, FileEdge, FileContent
from app.core.config import settings


class TestFileServiceIntegration(unittest.TestCase):
    """Integration tests for file service functionality."""
    
    def setUp(self):
        """Set up test fixtures with sample Python files."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.original_backend_dir = settings.BACKEND_DIR
        
        # Override backend directory for testing
        settings.BACKEND_DIR = self.test_dir
        
        # Create test file structure
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original backend directory
        settings.BACKEND_DIR = self.original_backend_dir
        
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create sample Python files for testing."""
        # Main module file
        main_content = '''#!/usr/bin/env python3
"""Main module for testing."""
import os
import sys
from utils.helper import process_data
from models.user import User
import external_lib

def main():
    """Main function."""
    user = User("test")
    data = process_data(user.name)
    print(f"Processed: {data}")

if __name__ == "__main__":
    main()
'''
        
        # Helper utility file
        utils_dir = os.path.join(self.test_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        helper_content = '''"""Helper utilities."""
import json
from typing import Any

def process_data(data: Any) -> str:
    """Process input data."""
    return json.dumps({"processed": str(data)})

def validate_input(value: str) -> bool:
    """Validate input value."""
    return len(value) > 0
'''
        
        # Model file
        models_dir = os.path.join(self.test_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        user_content = '''"""User model."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """User data class."""
    name: str
    email: Optional[str] = None
    
    def __str__(self) -> str:
        return f"User({self.name})"
'''
        
        # Write test files
        with open(os.path.join(self.test_dir, "main.py"), "w") as f:
            f.write(main_content)
        
        with open(os.path.join(utils_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(utils_dir, "helper.py"), "w") as f:
            f.write(helper_content)
        
        with open(os.path.join(models_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(models_dir, "user.py"), "w") as f:
            f.write(user_content)
    
    def test_file_scanning_and_discovery(self):
        """Test file scanning functionality."""
        # Test python file discovery
        python_files = get_python_file_path_list(self.test_dir)
        
        # Should find all .py files
        expected_files = {
            "main.py",
            "utils/__init__.py",
            "utils/helper.py",
            "models/__init__.py",
            "models/user.py"
        }
        
        found_files = {os.path.relpath(f.full, self.test_dir) for f in python_files}
        self.assertEqual(found_files, expected_files)
        
        # Verify file path structure
        for file_path in python_files:
            self.assertTrue(file_path.full.startswith(self.test_dir))
            self.assertEqual(file_path.base, self.test_dir)
            self.assertTrue(file_path.relative.endswith('.py'))
    
    def test_dependency_extraction(self):
        """Test dependency extraction from Python files."""
        # Get file information with dependencies
        files_info = get_files_info()
        
        # Should have files with proper structure
        self.assertIsInstance(files_info, list)
        self.assertGreater(len(files_info), 0)
        
        # Find main.py file node
        main_file_node = None
        for file_node in files_info:
            if file_node.name.endswith("main.py"):
                main_file_node = file_node
                break
        
        self.assertIsNotNone(main_file_node)
        self.assertEqual(main_file_node.type, "file")
        
        # Verify file data structure
        file_data = get_file_data()
        self.assertIsInstance(file_data, FileData)
        self.assertIsInstance(file_data.files, list)
        self.assertIsInstance(file_data.relationships, list)
        
        # Should have relationships between files
        self.assertGreater(len(file_data.files), 0)
    
    def test_file_content_retrieval(self):
        """Test secure file content retrieval."""
        # Test reading valid file
        main_file_path = os.path.join(self.test_dir, "main.py")
        file_content = get_file_content(main_file_path)
        
        self.assertIsInstance(file_content, FileContent)
        self.assertIn("def main():", file_content.content)
        self.assertEqual(file_content.encoding, "utf-8")
        self.assertEqual(file_content.path, main_file_path)
        
        # Test reading file from subdirectory
        helper_file_path = os.path.join(self.test_dir, "utils", "helper.py")
        helper_content = get_file_content(helper_file_path)
        
        self.assertIsInstance(helper_content, FileContent)
        self.assertIn("def process_data", helper_content.content)
    
    def test_security_path_validation(self):
        """Test security path validation functionality."""
        # Test valid paths within backend directory
        valid_path = os.path.join(self.test_dir, "main.py")
        validated = _validate_file_path(valid_path)
        self.assertTrue(validated.startswith(self.test_dir))
        
        # Test path traversal attempts
        with self.assertRaises(PermissionError):
            _validate_file_path("../../../etc/passwd")
        
        with self.assertRaises(PermissionError):
            _validate_file_path("..\\..\\windows\\system32\\config")
        
        with self.assertRaises(PermissionError):
            _validate_file_path("/etc/passwd")
        
        # Test empty path
        with self.assertRaises(PermissionError):
            _validate_file_path("")
        
        with self.assertRaises(PermissionError):
            _validate_file_path("   ")
        
        # Test suspicious patterns
        with self.assertRaises(PermissionError):
            _validate_file_path("~/secret_file.py")
    
    def test_file_access_outside_backend_directory(self):
        """Test that files outside backend directory are blocked."""
        # Create a file outside the backend directory
        outside_dir = tempfile.mkdtemp()
        outside_file = os.path.join(outside_dir, "outside.py")
        
        try:
            with open(outside_file, "w") as f:
                f.write("print('This should not be accessible')")
            
            # Attempt to access file outside backend directory
            with self.assertRaises(PermissionError):
                get_file_content(outside_file)
        
        finally:
            # Clean up
            if os.path.exists(outside_dir):
                shutil.rmtree(outside_dir)
    
    def test_file_not_found_handling(self):
        """Test handling of non-existent files."""
        non_existent_path = os.path.join(self.test_dir, "non_existent.py")
        
        with self.assertRaises(FileNotFoundError):
            get_file_content(non_existent_path)
    
    def test_large_file_handling(self):
        """Test handling of files that exceed size limits."""
        # Create a large file that exceeds the limit
        large_file_path = os.path.join(self.test_dir, "large_file.py")
        
        # Mock the file size check to simulate a large file
        with patch('os.path.getsize', return_value=settings.MAX_FILE_SIZE + 1):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.isfile', return_value=True):
                    with self.assertRaises(PermissionError) as context:
                        get_file_content(large_file_path)
                    
                    self.assertIn("File too large", str(context.exception))
    
    def test_invalid_file_extension_handling(self):
        """Test handling of files with invalid extensions."""
        # Create a file with invalid extension
        invalid_file_path = os.path.join(self.test_dir, "test.txt")
        
        with open(invalid_file_path, "w") as f:
            f.write("This is a text file")
        
        with self.assertRaises(PermissionError) as context:
            get_file_content(invalid_file_path)
        
        self.assertIn("File extension .txt not allowed", str(context.exception))
    
    def test_syntax_error_handling(self):
        """Test handling of Python files with syntax errors."""
        # Create a file with syntax error for this specific test
        error_content = '''"""File with syntax error."""
def broken_function(
    # Missing closing parenthesis and colon
    pass
'''
        syntax_error_path = os.path.join(self.test_dir, "syntax_error.py")
        with open(syntax_error_path, "w") as f:
            f.write(error_content)
        
        # The file service should handle syntax errors gracefully
        # When a syntax error occurs during import extraction, it should raise an exception
        with self.assertRaises(Exception):
            get_files_info()
        
        # However, we should still be able to read the file content
        content = get_file_content(syntax_error_path)
        self.assertIsInstance(content, FileContent)
        self.assertIn("broken_function", content.content)


if __name__ == '__main__':
    unittest.main()