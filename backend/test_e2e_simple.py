#!/usr/bin/env python3
"""
Simplified end-to-end integration tests for the LLM Code Navigator.
Tests complete user workflows and system behavior.
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

# Set up test environment before importing app modules
test_backend_dir = tempfile.mkdtemp(prefix="e2e_test_")
os.environ["BACKEND_DIR"] = test_backend_dir
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise

from fastapi.testclient import TestClient
from app.main import app


class TestEndToEndWorkflows(unittest.TestCase):
    """End-to-end integration tests for complete user workflows."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment with realistic codebase."""
        cls.test_dir = test_backend_dir
        cls.client = TestClient(app, headers={"host": "localhost"})
        
        # Create realistic test codebase
        cls.create_realistic_codebase()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_realistic_codebase(cls):
        """Create a realistic Python codebase for testing."""
        # Main application file
        main_content = '''#!/usr/bin/env python3
"""
E-commerce web application built with Flask.
Handles user authentication, product catalog, and order management.
"""
import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Import application modules
from models.user import User, UserRole
from models.product import Product, Category
from models.order import Order, OrderItem, OrderStatus
from services.auth_service import AuthenticationService
from services.product_service import ProductService
from services.order_service import OrderService
from services.payment_service import PaymentService
from utils.validators import validate_email, validate_phone
from utils.decorators import login_required, admin_required
from utils.helpers import format_currency, calculate_tax

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ecommerce.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize services
auth_service = AuthenticationService(db)
product_service = ProductService(db)
order_service = OrderService(db)
payment_service = PaymentService()


@app.route('/')
def home():
    """Home page with featured products."""
    try:
        featured_products = product_service.get_featured_products(limit=8)
        categories = product_service.get_all_categories()
        
        return render_template('home.html', 
                             products=featured_products,
                             categories=categories)
    except Exception as e:
        logger.error(f"Error loading home page: {e}")
        return render_template('error.html', message="Unable to load home page"), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Create user
        user = auth_service.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone')
        )
        
        if user:
            session['user_id'] = user.id
            return jsonify({
                'message': 'Registration successful',
                'user': user.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Email already exists'}), 409
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = auth_service.authenticate_user(email, password)
        if user:
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/products')
def get_products():
    """Get products with optional filtering."""
    try:
        category_id = request.args.get('category_id', type=int)
        search_query = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        products = product_service.get_products(
            category_id=category_id,
            search_query=search_query,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'products': [p.to_dict() for p in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': products.page
        })
    
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({'error': 'Unable to load products'}), 500


@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Get single product details."""
    try:
        product = product_service.get_product_by_id(product_id)
        if product:
            return jsonify(product.to_dict())
        else:
            return jsonify({'error': 'Product not found'}), 404
    
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        return jsonify({'error': 'Unable to load product'}), 500


@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add product to shopping cart."""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'error': 'Product ID required'}), 400
        
        # Add to cart logic would go here
        # For now, just return success
        return jsonify({'message': 'Product added to cart'})
    
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return jsonify({'error': 'Unable to add to cart'}), 500


@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    """Create new order."""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        # Validate order data
        if not data.get('items'):
            return jsonify({'error': 'Order items required'}), 400
        
        # Create order
        order = order_service.create_order(
            user_id=user_id,
            items=data['items'],
            shipping_address=data.get('shipping_address'),
            billing_address=data.get('billing_address')
        )
        
        if order:
            return jsonify({
                'message': 'Order created successfully',
                'order': order.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Unable to create order'}), 500
    
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({'error': 'Order creation failed'}), 500


@app.route('/api/admin/products', methods=['POST'])
@admin_required
def create_product():
    """Create new product (admin only)."""
    try:
        data = request.get_json()
        
        product = product_service.create_product(
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            category_id=data['category_id'],
            stock_quantity=data.get('stock_quantity', 0)
        )
        
        if product:
            return jsonify({
                'message': 'Product created successfully',
                'product': product.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Unable to create product'}), 500
    
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return jsonify({'error': 'Product creation failed'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        
        # Models directory
        models_dir = os.path.join(cls.test_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        user_model = '''"""User model for authentication and user management."""
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    CUSTOMER = "customer"
    STAFF = "staff"


class User(db.Model):
    """User model."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    def get_full_name(self):
        """Get full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'phone': self.phone,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
