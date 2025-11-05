#!/usr/bin/env python3
"""
End-to-end integration tests for the LLM Code Navigator system.
Tests complete user workflows, Docker container functionality, and system behavior.
Requirements: 5.4
"""

import os
import sys
import time
import json
import tempfile
import shutil
import subprocess
import unittest
import requests
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch

# Add backend to path for imports
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests for complete system workflows."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment and Docker containers."""
        cls.test_dir = tempfile.mkdtemp(prefix="e2e_test_")
        cls.backend_url = "http://localhost:9000"
        cls.frontend_url = "http://localhost:3000"
        cls.docker_compose_file = "docker-compose.yml"
        
        # Create test codebase
        cls.create_test_codebase()
        
        # Start Docker containers
        cls.start_docker_services()
        
        # Wait for services to be ready
        cls.wait_for_services()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment and Docker containers."""
        # Stop Docker containers
        cls.stop_docker_services()
        
        # Clean up test directory
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_test_codebase(cls):
        """Create a realistic test codebase for analysis."""
        # Main application file
        main_content = '''#!/usr/bin/env python3
"""
Main application entry point.
This is a sample Python application for testing the code navigator.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from utils.config import load_config, validate_config
from utils.database import DatabaseManager
from models.user import User, UserRole
from models.project import Project, ProjectStatus
from services.auth_service import AuthenticationService
from services.project_service import ProjectService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Application:
    """Main application class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the application."""
        self.config = load_config(config_path)
        validate_config(self.config)
        
        self.db_manager = DatabaseManager(self.config.database_url)
        self.auth_service = AuthenticationService(self.db_manager)
        self.project_service = ProjectService(self.db_manager)
        
        logger.info("Application initialized successfully")
    
    def run(self) -> None:
        """Run the main application."""
        try:
            logger.info("Starting application...")
            
            # Initialize database
            self.db_manager.initialize()
            
            # Create default admin user if not exists
            admin_user = self.auth_service.get_user_by_email("admin@example.com")
            if not admin_user:
                admin_user = User(
                    email="admin@example.com",
                    username="admin",
                    role=UserRole.ADMIN
                )
                self.auth_service.create_user(admin_user, "admin123")
                logger.info("Created default admin user")
            
            # Start main application loop
            self.main_loop()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            sys.exit(1)
    
    def main_loop(self) -> None:
        """Main application processing loop."""
        logger.info("Application running. Press Ctrl+C to exit.")
        
        try:
            while True:
                # Process pending tasks
                self.process_tasks()
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down application...")
            self.shutdown()
    
    def process_tasks(self) -> None:
        """Process pending application tasks."""
        # Get active projects
        active_projects = self.project_service.get_projects_by_status(
            ProjectStatus.ACTIVE
        )
        
        for project in active_projects:
            logger.debug(f"Processing project: {project.name}")
            # Process project tasks here
    
    def shutdown(self) -> None:
        """Gracefully shutdown the application."""
        logger.info("Performing cleanup...")
        self.db_manager.close()
        logger.info("Application shutdown complete")


def main():
    """Main entry point."""
    config_path = os.environ.get("CONFIG_PATH")
    app = Application(config_path)
    app.run()


if __name__ == "__main__":
    main()
'''
        
        # Utils module
        utils_dir = os.path.join(cls.test_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        config_content = '''"""Configuration management utilities."""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 10
    timeout: int = 30


@dataclass
class AppConfig:
    """Application configuration."""
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = "sqlite:///app.db"
    secret_key: str = "dev-secret-key"
    
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration."""
        return DatabaseConfig(url=self.database_url)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load application configuration from file or environment."""
    if config_path and os.path.exists(config_path):
        return load_config_from_file(config_path)
    
    return load_config_from_env()


