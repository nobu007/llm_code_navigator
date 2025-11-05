#!/usr/bin/env python3
"""
Final integration test for the LLM Code Navigator system.
Tests complete functionality, security, error handling, and performance.
Requirements: 1.1, 2.1, 3.1, 4.1, 5.1
"""

import os
import sys
import tempfile
import shutil
import unittest
import json
import time
import threading
import queue
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch

# Set up test environment before importing app modules
test_backend_dir = tempfile.mkdtemp(prefix="integration_final_")
os.environ["BACKEND_DIR"] = test_backend_dir
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app


class TestIntegrationFinal(unittest.TestCase):
    """Final integration tests for complete system functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_dir = test_backend_dir
        cls.client = TestClient(app, headers={"host": "localhost"})
        
        # Create test codebase
        cls.create_test_codebase()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_test_codebase(cls):
        """Create a test Python codebase."""
        # Main application file
        main_content = '''#!/usr/bin/env python3
"""
Main application for testing code analysis features.
"""
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional

from models.user import User, UserRole
from models.project import Project, ProjectStatus
from services.auth_service import AuthService
from services.data_service import DataService
from utils.validators import validate_email
from utils.helpers import format_datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize application."""
        self.auth_service = AuthService()
        self.data_service = DataService()
        self.users = []
        self.projects = []
        
        logger.info("Application initialized")
    
    def create_user(self, email: str, name: str) -> User:
        """Create a new user."""
        if not validate_email(email):
            raise ValueError("Invalid email")
        
        user = User(email=email, name=name, role=UserRole.USER)
        self.users.append(user)
        
        logger.info(f"Created user: {email}")
        return user
    
    def create_project(self, name: str, owner_id: int) -> Project:
        """Create a new project."""
        project = Project(
            name=name,
            owner_id=owner_id,
            status=ProjectStatus.ACTIVE
        )
        self.projects.append(project)
        
        logger.info(f"Created project: {name}")
        return project
    
    def get_user_projects(self, user_id: int) -> List[Project]:
        """Get projects for a user."""
        return [p for p in self.projects if p.owner_id == user_id]
    
    def process_data(self, data: Dict) -> Dict:
        """Process data using data service."""
        return self.data_service.process(data)
    
    def run(self):
        """Run the application."""
        logger.info("Application running")
        
        # Create sample data
        user = self.create_user("admin@example.com", "Admin User")
        project = self.create_project("Sample Project", user.id)
        
        # Process some data
        result = self.process_data({"test": "data"})
        
        logger.info(f"Processed data: {result}")


if __name__ == "__main__":
    app = Application()
    app.run()
'''
        
        # Models
        models_dir = os.path.join(cls.test_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        user_model = '''"""User model."""
from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User:
    """User model."""
    
    def __init__(self, email: str, name: str, role: UserRole = UserRole.USER):
        """Initialize user."""
        self.id = id(self)  # Simple ID generation
        self.email = email
        self.name = name
        self.role = role
        self.created_at = datetime.utcnow()
    
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role.value,
            "created_at": self.created_at.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
'''
        
        project_model = '''"""Project model."""
from datetime import datetime
from enum import Enum
from typing import Optional


