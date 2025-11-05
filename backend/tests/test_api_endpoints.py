#!/usr/bin/env python3
"""
Integration tests for all API endpoints.
Tests error scenarios, edge cases, and proper HTTP status codes and response formats.
Requirements: 5.4
"""

import os
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


class TestAPIEndpoints(unittest.TestCase):
    """Integration tests for API endpoints."""
    
    def setUp(self):
        """Set up test fixtures and client."""
        # Create test client with custom headers to bypass TrustedHostMiddleware
        self.client = TestClient(app, headers={"host": "localhost"})
        
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

def main():
    """Main function."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
        
        # Helper utility file
        utils_dir = os.path.join(self.test_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        helper_content = '''"""Helper utilities."""
import json

def process_data(data):
    """Process input data."""
    return json.dumps({"processed": str(data)})
'''
        
        # Write test files
        with open(os.path.join(self.test_dir, "main.py"), "w") as f:
            f.write(main_content)
        
        with open(os.path.join(utils_dir, "__init__.py"), "w") as f:
            f.write("")
        
        with open(os.path.join(utils_dir, "helper.py"), "w") as f:
            f.write(helper_content)

    # Root endpoint tests
    def test_root_endpoint_success(self):
        """Test root endpoint returns welcome message."""
        response = self.client.get("/api/root/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Welcome to the LLM Code Navigator API")

    def test_health_endpoint_success(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("project", data)
        self.assertIn("backend_dir", data)

    # Files endpoint tests
    def test_files_info_endpoint_success(self):
        """Test files info endpoint returns proper file data structure."""
        response = self.client.get("/api/files/files_info")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure matches FileData model
        self.assertIn("files", data)
        self.assertIn("relationships", data)
        self.assertIsInstance(data["files"], list)
        self.assertIsInstance(data["relationships"], list)
        
        # Should have at least our test files
        self.assertGreater(len(data["files"]), 0)

    def test_files_info_endpoint_error_handling(self):
        """Test files info endpoint error handling."""
        # Mock file service to raise exception
        with patch('app.api.endpoints.files.get_file_data') as mock_get_data:
            mock_get_data.side_effect = Exception("Service error")
            
            response = self.client.get("/api/files/files_info")
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn("error", data)

    def test_file_content_endpoint_success(self):
        """Test file content endpoint returns proper file content."""
        file_path = os.path.join(self.test_dir, "main.py")
        
        response = self.client.get(f"/api/files/file_content/{file_path}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure matches FileContent model
        self.assertIn("content", data)
        self.assertIn("path", data)
        self.assertIn("encoding", data)
        
        # Verify content
        self.assertIn("def main():", data["content"])
        self.assertEqual(data["path"], file_path)
        self.assertEqual(data["encoding"], "utf-8")

    def test_file_content_endpoint_file_not_found(self):
        """Test file content endpoint with non-existent file."""
        non_existent_path = os.path.join(self.test_dir, "non_existent.py")
        
        response = self.client.get(f"/api/files/file_content/{non_existent_path}")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("File not found", data["error"])

    def test_file_content_endpoint_access_denied(self):
        """Test file content endpoint with path outside backend directory."""
        # Try to access file outside backend directory
        outside_path = "/etc/passwd"
        
        response = self.client.get(f"/api/files/file_content/{outside_path}")
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("Access denied", data["error"])

    def test_file_content_endpoint_path_traversal_attack(self):
        """Test file content endpoint blocks path traversal attacks."""
        # Try various path traversal patterns (URL encoded to avoid routing issues)
        traversal_paths = [
            "..%2F..%2F..%2Fetc%2Fpasswd",  # ../../../etc/passwd
            "..%5C..%5C..%5Cwindows%5Csystem32%5Cconfig",  # ..\..\..\windows\system32\config
            "~%2Fsecret_file.py"  # ~/secret_file.py
        ]
        
        for path in traversal_paths:
            response = self.client.get(f"/api/files/file_content/{path}")
            
            self.assertEqual(response.status_code, 403)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("Access denied", data["error"])

    def test_file_content_endpoint_invalid_extension(self):
        """Test file content endpoint with invalid file extension."""
        # Create a file with invalid extension
        invalid_file_path = os.path.join(self.test_dir, "test.txt")
        with open(invalid_file_path, "w") as f:
            f.write("This is a text file")
        
        response = self.client.get(f"/api/files/file_content/{invalid_file_path}")
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("Access denied", data["error"])

    def test_file_content_endpoint_unicode_error(self):
        """Test file content endpoint with unicode decode error."""
        # Mock file service to raise UnicodeDecodeError
        with patch('app.api.endpoints.files.get_file_content') as mock_get_content:
            mock_get_content.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')
            
            file_path = os.path.join(self.test_dir, "main.py")
            response = self.client.get(f"/api/files/file_content/{file_path}")
            
            self.assertEqual(response.status_code, 422)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("File encoding error", data["error"])

    def test_file_content_endpoint_os_error(self):
        """Test file content endpoint with OS error."""
        # Mock file service to raise OSError
        with patch('app.api.endpoints.files.get_file_content') as mock_get_content:
            mock_get_content.side_effect = OSError("Disk error")
            
            file_path = os.path.join(self.test_dir, "main.py")
            response = self.client.get(f"/api/files/file_content/{file_path}")
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("File system error", data["error"])

    def test_file_content_endpoint_general_error(self):
        """Test file content endpoint with general exception."""
        # Mock file service to raise general exception
        with patch('app.api.endpoints.files.get_file_content') as mock_get_content:
            mock_get_content.side_effect = Exception("Unexpected error")
            
            file_path = os.path.join(self.test_dir, "main.py")
            response = self.client.get(f"/api/files/file_content/{file_path}")
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn("error", data)

    # PMD endpoint tests
    def test_pmd_analysis_endpoint_success(self):
        """Test PMD analysis endpoint returns proper analysis results."""
        file_path = os.path.join(self.test_dir, "main.py")
        
        # Mock PMD service to return successful result
        mock_result = {
            "violations": [
                {
                    "rule": "UnusedImport",
                    "priority": 3,
                    "message": "Unused import 'sys'",
                    "line": 3,
                    "column": 1
                }
            ],
            "summary": {
                "totalViolations": 1,
                "fileAnalyzed": file_path
            }
        }
        
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            mock_pmd.return_value = mock_result
            
            response = self.client.get(f"/api/pmd/analysis/{file_path}")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify response structure matches PmdResult model
            self.assertIn("violations", data)
            self.assertIn("summary", data)
            self.assertIsInstance(data["violations"], list)
            self.assertIsInstance(data["summary"], dict)

    def test_pmd_analysis_endpoint_access_denied(self):
        """Test PMD analysis endpoint with path outside backend directory."""
        outside_path = "/etc/passwd"
        
        response = self.client.get(f"/api/pmd/analysis/{outside_path}")
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("Access denied", data["error"])

    def test_pmd_analysis_endpoint_runtime_error(self):
        """Test PMD analysis endpoint with PMD runtime error."""
        file_path = os.path.join(self.test_dir, "main.py")
        
        # Mock PMD service to raise RuntimeError
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            mock_pmd.side_effect = RuntimeError("PMD command failed")
            
            response = self.client.get(f"/api/pmd/analysis/{file_path}")
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("PMD command failed", data["error"])

    def test_pmd_analysis_endpoint_path_traversal_attack(self):
        """Test PMD analysis endpoint blocks path traversal attacks."""
        # Try various path traversal patterns (URL encoded to avoid routing issues)
        traversal_paths = [
            "..%2F..%2F..%2Fetc%2Fpasswd",  # ../../../etc/passwd
            "..%5C..%5C..%5Cwindows%5Csystem32%5Cconfig"  # ..\..\..\windows\system32\config
        ]
        
        for path in traversal_paths:
            response = self.client.get(f"/api/pmd/analysis/{path}")
            
            self.assertEqual(response.status_code, 403)
            data = response.json()
            self.assertIn("error", data)
            self.assertIn("Access denied", data["error"])

    # HTTP method tests
    def test_unsupported_http_methods(self):
        """Test that unsupported HTTP methods return proper errors."""
        endpoints = [
            "/api/root/",
            "/api/files/files_info",
            f"/api/files/file_content/{os.path.join(self.test_dir, 'main.py')}",
            f"/api/pmd/analysis/{os.path.join(self.test_dir, 'main.py')}"
        ]
        
        for endpoint in endpoints:
            # Test POST method (should not be allowed for these endpoints)
            response = self.client.post(endpoint)
            self.assertEqual(response.status_code, 405)
            
            # Test PUT method
            response = self.client.put(endpoint)
            self.assertEqual(response.status_code, 405)
            
            # Test DELETE method
            response = self.client.delete(endpoint)
            self.assertEqual(response.status_code, 405)

    # Response format tests
    def test_response_headers(self):
        """Test that responses include proper headers."""
        response = self.client.get("/api/root/")
        
        # Should have content type
        self.assertEqual(response.headers["content-type"], "application/json")
        
        # Should have process time header (from middleware)
        self.assertIn("x-process-time", response.headers)

    def test_invalid_json_response_format(self):
        """Test that all error responses follow consistent JSON format."""
        # Test various error scenarios and verify JSON structure
        # Note: non_existent.py will be treated as relative path and cause 403 (access denied)
        # because it's outside the test directory
        error_endpoints = [
            (f"/api/files/file_content/{os.path.join(self.test_dir, 'non_existent.py')}", 404),
            ("/api/files/file_content/..%2F..%2F..%2Fetc%2Fpasswd", 403),
            ("/api/pmd/analysis/..%2F..%2F..%2Fetc%2Fpasswd", 403)
        ]
        
        for endpoint, expected_status in error_endpoints:
            response = self.client.get(endpoint)
            
            self.assertEqual(response.status_code, expected_status)
            
            # Verify JSON response format
            data = response.json()
            self.assertIn("error", data)
            self.assertIsInstance(data["error"], str)

    # Edge case tests
    def test_empty_path_handling(self):
        """Test handling of empty or whitespace paths."""
        # Test empty path (URL encoded)
        response = self.client.get("/api/files/file_content/")
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get("/api/pmd/analysis/")
        self.assertEqual(response.status_code, 403)
        
        # Test space-only path (URL encoded)
        response = self.client.get("/api/files/file_content/%20%20%20")
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get("/api/pmd/analysis/%20%20%20")
        self.assertEqual(response.status_code, 403)

    def test_very_long_path_handling(self):
        """Test handling of extremely long file paths."""
        # Create a very long path
        long_path = "a" * 1000 + ".py"
        
        response = self.client.get(f"/api/files/file_content/{long_path}")
        
        # Should handle gracefully (either 403 for security or 404 for not found)
        self.assertIn(response.status_code, [403, 404])

    def test_special_characters_in_path(self):
        """Test handling of special characters in file paths."""
        special_paths = [
            "file with spaces.py",
            "file-with-dashes.py",
            "file_with_underscores.py",
            "file.with.dots.py"
        ]
        
        for path in special_paths:
            full_path = os.path.join(self.test_dir, path)
            
            # Create the file
            with open(full_path, "w") as f:
                f.write("# Test file with special characters")
            
            # Test file content endpoint
            response = self.client.get(f"/api/files/file_content/{full_path}")
            self.assertEqual(response.status_code, 200)
            
            # Clean up
            os.remove(full_path)


if __name__ == '__main__':
    unittest.main()