#!/usr/bin/env python3
"""
Debug script to check API responses.
"""

import os
import sys
import tempfile

# Set up test environment before importing app modules
test_backend_dir = tempfile.mkdtemp(prefix="debug_test_")
os.environ["BACKEND_DIR"] = test_backend_dir
os.environ["LOG_LEVEL"] = "ERROR"

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)

# Test endpoints
endpoints = ["/health", "/api/root/", "/api/files/files_info"]

for endpoint in endpoints:
    print(f"\n=== Testing {endpoint} ===")
    response = client.get(endpoint)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text}")