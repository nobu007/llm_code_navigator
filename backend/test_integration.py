#!/usr/bin/env python3
"""
Simple integration test to verify the file content retrieval service works correctly.
This test creates a temporary file and tests the API endpoint.
"""

import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def test_file_content_retrieval():
    """Test the file content retrieval API endpoint."""
    client = TestClient(app)
    
    # Create a temporary test file in the backend directory
    test_content = "print('Hello, World!')\n# This is a test file\nimport os"
    
    # Create a temporary file within the backend directory
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, 
                                   dir=settings.BACKEND_DIR) as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        # Get the relative path from the backend directory
        relative_path = os.path.relpath(temp_file_path, settings.BACKEND_DIR)
        
        # Test the API endpoint
        response = client.get(f"/api/files/file_content/{temp_file_path}")
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.json()}")
        
        # Verify the response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["content"] == test_content
        assert response_data["path"] == temp_file_path
        assert response_data["encoding"] == "utf-8"
        
        print("✅ File content retrieval test passed!")
        
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    test_file_content_retrieval()