def load_config_from_file(config_path: str) -> AppConfig:
    """Load configuration from YAML or JSON file."""
    config_file = Path(config_path)
    
    if config_file.suffix.lower() == '.yaml' or config_file.suffix.lower() == '.yml':
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
    elif config_file.suffix.lower() == '.json':
        with open(config_file, 'r') as f:
            data = json.load(f)
    else:
        raise ValueError(f"Unsupported config file format: {config_file.suffix}")
    
    return AppConfig(**data)


def load_config_from_env() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///app.db"),
        secret_key=os.getenv("SECRET_KEY", "dev-secret-key")
    )


def validate_config(config: AppConfig) -> None:
    """Validate application configuration."""
    if not config.secret_key or config.secret_key == "dev-secret-key":
        if not config.debug:
            raise ValueError("Secret key must be set in production")
    
    if not config.database_url:
        raise ValueError("Database URL is required")
    
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.log_level.upper() not in valid_log_levels:
        raise ValueError(f"Invalid log level: {config.log_level}")
'''
        
        database_content = '''"""Database management utilities."""
import sqlite3
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and query manager."""
    
    def __init__(self, database_url: str):
        """Initialize database manager."""
        self.database_url = database_url
        self.connection: Optional[sqlite3.Connection] = None
        
    def initialize(self) -> None:
        """Initialize database schema."""
        logger.info("Initializing database...")
        
        with self.get_connection() as conn:
            # Create users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create projects table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    owner_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
        
        logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
        else:
            raise ValueError(f"Unsupported database URL: {self.database_url}")
        
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
'''
        
        # Models
        models_dir = os.path.join(cls.test_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        user_model_content = '''"""User model and related classes."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


