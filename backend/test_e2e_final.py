#!/usr/bin/env python3
"""
Final end-to-end integration tests for the LLM Code Navigator.
Tests complete user workflows and system behavior under different scenarios.
Requirements: 5.4
"""

import os
import sys
import tempfile
import shutil
import unittest
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch

# Set up test environment before importing app modules
test_backend_dir = tempfile.mkdtemp(prefix="e2e_final_")
os.environ["BACKEND_DIR"] = test_backend_dir
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests for complete user workflows."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment with realistic codebase."""
        cls.test_dir = test_backend_dir
        cls.client = TestClient(app, headers={"host": "localhost"})
        
        # Create realistic test codebase
        cls.create_test_codebase()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_test_codebase(cls):
        """Create a realistic Python codebase for testing."""
        # Main application file
        main_content = '''#!/usr/bin/env python3
"""
Task management web application.
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify

from models.user import User
from models.task import Task
from services.auth_service import AuthService
from services.task_service import TaskService
from utils.validators import validate_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize services
auth_service = AuthService()
task_service = TaskService()


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email'}), 400
        
        user = auth_service.authenticate_user(email, password)
        if user:
            return jsonify({'user': user.to_dict()})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get user tasks."""
    try:
        user_id = request.args.get('user_id', type=int)
        tasks = task_service.get_user_tasks(user_id)
        return jsonify([task.to_dict() for task in tasks])
    
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        return jsonify({'error': 'Unable to load tasks'}), 500


if __name__ == '__main__':
    app.run(debug=True)
'''
        
        # Models
        models_dir = os.path.join(cls.test_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        user_model = '''"""User model."""
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"


class User:
    """User model."""
    
    def __init__(self, email, name, role=UserRole.USER):
        self.email = email
        self.name = name
        self.role = role
        self.created_at = datetime.utcnow()
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role.value,
            'created_at': self.created_at.isoformat()
        }
'''
        
        task_model = '''"""Task model."""
from datetime import datetime
from enum import Enum
from models.user import User


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"


class Task:
    """Task model."""
    
    def __init__(self, title, description="", user_id=None):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.status = TaskStatus.PENDING
        self.created_at = datetime.utcnow()
    
    def mark_completed(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'title': self.title,
            'description': self.description,
            'user_id': self.user_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }
'''
        
        # Services
        services_dir = os.path.join(cls.test_dir, "services")
        os.makedirs(services_dir, exist_ok=True)
        
        auth_service = '''"""Authentication service."""
import logging
from typing import Optional, List
from models.user import User, UserRole

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""
    
    def __init__(self):
        self.users = []
    
    def create_user(self, email, name, role=UserRole.USER):
        """Create new user."""
        user = User(email=email, name=name, role=role)
        self.users.append(user)
        logger.info(f"Created user: {email}")
        return user
    
    def authenticate_user(self, email, password):
        """Authenticate user."""
        # Simple authentication for demo
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    def get_all_users(self):
        """Get all users."""
        return self.users
'''
        
        task_service = '''"""Task service."""
import logging
from typing import List
from models.task import Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskService:
    """Task service."""
    
    def __init__(self):
        self.tasks = []
    
    def create_task(self, title, description="", user_id=None):
        """Create new task."""
        task = Task(title=title, description=description, user_id=user_id)
        self.tasks.append(task)
        logger.info(f"Created task: {title}")
        return task
    
    def get_user_tasks(self, user_id):
        """Get tasks for user."""
        return [task for task in self.tasks if task.user_id == user_id]
    
    def get_all_tasks(self):
        """Get all tasks."""
        return self.tasks
'''
        
        # Utils
        utils_dir = os.path.join(cls.test_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        validators = '''"""Input validation utilities."""
import re


def validate_email(email):
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_password(password):
    """Validate password strength."""
    if not password or not isinstance(password, str):
        return False
    
    return len(password) >= 8
'''
        
        # Write all files
        files_to_write = [
            ("main.py", main_content),
            ("models/__init__.py", ""),
            ("models/user.py", user_model),
            ("models/task.py", task_model),
            ("services/__init__.py", ""),
            ("services/auth_service.py", auth_service),
            ("services/task_service.py", task_service),
            ("utils/__init__.py", ""),
            ("utils/validators.py", validators),
        ]
        
        for file_path, content in files_to_write:
            full_path = os.path.join(cls.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
    
    def test_complete_user_workflow_file_analysis_to_pmd(self):
        """Test complete user workflow: file discovery → content viewing → PMD analysis."""
        print("\n=== Testing Complete User Workflow: File Analysis to PMD ===")
        
        # Step 1: User discovers files in their codebase
        print("Step 1: Discovering files...")
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        self.assertIn("files", file_data)
        self.assertIn("relationships", file_data)
        
        files = file_data["files"]
        relationships = file_data["relationships"]
        
        # Verify we have the expected files
        file_names = [f["name"] for f in files if f["type"] == "file"]
        expected_files = ["main.py", "user.py", "task.py", "auth_service.py", "validators.py"]
        
        found_files = []
        for expected_file in expected_files:
            if any(expected_file in name for name in file_names):
                found_files.append(expected_file)
        
        self.assertGreaterEqual(len(found_files), 4, f"Should find most expected files. Found: {found_files}")
        print(f"✅ Discovered {len(files)} files")
        
        # Step 2: User selects main.py to view its content
        print("Step 2: Viewing main.py content...")
        main_files = [f for f in files if f["name"].endswith("main.py")]
        self.assertGreater(len(main_files), 0, "Should find main.py")
        
        main_file = main_files[0]
        response = self.client.get(f"/api/files/file_content/{main_file['id']}")
        self.assertEqual(response.status_code, 200)
        
        content_data = response.json()
        self.assertIn("content", content_data)
        self.assertIn("path", content_data)
        
        content = content_data["content"]
        self.assertIn("Flask", content)
        self.assertIn("@app.route", content)
        print(f"✅ Retrieved main.py content ({len(content)} characters)")
        
        # Step 3: User runs PMD analysis on main.py
        print("Step 3: Running PMD analysis...")
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            # Mock realistic PMD analysis results
            mock_pmd.return_value = {
                "violations": [
                    {
                        "rule": "TooManyImports",
                        "priority": 3,
                        "message": "Too many imports (8). Consider refactoring.",
                        "line": 1,
                        "column": 1
                    },
                    {
                        "rule": "UnusedImport",
                        "priority": 3,
                        "message": "Unused import 'datetime'",
                        "line": 6,
                        "column": 1
                    }
                ],
                "summary": {
                    "totalViolations": 2,
                    "fileAnalyzed": main_file['id']
                }
            }
            
            response = self.client.get(f"/api/pmd/analysis/{main_file['id']}")
            self.assertEqual(response.status_code, 200)
            
            pmd_result = response.json()
            self.assertIn("violations", pmd_result)
            self.assertIn("summary", pmd_result)
            
            violations = pmd_result["violations"]
            self.assertEqual(len(violations), 2)
            print(f"✅ PMD analysis found {len(violations)} violations")
        
        # Step 4: User explores relationships between files
        print("Step 4: Exploring file relationships...")
        if len(relationships) > 0:
            print(f"✅ Found {len(relationships)} import relationships")
            
            # Verify relationship structure
            for rel in relationships[:3]:  # Check first 3 relationships
                self.assertIn("source", rel)
                self.assertIn("target", rel)
        else:
            print("⚠️  No import relationships found (files may have syntax issues)")
        
        print("✅ Complete user workflow test passed!")
    
    def test_docker_container_simulation(self):
        """Test system behavior simulating Docker container environment."""
        print("\n=== Testing Docker Container Simulation ===")
        
        # Simulate container health checks
        print("Simulating container health checks...")
        health_checks = []
        
        for i in range(5):
            start_time = time.time()
            response = self.client.get("/health")
            end_time = time.time()
            
            health_checks.append({
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "healthy": response.status_code == 200
            })
        
        healthy_checks = sum(1 for check in health_checks if check["healthy"])
        avg_response_time = sum(check["response_time"] for check in health_checks) / len(health_checks)
        
        print(f"✅ Health checks: {healthy_checks}/{len(health_checks)} healthy")
        print(f"✅ Average health check time: {avg_response_time:.3f}s")
        
        self.assertGreaterEqual(healthy_checks, 4, "Most health checks should pass")
        self.assertLess(avg_response_time, 1.0, "Health checks should be fast")
        
        # Simulate container communication between services
        print("Simulating inter-service communication...")
        api_endpoints = [
            "/api/root/",
            "/api/files/files_info"
        ]
        
        communication_results = []
        for endpoint in api_endpoints:
            response = self.client.get(endpoint)
            communication_results.append({
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
        
        successful_communications = sum(1 for result in communication_results if result["success"])
        print(f"✅ Inter-service communication: {successful_communications}/{len(communication_results)} successful")
        
        self.assertEqual(successful_communications, len(communication_results), "All communications should succeed")
    
    def test_system_behavior_under_different_scenarios(self):
        """Test system behavior under various scenarios and edge cases."""
        print("\n=== Testing System Behavior Under Different Scenarios ===")
        
        # Scenario 1: Empty codebase
        print("Scenario 1: Testing with empty codebase...")
        empty_dir = tempfile.mkdtemp(prefix="empty_test_")
        
        # Temporarily change backend directory
        original_dir = os.environ.get("BACKEND_DIR")
        os.environ["BACKEND_DIR"] = empty_dir
        
        try:
            # Reload settings to pick up new directory
            from app.core.config import Settings
            from app.core import config
            config.settings = Settings()
            
            response = self.client.get("/api/files/files_info")
            self.assertEqual(response.status_code, 200)
            
            file_data = response.json()
            self.assertEqual(len(file_data["files"]), 0, "Empty directory should have no files")
            self.assertEqual(len(file_data["relationships"]), 0, "Empty directory should have no relationships")
            print("✅ Empty codebase handled correctly")
        
        finally:
            # Restore original directory
            os.environ["BACKEND_DIR"] = original_dir
            config.settings = Settings()
            shutil.rmtree(empty_dir)
        
        # Scenario 2: Large number of concurrent requests
        print("Scenario 2: Testing high concurrent load...")
        import threading
        import queue
        
        results = queue.Queue()
        num_threads = 10
        requests_per_thread = 5
        
        def make_requests():
            thread_results = []
            for i in range(requests_per_thread):
                try:
                    response = self.client.get("/api/files/files_info")
                    thread_results.append({
                        "success": response.status_code == 200,
                        "status_code": response.status_code
                    })
                except Exception as e:
                    thread_results.append({
                        "success": False,
                        "error": str(e)
                    })
            results.put(thread_results)
        
        # Start threads
        threads = []
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=make_requests)
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
        
        print(f"✅ High load test: {successful}/{total} successful ({success_rate:.1%}) in {end_time - start_time:.2f}s")
        self.assertGreater(success_rate, 0.8, "Should handle high load with >80% success rate")
        
        # Scenario 3: Security attack simulation
        print("Scenario 3: Testing security attack resistance...")
        attack_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "/etc/passwd",
            "~/secret_file.py",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        blocked_attacks = 0
        for attack in attack_attempts:
            response = self.client.get(f"/api/files/file_content/{attack}")
            if response.status_code in [403, 404]:  # Blocked or not found
                blocked_attacks += 1
        
        print(f"✅ Security test: {blocked_attacks}/{len(attack_attempts)} attacks blocked")
        self.assertEqual(blocked_attacks, len(attack_attempts), "All attacks should be blocked")
        
        # Scenario 4: Error recovery
        print("Scenario 4: Testing error recovery...")
        
        # Test recovery after invalid requests
        invalid_requests = [
            "/api/files/file_content/invalid_file.txt",
            "/api/pmd/analysis/nonexistent.py",
            "/api/files/file_content/"
        ]
        
        for invalid_request in invalid_requests:
            response = self.client.get(invalid_request)
            self.assertIn(response.status_code, [400, 403, 404, 422], f"Invalid request should return error: {invalid_request}")
        
        # Verify system still works after errors
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200, "System should recover after errors")
        
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200, "File discovery should work after errors")
        
        print("✅ Error recovery test passed")
    
    def test_api_consistency_and_reliability(self):
        """Test API consistency and reliability across multiple calls."""
        print("\n=== Testing API Consistency and Reliability ===")
        
        # Test response consistency
        print("Testing response consistency...")
        endpoints_to_test = [
            "/health",
            "/api/root/",
            "/api/files/files_info"
        ]
        
        for endpoint in endpoints_to_test:
            responses = []
            
            # Make multiple calls to the same endpoint
            for i in range(5):
                response = self.client.get(endpoint)
                responses.append({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "response_size": len(response.content)
                })
            
            # Verify consistency
            status_codes = [r["status_code"] for r in responses]
            self.assertTrue(all(code == status_codes[0] for code in status_codes), 
                          f"Status codes should be consistent for {endpoint}")
            
            # Verify all responses have required headers
            for response in responses:
                self.assertIn("content-type", response["headers"])
                self.assertIn("x-process-time", response["headers"])
            
            print(f"✅ {endpoint} responses are consistent")
        
        # Test response time stability
        print("Testing response time stability...")
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            response = self.client.get("/api/files/files_info")
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            response_times.append(end_time - start_time)
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"✅ Response times - avg: {avg_time:.3f}s, min: {min_time:.3f}s, max: {max_time:.3f}s")
        
        # Response times should be reasonable and not too variable
        self.assertLess(avg_time, 2.0, "Average response time should be under 2s")
        self.assertLess(max_time - min_time, 1.0, "Response time variance should be reasonable")
        
        # Test data integrity
        print("Testing data integrity...")
        
        # Get file data multiple times and verify it's the same
        file_data_responses = []
        for i in range(3):
            response = self.client.get("/api/files/files_info")
            self.assertEqual(response.status_code, 200)
            file_data_responses.append(response.json())
        
        # Verify file counts are consistent
        file_counts = [len(data["files"]) for data in file_data_responses]
        self.assertTrue(all(count == file_counts[0] for count in file_counts), 
                       "File counts should be consistent across calls")
        
        relationship_counts = [len(data["relationships"]) for data in file_data_responses]
        self.assertTrue(all(count == relationship_counts[0] for count in relationship_counts), 
                       "Relationship counts should be consistent across calls")
        
        print(f"✅ Data integrity verified - {file_counts[0]} files, {relationship_counts[0]} relationships")


if __name__ == '__main__':
    unittest.main(verbosity=2)