class ProjectStatus(Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project:
    """Project model."""
    
    def __init__(self, name: str, owner_id: int, status: ProjectStatus = ProjectStatus.ACTIVE):
        """Initialize project."""
        self.id = id(self)  # Simple ID generation
        self.name = name
        self.owner_id = owner_id
        self.status = status
        self.created_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status == ProjectStatus.ACTIVE
    
    def complete(self) -> None:
        """Mark project as completed."""
        self.status = ProjectStatus.COMPLETED
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<Project {self.name}>"
'''
        
        # Services
        services_dir = os.path.join(cls.test_dir, "services")
        os.makedirs(services_dir, exist_ok=True)
        
        auth_service = '''"""Authentication service."""
import logging
from typing import Optional
from models.user import User, UserRole

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""
    
    def __init__(self):
        """Initialize auth service."""
        self.users = []
    
    def create_user(self, email: str, name: str, role: UserRole = UserRole.USER) -> User:
        """Create a new user."""
        user = User(email=email, name=name, role=role)
        self.users.append(user)
        logger.info(f"Created user: {email}")
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = self.get_user_by_email(email)
        if user:
            # Simple authentication for demo
            logger.info(f"User authenticated: {email}")
            return user
        return None
    
    def get_all_users(self) -> list:
        """Get all users."""
        return self.users.copy()
'''
        
        data_service = '''"""Data processing service."""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DataService:
    """Data processing service."""
    
    def __init__(self):
        """Initialize data service."""
        self.processed_count = 0
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data."""
        self.processed_count += 1
        
        result = {
            "original_data": data,
            "processed_at": datetime.utcnow().isoformat(),
            "processing_id": self.processed_count,
            "data_size": len(str(data)),
            "status": "processed"
        }
        
        logger.info(f"Processed data item {self.processed_count}")
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "total_processed": self.processed_count,
            "service_status": "active"
        }
'''
        
        # Utils
        utils_dir = os.path.join(cls.test_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        validators = '''"""Input validation utilities."""
import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if not password or not isinstance(password, str):
        return False
    
    return len(password) >= 8


def validate_project_name(name: str) -> bool:
    """Validate project name."""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    return 1 <= len(name) <= 100
'''
        
        helpers = '''"""Helper utility functions."""
from datetime import datetime
from typing import Any


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime."""
    if not isinstance(dt, datetime):
        return ""
    
    return dt.strftime(format_str)


def calculate_hash(data: Any) -> str:
    """Calculate simple hash of data."""
    import hashlib
    data_str = str(data)
    return hashlib.md5(data_str.encode()).hexdigest()


def generate_uuid() -> str:
    """Generate UUID."""
    import uuid
    return str(uuid.uuid4())
'''
        
        # Write all files
        files_to_write = [
            ("main.py", main_content),
            ("models/__init__.py", ""),
            ("models/user.py", user_model),
            ("models/project.py", project_model),
            ("services/__init__.py", ""),
            ("services/auth_service.py", auth_service),
            ("services/data_service.py", data_service),
            ("utils/__init__.py", ""),
            ("utils/validators.py", validators),
            ("utils/helpers.py", helpers),
        ]
        
        for file_path, content in files_to_write:
            full_path = os.path.join(cls.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding='utf-8') as f:
                f.write(content)
    
    def test_complete_user_workflow_integration(self):
        """Test complete user workflow from file discovery to PMD analysis."""
        print("\n=== Testing Complete User Workflow Integration ===")
        
        # Step 1: File Discovery and Analysis
        print("Step 1: File Discovery and Analysis")
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        self.assertIn("files", file_data)
        self.assertIn("relationships", file_data)
        
        files = file_data["files"]
        relationships = file_data["relationships"]
        
        # Verify file discovery
        file_names = [f["name"] for f in files if f["type"] == "file"]
        expected_files = ["main.py", "user.py", "project.py", "auth_service.py", "validators.py"]
        
        found_files = []
        for expected_file in expected_files:
            if any(expected_file in name for name in file_names):
                found_files.append(expected_file)
        
        self.assertGreaterEqual(len(found_files), 4, f"Should find most expected files. Found: {found_files}")
        print(f"✅ Discovered {len(files)} files with {len(relationships)} relationships")
        
        # Step 2: File Content Retrieval
        print("Step 2: File Content Retrieval")
        main_files = [f for f in files if f["name"].endswith("main.py")]
        self.assertGreater(len(main_files), 0, "Should find main.py")
        
        # Use the full file path from the name field, not the ID
        main_file_path = main_files[0]["name"]
        response = self.client.get(f"/api/files/file_content/{main_file_path}")
        self.assertEqual(response.status_code, 200)
        
        content_data = response.json()
        self.assertIn("content", content_data)
        content = content_data["content"]
        
        # Verify content patterns
        expected_patterns = [
            "class Application",
            "def create_user",
            "from models.user import",
            "from services.auth_service import"
        ]
        
        for pattern in expected_patterns:
            self.assertIn(pattern, content, f"Expected pattern '{pattern}' not found")
        
        print(f"✅ Retrieved file content ({len(content)} characters)")
        
        # Step 3: PMD Analysis
        print("Step 3: PMD Static Analysis")
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            mock_pmd.return_value = {
                "violations": [
                    {
                        "rule": "TooManyImports",
                        "priority": 3,
                        "message": "Too many imports (8). Consider refactoring.",
                        "line": 1,
                        "column": 1
                    }
                ],
                "summary": {
                    "totalViolations": 1,
                    "fileAnalyzed": main_file_path
                }
            }
            
            response = self.client.get(f"/api/pmd/analysis/{main_file_path}")
            self.assertEqual(response.status_code, 200)
            
            pmd_result = response.json()
            self.assertIn("violations", pmd_result)
            self.assertIn("summary", pmd_result)
            
            violations = pmd_result["violations"]
            self.assertEqual(len(violations), 1)
            
            print(f"✅ PMD analysis found {len(violations)} violations")
        
        print("✅ Complete user workflow integration test passed!")
    
    def test_security_and_error_handling(self):
        """Test security measures and error handling."""
        print("\n=== Testing Security and Error Handling ===")
        
        # Test path traversal prevention
        print("Testing path traversal prevention...")
        traversal_attacks = [
            "../../../etc/passwd",
            "/etc/passwd",
            "~/secret_file.py"
        ]
        
        blocked_attacks = 0
        for attack in traversal_attacks:
            response = self.client.get(f"/api/files/file_content/{attack}")
            if response.status_code in [403, 404]:
                blocked_attacks += 1
        
        print(f"✅ Path traversal: {blocked_attacks}/{len(traversal_attacks)} attacks blocked")
        self.assertGreater(blocked_attacks, 0, "Some path traversal attacks should be blocked")
        
        # Test file not found handling
        print("Testing file not found handling...")
        response = self.client.get(f"/api/files/file_content/{os.path.join(self.test_dir, 'nonexistent.py')}")
        self.assertEqual(response.status_code, 404)
        
        error_data = response.json()
        self.assertIn("error", error_data)
        print("✅ File not found errors handled correctly")
        
        # Test invalid file extensions
        print("Testing invalid file extensions...")
        invalid_file = os.path.join(self.test_dir, "test.txt")
        with open(invalid_file, "w") as f:
            f.write("This is a text file")
        
        response = self.client.get(f"/api/files/file_content/{invalid_file}")
        self.assertEqual(response.status_code, 403)
        
        error_data = response.json()
        self.assertIn("error", error_data)
        print("✅ Invalid file extensions blocked correctly")
        
        # Clean up
        os.remove(invalid_file)
    
    def test_concurrent_load_and_performance(self):
        """Test system performance under concurrent load."""
        print("\n=== Testing Concurrent Load and Performance ===")
        
        results = queue.Queue()
        num_threads = 5
        requests_per_thread = 3
        
        def make_concurrent_requests():
            thread_results = []
            for i in range(requests_per_thread):
                try:
                    start_time = time.time()
                    response = self.client.get("/api/files/files_info")
                    end_time = time.time()
                    
                    thread_results.append({
                        "success": response.status_code == 200,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time
                    })
                except Exception as e:
                    thread_results.append({
                        "success": False,
                        "error": str(e),
                        "response_time": 0
                    })
            
            results.put(thread_results)
        
        # Start concurrent threads
        threads = []
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=make_concurrent_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        end_time = time.time()
        
        # Analyze results
        all_results = []
        while not results.empty():
            all_results.extend(results.get())
        
        successful = sum(1 for r in all_results if r["success"])
        total = len(all_results)
        success_rate = successful / total if total > 0 else 0
        avg_response_time = sum(r["response_time"] for r in all_results if r["success"]) / successful if successful > 0 else 0
        
        print(f"✅ Concurrent load: {successful}/{total} successful ({success_rate:.1%})")
        print(f"✅ Average response time: {avg_response_time:.3f}s")
        print(f"✅ Total test time: {end_time - start_time:.2f}s")
        
        # Performance assertions
        self.assertGreater(success_rate, 0.8, "Success rate should be above 80%")
        self.assertLess(avg_response_time, 2.0, "Average response time should be under 2s")
    
    def test_api_consistency_and_reliability(self):
        """Test API consistency and reliability."""
        print("\n=== Testing API Consistency and Reliability ===")
        
        # Test response format consistency
        print("Testing response format consistency...")
        endpoints = [
            ("/health", 200),
            ("/api/root/", 200),
            ("/api/files/files_info", 200)
        ]
        
        for endpoint, expected_status in endpoints:
            responses = []
            
            # Make multiple calls
            for i in range(3):
                response = self.client.get(endpoint)
                responses.append({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_type": response.headers.get("content-type")
                })
            
            # Verify consistency
            status_codes = [r["status_code"] for r in responses]
            self.assertTrue(all(code == expected_status for code in status_codes),
                          f"Status codes should be {expected_status} for {endpoint}")
            
            # Verify required headers
            for response in responses:
                self.assertIn("x-process-time", response["headers"])
            
            print(f"✅ {endpoint} responses are consistent")
        
        # Test data integrity
        print("Testing data integrity...")
        file_data_responses = []
        for i in range(3):
            response = self.client.get("/api/files/files_info")
            self.assertEqual(response.status_code, 200)
            file_data_responses.append(response.json())
        
        # Verify consistency
        file_counts = [len(data["files"]) for data in file_data_responses]
        self.assertTrue(all(count == file_counts[0] for count in file_counts),
                       "File counts should be consistent")
        
        relationship_counts = [len(data["relationships"]) for data in file_data_responses]
        self.assertTrue(all(count == relationship_counts[0] for count in relationship_counts),
                       "Relationship counts should be consistent")
        
        print(f"✅ Data integrity verified: {file_counts[0]} files, {relationship_counts[0]} relationships")
    
    def test_system_health_and_monitoring(self):
        """Test system health and monitoring capabilities."""
        print("\n=== Testing System Health and Monitoring ===")
        
        # Test health endpoint
        print("Testing health endpoint...")
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        health_data = response.json()
        self.assertIn("status", health_data)
        self.assertEqual(health_data["status"], "healthy")
        self.assertIn("backend_dir", health_data)
        
        print("✅ Health endpoint working correctly")
        
        # Test API root endpoint
        print("Testing API root endpoint...")
        response = self.client.get("/api/root/")
        self.assertEqual(response.status_code, 200)
        
        root_data = response.json()
        self.assertIn("message", root_data)
        
        print("✅ API root endpoint working correctly")
        
        # Test response times
        print("Testing response times...")
        response_times = []
        for i in range(10):
            start_time = time.time()
            response = self.client.get("/health")
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            response_times.append(end_time - start_time)
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        print(f"✅ Response times: avg={avg_time:.3f}s, max={max_time:.3f}s")
        
        self.assertLess(avg_time, 1.0, "Average response time should be under 1s")
        self.assertLess(max_time, 2.0, "Max response time should be under 2s")


if __name__ == '__main__':
    unittest.main(verbosity=2)