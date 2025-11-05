#!/usr/bin/env python3
"""
System integration tests for the LLM Code Navigator.
Tests complete user workflows and system behavior without requiring Docker.
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
from unittest.mock import patch, MagicMock

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


class TestSystemIntegration(unittest.TestCase):
    """System integration tests for complete user workflows."""
    
    def setUp(self):
        """Set up test environment with realistic codebase."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp(prefix="system_test_")
        self.original_backend_dir = getattr(settings, 'BACKEND_DIR', None)
        
        # Override backend directory for testing
        os.environ["BACKEND_DIR"] = self.test_dir
        
        # Reload settings to pick up new environment variable
        from app.core.config import Settings
        settings.__dict__.update(Settings().__dict__)
        
        # Create test client after setting up environment
        self.client = TestClient(app)
        
        # Create realistic test codebase
        self.create_realistic_codebase()
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore original backend directory
        if self.original_backend_dir:
            os.environ["BACKEND_DIR"] = self.original_backend_dir
        elif "BACKEND_DIR" in os.environ:
            del os.environ["BACKEND_DIR"]
        
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_realistic_codebase(self):
        """Create a realistic Python codebase for testing."""
        # Web application structure
        app_content = '''#!/usr/bin/env python3
"""
Flask web application for task management.
"""
import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import User, db as user_db
from models.task import Task, TaskStatus
from services.auth_service import AuthService
from services.task_service import TaskService
from utils.validators import validate_email, validate_password
from utils.decorators import login_required, admin_required

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize services
auth_service = AuthService(db)
task_service = TaskService(db)


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        user = auth_service.authenticate_user(email, password)
        if user:
            token = auth_service.generate_token(user)
            return jsonify({
                'token': token,
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        # Validate input
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Password does not meet requirements'}), 400
        
        # Create user
        user = auth_service.create_user(email, password, name)
        if user:
            token = auth_service.generate_token(user)
            return jsonify({
                'token': token,
                'user': user.to_dict()
            }), 201
        else:
            return jsonify({'error': 'User already exists'}), 409
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get user tasks."""
    try:
        user_id = request.user.id
        tasks = task_service.get_user_tasks(user_id)
        return jsonify([task.to_dict() for task in tasks])
    
    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    """Create new task."""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        task = task_service.create_task(
            user_id=request.user.id,
            title=title,
            description=description
        )
        
        return jsonify(task.to_dict()), 201
    
    except Exception as e:
        logger.error(f"Create task error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update task."""
    try:
        data = request.get_json()
        task = task_service.update_task(task_id, request.user.id, data)
        
        if task:
            return jsonify(task.to_dict())
        else:
            return jsonify({'error': 'Task not found or access denied'}), 404
    
    except Exception as e:
        logger.error(f"Update task error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)."""
    try:
        users = auth_service.get_all_users()
        return jsonify([user.to_dict() for user in users])
    
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        
        # Models
        models_dir = os.path.join(self.test_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        user_model_content = '''"""User model for authentication and authorization."""
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class User(db.Model):
    """User model for database."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, name, password=None, role=UserRole.USER):
        """Initialize user."""
        self.email = email
        self.name = name
        self.role = role
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        """Set user password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    def is_moderator(self):
        """Check if user is moderator or admin."""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
    
    def can_edit_task(self, task):
        """Check if user can edit a task."""
        return self.is_admin() or task.user_id == self.id
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'task_count': len(self.tasks)
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
'''
        
        task_model_content = '''"""Task model for task management."""
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

