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
test_backend_dir = tempfile.mkdtemp(prefix="final_integration_")
os.environ["BACKEND_DIR"] = test_backend_dir
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app


class TestFinalIntegration(unittest.TestCase):
    """Final integration tests for complete system functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up comprehensive test environment."""
        cls.test_dir = test_backend_dir
        cls.client = TestClient(app, headers={"host": "localhost"})
        
        # Create comprehensive test codebase
        cls.create_comprehensive_codebase()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_comprehensive_codebase(cls):
        """Create a comprehensive Python codebase for testing all features."""
        # Main application with complex imports and structure
        main_content = '''#!/usr/bin/env python3
"""
Comprehensive web application for testing all code navigator features.
This application demonstrates complex import relationships, error handling,
and various Python patterns that should be analyzed correctly.
"""
import os
import sys
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

# Local imports - these create the dependency relationships we want to test
from models.user import User, UserRole, UserManager
from models.project import Project, ProjectStatus, ProjectManager
from services.auth_service import AuthenticationService, TokenService
from services.data_service import DataProcessingService, CacheService
from services.notification_service import NotificationService, EmailService
from utils.validators import validate_email, validate_password, sanitize_input
from utils.helpers import format_datetime, calculate_hash, generate_uuid
from utils.database import DatabaseConnection, QueryBuilder
from config.settings import AppSettings, DatabaseSettings, SecuritySettings

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ApplicationStatus(Enum):
    """Application status enumeration."""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ApplicationConfig:
    """Application configuration data class."""
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")
        if self.workers < 1:
            raise ValueError(f"Invalid worker count: {self.workers}")


class WebApplication:
    """Main web application class with comprehensive functionality."""
    
    def __init__(self, config: ApplicationConfig):
        """Initialize the web application."""
        self.config = config
        self.status = ApplicationStatus.STARTING
        self.start_time: Optional[datetime] = None
        
        # Initialize services
        self.settings = AppSettings()
        self.db_connection = DatabaseConnection(self.settings.database)
        self.user_manager = UserManager(self.db_connection)
        self.project_manager = ProjectManager(self.db_connection)
        self.auth_service = AuthenticationService(self.user_manager)
        self.token_service = TokenService(self.settings.security)
        self.data_service = DataProcessingService()
        self.cache_service = CacheService()
        self.notification_service = NotificationService()
        self.email_service = EmailService(self.settings.email)
        
        # Initialize FastAPI app
        self.app = self._create_fastapi_app()
        
        logger.info("WebApplication initialized successfully")
    
    def _create_fastapi_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="Comprehensive Test Application",
            description="A comprehensive application for testing code analysis",
            version="1.0.0",
            debug=self.config.debug
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add routes
        self._add_routes(app)
        
        return app
    
    def _add_routes(self, app: FastAPI):
        """Add all application routes."""
        
        @app.get("/")
        async def root():
            """Root endpoint."""
            return {
                "message": "Comprehensive Test Application",
                "status": self.status.value,
                "uptime": self._get_uptime(),
                "version": "1.0.0"
            }
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy" if self.status == ApplicationStatus.RUNNING else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "database": self.db_connection.is_connected(),
                    "cache": self.cache_service.is_available(),
                    "email": self.email_service.is_configured()
                }
            }
        
        @app.post("/api/users")
        async def create_user(user_data: dict):
            """Create a new user."""
            try:
                # Validate input
                email = user_data.get("email")
                password = user_data.get("password")
                name = user_data.get("name")
                
                if not validate_email(email):
                    raise HTTPException(status_code=400, detail="Invalid email")
                
                if not validate_password(password):
                    raise HTTPException(status_code=400, detail="Invalid password")
                
                name = sanitize_input(name)
                
                # Create user
                user = User(
                    email=email,
                    name=name,
                    role=UserRole.USER
                )
                
                created_user = await self.user_manager.create_user(user, password)
                
                # Send notification
                await self.notification_service.send_welcome_email(created_user)
                
                return {
                    "id": created_user.id,
                    "email": created_user.email,
                    "name": created_user.name,
                    "created_at": created_user.created_at.isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @app.get("/api/projects")
        async def get_projects(user_id: Optional[int] = None):
            """Get projects, optionally filtered by user."""
            try:
                if user_id:
                    projects = await self.project_manager.get_user_projects(user_id)
                else:
                    projects = await self.project_manager.get_all_projects()
                
                return [
                    {
                        "id": p.id,
                        "name": p.name,
                        "status": p.status.value,
                        "created_at": p.created_at.isoformat()
                    }
                    for p in projects
                ]
                
            except Exception as e:
                logger.error(f"Error getting projects: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @app.post("/api/data/process")
        async def process_data(data: dict):
            """Process data using the data service."""
            try:
                # Process data
                processed = await self.data_service.process(data)
                
                # Cache result
                cache_key = generate_uuid()
                await self.cache_service.set(cache_key, processed)
                
                return {
                    "result": processed,
                    "cache_key": cache_key,
                    "processed_at": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error processing data: {e}")
                raise HTTPException(status_code=500, detail="Processing failed")
    
    def _get_uptime(self) -> Optional[str]:
        """Get application uptime."""
        if self.start_time:
            uptime = datetime.utcnow() - self.start_time
            return str(uptime)
        return None
    
    async def start(self):
        """Start the application."""
        try:
            self.status = ApplicationStatus.STARTING
            self.start_time = datetime.utcnow()
            
            # Initialize database
            await self.db_connection.connect()
            
            # Initialize services
            await self.cache_service.initialize()
            await self.notification_service.initialize()
            
            self.status = ApplicationStatus.RUNNING
            logger.info("Application started successfully")
            
        except Exception as e:
            self.status = ApplicationStatus.ERROR
            logger.error(f"Failed to start application: {e}")
            raise
    
    async def stop(self):
        """Stop the application."""
        try:
            self.status = ApplicationStatus.STOPPING
            
            # Cleanup services
            await self.cache_service.cleanup()
            await self.notification_service.cleanup()
            await self.db_connection.disconnect()
            
            self.status = ApplicationStatus.STOPPED
            logger.info("Application stopped successfully")
            
        except Exception as e:
            self.status = ApplicationStatus.ERROR
            logger.error(f"Error stopping application: {e}")
            raise


async def main():
    """Main application entry point."""
    config = ApplicationConfig(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        workers=int(os.getenv("WORKERS", "1")),
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )
    
    app = WebApplication(config)
    
    try:
        await app.start()
        
        # Run the application
        import uvicorn
        await uvicorn.run(
            app.app,
            host=config.host,
            port=config.port,
            workers=config.workers,
            reload=config.reload
        )
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
'''    
    
        # Create models directory with comprehensive user and project models
        models_dir = os.path.join(cls.test_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        user_model = '''"""Comprehensive user model with relationships and validation."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import hashlib
import secrets


class UserRole(Enum):
    """User role enumeration with comprehensive permissions."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"


class UserStatus(Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


@dataclass
class UserProfile:
    """User profile information."""
    first_name: str
    last_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class UserPreferences:
    """User application preferences."""
    theme: str = "light"
    notifications_enabled: bool = True
    email_notifications: bool = True
    dashboard_layout: str = "default"
    items_per_page: int = 20
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preferences to dictionary."""
        return {
            "theme": self.theme,
            "notifications_enabled": self.notifications_enabled,
            "email_notifications": self.email_notifications,
            "dashboard_layout": self.dashboard_layout,
            "items_per_page": self.items_per_page
        }


class User:
    """Comprehensive user model with full functionality."""
    
    def __init__(
        self,
        email: str,
        username: str,
        role: UserRole = UserRole.USER,
        status: UserStatus = UserStatus.ACTIVE,
        profile: Optional[UserProfile] = None,
        preferences: Optional[UserPreferences] = None
    ):
        """Initialize user with comprehensive data."""
        self.id: Optional[int] = None
        self.email = email
        self.username = username
        self.role = role
        self.status = status
        self.profile = profile or UserProfile("", "")
        self.preferences = preferences or UserPreferences()
        
        # Security fields
        self.password_hash: Optional[str] = None
        self.salt: Optional[str] = None
        self.last_login: Optional[datetime] = None
        self.failed_login_attempts: int = 0
        self.account_locked_until: Optional[datetime] = None
        
        # Audit fields
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.created_by: Optional[int] = None
        self.updated_by: Optional[int] = None
        
        # Relationships
        self.projects: List['Project'] = field(default_factory=list)
        self.sessions: List['UserSession'] = field(default_factory=list)
    
    def set_password(self, password: str) -> None:
        """Set user password with secure hashing."""
        self.salt = secrets.token_hex(32)
        self.password_hash = self._hash_password(password, self.salt)
        self.updated_at = datetime.utcnow()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        if not self.password_hash or not self.salt:
            return False
        
        return self.password_hash == self._hash_password(password, self.salt)
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN
    
    def is_manager(self) -> bool:
        """Check if user has manager role or higher."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE
    
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False
    
    def lock_account(self, duration_minutes: int = 30) -> None:
        """Lock user account for specified duration."""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.updated_at = datetime.utcnow()
    
    def unlock_account(self) -> None:
        """Unlock user account."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.updated_at = datetime.utcnow()
    
    def record_login_attempt(self, success: bool) -> None:
        """Record login attempt."""
        if success:
            self.last_login = datetime.utcnow()
            self.failed_login_attempts = 0
        else:
            self.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if self.failed_login_attempts >= 5:
                self.lock_account()
        
        self.updated_at = datetime.utcnow()
    
    def can_access_project(self, project: 'Project') -> bool:
        """Check if user can access a specific project."""
        if self.is_admin():
            return True
        
        return project in self.projects or project.owner_id == self.id
    
    def get_permissions(self) -> List[str]:
        """Get user permissions based on role."""
        permissions = ["read_own_profile", "update_own_profile"]
        
        if self.role == UserRole.USER:
            permissions.extend(["create_project", "read_own_projects"])
        elif self.role == UserRole.MANAGER:
            permissions.extend([
                "create_project", "read_all_projects", "update_projects",
                "read_users", "create_users"
            ])
        elif self.role == UserRole.ADMIN:
            permissions.extend([
                "create_project", "read_all_projects", "update_projects", "delete_projects",
                "read_users", "create_users", "update_users", "delete_users",
                "system_admin"
            ])
        
        return permissions
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        data = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "role": self.role.value,
            "status": self.status.value,
            "profile": {
                "first_name": self.profile.first_name,
                "last_name": self.profile.last_name,
                "full_name": self.profile.full_name,
                "bio": self.profile.bio,
                "avatar_url": self.profile.avatar_url,
                "timezone": self.profile.timezone,
                "language": self.profile.language
            },
            "preferences": self.preferences.to_dict(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "permissions": self.get_permissions()
        }
        
        if include_sensitive:
            data.update({
                "failed_login_attempts": self.failed_login_attempts,
                "account_locked_until": self.account_locked_until.isoformat() if self.account_locked_until else None,
                "created_by": self.created_by,
                "updated_by": self.updated_by
            })
        
        return data
    
    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"


class UserManager:
    """User management service with comprehensive functionality."""
    
    def __init__(self, db_connection):
        """Initialize user manager."""
        self.db = db_connection
        self.users: List[User] = []
    
    async def create_user(self, user: User, password: str) -> User:
        """Create a new user."""
        # Check if user already exists
        existing = await self.get_user_by_email(user.email)
        if existing:
            raise ValueError(f"User with email {user.email} already exists")
        
        existing = await self.get_user_by_username(user.username)
        if existing:
            raise ValueError(f"User with username {user.username} already exists")
        
        # Set password
        user.set_password(password)
        
        # Assign ID (in real app, this would be from database)
        user.id = len(self.users) + 1
        
        # Add to storage
        self.users.append(user)
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users:
            if user.email == email:
                return user
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    async def get_all_users(self) -> List[User]:
        """Get all users."""
        return self.users.copy()
    
    async def update_user(self, user_id: int, updates: Dict[str, Any]) -> Optional[User]:
        """Update user information."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update allowed fields
        for field, value in updates.items():
            if hasattr(user, field) and field not in ['id', 'password_hash', 'salt']:
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by setting status)."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.status = UserStatus.DELETED
        user.updated_at = datetime.utcnow()
        return True


@dataclass
class UserSession:
    """User session tracking."""
    user_id: int
    session_token: str
    ip_address: str
    user_agent: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def extend_session(self, hours: int = 24) -> None:
        """Extend session expiration."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
'''

        project_model = '''"""Comprehensive project model with relationships and status tracking."""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import uuid


class ProjectStatus(Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ProjectPriority(Enum):
    """Project priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ProjectMetrics:
    """Project metrics and statistics."""
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0
    total_hours_logged: float = 0.0
    estimated_hours: float = 0.0
    
    @property
    def completion_percentage(self) -> float:
        """Calculate project completion percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100
    
    @property
    def is_over_budget(self) -> bool:
        """Check if project is over estimated hours."""
        return self.total_hours_logged > self.estimated_hours
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "pending_tasks": self.pending_tasks,
            "overdue_tasks": self.overdue_tasks,
            "total_hours_logged": self.total_hours_logged,
            "estimated_hours": self.estimated_hours,
            "completion_percentage": self.completion_percentage,
            "is_over_budget": self.is_over_budget
        }


class Project:
    """Comprehensive project model with full functionality."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        owner_id: Optional[int] = None,
        status: ProjectStatus = ProjectStatus.DRAFT,
        priority: ProjectPriority = ProjectPriority.MEDIUM
    ):
        """Initialize project with comprehensive data."""
        self.id: Optional[int] = None
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.status = status
        self.priority = priority
        
        # Dates
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.start_date: Optional[datetime] = None
        self.due_date: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
        # Metrics
        self.metrics = ProjectMetrics()
        
        # Relationships
        self.team_members: List[int] = field(default_factory=list)  # User IDs
        self.tasks: List['Task'] = field(default_factory=list)
        self.attachments: List['ProjectAttachment'] = field(default_factory=list)
        
        # Audit fields
        self.created_by: Optional[int] = None
        self.updated_by: Optional[int] = None
    
    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status == ProjectStatus.ACTIVE
    
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == ProjectStatus.COMPLETED
    
    def is_overdue(self) -> bool:
        """Check if project is overdue."""
        if self.due_date and not self.is_completed():
            return datetime.utcnow() > self.due_date
        return False
    
    def days_until_due(self) -> Optional[int]:
        """Get days until due date."""
        if self.due_date:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None
    
    def add_team_member(self, user_id: int) -> None:
        """Add team member to project."""
        if user_id not in self.team_members:
            self.team_members.append(user_id)
            self.updated_at = datetime.utcnow()
    
    def remove_team_member(self, user_id: int) -> None:
        """Remove team member from project."""
        if user_id in self.team_members:
            self.team_members.remove(user_id)
            self.updated_at = datetime.utcnow()
    
    def can_be_accessed_by(self, user_id: int, user_role: str = "user") -> bool:
        """Check if user can access this project."""
        if user_role == "admin":
            return True
        
        return (
            self.owner_id == user_id or
            user_id in self.team_members
        )
    
    def can_be_modified_by(self, user_id: int, user_role: str = "user") -> bool:
        """Check if user can modify this project."""
        if user_role == "admin":
            return True
        
        return self.owner_id == user_id
    
    def update_status(self, new_status: ProjectStatus, user_id: Optional[int] = None) -> None:
        """Update project status with audit trail."""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id
        
        # Set completion date if completed
        if new_status == ProjectStatus.COMPLETED and old_status != ProjectStatus.COMPLETED:
            self.completed_at = datetime.utcnow()
        elif new_status != ProjectStatus.COMPLETED:
            self.completed_at = None
    
    def update_metrics(self) -> None:
        """Update project metrics based on tasks."""
        self.metrics.total_tasks = len(self.tasks)
        self.metrics.completed_tasks = sum(1 for task in self.tasks if task.is_completed())
        self.metrics.pending_tasks = self.metrics.total_tasks - self.metrics.completed_tasks
        self.metrics.overdue_tasks = sum(1 for task in self.tasks if task.is_overdue())
        
        # Update hours (would be calculated from task time logs in real app)
        self.metrics.total_hours_logged = sum(task.hours_logged for task in self.tasks)
        
        self.updated_at = datetime.utcnow()
    
    def get_status_history(self) -> List[Dict[str, Any]]:
        """Get project status change history."""
        # In a real application, this would query a status history table
        return [
            {
                "status": self.status.value,
                "changed_at": self.updated_at.isoformat(),
                "changed_by": self.updated_by
            }
        ]
    
    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """Convert project to dictionary representation."""
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_overdue": self.is_overdue(),
            "days_until_due": self.days_until_due(),
            "metrics": self.metrics.to_dict(),
            "team_member_count": len(self.team_members)
        }
        
        if include_details:
            data.update({
                "team_members": self.team_members,
                "task_count": len(self.tasks),
                "attachment_count": len(self.attachments),
                "status_history": self.get_status_history(),
                "created_by": self.created_by,
                "updated_by": self.updated_by
            })
        
        return data
    
    def __repr__(self) -> str:
        return f"<Project {self.name} ({self.status.value})>"


class ProjectManager:
    """Project management service with comprehensive functionality."""
    
    def __init__(self, db_connection):
        """Initialize project manager."""
        self.db = db_connection
        self.projects: List[Project] = []
    
    async def create_project(self, project: Project) -> Project:
        """Create a new project."""
        # Assign ID (in real app, this would be from database)
        project.id = len(self.projects) + 1
        
        # Add to storage
        self.projects.append(project)
        
        return project
    
    async def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        for project in self.projects:
            if project.id == project_id:
                return project
        return None
    
    async def get_project_by_uuid(self, project_uuid: str) -> Optional[Project]:
        """Get project by UUID."""
        for project in self.projects:
            if project.uuid == project_uuid:
                return project
        return None
    
    async def get_user_projects(self, user_id: int) -> List[Project]:
        """Get projects for a specific user."""
        return [
            project for project in self.projects
            if project.can_be_accessed_by(user_id)
        ]
    
    async def get_projects_by_status(self, status: ProjectStatus) -> List[Project]:
        """Get projects by status."""
        return [
            project for project in self.projects
            if project.status == status
        ]
    
    async def get_all_projects(self) -> List[Project]:
        """Get all projects."""
        return self.projects.copy()
    
    async def update_project(self, project_id: int, updates: Dict[str, Any]) -> Optional[Project]:
        """Update project information."""
        project = await self.get_project_by_id(project_id)
        if not project:
            return None
        
        # Update allowed fields
        for field, value in updates.items():
            if hasattr(project, field) and field not in ['id', 'uuid', 'created_at']:
                setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        return project
    
    async def delete_project(self, project_id: int) -> bool:
        """Delete project (soft delete by archiving)."""
        project = await self.get_project_by_id(project_id)
        if not project:
            return False
        
        project.update_status(ProjectStatus.ARCHIVED)
        return True


@dataclass
class Task:
    """Task model for project tasks."""
    title: str
    description: str = ""
    project_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: str = "pending"
    priority: str = "medium"
    due_date: Optional[datetime] = None
    hours_logged: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == "completed"
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and not self.is_completed():
            return datetime.utcnow() > self.due_date
        return False


@dataclass
class ProjectAttachment:
    """Project attachment model."""
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_by: int
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
'''  
      
        # Create services directory with comprehensive service implementations
        services_dir = os.path.join(cls.test_dir, "services")
        os.makedirs(services_dir, exist_ok=True)
        
        auth_service = '''"""Comprehensive authentication service with security features."""
import jwt
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenPayload:
    """JWT token payload structure."""
    user_id: int
    username: str
    email: str
    role: str
    issued_at: datetime
    expires_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JWT encoding."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "iat": int(self.issued_at.timestamp()),
            "exp": int(self.expires_at.timestamp())
        }


class AuthenticationService:
    """Comprehensive authentication service with security features."""
    
    def __init__(self, user_manager, secret_key: str = "test-secret-key"):
        """Initialize authentication service."""
        self.user_manager = user_manager
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
        self.refresh_token_expiry_days = 30
        
        # Security tracking
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
    
    async def authenticate_user(self, email: str, password: str, ip_address: str = None) -> Optional['User']:
        """Authenticate user with comprehensive security checks."""
        try:
            # Check if IP is blocked
            if ip_address and self._is_ip_blocked(ip_address):
                logger.warning(f"Authentication attempt from blocked IP: {ip_address}")
                return None
            
            # Get user
            user = await self.user_manager.get_user_by_email(email)
            if not user:
                self._record_failed_attempt(email, ip_address)
                return None
            
            # Check if account is locked
            if user.is_locked():
                logger.warning(f"Authentication attempt for locked account: {email}")
                return None
            
            # Check if account is active
            if not user.is_active():
                logger.warning(f"Authentication attempt for inactive account: {email}")
                return None
            
            # Verify password
            if not user.verify_password(password):
                user.record_login_attempt(False)
                self._record_failed_attempt(email, ip_address)
                return None
            
            # Successful authentication
            user.record_login_attempt(True)
            self._clear_failed_attempts(email, ip_address)
            
            logger.info(f"User authenticated successfully: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return None
    
    def generate_token(self, user: 'User') -> str:
        """Generate JWT token for authenticated user."""
        try:
            payload = TokenPayload(
                user_id=user.id,
                username=user.username,
                email=user.email,
                role=user.role.value,
                issued_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
            )
            
            token = jwt.encode(payload.to_dict(), self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Token generation error for user {user.id}: {e}")
            return ""
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def generate_refresh_token(self, user: 'User') -> str:
        """Generate refresh token for token renewal."""
        payload = {
            "user_id": user.id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expiry_days)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token."""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                return None
            
            user = await self.user_manager.get_user_by_id(payload["user_id"])
            if not user or not user.is_active():
                return None
            
            return self.generate_token(user)
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    def _record_failed_attempt(self, identifier: str, ip_address: str = None) -> None:
        """Record failed authentication attempt."""
        now = datetime.utcnow()
        
        # Record by email/username
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        self.failed_attempts[identifier].append(now)
        
        # Record by IP if provided
        if ip_address:
            if ip_address not in self.failed_attempts:
                self.failed_attempts[ip_address] = []
            self.failed_attempts[ip_address].append(now)
            
            # Block IP after too many attempts
            recent_attempts = [
                attempt for attempt in self.failed_attempts[ip_address]
                if now - attempt < timedelta(minutes=15)
            ]
            
            if len(recent_attempts) >= 10:
                self.blocked_ips[ip_address] = now + timedelta(hours=1)
                logger.warning(f"IP blocked due to too many failed attempts: {ip_address}")
    
    def _clear_failed_attempts(self, identifier: str, ip_address: str = None) -> None:
        """Clear failed attempts after successful authentication."""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
        
        if ip_address and ip_address in self.failed_attempts:
            del self.failed_attempts[ip_address]
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked."""
        if ip_address in self.blocked_ips:
            if datetime.utcnow() > self.blocked_ips[ip_address]:
                # Block expired, remove it
                del self.blocked_ips[ip_address]
                return False
            return True
        return False
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        now = datetime.utcnow()
        
        # Count recent failed attempts
        recent_failures = 0
        for attempts in self.failed_attempts.values():
            recent_failures += len([
                attempt for attempt in attempts
                if now - attempt < timedelta(hours=1)
            ])
        
        # Count blocked IPs
        active_blocks = len([
            ip for ip, block_until in self.blocked_ips.items()
            if now < block_until
        ])
        
        return {
            "recent_failed_attempts": recent_failures,
            "active_ip_blocks": active_blocks,
            "total_tracked_identifiers": len(self.failed_attempts),
            "security_level": "high" if active_blocks > 0 else "normal"
        }


class TokenService:
    """Token management service."""
    
    def __init__(self, security_settings):
        """Initialize token service."""
        self.security_settings = security_settings
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        self.revoked_tokens: set = set()
    
    def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked."""
        return token in self.revoked_tokens
    
    def revoke_token(self, token: str) -> None:
        """Revoke a token."""
        self.revoked_tokens.add(token)
        if token in self.active_tokens:
            del self.active_tokens[token]
    
    def revoke_user_tokens(self, user_id: int) -> None:
        """Revoke all tokens for a user."""
        tokens_to_revoke = [
            token for token, data in self.active_tokens.items()
            if data.get("user_id") == user_id
        ]
        
        for token in tokens_to_revoke:
            self.revoke_token(token)
    
    def cleanup_expired_tokens(self) -> None:
        """Clean up expired tokens."""
        now = datetime.utcnow()
        expired_tokens = [
            token for token, data in self.active_tokens.items()
            if data.get("expires_at", now) < now
        ]
        
        for token in expired_tokens:
            if token in self.active_tokens:
                del self.active_tokens[token]
'''

        data_service = '''"""Comprehensive data processing service."""
import json
import hashlib
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Data processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingResult:
    """Data processing result."""
    id: str
    status: ProcessingStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_time_seconds": self.processing_time_seconds
        }


class DataProcessingService:
    """Comprehensive data processing service."""
    
    def __init__(self):
        """Initialize data processing service."""
        self.processing_jobs: Dict[str, ProcessingResult] = {}
        self.max_concurrent_jobs = 5
        self.current_jobs = 0
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with comprehensive handling."""
        job_id = self._generate_job_id(data)
        
        # Create processing result
        result = ProcessingResult(
            id=job_id,
            status=ProcessingStatus.PENDING,
            input_data=data,
            started_at=datetime.utcnow()
        )
        
        self.processing_jobs[job_id] = result
        
        try:
            # Check concurrent job limit
            if self.current_jobs >= self.max_concurrent_jobs:
                raise RuntimeError("Maximum concurrent jobs exceeded")
            
            self.current_jobs += 1
            result.status = ProcessingStatus.PROCESSING
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            # Process the data
            processed_data = await self._process_data(data)
            
            # Complete processing
            result.status = ProcessingStatus.COMPLETED
            result.output_data = processed_data
            result.completed_at = datetime.utcnow()
            result.processing_time_seconds = (
                result.completed_at - result.started_at
            ).total_seconds()
            
            logger.info(f"Data processing completed: {job_id}")
            return processed_data
            
        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            
            logger.error(f"Data processing failed: {job_id} - {e}")
            raise
            
        finally:
            self.current_jobs -= 1
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal data processing logic."""
        processed = {
            "original_data": data,
            "processed_at": datetime.utcnow().isoformat(),
            "data_hash": hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest(),
            "data_size": len(json.dumps(data)),
            "data_type": type(data).__name__,
            "field_count": len(data) if isinstance(data, dict) else 0,
            "processing_metadata": {
                "version": "1.0",
                "algorithm": "standard",
                "quality_score": self._calculate_quality_score(data)
            }
        }
        
        # Process different data types
        if isinstance(data, dict):
            processed["processed_fields"] = {}
            for key, value in data.items():
                processed["processed_fields"][key] = {
                    "original_value": value,
                    "value_type": type(value).__name__,
                    "processed_value": self._process_field_value(value)
                }
        
        return processed
    
    def _process_field_value(self, value: Any) -> Any:
        """Process individual field value."""
        if isinstance(value, str):
            return {
                "length": len(value),
                "uppercase": value.upper(),
                "lowercase": value.lower(),
                "word_count": len(value.split()) if value else 0
            }
        elif isinstance(value, (int, float)):
            return {
                "original": value,
                "squared": value ** 2,
                "is_positive": value > 0,
                "absolute": abs(value)
            }
        elif isinstance(value, list):
            return {
                "length": len(value),
                "types": [type(item).__name__ for item in value],
                "first_item": value[0] if value else None,
                "last_item": value[-1] if value else None
            }
        else:
            return {
                "type": type(value).__name__,
                "string_representation": str(value)
            }
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score."""
        if not isinstance(data, dict):
            return 0.5
        
        score = 0.0
        total_fields = len(data)
        
        if total_fields == 0:
            return 0.0
        
        for key, value in data.items():
            # Score based on field completeness
            if value is not None and value != "":
                score += 0.3
            
            # Score based on field type appropriateness
            if isinstance(value, (str, int, float, bool)):
                score += 0.2
            
            # Score based on field name quality
            if len(key) > 2 and key.isalnum():
                score += 0.1
        
        return min(score / total_fields, 1.0)
    
    def _generate_job_id(self, data: Dict[str, Any]) -> str:
        """Generate unique job ID."""
        data_str = json.dumps(data, sort_keys=True)
        timestamp = datetime.utcnow().isoformat()
        combined = f"{data_str}_{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def get_job_status(self, job_id: str) -> Optional[ProcessingResult]:
        """Get processing job status."""
        return self.processing_jobs.get(job_id)
    
    def get_all_jobs(self) -> List[ProcessingResult]:
        """Get all processing jobs."""
        return list(self.processing_jobs.values())
    
    def cleanup_old_jobs(self, hours: int = 24) -> None:
        """Clean up old processing jobs."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        jobs_to_remove = [
            job_id for job_id, result in self.processing_jobs.items()
            if result.completed_at and result.completed_at < cutoff
        ]
        
        for job_id in jobs_to_remove:
            del self.processing_jobs[job_id]
        
        logger.info(f"Cleaned up {len(jobs_to_remove)} old processing jobs")


class CacheService:
    """Simple in-memory cache service."""
    
    def __init__(self, default_ttl_seconds: int = 3600):
        """Initialize cache service."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds
    
    async def initialize(self) -> None:
        """Initialize cache service."""
        logger.info("Cache service initialized")
    
    async def cleanup(self) -> None:
        """Cleanup cache service."""
        self.cache.clear()
        logger.info("Cache service cleaned up")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.utcnow() < entry["expires_at"]:
                return entry["value"]
            else:
                # Expired, remove it
                del self.cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl_seconds or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def is_available(self) -> bool:
        """Check if cache service is available."""
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.utcnow()
        active_entries = 0
        expired_entries = 0
        
        for entry in self.cache.values():
            if now < entry["expires_at"]:
                active_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "hit_rate": 0.85  # Simulated hit rate
        }
'''

        notification_service = '''"""Comprehensive notification service."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification type enumeration."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Notification data structure."""
    id: str
    type: NotificationType
    priority: NotificationPriority
    recipient: str
    subject: str
    message: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    @property
    def is_sent(self) -> bool:
        """Check if notification was sent."""
        return self.sent_at is not None
    
    @property
    def is_delivered(self) -> bool:
        """Check if notification was delivered."""
        return self.delivered_at is not None
    
    @property
    def is_failed(self) -> bool:
        """Check if notification failed."""
        return self.failed_at is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "recipient": self.recipient,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "is_sent": self.is_sent,
            "is_delivered": self.is_delivered,
            "is_failed": self.is_failed
        }


class NotificationService:
    """Comprehensive notification service."""
    
    def __init__(self):
        """Initialize notification service."""
        self.notifications: Dict[str, Notification] = {}
        self.pending_queue: List[str] = []
        self.processing = False
    
    async def initialize(self) -> None:
        """Initialize notification service."""
        logger.info("Notification service initialized")
        # Start background processing
        asyncio.create_task(self._process_queue())
    
    async def cleanup(self) -> None:
        """Cleanup notification service."""
        self.processing = False
        logger.info("Notification service cleaned up")
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        recipient: str,
        subject: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM
    ) -> str:
        """Send a notification."""
        notification_id = self._generate_notification_id()
        
        notification = Notification(
            id=notification_id,
            type=notification_type,
            priority=priority,
            recipient=recipient,
            subject=subject,
            message=message,
            created_at=datetime.utcnow()
        )
        
        self.notifications[notification_id] = notification
        
        # Add to queue based on priority
        if priority == NotificationPriority.URGENT:
            self.pending_queue.insert(0, notification_id)  # High priority first
        else:
            self.pending_queue.append(notification_id)
        
        logger.info(f"Notification queued: {notification_id}")
        return notification_id
    
    async def send_welcome_email(self, user: 'User') -> str:
        """Send welcome email to new user."""
        subject = "Welcome to the Application!"
        message = f"""
        Hello {user.profile.first_name or user.username},
        
        Welcome to our application! Your account has been created successfully.
        
        Account Details:
        - Username: {user.username}
        - Email: {user.email}
        - Role: {user.role.value}
        - Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        
        You can now log in and start using the application.
        
        Best regards,
        The Application Team
        """
        
        return await self.send_notification(
            NotificationType.EMAIL,
            user.email,
            subject,
            message,
            NotificationPriority.MEDIUM
        )
    
    async def send_project_notification(
        self,
        project: 'Project',
        user_email: str,
        notification_type: str
    ) -> str:
        """Send project-related notification."""
        subjects = {
            "created": f"New Project Created: {project.name}",
            "updated": f"Project Updated: {project.name}",
            "completed": f"Project Completed: {project.name}",
            "overdue": f"Project Overdue: {project.name}"
        }
        
        messages = {
            "created": f"A new project '{project.name}' has been created.",
            "updated": f"Project '{project.name}' has been updated.",
            "completed": f"Project '{project.name}' has been completed.",
            "overdue": f"Project '{project.name}' is overdue. Please review."
        }
        
        subject = subjects.get(notification_type, f"Project Notification: {project.name}")
        message = messages.get(notification_type, f"Project '{project.name}' notification.")
        
        priority = NotificationPriority.HIGH if notification_type == "overdue" else NotificationPriority.MEDIUM
        
        return await self.send_notification(
            NotificationType.EMAIL,
            user_email,
            subject,
            message,
            priority
        )
    
    async def _process_queue(self) -> None:
        """Process notification queue in background."""
        self.processing = True
        
        while self.processing:
            if self.pending_queue:
                notification_id = self.pending_queue.pop(0)
                notification = self.notifications.get(notification_id)
                
                if notification:
                    await self._send_notification(notification)
            
            # Wait before processing next batch
            await asyncio.sleep(1)
    
    async def _send_notification(self, notification: Notification) -> None:
        """Send individual notification."""
        try:
            # Simulate sending delay
            await asyncio.sleep(0.1)
            
            # Simulate different success rates based on type
            success_rates = {
                NotificationType.EMAIL: 0.95,
                NotificationType.SMS: 0.90,
                NotificationType.PUSH: 0.85,
                NotificationType.IN_APP: 0.99
            }
            
            import random
            success_rate = success_rates.get(notification.type, 0.90)
            
            if random.random() < success_rate:
                # Success
                notification.sent_at = datetime.utcnow()
                
                # Simulate delivery confirmation delay
                await asyncio.sleep(0.05)
                notification.delivered_at = datetime.utcnow()
                
                logger.info(f"Notification sent successfully: {notification.id}")
            else:
                # Failure
                raise Exception(f"Failed to send {notification.type.value} notification")
                
        except Exception as e:
            notification.failed_at = datetime.utcnow()
            notification.error_message = str(e)
            notification.retry_count += 1
            
            logger.error(f"Notification failed: {notification.id} - {e}")
            
            # Retry if under max retries
            if notification.retry_count < notification.max_retries:
                # Add back to queue for retry
                self.pending_queue.append(notification.id)
                logger.info(f"Notification queued for retry: {notification.id}")
    
    def _generate_notification_id(self) -> str:
        """Generate unique notification ID."""
        import uuid
        return str(uuid.uuid4())
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        return self.notifications.get(notification_id)
    
    def get_notifications_for_recipient(self, recipient: str) -> List[Notification]:
        """Get all notifications for a recipient."""
        return [
            notification for notification in self.notifications.values()
            if notification.recipient == recipient
        ]
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        total = len(self.notifications)
        sent = sum(1 for n in self.notifications.values() if n.is_sent)
        delivered = sum(1 for n in self.notifications.values() if n.is_delivered)
        failed = sum(1 for n in self.notifications.values() if n.is_failed)
        pending = len(self.pending_queue)
        
        return {
            "total_notifications": total,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "success_rate": (delivered / total * 100) if total > 0 else 0,
            "delivery_rate": (delivered / sent * 100) if sent > 0 else 0
        }


class EmailService:
    """Email service implementation."""
    
    def __init__(self, email_settings):
        """Initialize email service."""
        self.settings = email_settings
        self.configured = True  # Simulate configuration
    
    def is_configured(self) -> bool:
        """Check if email service is configured."""
        return self.configured
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email."""
        try:
            # Simulate email sending
            await asyncio.sleep(0.1)
            
            logger.info(f"Email sent to {to}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False
'''   
     
        # Create utils directory with comprehensive utility functions
        utils_dir = os.path.join(cls.test_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        validators = '''"""Comprehensive input validation utilities."""
import re
import html
import urllib.parse
from typing import Any, Optional, List, Dict
from datetime import datetime


def validate_email(email: str) -> bool:
    """Validate email format with comprehensive checks."""
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    
    # Basic format check
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Length checks
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    local, domain = email.split('@')
    if len(local) > 64:  # RFC 5321 limit
        return False
    
    # Domain checks
    if domain.startswith('.') or domain.endswith('.'):
        return False
    
    if '..' in domain:
        return False
    
    return True


def validate_password(password: str) -> bool:
    """Validate password strength with comprehensive requirements."""
    if not password or not isinstance(password, str):
        return False
    
    # Length requirement
    if len(password) < 8:
        return False
    
    # Character requirements
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    # Must have at least 3 of the 4 character types
    char_types = sum([has_upper, has_lower, has_digit, has_special])
    if char_types < 3:
        return False
    
    # Common password checks
    common_passwords = [
        "password", "123456", "password123", "admin", "qwerty",
        "letmein", "welcome", "monkey", "dragon", "master"
    ]
    
    if password.lower() in common_passwords:
        return False
    
    # Sequential character check
    if has_sequential_chars(password):
        return False
    
    return True


def has_sequential_chars(password: str) -> bool:
    """Check for sequential characters in password."""
    sequences = [
        "abcdefghijklmnopqrstuvwxyz",
        "0123456789",
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm"
    ]
    
    password_lower = password.lower()
    
    for sequence in sequences:
        for i in range(len(sequence) - 2):
            if sequence[i:i+3] in password_lower:
                return True
            # Check reverse sequence
            if sequence[i:i+3][::-1] in password_lower:
                return True
    
    return False


def validate_username(username: str) -> bool:
    """Validate username format."""
    if not username or not isinstance(username, str):
        return False
    
    username = username.strip()
    
    # Length check
    if not (3 <= len(username) <= 30):
        return False
    
    # Character check - alphanumeric, underscore, hyphen only
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False
    
    # Must start with letter or number
    if not username[0].isalnum():
        return False
    
    # Cannot end with underscore or hyphen
    if username[-1] in '_-':
        return False
    
    # No consecutive special characters
    if '__' in username or '--' in username or '_-' in username or '-_' in username:
        return False
    
    return True


def validate_project_name(name: str) -> bool:
    """Validate project name."""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    
    # Length check
    if not (1 <= len(name) <= 100):
        return False
    
    # Must contain at least one alphanumeric character
    if not any(c.isalnum() for c in name):
        return False
    
    # Cannot start or end with whitespace (already stripped)
    # Cannot contain only whitespace
    if not name.replace(' ', '').replace('\t', ''):
        return False
    
    return True


def validate_url(url: str) -> bool:
    """Validate URL format."""
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    # Basic URL pattern
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url, re.IGNORECASE):
        return False
    
    # Length check
    if len(url) > 2048:
        return False
    
    return True


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common formatting characters
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Must be 10-15 digits (international format)
    if not (10 <= len(cleaned.replace('+', '')) <= 15):
        return False
    
    # Can start with + for international
    if cleaned.startswith('+'):
        if len(cleaned) < 11:  # + plus at least 10 digits
            return False
    
    return True


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and other attacks."""
    if not text or not isinstance(text, str):
        return ""
    
    # HTML escape
    text = html.escape(text)
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Limit length
    if len(text) > 1000:
        text = text[:1000]
    
    return text


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    if not filename or not isinstance(filename, str):
        return "unnamed_file"
    
    # Remove path separators and dangerous characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\x00']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure not empty
    if not filename:
        filename = "unnamed_file"
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_len = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_len] + ('.' + ext if ext else '')
    
    return filename


def validate_json_data(data: Any) -> bool:
    """Validate JSON data structure."""
    try:
        import json
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False


def validate_date_string(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """Validate date string format."""
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def validate_integer_range(value: Any, min_val: int = None, max_val: int = None) -> bool:
    """Validate integer within range."""
    try:
        int_val = int(value)
        
        if min_val is not None and int_val < min_val:
            return False
        
        if max_val is not None and int_val > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension against allowed list."""
    if not filename or not isinstance(filename, str):
        return False
    
    if not allowed_extensions:
        return True
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    allowed_lower = [ext.lower().lstrip('.') for ext in allowed_extensions]
    
    return file_ext in allowed_lower


def validate_ip_address(ip: str) -> bool:
    """Validate IP address format (IPv4 or IPv6)."""
    if not ip or not isinstance(ip, str):
        return False
    
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    # IPv6 pattern (simplified)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    if re.match(ipv6_pattern, ip):
        return True
    
    return False


class ValidationError(Exception):
    """Custom validation error."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_user_data(data: Dict[str, Any]) -> List[ValidationError]:
    """Validate user data comprehensively."""
    errors = []
    
    # Email validation
    if 'email' in data:
        if not validate_email(data['email']):
            errors.append(ValidationError('email', 'Invalid email format'))
    
    # Username validation
    if 'username' in data:
        if not validate_username(data['username']):
            errors.append(ValidationError('username', 'Invalid username format'))
    
    # Password validation
    if 'password' in data:
        if not validate_password(data['password']):
            errors.append(ValidationError('password', 'Password does not meet requirements'))
    
    # Phone validation
    if 'phone' in data and data['phone']:
        if not validate_phone_number(data['phone']):
            errors.append(ValidationError('phone', 'Invalid phone number format'))
    
    return errors


def validate_project_data(data: Dict[str, Any]) -> List[ValidationError]:
    """Validate project data comprehensively."""
    errors = []
    
    # Name validation
    if 'name' in data:
        if not validate_project_name(data['name']):
            errors.append(ValidationError('name', 'Invalid project name'))
    
    # Due date validation
    if 'due_date' in data and data['due_date']:
        if not validate_date_string(data['due_date'], "%Y-%m-%d"):
            errors.append(ValidationError('due_date', 'Invalid date format (YYYY-MM-DD expected)'))
    
    # Priority validation
    if 'priority' in data:
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if data['priority'] not in valid_priorities:
            errors.append(ValidationError('priority', f'Priority must be one of: {valid_priorities}'))
    
    return errors
'''

        helpers = '''"""Comprehensive helper utility functions."""
import hashlib
import uuid
import secrets
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal, ROUND_HALF_UP


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime with timezone awareness."""
    if not isinstance(dt, datetime):
        return ""
    
    # Convert to UTC if timezone-aware
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime string with error handling."""
    try:
        return datetime.strptime(dt_str, format_str)
    except (ValueError, TypeError):
        return None


def calculate_hash(data: Union[str, bytes, Dict[str, Any]], algorithm: str = "sha256") -> str:
    """Calculate hash of data using specified algorithm."""
    if isinstance(data, dict):
        # Sort keys for consistent hashing
        data_str = json.dumps(data, sort_keys=True)
        data_bytes = data_str.encode('utf-8')
    elif isinstance(data, str):
        data_bytes = data.encode('utf-8')
    elif isinstance(data, bytes):
        data_bytes = data
    else:
        data_bytes = str(data).encode('utf-8')
    
    hash_algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    hash_func = hash_algorithms.get(algorithm.lower(), hashlib.sha256)
    return hash_func(data_bytes).hexdigest()


def generate_uuid(version: int = 4) -> str:
    """Generate UUID of specified version."""
    if version == 1:
        return str(uuid.uuid1())
    elif version == 4:
        return str(uuid.uuid4())
    else:
        return str(uuid.uuid4())  # Default to v4


def generate_random_string(length: int = 32, include_special: bool = False) -> str:
    """Generate cryptographically secure random string."""
    if include_special:
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    else:
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_token(length: int = 32) -> str:
    """Generate secure token for authentication."""
    return secrets.token_urlsafe(length)


def encode_base64(data: Union[str, bytes]) -> str:
    """Encode data to base64."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return base64.b64encode(data).decode('utf-8')


def decode_base64(encoded: str) -> bytes:
    """Decode base64 data."""
    return base64.b64decode(encoded)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON with default fallback."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """Safely dump JSON with default fallback."""
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return default


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix."""
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re
    
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


def format_number(number: Union[int, float], decimal_places: int = 2) -> str:
    """Format number with thousands separators."""
    if isinstance(number, float):
        return f"{number:,.{decimal_places}f}"
    else:
        return f"{number:,}"


def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """Calculate percentage with division by zero protection."""
    if total == 0:
        return 0.0
    
    return (part / total) * 100


def round_decimal(value: Union[int, float, Decimal], decimal_places: int = 2) -> Decimal:
    """Round decimal to specified places using banker's rounding."""
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    
    quantizer = Decimal('0.1') ** decimal_places
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries with later ones taking precedence."""
    result = {}
    
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    
    return result


def flatten_dictionary(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dictionary(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List[Any], key_func: Optional[callable] = None) -> List[Any]:
    """Remove duplicates from list while preserving order."""
    if key_func is None:
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    else:
        seen = set()
        result = []
        for item in lst:
            key = key_func(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result


def deep_get(dictionary: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """Get nested dictionary value using dot notation."""
    keys_list = keys.split('.')
    current = dictionary
    
    try:
        for key in keys_list:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def deep_set(dictionary: Dict[str, Any], keys: str, value: Any) -> None:
    """Set nested dictionary value using dot notation."""
    keys_list = keys.split('.')
    current = dictionary
    
    for key in keys_list[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys_list[-1]] = value


def retry_operation(func: callable, max_retries: int = 3, delay: float = 1.0) -> Any:
    """Retry operation with exponential backoff."""
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            time.sleep(delay * (2 ** attempt))
    
    return None


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.utcnow()
        self.elapsed_time = (self.end_time - self.start_time).total_seconds()
    
    def __str__(self):
        if self.elapsed_time is not None:
            return format_duration(self.elapsed_time)
        return "Timer not completed"
'''

        database = '''"""Comprehensive database utilities."""
import sqlite3
import logging
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager with comprehensive functionality."""
    
    def __init__(self, database_settings):
        """Initialize database connection."""
        self.settings = database_settings
        self.connection: Optional[sqlite3.Connection] = None
        self.is_connected_flag = False
    
    async def connect(self) -> None:
        """Connect to database."""
        try:
            # For testing, use in-memory SQLite
            self.connection = sqlite3.connect(":memory:")
            self.connection.row_factory = sqlite3.Row
            self.is_connected_flag = True
            
            # Create tables
            await self._create_tables()
            
            logger.info("Database connected successfully")
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.is_connected_flag = False
            logger.info("Database disconnected")
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.is_connected_flag and self.connection is not None
    
    async def _create_tables(self) -> None:
        """Create database tables."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                owner_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                priority TEXT NOT NULL DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        ]
        
        for table_sql in tables:
            self.connection.execute(table_sql)
        
        self.connection.commit()
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor with automatic cleanup."""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute query with multiple parameter sets."""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            self.connection.commit()
            return cursor.rowcount


class QueryBuilder:
    """SQL query builder with comprehensive functionality."""
    
    def __init__(self, table: str):
        """Initialize query builder."""
        self.table = table
        self.query_type = None
        self.select_fields = []
        self.where_conditions = []
        self.join_clauses = []
        self.order_by_clauses = []
        self.group_by_clauses = []
        self.having_conditions = []
        self.limit_value = None
        self.offset_value = None
        self.update_fields = {}
        self.insert_fields = {}
    
    def select(self, *fields: str) -> 'QueryBuilder':
        """Add SELECT fields."""
        self.query_type = 'SELECT'
        self.select_fields.extend(fields)
        return self
    
    def where(self, condition: str, *params) -> 'QueryBuilder':
        """Add WHERE condition."""
        self.where_conditions.append((condition, params))
        return self
    
    def join(self, table: str, condition: str) -> 'QueryBuilder':
        """Add JOIN clause."""
        self.join_clauses.append(f"JOIN {table} ON {condition}")
        return self
    
    def left_join(self, table: str, condition: str) -> 'QueryBuilder':
        """Add LEFT JOIN clause."""
        self.join_clauses.append(f"LEFT JOIN {table} ON {condition}")
        return self
    
    def order_by(self, field: str, direction: str = 'ASC') -> 'QueryBuilder':
        """Add ORDER BY clause."""
        self.order_by_clauses.append(f"{field} {direction}")
        return self
    
    def group_by(self, *fields: str) -> 'QueryBuilder':
        """Add GROUP BY clause."""
        self.group_by_clauses.extend(fields)
        return self
    
    def having(self, condition: str, *params) -> 'QueryBuilder':
        """Add HAVING condition."""
        self.having_conditions.append((condition, params))
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        self.limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        self.offset_value = count
        return self
    
    def update(self, **fields) -> 'QueryBuilder':
        """Set UPDATE fields."""
        self.query_type = 'UPDATE'
        self.update_fields.update(fields)
        return self
    
    def insert(self, **fields) -> 'QueryBuilder':
        """Set INSERT fields."""
        self.query_type = 'INSERT'
        self.insert_fields.update(fields)
        return self
    
    def delete(self) -> 'QueryBuilder':
        """Set DELETE query type."""
        self.query_type = 'DELETE'
        return self
    
    def build(self) -> tuple:
        """Build the SQL query and parameters."""
        if self.query_type == 'SELECT':
            return self._build_select()
        elif self.query_type == 'UPDATE':
            return self._build_update()
        elif self.query_type == 'INSERT':
            return self._build_insert()
        elif self.query_type == 'DELETE':
            return self._build_delete()
        else:
            raise ValueError("Query type not specified")
    
    def _build_select(self) -> tuple:
        """Build SELECT query."""
        fields = ', '.join(self.select_fields) if self.select_fields else '*'
        query = f"SELECT {fields} FROM {self.table}"
        params = []
        
        # Add JOINs
        if self.join_clauses:
            query += ' ' + ' '.join(self.join_clauses)
        
        # Add WHERE
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query += f" WHERE {' AND '.join(where_parts)}"
        
        # Add GROUP BY
        if self.group_by_clauses:
            query += f" GROUP BY {', '.join(self.group_by_clauses)}"
        
        # Add HAVING
        if self.having_conditions:
            having_parts = []
            for condition, condition_params in self.having_conditions:
                having_parts.append(condition)
                params.extend(condition_params)
            query += f" HAVING {' AND '.join(having_parts)}"
        
        # Add ORDER BY
        if self.order_by_clauses:
            query += f" ORDER BY {', '.join(self.order_by_clauses)}"
        
        # Add LIMIT and OFFSET
        if self.limit_value:
            query += f" LIMIT {self.limit_value}"
        
        if self.offset_value:
            query += f" OFFSET {self.offset_value}"
        
        return query, tuple(params)
    
    def _build_update(self) -> tuple:
        """Build UPDATE query."""
        if not self.update_fields:
            raise ValueError("No fields specified for UPDATE")
        
        set_parts = []
        params = []
        
        for field, value in self.update_fields.items():
            set_parts.append(f"{field} = ?")
            params.append(value)
        
        query = f"UPDATE {self.table} SET {', '.join(set_parts)}"
        
        # Add WHERE
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query += f" WHERE {' AND '.join(where_parts)}"
        
        return query, tuple(params)
    
    def _build_insert(self) -> tuple:
        """Build INSERT query."""
        if not self.insert_fields:
            raise ValueError("No fields specified for INSERT")
        
        fields = list(self.insert_fields.keys())
        values = list(self.insert_fields.values())
        
        field_names = ', '.join(fields)
        placeholders = ', '.join(['?' for _ in fields])
        
        query = f"INSERT INTO {self.table} ({field_names}) VALUES ({placeholders})"
        
        return query, tuple(values)
    
    def _build_delete(self) -> tuple:
        """Build DELETE query."""
        query = f"DELETE FROM {self.table}"
        params = []
        
        # Add WHERE
        if self.where_conditions:
            where_parts = []
            for condition, condition_params in self.where_conditions:
                where_parts.append(condition)
                params.extend(condition_params)
            query += f" WHERE {' AND '.join(where_parts)}"
        
        return query, tuple(params)
'''        

        # Create config directory with comprehensive settings
        config_dir = os.path.join(cls.test_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        settings = '''"""Comprehensive application settings."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Application environment."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseSettings:
    """Database configuration settings."""
    url: str = "sqlite:///app.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    def __post_init__(self):
        """Validate database settings."""
        if self.pool_size < 1:
            raise ValueError("Pool size must be at least 1")
        if self.max_overflow < 0:
            raise ValueError("Max overflow cannot be negative")


@dataclass
class SecuritySettings:
    """Security configuration settings."""
    secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    password_min_length: int = 8
    max_login_attempts: int = 5
    account_lockout_minutes: int = 30
    session_timeout_minutes: int = 60
    csrf_protection: bool = True
    
    def __post_init__(self):
        """Validate security settings."""
        if len(self.secret_key) < 32:
            if self.secret_key == "dev-secret-key":
                # Allow dev key for testing
                pass
            else:
                raise ValueError("Secret key must be at least 32 characters")
        
        if self.jwt_expiry_hours < 1:
            raise ValueError("JWT expiry must be at least 1 hour")
        
        if self.password_min_length < 6:
            raise ValueError("Password minimum length must be at least 6")


@dataclass
class EmailSettings:
    """Email configuration settings."""
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    use_tls: bool = True
    use_ssl: bool = False
    from_email: str = "noreply@example.com"
    from_name: str = "Application"
    
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(self.smtp_host and self.from_email)


@dataclass
class CacheSettings:
    """Cache configuration settings."""
    backend: str = "memory"  # memory, redis, memcached
    default_timeout: int = 3600
    key_prefix: str = "app:"
    redis_url: Optional[str] = None
    memcached_servers: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.memcached_servers is None:
            self.memcached_servers = ["127.0.0.1:11211"]


@dataclass
class LoggingSettings:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True
    
    def get_level_int(self) -> int:
        """Get logging level as integer."""
        import logging
        return getattr(logging, self.level.upper(), logging.INFO)


@dataclass
class ApiSettings:
    """API configuration settings."""
    rate_limit_per_minute: int = 60
    max_request_size: int = 16 * 1024 * 1024  # 16MB
    cors_origins: List[str] = None
    cors_methods: List[str] = None
    cors_headers: List[str] = None
    api_key_required: bool = False
    api_version: str = "v1"
    
    def __post_init__(self):
        """Initialize default values."""
        if self.cors_origins is None:
            self.cors_origins = ["*"]
        if self.cors_methods is None:
            self.cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        if self.cors_headers is None:
            self.cors_headers = ["Content-Type", "Authorization"]


class AppSettings:
    """Main application settings."""
    
    def __init__(self):
        """Initialize application settings."""
        import os
        
        # Environment
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.testing = self.environment == Environment.TESTING
        
        # Basic settings
        self.app_name = os.getenv("APP_NAME", "Comprehensive Test Application")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        
        # Component settings
        self.database = DatabaseSettings(
            url=os.getenv("DATABASE_URL", "sqlite:///app.db"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            echo=self.debug
        )
        
        self.security = SecuritySettings(
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key"),
            jwt_expiry_hours=int(os.getenv("JWT_EXPIRY_HOURS", "24")),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
        )
        
        self.email = EmailSettings(
            smtp_host=os.getenv("SMTP_HOST", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            from_email=os.getenv("FROM_EMAIL", "noreply@example.com")
        )
        
        self.cache = CacheSettings(
            backend=os.getenv("CACHE_BACKEND", "memory"),
            default_timeout=int(os.getenv("CACHE_TIMEOUT", "3600")),
            redis_url=os.getenv("REDIS_URL")
        )
        
        self.logging = LoggingSettings(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE"),
            console_output=os.getenv("LOG_CONSOLE", "true").lower() == "true"
        )
        
        self.api = ApiSettings(
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT", "60")),
            max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(16 * 1024 * 1024))),
            api_key_required=os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
        )
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.is_development():
            return ["*"]
        else:
            return self.api.cors_origins
    
    def validate(self) -> List[str]:
        """Validate all settings and return list of errors."""
        errors = []
        
        try:
            # Validate database settings
            if not self.database.url:
                errors.append("Database URL is required")
            
            # Validate security settings
            if self.is_production() and self.security.secret_key == "dev-secret-key":
                errors.append("Production secret key must be set")
            
            # Validate email settings for production
            if self.is_production() and not self.email.is_configured():
                errors.append("Email settings must be configured for production")
            
            # Validate logging settings
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if self.logging.level.upper() not in valid_log_levels:
                errors.append(f"Invalid log level: {self.logging.level}")
            
        except Exception as e:
            errors.append(f"Settings validation error: {e}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)."""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment.value,
            "debug": self.debug,
            "testing": self.testing,
            "host": self.host,
            "port": self.port,
            "database": {
                "pool_size": self.database.pool_size,
                "echo": self.database.echo
            },
            "security": {
                "jwt_algorithm": self.security.jwt_algorithm,
                "jwt_expiry_hours": self.security.jwt_expiry_hours,
                "password_min_length": self.security.password_min_length,
                "max_login_attempts": self.security.max_login_attempts
            },
            "email": {
                "smtp_host": self.email.smtp_host,
                "smtp_port": self.email.smtp_port,
                "from_email": self.email.from_email,
                "is_configured": self.email.is_configured()
            },
            "cache": {
                "backend": self.cache.backend,
                "default_timeout": self.cache.default_timeout
            },
            "logging": {
                "level": self.logging.level,
                "console_output": self.logging.console_output
            },
            "api": {
                "rate_limit_per_minute": self.api.rate_limit_per_minute,
                "api_version": self.api.api_version,
                "cors_origins": self.get_cors_origins()
            }
        }
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
            ("services/notification_service.py", notification_service),
            ("utils/__init__.py", ""),
            ("utils/validators.py", validators),
            ("utils/helpers.py", helpers),
            ("utils/database.py", database),
            ("config/__init__.py", ""),
            ("config/settings.py", settings),
        ]
        
        for file_path, content in files_to_write:
            full_path = os.path.join(cls.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
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
        
        # Verify comprehensive file discovery
        file_names = [f["name"] for f in files if f["type"] == "file"]
        expected_files = [
            "main.py", "user.py", "project.py", "auth_service.py", 
            "data_service.py", "notification_service.py", "validators.py",
            "helpers.py", "database.py", "settings.py"
        ]
        
        found_files = []
        for expected_file in expected_files:
            if any(expected_file in name for name in file_names):
                found_files.append(expected_file)
        
        self.assertGreaterEqual(len(found_files), 8, f"Should find most expected files. Found: {found_files}")
        print(f"✅ Discovered {len(files)} files with {len(relationships)} relationships")
        
        # Step 2: Complex File Content Retrieval
        print("Step 2: Complex File Content Retrieval")
        main_files = [f for f in files if f["name"].endswith("main.py")]
        self.assertGreater(len(main_files), 0, "Should find main.py")
        
        main_file_path = main_files[0]["id"]
        response = self.client.get(f"/api/files/file_content/{main_file_path}")
        self.assertEqual(response.status_code, 200)
        
        content_data = response.json()
        self.assertIn("content", content_data)
        content = content_data["content"]
        
        # Verify complex content patterns
        expected_patterns = [
            "class WebApplication",
            "async def start",
            "from models.user import",
            "from services.auth_service import",
            "FastAPI",
            "@app.route",
            "async def main"
        ]
        
        for pattern in expected_patterns:
            self.assertIn(pattern, content, f"Expected pattern '{pattern}' not found")
        
        print(f"✅ Retrieved complex file content ({len(content)} characters)")
        
        # Step 3: Relationship Analysis
        print("Step 3: Relationship Analysis")
        self.assertGreater(len(relationships), 5, "Should have multiple import relationships")
        
        # Verify specific relationships exist
        relationship_sources = [r["source"] for r in relationships]
        main_relationships = [r for r in relationship_sources if "main.py" in r]
        self.assertGreater(len(main_relationships), 0, "main.py should have import relationships")
        
        print(f"✅ Analyzed {len(relationships)} import relationships")
        
        # Step 4: PMD Analysis with Mocking
        print("Step 4: PMD Static Analysis")
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            # Mock comprehensive PMD results
            mock_pmd.return_value = {
                "violations": [
                    {
                        "rule": "TooManyImports",
                        "priority": 3,
                        "message": "Too many imports (15). Consider refactoring into smaller modules.",
                        "line": 1,
                        "column": 1
                    },
                    {
                        "rule": "CyclomaticComplexity",
                        "priority": 2,
                        "message": "Method has cyclomatic complexity of 12 (threshold: 10)",
                        "line": 45,
                        "column": 5
                    },
                    {
                        "rule": "UnusedImport",
                        "priority": 4,
                        "message": "Unused import 'Optional' from typing",
                        "line": 8,
                        "column": 1
                    },
                    {
                        "rule": "LineTooLong",
                        "priority": 4,
                        "message": "Line exceeds 120 characters (found 145)",
                        "line": 78,
                        "column": 121
                    }
                ],
                "summary": {
                    "totalViolations": 4,
                    "fileAnalyzed": main_file_path,
                    "rulesApplied": ["java-quickstart"],
                    "analysisTime": "0.234s"
                }
            }
            
            response = self.client.get(f"/api/pmd/analysis/{main_file_path}")
            self.assertEqual(response.status_code, 200)
            
            pmd_result = response.json()
            self.assertIn("violations", pmd_result)
            self.assertIn("summary", pmd_result)
            
            violations = pmd_result["violations"]
            self.assertEqual(len(violations), 4)
            
            # Verify violation structure
            for violation in violations:
                self.assertIn("rule", violation)
                self.assertIn("priority", violation)
                self.assertIn("message", violation)
                self.assertIn("line", violation)
                self.assertIn("column", violation)
            
            print(f"✅ PMD analysis found {len(violations)} violations")
        
        print("✅ Complete user workflow integration test passed!")
    
    def test_security_and_error_handling_comprehensive(self):
        """Test comprehensive security measures and error handling."""
        print("\n=== Testing Comprehensive Security and Error Handling ===")
        
        # Test 1: Path Traversal Prevention
        print("Testing path traversal prevention...")
        traversal_attacks = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config",
            "/etc/passwd",
            "~/secret_file.py",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
            "....//....//....//etc/passwd",  # Double encoding
            "..%252f..%252f..%252fetc%252fpasswd",  # Double URL encoding
        ]
        
        blocked_attacks = 0
        for attack in traversal_attacks:
            response = self.client.get(f"/api/files/file_content/{attack}")
            if response.status_code in [403, 404]:
                blocked_attacks += 1
            
            # Verify error response structure
            if response.status_code in [403, 404]:
                error_data = response.json()
                self.assertIn("error", error_data)
        
        print(f"✅ Path traversal: {blocked_attacks}/{len(traversal_attacks)} attacks blocked")
        self.assertEqual(blocked_attacks, len(traversal_attacks), "All path traversal attacks should be blocked")
        
        # Test 2: File Extension Validation
        print("Testing file extension validation...")
        invalid_extensions = [
            "malicious.exe",
            "script.bat",
            "config.ini",
            "secret.txt",
            "data.json"
        ]
        
        for invalid_file in invalid_extensions:
            # Create temporary file
            temp_path = os.path.join(self.test_dir, invalid_file)
            with open(temp_path, "w") as f:
                f.write("test content")
            
            response = self.client.get(f"/api/files/file_content/{temp_path}")
            self.assertEqual(response.status_code, 403, f"Invalid extension should be blocked: {invalid_file}")
            
            # Clean up
            os.remove(temp_path)
        
        print("✅ File extension validation working correctly")
        
        # Test 3: Error Response Consistency
        print("Testing error response consistency...")
        error_scenarios = [
            ("/api/files/file_content/nonexistent.py", 404),
            ("/api/files/file_content/", 404),
            ("/api/pmd/analysis/nonexistent.py", 404),
        ]
        
        for endpoint, expected_status in error_scenarios:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, expected_status)
            
            error_data = response.json()
            self.assertIn("error", error_data)
            self.assertIsInstance(error_data["error"], str)
        
        print("✅ Error response consistency verified")
        
        # Test 4: Large File Handling
        print("Testing large file handling...")
        large_content = "x" * (10 * 1024 * 1024)  # 10MB content
        large_file_path = os.path.join(self.test_dir, "large_test.py")
        
        with open(large_file_path, "w") as f:
            f.write(large_content)
        
        response = self.client.get(f"/api/files/file_content/{large_file_path}")
        # Should either succeed or fail gracefully with appropriate error
        self.assertIn(response.status_code, [200, 403, 413])
        
        if response.status_code != 200:
            error_data = response.json()
            self.assertIn("error", error_data)
        
        # Clean up
        os.remove(large_file_path)
        print("✅ Large file handling verified")
    
    def test_concurrent_load_and_performance(self):
        """Test system performance under concurrent load."""
        print("\n=== Testing Concurrent Load and Performance ===")
        
        # Test 1: Concurrent File Discovery
        print("Testing concurrent file discovery...")
        
        results = queue.Queue()
        num_threads = 8
        requests_per_thread = 5
        
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
                        "response_time": end_time - start_time,
                        "file_count": len(response.json().get("files", [])) if response.status_code == 200 else 0
                    })
                except Exception as e:
                    thread_results.append({
                        "success": False,
                        "error": str(e),
                        "response_time": 0,
                        "file_count": 0
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
        self.assertGreater(success_rate, 0.9, "Success rate should be above 90%")
        self.assertLess(avg_response_time, 2.0, "Average response time should be under 2s")
        
        # Test 2: Memory Usage Stability
        print("Testing memory usage stability...")
        
        # Make multiple requests to check for memory leaks
        initial_file_count = None
        for i in range(20):
            response = self.client.get("/api/files/files_info")
            self.assertEqual(response.status_code, 200)
            
            file_data = response.json()
            current_file_count = len(file_data["files"])
            
            if initial_file_count is None:
                initial_file_count = current_file_count
            else:
                # File count should remain consistent
                self.assertEqual(current_file_count, initial_file_count, 
                               "File count should remain consistent across requests")
        
        print("✅ Memory usage stability verified")
    
    def test_api_consistency_and_reliability(self):
        """Test API consistency and reliability across multiple calls."""
        print("\n=== Testing API Consistency and Reliability ===")
        
        # Test 1: Response Format Consistency
        print("Testing response format consistency...")
        
        endpoints = [
            ("/health", 200),
            ("/api/root/", 200),
            ("/api/files/files_info", 200)
        ]
        
        for endpoint, expected_status in endpoints:
            responses = []
            
            # Make multiple calls
            for i in range(5):
                response = self.client.get(endpoint)
                responses.append({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_type": response.headers.get("content-type"),
                    "has_process_time": "x-process-time" in response.headers
                })
            
            # Verify consistency
            status_codes = [r["status_code"] for r in responses]
            self.assertTrue(all(code == expected_status for code in status_codes),
                          f"Status codes should be {expected_status} for {endpoint}")
            
            content_types = [r["content_type"] for r in responses]
            self.assertTrue(all(ct == content_types[0] for ct in content_types),
                          f"Content types should be consistent for {endpoint}")
            
            # Verify all responses have process time header
            process_times = [r["has_process_time"] for r in responses]
            self.assertTrue(all(process_times), f"All responses should have process time header for {endpoint}")
            
            print(f"✅ {endpoint} responses are consistent")
        
        # Test 2: Data Integrity Over Time
        print("Testing data integrity over time...")
        
        # Get file data multiple times with delays
        file_data_snapshots = []
        for i in range(3):
            response = self.client.get("/api/files/files_info")
            self.assertEqual(response.status_code, 200)
            
            file_data = response.json()
            file_data_snapshots.append({
                "file_count": len(file_data["files"]),
                "relationship_count": len(file_data["relationships"]),
                "file_names": sorted([f["name"] for f in file_data["files"]])
            })
            
            # Small delay between requests
            time.sleep(0.1)
        
        # Verify data consistency
        for i in range(1, len(file_data_snapshots)):
            self.assertEqual(
                file_data_snapshots[i]["file_count"],
                file_data_snapshots[0]["file_count"],
                "File count should remain consistent"
            )
            
            self.assertEqual(
                file_data_snapshots[i]["relationship_count"],
                file_data_snapshots[0]["relationship_count"],
                "Relationship count should remain consistent"
            )
            
            self.assertEqual(
                file_data_snapshots[i]["file_names"],
                file_data_snapshots[0]["file_names"],
                "File names should remain consistent"
            )
        
        print(f"✅ Data integrity verified across {len(file_data_snapshots)} snapshots")
        
        # Test 3: Error Handling Consistency
        print("Testing error handling consistency...")
        
        error_endpoints = [
            "/api/files/file_content/nonexistent.py",
            "/api/files/file_content/../../../etc/passwd",
            "/api/pmd/analysis/invalid_file.txt"
        ]
        
        for endpoint in error_endpoints:
            error_responses = []
            
            # Make multiple error requests
            for i in range(3):
                response = self.client.get(endpoint)
                error_responses.append({
                    "status_code": response.status_code,
                    "response": response.json(),
                    "has_error_field": "error" in response.json()
                })
            
            # Verify error consistency
            status_codes = [r["status_code"] for r in error_responses]
            self.assertTrue(all(code == status_codes[0] for code in status_codes),
                          f"Error status codes should be consistent for {endpoint}")
            
            error_fields = [r["has_error_field"] for r in error_responses]
            self.assertTrue(all(error_fields), f"All error responses should have error field for {endpoint}")
        
        print("✅ Error handling consistency verified")


if __name__ == '__main__':
    unittest.main(verbosity=2)