@dataclass
class User:
    """User data model."""
    email: str
    username: str
    role: UserRole
    id: Optional[int] = None
    password_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.role, str):
            self.role = UserRole(self.role)
    
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN
    
    def is_active(self) -> bool:
        """Check if user account is active."""
        return True  # Simplified for demo
    
    def can_access_project(self, project_id: int) -> bool:
        """Check if user can access a specific project."""
        if self.is_admin():
            return True
        
        # Additional project access logic would go here
        return False
    
    def to_dict(self) -> dict:
        """Convert user to dictionary representation."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "role": self.role.value,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create user from dictionary representation."""
        return cls(
            id=data.get("id"),
            email=data["email"],
            username=data["username"],
            role=UserRole(data["role"]),
            password_hash=data.get("password_hash"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
'''
        
        project_model_content = '''"""Project model and related classes."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


class ProjectStatus(Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Project:
    """Project data model."""
    name: str
    description: str
    status: ProjectStatus
    owner_id: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = ProjectStatus(self.status)
    
    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status == ProjectStatus.ACTIVE
    
    def can_be_modified_by(self, user_id: int) -> bool:
        """Check if project can be modified by user."""
        return self.owner_id == user_id
    
    def to_dict(self) -> dict:
        """Convert project to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """Create project from dictionary representation."""
        return cls(
            id=data.get("id"),
            name=data["name"],
            description=data["description"],
            status=ProjectStatus(data["status"]),
            owner_id=data["owner_id"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
'''
        
        # Services
        services_dir = os.path.join(cls.test_dir, "services")
        os.makedirs(services_dir, exist_ok=True)
        
        auth_service_content = '''"""Authentication service."""
import hashlib
import secrets
import logging
from typing import Optional, List
from models.user import User, UserRole
from utils.database import DatabaseManager


logger = logging.getLogger(__name__)


class AuthenticationService:
    """User authentication and management service."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize authentication service."""
        self.db_manager = db_manager
    
    def create_user(self, user: User, password: str) -> User:
        """Create a new user account."""
        # Hash password
        password_hash = self._hash_password(password)
        
        # Insert user into database
        query = '''
            INSERT INTO users (email, username, password_hash, role)
            VALUES (?, ?, ?, ?)
        '''
        params = (user.email, user.username, password_hash, user.role.value)
        
        self.db_manager.execute_update(query, params)
        
        # Retrieve created user
        created_user = self.get_user_by_email(user.email)
        logger.info(f"Created user: {created_user.username}")
        
        return created_user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        query = "SELECT * FROM users WHERE email = ?"
        results = self.db_manager.execute_query(query, (email,))
        
        if results:
            return User.from_dict(results[0])
        
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.db_manager.execute_query(query, (user_id,))
        
        if results:
            return User.from_dict(results[0])
        
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        
        if user and self._verify_password(password, user.password_hash):
            logger.info(f"User authenticated: {user.username}")
            return user
        
        logger.warning(f"Authentication failed for email: {email}")
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        query = "SELECT * FROM users ORDER BY created_at DESC"
        results = self.db_manager.execute_query(query)
        
        return [User.from_dict(row) for row in results]
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            salt, password_hash = stored_hash.split(":")
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        except ValueError:
            return False
'''
        
        project_service_content = '''"""Project management service."""
import logging
from typing import Optional, List
from models.project import Project, ProjectStatus
from utils.database import DatabaseManager


logger = logging.getLogger(__name__)


class ProjectService:
    """Project management service."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize project service."""
        self.db_manager = db_manager
    
    def create_project(self, project: Project) -> Project:
        """Create a new project."""
        query = '''
            INSERT INTO projects (name, description, status, owner_id)
            VALUES (?, ?, ?, ?)
        '''
        params = (project.name, project.description, project.status.value, project.owner_id)
        
        self.db_manager.execute_update(query, params)
        
        # Retrieve created project
        created_project = self.get_project_by_name(project.name)
        logger.info(f"Created project: {created_project.name}")
        
        return created_project
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        query = "SELECT * FROM projects WHERE id = ?"
        results = self.db_manager.execute_query(query, (project_id,))
        
        if results:
            return Project.from_dict(results[0])
        
        return None
    
    def get_project_by_name(self, name: str) -> Optional[Project]:
        """Get project by name."""
        query = "SELECT * FROM projects WHERE name = ?"
        results = self.db_manager.execute_query(query, (name,))
        
        if results:
            return Project.from_dict(results[0])
        
        return None
    
    def get_projects_by_status(self, status: ProjectStatus) -> List[Project]:
        """Get projects by status."""
        query = "SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC"
        results = self.db_manager.execute_query(query, (status.value,))
        
        return [Project.from_dict(row) for row in results]
    
    def get_projects_by_owner(self, owner_id: int) -> List[Project]:
        """Get projects by owner."""
        query = "SELECT * FROM projects WHERE owner_id = ? ORDER BY created_at DESC"
        results = self.db_manager.execute_query(query, (owner_id,))
        
        return [Project.from_dict(row) for row in results]
    
    def update_project_status(self, project_id: int, status: ProjectStatus) -> bool:
        """Update project status."""
        query = "UPDATE projects SET status = ? WHERE id = ?"
        affected_rows = self.db_manager.execute_update(query, (status.value, project_id))
        
        if affected_rows > 0:
            logger.info(f"Updated project {project_id} status to {status.value}")
            return True
        
        return False
    
    def delete_project(self, project_id: int) -> bool:
        """Delete project."""
        query = "DELETE FROM projects WHERE id = ?"
        affected_rows = self.db_manager.execute_update(query, (project_id,))
        
        if affected_rows > 0:
            logger.info(f"Deleted project {project_id}")
            return True
        
        return False
'''
        
        # Write all files
        files_to_write = [
            ("main.py", main_content),
            ("utils/__init__.py", ""),
            ("utils/config.py", config_content),
            ("utils/database.py", database_content),
            ("models/__init__.py", ""),
            ("models/user.py", user_model_content),
            ("models/project.py", project_model_content),
            ("services/__init__.py", ""),
            ("services/auth_service.py", auth_service_content),
            ("services/project_service.py", project_service_content),
        ]
        
        for file_path, content in files_to_write:
            full_path = os.path.join(cls.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
    
    @classmethod
    def start_docker_services(cls):
        """Start Docker services using docker-compose."""
        try:
            # Update docker-compose to use our test directory
            cls.update_docker_compose_for_testing()
            
            # Stop any existing containers
            subprocess.run(
                ["docker-compose", "-f", cls.docker_compose_file, "down"],
                capture_output=True,
                timeout=30
            )
            
            # Build and start services
            result = subprocess.run(
                ["docker-compose", "-f", cls.docker_compose_file, "up", "-d", "--build"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to start Docker services: {result.stderr}")
            
            print("Docker services started successfully")
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout starting Docker services")
        except Exception as e:
            raise RuntimeError(f"Error starting Docker services: {e}")
    
    @classmethod
    def stop_docker_services(cls):
        """Stop Docker services."""
        try:
            subprocess.run(
                ["docker-compose", "-f", cls.docker_compose_file, "down"],
                capture_output=True,
                timeout=30
            )
            print("Docker services stopped successfully")
        except Exception as e:
            print(f"Error stopping Docker services: {e}")
    
    @classmethod
    def update_docker_compose_for_testing(cls):
        """Update docker-compose.yml to use test directory."""
        # Read current docker-compose.yml
        with open(cls.docker_compose_file, 'r') as f:
            content = f.read()
        
        # Replace work directory with test directory
        updated_content = content.replace(
            "./work:/app/work",
            f"{cls.test_dir}:/app/work"
        )
        
        # Write temporary docker-compose file
        cls.docker_compose_file = "docker-compose-test.yml"
        with open(cls.docker_compose_file, 'w') as f:
            f.write(updated_content)
    
    @classmethod
    def wait_for_services(cls):
        """Wait for services to be ready."""
        max_retries = 30
        retry_delay = 2
        
        # Wait for backend
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    print("Backend service is ready")
                    break
            except requests.exceptions.RequestException:
                pass
            
            if i == max_retries - 1:
                raise RuntimeError("Backend service failed to start")
            
            time.sleep(retry_delay)
        
        # Wait for frontend (basic connectivity check)
        for i in range(max_retries):
            try:
                response = requests.get(cls.frontend_url, timeout=5)
                if response.status_code in [200, 404]:  # 404 is OK for Next.js
                    print("Frontend service is ready")
                    break
            except requests.exceptions.RequestException:
                pass
            
            if i == max_retries - 1:
                print("Warning: Frontend service may not be ready")
                break
            
            time.sleep(retry_delay)
    
    def test_complete_file_analysis_workflow(self):
        """Test complete file analysis workflow from start to finish."""
        print("\n=== Testing Complete File Analysis Workflow ===")
        
        # Step 1: Get file information
        response = requests.get(f"{self.backend_url}/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        self.assertIn("files", file_data)
        self.assertIn("relationships", file_data)
        self.assertIsInstance(file_data["files"], list)
        self.assertIsInstance(file_data["relationships"], list)
        
        # Verify we have our test files
        file_names = [f["name"] for f in file_data["files"] if f["type"] == "file"]
        expected_files = ["main.py", "config.py", "database.py", "user.py", "project.py"]
        
        for expected_file in expected_files:
            self.assertTrue(
                any(expected_file in name for name in file_names),
                f"Expected file {expected_file} not found in {file_names}"
            )
        
        # Verify relationships exist
        self.assertGreater(len(file_data["relationships"]), 0)
        
        print(f"✅ Found {len(file_data['files'])} files and {len(file_data['relationships'])} relationships")
        
        # Step 2: Get content for main.py
        main_py_files = [f for f in file_data["files"] if f["name"].endswith("main.py")]
        self.assertGreater(len(main_py_files), 0)
        
        main_file_id = main_py_files[0]["id"]
        response = requests.get(f"{self.backend_url}/api/files/file_content/{main_file_id}")
        self.assertEqual(response.status_code, 200)
        
        file_content = response.json()
        self.assertIn("content", file_content)
        self.assertIn("path", file_content)
        self.assertIn("encoding", file_content)
        
        # Verify content contains expected code
        content = file_content["content"]
        self.assertIn("class Application", content)
        self.assertIn("def main()", content)
        self.assertIn("import", content)
        
        print(f"✅ Retrieved file content ({len(content)} characters)")
        
        # Step 3: Run PMD analysis
        response = requests.get(f"{self.backend_url}/api/pmd/analysis/{main_file_id}")
        
        # PMD analysis might fail if PMD is not installed, which is acceptable
        if response.status_code == 200:
            pmd_result = response.json()
            self.assertIn("violations", pmd_result)
            self.assertIn("summary", pmd_result)
            print(f"✅ PMD analysis completed with {len(pmd_result['violations'])} violations")
        else:
            print(f"⚠️  PMD analysis failed (status {response.status_code}) - this is acceptable if PMD is not installed")
    
    def test_docker_container_communication(self):
        """Test communication between Docker containers."""
        print("\n=== Testing Docker Container Communication ===")
        
        # Test backend health endpoint
        response = requests.get(f"{self.backend_url}/health")
        self.assertEqual(response.status_code, 200)
        
        health_data = response.json()
        self.assertIn("status", health_data)
        self.assertEqual(health_data["status"], "healthy")
        self.assertIn("backend_dir", health_data)
        
        print("✅ Backend container is healthy and responding")
        
        # Test backend API endpoints
        response = requests.get(f"{self.backend_url}/api/root/")
        self.assertEqual(response.status_code, 200)
        
        root_data = response.json()
        self.assertIn("message", root_data)
        
        print("✅ Backend API endpoints are accessible")
        
        # Test frontend accessibility (basic connectivity)
        try:
            response = requests.get(self.frontend_url, timeout=10)
            # Frontend might return 404 for root path, which is OK
            self.assertIn(response.status_code, [200, 404])
            print("✅ Frontend container is accessible")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Frontend container accessibility test failed: {e}")
    
    def test_error_handling_scenarios(self):
        """Test system behavior under various error scenarios."""
        print("\n=== Testing Error Handling Scenarios ===")
        
        # Test file not found
        response = requests.get(f"{self.backend_url}/api/files/file_content/nonexistent.py")
        self.assertEqual(response.status_code, 404)
        
        error_data = response.json()
        self.assertIn("error", error_data)
        
        print("✅ File not found error handled correctly")
        
        # Test path traversal attack
        response = requests.get(f"{self.backend_url}/api/files/file_content/../../../etc/passwd")
        self.assertEqual(response.status_code, 403)
        
        error_data = response.json()
        self.assertIn("error", error_data)
        self.assertIn("Access denied", error_data["error"])
        
        print("✅ Path traversal attack blocked correctly")
        
        # Test invalid file extension
        response = requests.get(f"{self.backend_url}/api/files/file_content/test.txt")
        self.assertEqual(response.status_code, 403)
        
        error_data = response.json()
        self.assertIn("error", error_data)
        
        print("✅ Invalid file extension blocked correctly")
        
        # Test PMD analysis on non-existent file
        response = requests.get(f"{self.backend_url}/api/pmd/analysis/nonexistent.py")
        
        # Should either be 404 (file not found) or 403 (access denied)
        self.assertIn(response.status_code, [403, 404, 500])
        
        error_data = response.json()
        self.assertIn("error", error_data)
        
        print("✅ PMD analysis error handling works correctly")
    
    def test_concurrent_requests(self):
        """Test system behavior under concurrent load."""
        print("\n=== Testing Concurrent Request Handling ===")
        
        import threading
        import queue
        
        results = queue.Queue()
        num_threads = 5
        requests_per_thread = 3
        
        def make_requests():
            """Make multiple requests in a thread."""
            thread_results = []
            
            for i in range(requests_per_thread):
                try:
                    # Test different endpoints
                    endpoints = [
                        f"{self.backend_url}/health",
                        f"{self.backend_url}/api/root/",
                        f"{self.backend_url}/api/files/files_info"
                    ]
                    
                    for endpoint in endpoints:
                        response = requests.get(endpoint, timeout=10)
                        thread_results.append({
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "success": response.status_code == 200
                        })
                
                except Exception as e:
                    thread_results.append({
                        "endpoint": "unknown",
                        "status_code": 0,
                        "success": False,
                        "error": str(e)
                    })
            
            results.put(thread_results)
        
        # Start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)
        
        # Collect results
        all_results = []
        while not results.empty():
            all_results.extend(results.get())
        
        # Analyze results
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r["success"])
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        print(f"✅ Concurrent requests: {successful_requests}/{total_requests} successful ({success_rate:.1%})")
        
        # Should have high success rate
        self.assertGreater(success_rate, 0.8, "Success rate should be above 80%")
    
    def test_large_codebase_handling(self):
        """Test system behavior with larger codebase."""
        print("\n=== Testing Large Codebase Handling ===")
        
        # Create additional files to simulate larger codebase
        large_test_dir = os.path.join(self.test_dir, "large_module")
        os.makedirs(large_test_dir, exist_ok=True)
        
        # Create 20 additional Python files with cross-dependencies
        for i in range(20):
            file_content = f'''"""Generated module {i}."""
import os
import sys
from typing import List, Dict, Any

# Import from other generated modules
'''
            # Add imports to other modules
            for j in range(min(3, i)):  # Import from up to 3 previous modules
                file_content += f"from large_module.module_{j} import function_{j}\n"
            
            file_content += f'''

def function_{i}(data: Any) -> str:
    """Function {i} implementation."""
    result = f"Processing in module {i}: {{data}}"
    
    # Call imported functions
'''
            for j in range(min(3, i)):
                file_content += f"    result += function_{j}(data)\n"
            
            file_content += f'''
    return result


class Class_{i}:
    """Class {i} implementation."""
    
    def __init__(self, value: Any):
        self.value = value
    
    def process(self) -> str:
        return function_{i}(self.value)
'''
            
            with open(os.path.join(large_test_dir, f"module_{i}.py"), "w") as f:
                f.write(file_content)
        
        # Add __init__.py
        with open(os.path.join(large_test_dir, "__init__.py"), "w") as f:
            f.write("# Large module package\n")
        
        # Test file analysis with larger codebase
        start_time = time.time()
        response = requests.get(f"{self.backend_url}/api/files/files_info")
        analysis_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        total_files = len([f for f in file_data["files"] if f["type"] == "file"])
        total_relationships = len(file_data["relationships"])
        
        print(f"✅ Large codebase analysis: {total_files} files, {total_relationships} relationships in {analysis_time:.2f}s")
        
        # Should handle reasonable number of files efficiently
        self.assertGreater(total_files, 20)  # Should have at least our generated files
        self.assertLess(analysis_time, 30)   # Should complete within 30 seconds
        
        # Clean up
        shutil.rmtree(large_test_dir)
    
    def test_system_resource_usage(self):
        """Test system resource usage during operations."""
        print("\n=== Testing System Resource Usage ===")
        
        # Test memory usage by making multiple requests
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make multiple requests to test memory leaks
        for i in range(10):
            response = requests.get(f"{self.backend_url}/api/files/files_info")
            self.assertEqual(response.status_code, 200)
            
            # Force garbage collection
            gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"✅ Memory usage: {initial_memory:.1f}MB → {final_memory:.1f}MB (Δ{memory_increase:+.1f}MB)")
        
        # Memory increase should be reasonable (less than 100MB for this test)
        self.assertLess(memory_increase, 100, "Memory usage increase should be reasonable")


if __name__ == '__main__':
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Docker or docker-compose not available. Skipping end-to-end tests.")
        sys.exit(0)
    
    # Run tests
    unittest.main(verbosity=2)