# Import db from user model to avoid circular imports
from models.user import db


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(db.Model):
    """Task model for database."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, title, description="", user_id=None, priority=TaskPriority.MEDIUM):
        """Initialize task."""
        self.title = title
        self.description = description
        self.user_id = user_id
        self.priority = priority
    
    def mark_completed(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def mark_in_progress(self):
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
    
    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.utcnow() > self.due_date
        return False
    
    def days_until_due(self):
        """Get days until due date."""
        if self.due_date:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None
    
    def to_dict(self):
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'is_overdue': self.is_overdue(),
            'days_until_due': self.days_until_due()
        }
    
    def __repr__(self):
        return f'<Task {self.title}>'
'''
        
        # Services
        services_dir = os.path.join(self.test_dir, "services")
        os.makedirs(services_dir, exist_ok=True)
        
        auth_service_content = '''"""Authentication service for user management."""
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from flask import current_app

from models.user import User, UserRole, db

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and user management service."""
    
    def __init__(self, database):
        """Initialize auth service."""
        self.db = database
    
    def create_user(self, email: str, password: str, name: str, role: UserRole = UserRole.USER) -> Optional[User]:
        """Create a new user."""
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                logger.warning(f"User creation failed: email {email} already exists")
                return None
            
            # Create new user
            user = User(email=email, name=name, password=password, role=role)
            self.db.session.add(user)
            self.db.session.commit()
            
            logger.info(f"Created user: {email}")
            return user
        
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            self.db.session.rollback()
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        try:
            user = User.query.filter_by(email=email, is_active=True).first()
            
            if user and user.check_password(password):
                logger.info(f"User authenticated: {email}")
                return user
            
            logger.warning(f"Authentication failed for: {email}")
            return None
        
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return User.query.filter_by(id=user_id, is_active=True).first()
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return User.query.filter_by(email=email, is_active=True).first()
        except Exception as e:
            logger.error(f"Error getting user {email}: {e}")
            return None
    
    def get_all_users(self) -> List[User]:
        """Get all active users."""
        try:
            return User.query.filter_by(is_active=True).order_by(User.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information."""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            self.db.session.commit()
            
            logger.info(f"Updated user: {user.email}")
            return user
        
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            self.db.session.rollback()
            return None
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account."""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            self.db.session.commit()
            
            logger.info(f"Deactivated user: {user.email}")
            return True
        
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            self.db.session.rollback()
            return False
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token for user."""
        try:
            payload = {
                'user_id': user.id,
                'email': user.email,
                'role': user.role.value,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            return token
        
        except Exception as e:
            logger.error(f"Error generating token for user {user.id}: {e}")
            return ""
    
    def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user."""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if user_id:
                return self.get_user_by_id(user_id)
            
            return None
        
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
'''
        
        task_service_content = '''"""Task management service."""
import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy import and_, or_

from models.task import Task, TaskStatus, TaskPriority, db
from models.user import User

logger = logging.getLogger(__name__)


class TaskService:
    """Task management service."""
    
    def __init__(self, database):
        """Initialize task service."""
        self.db = database
    
    def create_task(self, user_id: int, title: str, description: str = "", 
                   priority: TaskPriority = TaskPriority.MEDIUM, due_date: datetime = None) -> Optional[Task]:
        """Create a new task."""
        try:
            task = Task(
                title=title,
                description=description,
                user_id=user_id,
                priority=priority
            )
            
            if due_date:
                task.due_date = due_date
            
            self.db.session.add(task)
            self.db.session.commit()
            
            logger.info(f"Created task: {title} for user {user_id}")
            return task
        
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            self.db.session.rollback()
            return None
    
    def get_task_by_id(self, task_id: int, user_id: int = None) -> Optional[Task]:
        """Get task by ID, optionally filtered by user."""
        try:
            query = Task.query.filter_by(id=task_id)
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            return query.first()
        
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            return None
    
    def get_user_tasks(self, user_id: int, status: TaskStatus = None, 
                      priority: TaskPriority = None) -> List[Task]:
        """Get tasks for a specific user."""
        try:
            query = Task.query.filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            if priority:
                query = query.filter_by(priority=priority)
            
            return query.order_by(Task.created_at.desc()).all()
        
        except Exception as e:
            logger.error(f"Error getting tasks for user {user_id}: {e}")
            return []
    
    def update_task(self, task_id: int, user_id: int, updates: dict) -> Optional[Task]:
        """Update task information."""
        try:
            task = self.get_task_by_id(task_id, user_id)
            if not task:
                return None
            
            # Update allowed fields
            allowed_fields = ['title', 'description', 'status', 'priority', 'due_date']
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(task, field):
                    if field == 'status' and isinstance(value, str):
                        value = TaskStatus(value)
                    elif field == 'priority' and isinstance(value, str):
                        value = TaskPriority(value)
                    elif field == 'due_date' and isinstance(value, str):
                        value = datetime.fromisoformat(value)
                    
                    setattr(task, field, value)
            
            # Update completion timestamp if status changed to completed
            if task.status == TaskStatus.COMPLETED and not task.completed_at:
                task.completed_at = datetime.utcnow()
            elif task.status != TaskStatus.COMPLETED:
                task.completed_at = None
            
            task.updated_at = datetime.utcnow()
            self.db.session.commit()
            
            logger.info(f"Updated task {task_id}")
            return task
        
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            self.db.session.rollback()
            return None
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Delete a task."""
        try:
            task = self.get_task_by_id(task_id, user_id)
            if not task:
                return False
            
            self.db.session.delete(task)
            self.db.session.commit()
            
            logger.info(f"Deleted task {task_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            self.db.session.rollback()
            return False
    
    def get_overdue_tasks(self, user_id: int = None) -> List[Task]:
        """Get overdue tasks."""
        try:
            query = Task.query.filter(
                and_(
                    Task.due_date < datetime.utcnow(),
                    Task.status != TaskStatus.COMPLETED
                )
            )
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            return query.order_by(Task.due_date.asc()).all()
        
        except Exception as e:
            logger.error(f"Error getting overdue tasks: {e}")
            return []
    
    def get_task_statistics(self, user_id: int) -> dict:
        """Get task statistics for a user."""
        try:
            total_tasks = Task.query.filter_by(user_id=user_id).count()
            completed_tasks = Task.query.filter_by(user_id=user_id, status=TaskStatus.COMPLETED).count()
            pending_tasks = Task.query.filter_by(user_id=user_id, status=TaskStatus.PENDING).count()
            in_progress_tasks = Task.query.filter_by(user_id=user_id, status=TaskStatus.IN_PROGRESS).count()
            overdue_tasks = len(self.get_overdue_tasks(user_id))
            
            return {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': pending_tasks,
                'in_progress': in_progress_tasks,
                'overdue': overdue_tasks,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Error getting task statistics for user {user_id}: {e}")
            return {}
'''
        
        # Utils
        utils_dir = os.path.join(self.test_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        validators_content = '''"""Input validation utilities."""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_password(password: str) -> bool:
    """Validate password strength."""
    if not password or not isinstance(password, str):
        return False
    
    # Password requirements:
    # - At least 8 characters
    # - At least one uppercase letter
    # - At least one lowercase letter
    # - At least one digit
    
    if len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'\d', password):
        return False
    
    return True


def validate_task_title(title: str) -> bool:
    """Validate task title."""
    if not title or not isinstance(title, str):
        return False
    
    title = title.strip()
    return 1 <= len(title) <= 200


def validate_task_description(description: str) -> bool:
    """Validate task description."""
    if description is None:
        return True  # Description is optional
    
    if not isinstance(description, str):
        return False
    
    return len(description.strip()) <= 1000


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text


def validate_user_name(name: str) -> bool:
    """Validate user name."""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    
    # Name should be 2-50 characters, letters and spaces only
    if not (2 <= len(name) <= 50):
        return False
    
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return False
    
    return True


def validate_priority(priority: str) -> bool:
    """Validate task priority."""
    valid_priorities = ['low', 'medium', 'high', 'urgent']
    return priority in valid_priorities


def validate_status(status: str) -> bool:
    """Validate task status."""
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    return status in valid_statuses
'''
        
        decorators_content = '''"""Authentication and authorization decorators."""
import functools
import logging
from flask import request, jsonify, g
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator to require authentication."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            token_parts = auth_header.split(' ')
            if len(token_parts) != 2 or token_parts[0] != 'Bearer':
                return jsonify({'error': 'Invalid authorization header format'}), 401
            
            token = token_parts[1]
            
            # Verify token and get user
            from app import auth_service  # Import here to avoid circular imports
            user = auth_service.verify_token(token)
            
            if not user:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Store user in request context
            request.user = user
            
            return f(*args, **kwargs)
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function


def admin_required(f):
    """Decorator to require admin role."""
    @functools.wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not request.user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def moderator_required(f):
    """Decorator to require moderator or admin role."""
    @functools.wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not request.user.is_moderator():
            return jsonify({'error': 'Moderator access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit(max_requests=100, window_seconds=3600):
    """Decorator to implement rate limiting."""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting implementation
            # In production, use Redis or similar for distributed rate limiting
            
            client_ip = request.remote_addr
            current_time = time.time()
            
            # For this demo, we'll just log the rate limit check
            logger.info(f"Rate limit check for {client_ip}: {max_requests} requests per {window_seconds}s")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
'''
        
        # Write all files
        files_to_write = [
            ("app.py", app_content),
            ("models/__init__.py", ""),
            ("models/user.py", user_model_content),
            ("models/task.py", task_model_content),
            ("services/__init__.py", ""),
            ("services/auth_service.py", auth_service_content),
            ("services/task_service.py", task_service_content),
            ("utils/__init__.py", ""),
            ("utils/validators.py", validators_content),
            ("utils/decorators.py", decorators_content),
        ]
        
        for file_path, content in files_to_write:
            full_path = os.path.join(self.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
    
    def test_complete_file_analysis_workflow(self):
        """Test complete file analysis workflow from discovery to content retrieval."""
        print("\n=== Testing Complete File Analysis Workflow ===")
        
        # Step 1: Discover files in the codebase
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        self.assertIn("files", file_data)
        self.assertIn("relationships", file_data)
        
        # Verify we have the expected files
        file_names = [f["name"] for f in file_data["files"] if f["type"] == "file"]
        expected_files = ["app.py", "user.py", "task.py", "auth_service.py", "task_service.py"]
        
        for expected_file in expected_files:
            self.assertTrue(
                any(expected_file in name for name in file_names),
                f"Expected file {expected_file} not found"
            )
        
        print(f"✅ Discovered {len(file_data['files'])} files with {len(file_data['relationships'])} relationships")
        
        # Step 2: Verify relationships between files
        relationships = file_data["relationships"]
        self.assertGreater(len(relationships), 0, "Should have import relationships")
        
        # Check for specific relationships we expect
        relationship_pairs = [(r["source"], r["target"]) for r in relationships]
        
        # app.py should import from models and services
        app_relationships = [r for r in relationship_pairs if "app.py" in r[0]]
        self.assertGreater(len(app_relationships), 0, "app.py should have import relationships")
        
        print(f"✅ Verified {len(relationships)} import relationships")
        
        # Step 3: Retrieve content for main application file
        app_files = [f for f in file_data["files"] if f["name"].endswith("app.py")]
        self.assertGreater(len(app_files), 0, "Should find app.py file")
        
        app_file_id = app_files[0]["id"]
        response = self.client.get(f"/api/files/file_content/{app_file_id}")
        self.assertEqual(response.status_code, 200)
        
        file_content = response.json()
        self.assertIn("content", file_content)
        self.assertIn("path", file_content)
        
        content = file_content["content"]
        
        # Verify content contains expected Flask application code
        expected_patterns = [
            "from flask import",
            "app = Flask(__name__)",
            "@app.route",
            "def login():",
            "def register():",
            "if __name__ == '__main__':"
        ]
        
        for pattern in expected_patterns:
            self.assertIn(pattern, content, f"Expected pattern '{pattern}' not found in content")
        
        print(f"✅ Retrieved and validated file content ({len(content)} characters)")
        
        # Step 4: Test content retrieval for different file types
        test_files = ["user.py", "task.py", "validators.py"]
        
        for test_file in test_files:
            matching_files = [f for f in file_data["files"] if f["name"].endswith(test_file)]
            if matching_files:
                file_id = matching_files[0]["id"]
                response = self.client.get(f"/api/files/file_content/{file_id}")
                self.assertEqual(response.status_code, 200, f"Failed to retrieve {test_file}")
                
                content_data = response.json()
                self.assertIn("content", content_data)
                self.assertGreater(len(content_data["content"]), 0)
        
        print(f"✅ Successfully retrieved content for multiple file types")
    
    def test_pmd_analysis_integration(self):
        """Test PMD static analysis integration."""
        print("\n=== Testing PMD Analysis Integration ===")
        
        # Get file data first
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        python_files = [f for f in file_data["files"] if f["name"].endswith(".py")]
        self.assertGreater(len(python_files), 0)
        
        # Test PMD analysis on a Python file
        test_file = python_files[0]
        file_id = test_file["id"]
        
        # Mock PMD service for testing since PMD might not be installed
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            # Mock successful PMD analysis
            mock_pmd.return_value = {
                "violations": [
                    {
                        "rule": "UnusedImport",
                        "priority": 3,
                        "message": "Unused import statement",
                        "line": 5,
                        "column": 1
                    },
                    {
                        "rule": "LineTooLong",
                        "priority": 4,
                        "message": "Line exceeds 120 characters",
                        "line": 25,
                        "column": 121
                    }
                ],
                "summary": {
                    "totalViolations": 2,
                    "fileAnalyzed": file_id
                }
            }
            
            response = self.client.get(f"/api/pmd/analysis/{file_id}")
            self.assertEqual(response.status_code, 200)
            
            pmd_result = response.json()
            self.assertIn("violations", pmd_result)
            self.assertIn("summary", pmd_result)
            
            violations = pmd_result["violations"]
            self.assertEqual(len(violations), 2)
            
            # Verify violation structure
            for violation in violations:
                self.assertIn("rule", violation)
                self.assertIn("priority", violation)
                self.assertIn("message", violation)
                self.assertIn("line", violation)
                self.assertIn("column", violation)
            
            print(f"✅ PMD analysis returned {len(violations)} violations")
        
        # Test PMD analysis error handling
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            mock_pmd.side_effect = RuntimeError("PMD command not found")
            
            response = self.client.get(f"/api/pmd/analysis/{file_id}")
            self.assertEqual(response.status_code, 500)
            
            error_data = response.json()
            self.assertIn("error", error_data)
            
            print("✅ PMD error handling works correctly")
    
    def test_security_and_error_handling(self):
        """Test security measures and error handling."""
        print("\n=== Testing Security and Error Handling ===")
        
        # Test path traversal prevention
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "/etc/passwd",
            "~/secret_file.py"
        ]
        
        for path in traversal_paths:
            response = self.client.get(f"/api/files/file_content/{path}")
            self.assertEqual(response.status_code, 403, f"Path traversal not blocked: {path}")
            
            error_data = response.json()
            self.assertIn("error", error_data)
            self.assertIn("Access denied", error_data["error"])
        
        print("✅ Path traversal attacks blocked correctly")
        
        # Test file not found handling
        response = self.client.get(f"/api/files/file_content/{os.path.join(self.test_dir, 'nonexistent.py')}")
        self.assertEqual(response.status_code, 404)
        
        error_data = response.json()
        self.assertIn("error", error_data)
        
        print("✅ File not found errors handled correctly")
        
        # Test invalid file extensions
        invalid_file = os.path.join(self.test_dir, "test.txt")
        with open(invalid_file, "w") as f:
            f.write("This is a text file")
        
        response = self.client.get(f"/api/files/file_content/{invalid_file}")
        self.assertEqual(response.status_code, 403)
        
        error_data = response.json()
        self.assertIn("error", error_data)
        
        print("✅ Invalid file extensions blocked correctly")
        
        # Test large file handling
        with patch('os.path.getsize', return_value=settings.MAX_FILE_SIZE + 1):
            response = self.client.get(f"/api/files/file_content/{os.path.join(self.test_dir, 'app.py')}")
            self.assertEqual(response.status_code, 403)
            
            error_data = response.json()
            self.assertIn("error", error_data)
        
        print("✅ Large file size limits enforced correctly")
    
    def test_concurrent_request_handling(self):
        """Test system behavior under concurrent load."""
        print("\n=== Testing Concurrent Request Handling ===")
        
        import threading
        import queue
        
        results = queue.Queue()
        num_threads = 5
        requests_per_thread = 3
        
        def make_concurrent_requests():
            """Make multiple requests concurrently."""
            thread_results = []
            
            for i in range(requests_per_thread):
                try:
                    # Test different endpoints
                    endpoints = [
                        "/health",
                        "/api/root/",
                        "/api/files/files_info"
                    ]
                    
                    for endpoint in endpoints:
                        response = self.client.get(endpoint)
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
        
        # Start concurrent threads
        threads = []
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=make_concurrent_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)
        
        end_time = time.time()
        
        # Collect and analyze results
        all_results = []
        while not results.empty():
            all_results.extend(results.get())
        
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r["success"])
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        print(f"✅ Concurrent load test: {successful_requests}/{total_requests} successful ({success_rate:.1%})")
        print(f"✅ Total time: {end_time - start_time:.2f}s")
        
        # Should handle concurrent requests well
        self.assertGreater(success_rate, 0.8, "Success rate should be above 80%")
        self.assertLess(end_time - start_time, 10, "Should complete within reasonable time")
    
    def test_complex_codebase_analysis(self):
        """Test analysis of complex codebase with deep dependencies."""
        print("\n=== Testing Complex Codebase Analysis ===")
        
        # Create additional complex files
        complex_dir = os.path.join(self.test_dir, "complex")
        os.makedirs(complex_dir, exist_ok=True)
        
        # Create files with circular dependencies and complex imports
        files_content = {
            "module_a.py": '''"""Module A with complex imports."""
import os
import sys
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from complex.module_b import ClassB, function_b
from complex.module_c import process_data
from utils.validators import validate_email
from models.user import User, UserRole

class ClassA:
    def __init__(self):
        self.b_instance = ClassB()
        self.data = defaultdict(list)
    
    def process(self, users: List[User]) -> Dict[str, int]:
        result = {}
        for user in users:
            if validate_email(user.email):
                processed = process_data(user.to_dict())
                result[user.email] = len(processed)
        return result
''',
            "module_b.py": '''"""Module B with dependencies."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from complex.module_c import helper_function
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

class ClassB:
    def __init__(self):
        self.auth_service = None
    
    def initialize(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        if self.auth_service:
            user = self.auth_service.get_user_by_id(user_id)
            if user:
                return helper_function(user.to_dict())
        return {}

def function_b(data: Any) -> str:
    return json.dumps(data, indent=2)
''',
            "module_c.py": '''"""Module C with utility functions."""
import re
import hashlib
from typing import Any, Dict, List, Optional

def process_data(data: Dict[str, Any]) -> List[str]:
    """Process dictionary data into list of strings."""
    result = []
    for key, value in data.items():
        if isinstance(value, str):
            result.append(f"{key}: {value}")
        elif isinstance(value, (int, float)):
            result.append(f"{key}: {value}")
        else:
            result.append(f"{key}: {type(value).__name__}")
    return result

def helper_function(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function for user data processing."""
    processed = {
        "id": user_data.get("id"),
        "email_hash": hashlib.md5(user_data.get("email", "").encode()).hexdigest(),
        "name_length": len(user_data.get("name", "")),
        "role": user_data.get("role"),
        "processed_at": "2024-01-01T00:00:00"
    }
    return processed

def validate_data_structure(data: Any) -> bool:
    """Validate complex data structure."""
    if not isinstance(data, dict):
        return False
    
    required_fields = ["id", "email", "name"]
    return all(field in data for field in required_fields)
'''
        }
        
        # Write complex files
        for filename, content in files_content.items():
            with open(os.path.join(complex_dir, filename), "w") as f:
                f.write(content)
        
        with open(os.path.join(complex_dir, "__init__.py"), "w") as f:
            f.write("# Complex module package\n")
        
        # Test analysis of complex codebase
        start_time = time.time()
        response = self.client.get("/api/files/files_info")
        analysis_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        total_files = len([f for f in file_data["files"] if f["type"] == "file"])
        total_relationships = len(file_data["relationships"])
        
        print(f"✅ Complex codebase analysis: {total_files} files, {total_relationships} relationships")
        print(f"✅ Analysis time: {analysis_time:.2f}s")
        
        # Verify we found the complex files
        file_names = [f["name"] for f in file_data["files"]]
        complex_files = ["module_a.py", "module_b.py", "module_c.py"]
        
        for complex_file in complex_files:
            self.assertTrue(
                any(complex_file in name for name in file_names),
                f"Complex file {complex_file} not found"
            )
        
        # Should have reasonable number of relationships
        self.assertGreater(total_relationships, 5, "Should have multiple import relationships")
        
        # Analysis should complete in reasonable time
        self.assertLess(analysis_time, 15, "Complex analysis should complete within 15 seconds")
        
        # Clean up
        shutil.rmtree(complex_dir)
    
    def test_api_response_consistency(self):
        """Test API response format consistency."""
        print("\n=== Testing API Response Consistency ===")
        
        # Test all main endpoints for consistent response format
        endpoints_to_test = [
            ("/health", 200),
            ("/api/root/", 200),
            ("/api/files/files_info", 200)
        ]
        
        for endpoint, expected_status in endpoints_to_test:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, expected_status)
            
            # Verify JSON response
            self.assertEqual(response.headers["content-type"], "application/json")
            
            data = response.json()
            self.assertIsInstance(data, dict)
            
            # Should have process time header
            self.assertIn("x-process-time", response.headers)
            
            print(f"✅ {endpoint} returns consistent JSON response")
        
        # Test error response consistency
        error_endpoints = [
            ("/api/files/file_content/nonexistent.py", 404),
            ("/api/files/file_content/../../../etc/passwd", 403)
        ]
        
        for endpoint, expected_status in error_endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, expected_status)
            
            data = response.json()
            self.assertIn("error", data)
            self.assertIsInstance(data["error"], str)
            
            print(f"✅ {endpoint} returns consistent error response")
    
    def test_system_performance_metrics(self):
        """Test system performance under various conditions."""
        print("\n=== Testing System Performance Metrics ===")
        
        # Test response times for different operations
        operations = [
            ("File discovery", "/api/files/files_info"),
            ("Health check", "/health"),
            ("Root endpoint", "/api/root/")
        ]
        
        performance_results = {}
        
        for operation_name, endpoint in operations:
            times = []
            
            # Make multiple requests to get average response time
            for i in range(5):
                start_time = time.time()
                response = self.client.get(endpoint)
                end_time = time.time()
                
                self.assertEqual(response.status_code, 200)
                times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            performance_results[operation_name] = {
                "avg": avg_time,
                "max": max_time,
                "min": min_time
            }
            
            print(f"✅ {operation_name}: avg={avg_time:.3f}s, max={max_time:.3f}s, min={min_time:.3f}s")
        
        # Verify reasonable performance
        for operation_name, metrics in performance_results.items():
            self.assertLess(metrics["avg"], 2.0, f"{operation_name} average time should be under 2s")
            self.assertLess(metrics["max"], 5.0, f"{operation_name} max time should be under 5s")


if __name__ == '__main__':
    unittest.main(verbosity=2)