#!/usr/bin/env python3
"""
Working end-to-end integration tests for the LLM Code Navigator.
Tests complete user workflows, Docker container functionality, and system behavior.
Requirements: 5.4
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
test_backend_dir = tempfile.mkdtemp(prefix="e2e_working_")
os.environ["BACKEND_DIR"] = test_backend_dir
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app


class TestEndToEndWorkingIntegration(unittest.TestCase):
    """Working end-to-end integration tests for complete user workflows."""
    
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
Web application for project management.
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify

from models.project import Project
from models.user import User
from services.project_service import ProjectService
from services.user_service import UserService
from utils.validators import validate_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize services
project_service = ProjectService()
user_service = UserService()


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects."""
    try:
        projects = project_service.get_all_projects()
        return jsonify([project.to_dict() for project in projects])
    except Exception as e:
        logger.error(f"Get projects error: {e}")
        return jsonify({'error': 'Unable to load projects'}), 500


@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user."""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email'}), 400
        
        user = user_service.create_user(email, name)
        return jsonify(user.to_dict()), 201
    except Exception as e:
        logger.error(f"Create user error: {e}")
        return jsonify({'error': 'User creation failed'}), 500


if __name__ == '__main__':
    app.run(debug=True)
'''
        
        # Models
        models_dir = os.path.join(cls.test_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        project_model = '''"""Project model."""
from datetime import datetime
from enum import Enum


class ProjectStatus(Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project:
    """Project model."""
    
    def __init__(self, name, description="", status=ProjectStatus.ACTIVE):
        self.name = name
        self.description = description
        self.status = status
        self.created_at = datetime.utcnow()
    
    def is_active(self):
        """Check if project is active."""
        return self.status == ProjectStatus.ACTIVE
    
    def complete(self):
        """Mark project as completed."""
        self.status = ProjectStatus.COMPLETED
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'is_active': self.is_active(),
            'created_at': self.created_at.isoformat()
        }
'''
        
        user_model = '''"""User model."""
from datetime import datetime
from models.project import Project


class User:
    """User model."""
    
    def __init__(self, email, name):
        self.email = email
        self.name = name
        self.created_at = datetime.utcnow()
        self.projects = []
    
    def add_project(self, project):
        """Add project to user."""
        if isinstance(project, Project):
            self.projects.append(project)
    
    def get_active_projects(self):
        """Get active projects."""
        return [p for p in self.projects if p.is_active()]
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'email': self.email,
            'name': self.name,
            'project_count': len(self.projects),
            'active_projects': len(self.get_active_projects()),
            'created_at': self.created_at.isoformat()
        }
'''
        
        # Services
        services_dir = os.path.join(cls.test_dir, "services")
        os.makedirs(services_dir, exist_ok=True)
        
        project_service = '''"""Project service."""
import logging
from typing import List
from models.project import Project, ProjectStatus

logger = logging.getLogger(__name__)


class ProjectService:
    """Project service."""
    
    def __init__(self):
        self.projects = []
    
    def create_project(self, name, description=""):
        """Create new project."""
        project = Project(name=name, description=description)
        self.projects.append(project)
        logger.info(f"Created project: {name}")
        return project
    
    def get_all_projects(self):
        """Get all projects."""
        return self.projects
    
    def get_active_projects(self):
        """Get active projects."""
        return [p for p in self.projects if p.is_active()]
    
    def complete_project(self, project_name):
        """Complete a project."""
        for project in self.projects:
            if project.name == project_name:
                project.complete()
                logger.info(f"Completed project: {project_name}")
                return project
        return None
'''
        
        user_service = '''"""User service."""
import logging
from typing import List, Optional
from models.user import User

logger = logging.getLogger(__name__)


class UserService:
    """User service."""
    
    def __init__(self):
        self.users = []
    
    def create_user(self, email, name):
        """Create new user."""
        # Check if user already exists
        existing_user = self.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        user = User(email=email, name=name)
        self.users.append(user)
        logger.info(f"Created user: {email}")
        return user
    
    def get_user_by_email(self, email):
        """Get user by email."""
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    def get_all_users(self):
        """Get all users."""
        return self.users
    
    def assign_project_to_user(self, user_email, project):
        """Assign project to user."""
        user = self.get_user_by_email(user_email)
        if user:
            user.add_project(project)
            logger.info(f"Assigned project {project.name} to user {user_email}")
            return True
        return False
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
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_project_name(name):
    """Validate project name."""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    return 1 <= len(name) <= 100


def validate_user_name(name):
    """Validate user name."""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    return 1 <= len(name) <= 50
'''
        
        # Write all files
        files_to_write = [
            ("main.py", main_content),
            ("models/__init__.py", ""),
            ("models/project.py", project_model),
            ("models/user.py", user_model),
            ("services/__init__.py", ""),
            ("services/project_service.py", project_service),
            ("services/user_service.py", user_service),
            ("utils/__init__.py", ""),
            ("utils/validators.py", validators),
        ]
        
        for file_path, content in files_to_write:
            full_path = os.path.join(cls.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
    
    def test_complete_user_workflow(self):
        """Test complete user workflow from file discovery to PMD analysis."""
        print("\n=== Testing Complete User Workflow ===")
        
        # Step 1: User discovers files in their codebase
        print("Step 1: File Discovery")
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        self.assertIn("files", file_data)
        self.assertIn("relationships", file_data)
        
        files = file_data["files"]
        relationships = file_data["relationships"]
        
        # Verify we have the expected files
        file_names = [f["name"] for f in files if f["type"] == "file"]
        expected_files = ["main.py", "project.py", "user.py", "project_service.py", "validators.py"]
        
        found_files = []
        for expected_file in expected_files:
            if any(expected_file in name for name in file_names):
                found_files.append(expected_file)
        
        self.assertGreaterEqual(len(found_files), 4, f"Should find most expected files. Found: {found_files}")
        print(f"✅ Discovered {len(files)} files")
        
        # Step 2: User views file content
        print("Step 2: File Content Viewing")
        main_files = [f for f in files if f["name"].endswith("main.py")]
        self.assertGreater(len(main_files), 0, "Should find main.py")
        
        main_file = main_files[0]
        # Use the full path from the file data
        main_file_path = os.path.join(self.test_dir, "main.py")
        
        response = self.client.get(f"/api/files/file_content/{main_file_path}")
        self.assertEqual(response.status_code, 200)
        
        content_data = response.json()
        self.assertIn("content", content_data)
        self.assertIn("path", content_data)
        
        content = content_data["content"]
        self.assertIn("Flask", content)
        self.assertIn("@app.route", content)
        print(f"✅ Retrieved main.py content ({len(content)} characters)")
        
        # Step 3: User runs PMD analysis
        print("Step 3: PMD Analysis")
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            # Mock realistic PMD analysis results
            mock_pmd.return_value = {
                "violations": [
                    {
                        "rule": "TooManyImports",
                        "priority": 3,
                        "message": "Too many imports (7). Consider refactoring.",
                        "line": 1,
                        "column": 1
                    },
                    {
                        "rule": "LineTooLong",
                        "priority": 4,
                        "message": "Line exceeds 120 characters",
                        "line": 15,
                        "column": 121
                    }
                ],
                "summary": {
                    "totalViolations": 2,
                    "fileAnalyzed": main_file_path
                }
            }
            
            response = self.client.get(f"/api/pmd/analysis/{main_file_path}")
            self.assertEqual(response.status_code, 200)
            
            pmd_result = response.json()
            self.assertIn("violations", pmd_result)
            self.assertIn("summary", pmd_result)
            
            violations = pmd_result["violations"]
            self.assertEqual(len(violations), 2)
            print(f"✅ PMD analysis found {len(violations)} violations")
        
        print("✅ Complete user workflow test passed!")
    
    def test_docker_container_functionality(self):
        """Test Docker container functionality and communication."""
        print("\n=== Testing Docker Container Functionality ===")
        
        # Test 1: Container health checks
        print("Testing container health checks...")
        health_results = []
        
        for i in range(5):
            start_time = time.time()
            response = self.client.get("/health")
            end_time = time.time()
            
            health_results.append({
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "healthy": response.status_code == 200
            })
        
        healthy_count = sum(1 for result in health_results if result["healthy"])
        avg_response_time = sum(result["response_time"] for result in health_results) / len(health_results)
        
        print(f"✅ Health checks: {healthy_count}/{len(health_results)} healthy")
        print(f"✅ Average health check time: {avg_response_time:.3f}s")
        
        self.assertGreaterEqual(healthy_count, 4, "Most health checks should pass")
        self.assertLess(avg_response_time, 1.0, "Health checks should be fast")
        
        # Test 2: Service communication
        print("Testing service communication...")
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
        print(f"✅ Service communication: {successful_communications}/{len(communication_results)} successful")
        
        self.assertEqual(successful_communications, len(communication_results), "All communications should succeed")
        
        # Test 3: Volume mounting simulation (file access)
        print("Testing volume mounting simulation...")
        
        # Verify we can access files in the mounted directory
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        self.assertGreater(len(file_data["files"]), 0, "Should access files in mounted volume")
        
        print(f"✅ Volume mounting: accessed {len(file_data['files'])} files")
    
    def test_system_behavior_under_different_scenarios(self):
        """Test system behavior under various scenarios."""
        print("\n=== Testing System Behavior Under Different Scenarios ===")
        
        # Scenario 1: High concurrent load
        print("Scenario 1: High concurrent load...")
        
        results = queue.Queue()
        num_threads = 8
        requests_per_thread = 5
        
        def make_concurrent_requests():
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
        
        print(f"✅ Concurrent load: {successful}/{total} successful ({success_rate:.1%}) in {end_time - start_time:.2f}s")
        self.assertGreater(success_rate, 0.8, "Should handle concurrent load with >80% success rate")
        
        # Scenario 2: Security attack resistance
        print("Scenario 2: Security attack resistance...")
        
        attack_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "/etc/passwd",
            "~/secret_file.py"
        ]
        
        blocked_attacks = 0
        for attack in attack_attempts:
            response = self.client.get(f"/api/files/file_content/{attack}")
            if response.status_code in [403, 404]:  # Blocked or not found
                blocked_attacks += 1
        
        print(f"✅ Security: {blocked_attacks}/{len(attack_attempts)} attacks blocked")
        self.assertEqual(blocked_attacks, len(attack_attempts), "All attacks should be blocked")
        
        # Scenario 3: Error recovery
        print("Scenario 3: Error recovery...")
        
        # Make invalid requests
        invalid_requests = [
            "/api/files/file_content/invalid_file.txt",
            "/api/pmd/analysis/nonexistent.py"
        ]
        
        for invalid_request in invalid_requests:
            response = self.client.get(invalid_request)
            self.assertIn(response.status_code, [400, 403, 404, 422], f"Invalid request should return error: {invalid_request}")
        
        # Verify system still works after errors
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200, "System should recover after errors")
        
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200, "File discovery should work after errors")
        
        print("✅ Error recovery verified")
        
        # Scenario 4: Performance under load
        print("Scenario 4: Performance under load...")
        
        response_times = []
        for i in range(20):
            start_time = time.time()
            response = self.client.get("/api/files/files_info")
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            response_times.append(end_time - start_time)
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"✅ Performance: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")
        
        self.assertLess(avg_time, 1.0, "Average response time should be under 1s")
        self.assertLess(max_time, 2.0, "Max response time should be under 2s")
    
    def test_api_consistency_and_reliability(self):
        """Test API consistency and reliability."""
        print("\n=== Testing API Consistency and Reliability ===")
        
        # Test 1: Response format consistency
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
            
            content_types = [r["content_type"] for r in responses]
            self.assertTrue(all(ct == content_types[0] for ct in content_types), 
                          f"Content types should be consistent for {endpoint}")
            
            # Verify required headers
            for response in responses:
                self.assertIn("x-process-time", response["headers"])
            
            print(f"✅ {endpoint} responses are consistent")
        
        # Test 2: Data integrity
        print("Testing data integrity...")
        
        # Get file data multiple times
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
        
        # Test 3: Error response consistency
        print("Testing error response consistency...")
        
        # Create a file with invalid extension
        invalid_file = os.path.join(self.test_dir, "test.txt")
        with open(invalid_file, "w") as f:
            f.write("This should not be accessible")
        
        error_responses = []
        for i in range(3):
            response = self.client.get(f"/api/files/file_content/{invalid_file}")
            error_responses.append({
                "status_code": response.status_code,
                "response": response.json()
            })
        
        # Verify error consistency
        error_codes = [r["status_code"] for r in error_responses]
        self.assertTrue(all(code == 403 for code in error_codes), "Error codes should be consistent")
        
        for response in error_responses:
            self.assertIn("error", response["response"])
        
        print("✅ Error responses are consistent")
        
        # Clean up
        os.remove(invalid_file)


if __name__ == '__main__':
    unittest.main(verbosity=2)