'''
        
        product_model = '''"""Product and category models."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models.user import db


class Category(db.Model):
    """Product category model."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'product_count': len(self.products)
        }


class Product(db.Model):
    """Product model."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock_quantity > 0
    
    def can_order_quantity(self, quantity):
        """Check if quantity can be ordered."""
        return self.stock_quantity >= quantity
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity."""
        if self.can_order_quantity(quantity):
            self.stock_quantity -= quantity
            return True
        return False
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'stock_quantity': self.stock_quantity,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'category': self.category.to_dict() if self.category else None,
            'in_stock': self.is_in_stock(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
'''
        
        order_model = '''"""Order and order item models."""
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from models.user import db


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(db.Model):
    """Order model."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_address = db.Column(db.Text)
    billing_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def calculate_total(self):
        """Calculate order total."""
        return sum(item.subtotal for item in self.items)
    
    def get_item_count(self):
        """Get total item count."""
        return sum(item.quantity for item in self.items)
    
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'status': self.status.value,
            'total_amount': float(self.total_amount),
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            'item_count': self.get_item_count(),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class OrderItem(db.Model):
    """Order item model."""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Foreign keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def calculate_subtotal(self):
        """Calculate item subtotal."""
        return self.quantity * self.unit_price
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal),
            'product': self.product.to_dict() if self.product else None
        }
'''
        
        # Services directory
        services_dir = os.path.join(cls.test_dir, "services")
        os.makedirs(services_dir, exist_ok=True)
        
        auth_service = '''"""Authentication service."""
import logging
from typing import Optional, List
from models.user import User, UserRole, db

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Authentication service."""
    
    def __init__(self, database):
        self.db = database
    
    def create_user(self, email: str, password: str, first_name: str, 
                   last_name: str, phone: str = None, role: UserRole = UserRole.CUSTOMER) -> Optional[User]:
        """Create new user."""
        try:
            # Check if user exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return None
            
            # Create user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=role
            )
            user.set_password(password)
            
            self.db.session.add(user)
            self.db.session.commit()
            
            logger.info(f"Created user: {email}")
            return user
        
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            self.db.session.rollback()
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user."""
        try:
            user = User.query.filter_by(email=email, is_active=True).first()
            if user and user.check_password(password):
                return user
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return User.query.filter_by(id=user_id, is_active=True).first()
'''
        
        product_service = '''"""Product service."""
import logging
from typing import Optional, List
from flask_sqlalchemy import Pagination
from models.product import Product, Category, db

logger = logging.getLogger(__name__)


class ProductService:
    """Product service."""
    
    def __init__(self, database):
        self.db = database
    
    def get_products(self, category_id: int = None, search_query: str = None,
                    page: int = 1, per_page: int = 20) -> Pagination:
        """Get products with filtering."""
        query = Product.query.filter_by(is_active=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if search_query:
            query = query.filter(Product.name.contains(search_query))
        
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        return Product.query.filter_by(id=product_id, is_active=True).first()
    
    def get_featured_products(self, limit: int = 10) -> List[Product]:
        """Get featured products."""
        return Product.query.filter_by(is_featured=True, is_active=True).limit(limit).all()
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        return Category.query.filter_by(is_active=True).all()
    
    def create_product(self, name: str, description: str, price: float,
                      category_id: int, stock_quantity: int = 0) -> Optional[Product]:
        """Create new product."""
        try:
            product = Product(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                stock_quantity=stock_quantity
            )
            
            self.db.session.add(product)
            self.db.session.commit()
            
            return product
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            self.db.session.rollback()
            return None
'''
        
        order_service = '''"""Order service."""
import logging
import uuid
from typing import Optional, List, Dict, Any
from models.order import Order, OrderItem, OrderStatus, db
from models.product import Product

logger = logging.getLogger(__name__)


class OrderService:
    """Order service."""
    
    def __init__(self, database):
        self.db = database
    
    def create_order(self, user_id: int, items: List[Dict[str, Any]],
                    shipping_address: str = None, billing_address: str = None) -> Optional[Order]:
        """Create new order."""
        try:
            # Generate order number
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            # Create order
            order = Order(
                order_number=order_number,
                user_id=user_id,
                shipping_address=shipping_address,
                billing_address=billing_address,
                total_amount=0
            )
            
            self.db.session.add(order)
            self.db.session.flush()  # Get order ID
            
            # Add order items
            total_amount = 0
            for item_data in items:
                product = Product.query.get(item_data['product_id'])
                if not product or not product.can_order_quantity(item_data['quantity']):
                    continue
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    unit_price=product.price,
                    subtotal=product.price * item_data['quantity']
                )
                
                self.db.session.add(order_item)
                total_amount += order_item.subtotal
                
                # Reduce stock
                product.reduce_stock(item_data['quantity'])
            
            order.total_amount = total_amount
            self.db.session.commit()
            
            return order
        
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            self.db.session.rollback()
            return None
'''
        
        payment_service = '''"""Payment service."""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PaymentService:
    """Payment processing service."""
    
    def __init__(self):
        self.payment_gateway = "mock"  # Mock payment gateway
    
    def process_payment(self, amount: float, payment_method: str,
                       card_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process payment."""
        try:
            # Mock payment processing
            if amount <= 0:
                return {
                    'success': False,
                    'error': 'Invalid amount'
                }
            
            # Simulate payment processing
            transaction_id = f"TXN-{hash(str(amount) + payment_method) % 1000000:06d}"
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'amount': amount,
                'payment_method': payment_method,
                'status': 'completed'
            }
        
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            return {
                'success': False,
                'error': 'Payment processing failed'
            }
    
    def refund_payment(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        """Process refund."""
        try:
            # Mock refund processing
            refund_id = f"REF-{hash(transaction_id + str(amount)) % 1000000:06d}"
            
            return {
                'success': True,
                'refund_id': refund_id,
                'transaction_id': transaction_id,
                'amount': amount,
                'status': 'refunded'
            }
        
        except Exception as e:
            logger.error(f"Refund processing error: {e}")
            return {
                'success': False,
                'error': 'Refund processing failed'
            }
'''
        
        # Utils directory
        utils_dir = os.path.join(cls.test_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        validators = '''"""Input validation utilities."""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number."""
    if not phone or not isinstance(phone, str):
        return True  # Phone is optional
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15
'''
        
        decorators = '''"""Authentication decorators."""
import functools
from flask import session, jsonify, request
from services.auth_service import AuthenticationService


def login_required(f):
    """Require user to be logged in."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Require admin role."""
    @functools.wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # In a real app, you'd check the user's role here
        return f(*args, **kwargs)
    return decorated_function
'''
        
        helpers = '''"""Helper utilities."""
import locale
from typing import Any


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency amount."""
    try:
        if currency == 'USD':
            return f"${amount:.2f}"
        else:
            return f"{amount:.2f} {currency}"
    except:
        return str(amount)


def calculate_tax(amount: float, tax_rate: float = 0.08) -> float:
    """Calculate tax amount."""
    return amount * tax_rate
'''
        
        # Write all files
        files_to_write = [
            ("main.py", main_content),
            ("models/__init__.py", ""),
            ("models/user.py", user_model),
            ("models/product.py", product_model),
            ("models/order.py", order_model),
            ("services/__init__.py", ""),
            ("services/auth_service.py", auth_service),
            ("services/product_service.py", product_service),
            ("services/order_service.py", order_service),
            ("services/payment_service.py", payment_service),
            ("utils/__init__.py", ""),
            ("utils/validators.py", validators),
            ("utils/decorators.py", decorators),
            ("utils/helpers.py", helpers),
        ]
        
        for file_path, content in files_to_write:
            full_path = os.path.join(cls.test_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
    
    def test_complete_file_discovery_workflow(self):
        """Test complete file discovery and analysis workflow."""
        print("\n=== Testing Complete File Discovery Workflow ===")
        
        # Step 1: Discover all files in the codebase
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        self.assertIn("files", file_data)
        self.assertIn("relationships", file_data)
        
        files = file_data["files"]
        relationships = file_data["relationships"]
        
        # Verify we have the expected files
        file_names = [f["name"] for f in files if f["type"] == "file"]
        expected_files = [
            "main.py", "user.py", "product.py", "order.py",
            "auth_service.py", "product_service.py", "order_service.py",
            "validators.py", "decorators.py", "helpers.py"
        ]
        
        found_files = []
        for expected_file in expected_files:
            matching = [name for name in file_names if expected_file in name]
            if matching:
                found_files.append(expected_file)
        
        self.assertGreaterEqual(len(found_files), 8, f"Should find most expected files. Found: {found_files}")
        
        print(f"✅ Discovered {len(files)} files with {len(relationships)} import relationships")
        
        # Step 2: Verify import relationships
        self.assertGreater(len(relationships), 0, "Should have import relationships")
        
        # Check for specific relationships we expect
        relationship_sources = [r["source"] for r in relationships]
        main_relationships = [r for r in relationship_sources if "main.py" in r]
        self.assertGreater(len(main_relationships), 0, "main.py should have imports")
        
        print(f"✅ Verified import relationships between files")
        
        # Step 3: Test file content retrieval for different file types
        test_files = ["main.py", "user.py", "auth_service.py"]
        
        for test_file in test_files:
            matching_files = [f for f in files if f["name"].endswith(test_file)]
            if matching_files:
                file_id = matching_files[0]["id"]
                response = self.client.get(f"/api/files/file_content/{file_id}")
                self.assertEqual(response.status_code, 200, f"Failed to retrieve {test_file}")
                
                content_data = response.json()
                self.assertIn("content", content_data)
                self.assertIn("path", content_data)
                self.assertIn("encoding", content_data)
                
                content = content_data["content"]
                self.assertGreater(len(content), 100, f"{test_file} should have substantial content")
                
                # Verify content contains expected patterns
                if test_file == "main.py":
                    self.assertIn("Flask", content)
                    self.assertIn("@app.route", content)
                elif test_file == "user.py":
                    self.assertIn("class User", content)
                    self.assertIn("db.Model", content)
                elif test_file == "auth_service.py":
                    self.assertIn("class AuthenticationService", content)
        
        print(f"✅ Successfully retrieved and validated content for multiple file types")
    
    def test_pmd_analysis_workflow(self):
        """Test PMD static analysis workflow."""
        print("\n=== Testing PMD Analysis Workflow ===")
        
        # Get file data first
        response = self.client.get("/api/files/files_info")
        self.assertEqual(response.status_code, 200)
        
        file_data = response.json()
        python_files = [f for f in file_data["files"] if f["name"].endswith(".py")]
        self.assertGreater(len(python_files), 0)
        
        # Test PMD analysis on main.py
        main_files = [f for f in python_files if f["name"].endswith("main.py")]
        self.assertGreater(len(main_files), 0)
        
        main_file = main_files[0]
        file_id = main_file["id"]
        
        # Mock PMD service since PMD might not be installed
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            # Mock successful PMD analysis with realistic violations
            mock_pmd.return_value = {
                "violations": [
                    {
                        "rule": "TooManyImports",
                        "priority": 3,
                        "message": "Too many imports (15). Maximum allowed is 10.",
                        "line": 1,
                        "column": 1
                    },
                    {
                        "rule": "UnusedImport",
                        "priority": 3,
                        "message": "Unused import 'datetime'",
                        "line": 8,
                        "column": 1
                    },
                    {
                        "rule": "LineTooLong",
                        "priority": 4,
                        "message": "Line exceeds 120 characters",
                        "line": 45,
                        "column": 121
                    }
                ],
                "summary": {
                    "totalViolations": 3,
                    "fileAnalyzed": file_id
                }
            }
            
            response = self.client.get(f"/api/pmd/analysis/{file_id}")
            self.assertEqual(response.status_code, 200)
            
            pmd_result = response.json()
            self.assertIn("violations", pmd_result)
            self.assertIn("summary", pmd_result)
            
            violations = pmd_result["violations"]
            self.assertEqual(len(violations), 3)
            
            # Verify violation structure
            for violation in violations:
                required_fields = ["rule", "priority", "message", "line", "column"]
                for field in required_fields:
                    self.assertIn(field, violation, f"Violation missing field: {field}")
                
                self.assertIsInstance(violation["priority"], int)
                self.assertIsInstance(violation["line"], int)
                self.assertIsInstance(violation["column"], int)
            
            summary = pmd_result["summary"]
            self.assertEqual(summary["totalViolations"], 3)
            self.assertEqual(summary["fileAnalyzed"], file_id)
            
            print(f"✅ PMD analysis returned {len(violations)} violations with proper structure")
        
        # Test PMD analysis error handling
        with patch('app.api.endpoints.pmd.run_pmd_analysis') as mock_pmd:
            mock_pmd.side_effect = RuntimeError("PMD command not found")
            
            response = self.client.get(f"/api/pmd/analysis/{file_id}")
            self.assertEqual(response.status_code, 500)
            
            error_data = response.json()
            self.assertIn("error", error_data)
            self.assertIn("PMD command not found", error_data["error"])
            
            print("✅ PMD error handling works correctly")
    
    def test_security_validation_workflow(self):
        """Test security validation and error handling workflow."""
        print("\n=== Testing Security Validation Workflow ===")
        
        # Test 1: Path traversal prevention
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "/etc/passwd",
            "~/secret_file.py",
            "file:///etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"  # URL encoded
        ]
        
        for malicious_path in malicious_paths:
            response = self.client.get(f"/api/files/file_content/{malicious_path}")
            self.assertEqual(response.status_code, 403, f"Path traversal not blocked: {malicious_path}")
            
            error_data = response.json()
            self.assertIn("error", error_data)
            self.assertIn("Access denied", error_data["error"])
        
        print(f"✅ Blocked {len(malicious_paths)} path traversal attempts")
        
        # Test 2: File extension validation
        invalid_extensions = ["test.txt", "config.ini", "secret.log", "data.json"]
        
        for invalid_file in invalid_extensions:
            # Create the file first
            invalid_path = os.path.join(self.test_dir, invalid_file)
            with open(invalid_path, "w") as f:
                f.write("This should not be accessible")
            
            response = self.client.get(f"/api/files/file_content/{invalid_path}")
            self.assertEqual(response.status_code, 403, f"Invalid extension not blocked: {invalid_file}")
            
            error_data = response.json()
            self.assertIn("error", error_data)
            
            # Clean up
            os.remove(invalid_path)
        
        print(f"✅ Blocked {len(invalid_extensions)} invalid file extensions")
        
        # Test 3: File not found handling
        nonexistent_path = os.path.join(self.test_dir, 'nonexistent.py')
        response = self.client.get(f"/api/files/file_content/{nonexistent_path}")
        self.assertEqual(response.status_code, 404)
        
        error_data = response.json()
        self.assertIn("error", error_data)
        self.assertIn("File not found", error_data["error"])
        
        print("✅ File not found errors handled correctly")
        
        # Test 4: Large file size limits
        with patch('os.path.getsize') as mock_size:
            mock_size.return_value = 50 * 1024 * 1024 + 1  # Exceed 50MB limit
            
            # Get a valid file path
            response = self.client.get("/api/files/files_info")
            file_data = response.json()
            valid_file = next(f for f in file_data["files"] if f["name"].endswith(".py"))
            
            response = self.client.get(f"/api/files/file_content/{valid_file['id']}")
            self.assertEqual(response.status_code, 403)
            
            error_data = response.json()
            self.assertIn("error", error_data)
            self.assertIn("File too large", error_data["error"])
        
        print("✅ Large file size limits enforced correctly")
    
    def test_concurrent_request_handling(self):
        """Test system behavior under concurrent load."""
        print("\n=== Testing Concurrent Request Handling ===")
        
        import threading
        import queue
        
        results = queue.Queue()
        num_threads = 8
        requests_per_thread = 5
        
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
                        start_time = time.time()
                        response = self.client.get(endpoint)
                        end_time = time.time()
                        
                        thread_results.append({
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "response_time": end_time - start_time,
                            "success": response.status_code == 200
                        })
                
                except Exception as e:
                    thread_results.append({
                        "endpoint": "unknown",
                        "status_code": 0,
                        "response_time": 0,
                        "success": False,
                        "error": str(e)
                    })
            
            results.put(thread_results)
        
        # Start concurrent threads
        threads = []
        overall_start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=make_concurrent_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=60)  # 60 second timeout
        
        overall_end_time = time.time()
        
        # Collect and analyze results
        all_results = []
        while not results.empty():
            all_results.extend(results.get())
        
        # Calculate statistics
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r["success"])
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        response_times = [r["response_time"] for r in all_results if r["success"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print(f"✅ Concurrent load test results:")
        print(f"   - Total requests: {total_requests}")
        print(f"   - Successful: {successful_requests} ({success_rate:.1%})")
        print(f"   - Average response time: {avg_response_time:.3f}s")
        print(f"   - Max response time: {max_response_time:.3f}s")
        print(f"   - Total test time: {overall_end_time - overall_start_time:.2f}s")
        
        # Assertions for acceptable performance
        self.assertGreater(success_rate, 0.9, "Success rate should be above 90%")
        self.assertLess(avg_response_time, 2.0, "Average response time should be under 2 seconds")
        self.assertLess(overall_end_time - overall_start_time, 30, "Test should complete within 30 seconds")
    
    def test_api_response_consistency(self):
        """Test API response format consistency across all endpoints."""
        print("\n=== Testing API Response Consistency ===")
        
        # Test successful responses
        success_endpoints = [
            ("/health", 200),
            ("/api/root/", 200),
            ("/api/files/files_info", 200)
        ]
        
        for endpoint, expected_status in success_endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, expected_status, f"Unexpected status for {endpoint}")
            
            # Verify JSON response
            self.assertEqual(response.headers["content-type"], "application/json")
            
            data = response.json()
            self.assertIsInstance(data, dict, f"Response should be JSON object for {endpoint}")
            
            # Should have process time header
            self.assertIn("x-process-time", response.headers, f"Missing process time header for {endpoint}")
            
            # Verify response time is reasonable
            process_time = float(response.headers["x-process-time"])
            self.assertLess(process_time, 5.0, f"Process time too high for {endpoint}: {process_time}s")
        
        print(f"✅ Verified consistent responses for {len(success_endpoints)} endpoints")
        
        # Test error response consistency
        nonexistent_path = os.path.join(self.test_dir, 'nonexistent.py')
        error_scenarios = [
            (f"/api/files/file_content/{nonexistent_path}", 404, "File not found"),
            ("/api/files/file_content/../../../etc/passwd", 403, "Access denied"),
            ("/api/files/file_content/test.txt", 403, "Access denied")
        ]
        
        for endpoint, expected_status, expected_error_type in error_scenarios:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, expected_status, f"Unexpected status for {endpoint}")
            
            # Verify JSON error response
            self.assertEqual(response.headers["content-type"], "application/json")
            
            data = response.json()
            self.assertIn("error", data, f"Error response missing 'error' field for {endpoint}")
            self.assertIsInstance(data["error"], str, f"Error message should be string for {endpoint}")
            self.assertIn(expected_error_type, data["error"], f"Error message should contain '{expected_error_type}' for {endpoint}")
        
        print(f"✅ Verified consistent error responses for {len(error_scenarios)} scenarios")
    
    def test_system_performance_benchmarks(self):
        """Test system performance benchmarks."""
        print("\n=== Testing System Performance Benchmarks ===")
        
        # Test file discovery performance
        discovery_times = []
        for i in range(3):
            start_time = time.time()
            response = self.client.get("/api/files/files_info")
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            discovery_times.append(end_time - start_time)
        
        avg_discovery_time = sum(discovery_times) / len(discovery_times)
        print(f"✅ File discovery performance: {avg_discovery_time:.3f}s average")
        
        # Test file content retrieval performance
        response = self.client.get("/api/files/files_info")
        file_data = response.json()
        test_files = [f for f in file_data["files"] if f["name"].endswith(".py")][:3]
        
        content_times = []
        for test_file in test_files:
            start_time = time.time()
            response = self.client.get(f"/api/files/file_content/{test_file['id']}")
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            content_times.append(end_time - start_time)
        
        avg_content_time = sum(content_times) / len(content_times)
        print(f"✅ File content retrieval performance: {avg_content_time:.3f}s average")
        
        # Performance assertions
        self.assertLess(avg_discovery_time, 3.0, "File discovery should complete within 3 seconds")
        self.assertLess(avg_content_time, 1.0, "File content retrieval should complete within 1 second")
        
        # Test memory usage stability
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make multiple requests to test for memory leaks
        for i in range(10):
            self.client.get("/api/files/files_info")
            if i % 3 == 0:
                gc.collect()  # Force garbage collection
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"✅ Memory usage: {initial_memory:.1f}MB → {final_memory:.1f}MB (Δ{memory_increase:+.1f}MB)")
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 50, "Memory usage increase should be under 50MB")


if __name__ == '__main__':
    unittest.main(verbosity=2)