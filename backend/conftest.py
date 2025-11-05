"""
Pytest configuration for the backend tests.
"""
import sys
import os
import tempfile
from pathlib import Path

# Add the backend directory to Python path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set up test environment variables before importing app modules
test_backend_dir = tempfile.mkdtemp(prefix="test_backend_")
os.environ["BACKEND_DIR"] = test_backend_dir
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise during tests

# Create some test files in the temporary directory
test_files_dir = Path(test_backend_dir)
(test_files_dir / "test_file.py").write_text("import os\nprint('hello')")
(test_files_dir / "another_file.py").write_text("from pathlib import Path\nfrom test_file import something")

def pytest_sessionfinish(session, exitstatus):
    """Clean up test directory after tests complete."""
    import shutil
    if os.path.exists(test_backend_dir):
        shutil.rmtree(test_backend_dir, ignore_errors=True)