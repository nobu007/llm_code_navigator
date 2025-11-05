#!/usr/bin/env python3
"""
Test runner script for the backend tests.
This script ensures proper environment setup and runs all tests.
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run all backend tests with proper configuration."""
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Run pytest with verbose output
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    
    print("Running backend tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())