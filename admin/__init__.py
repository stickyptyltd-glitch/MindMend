"""
MindMend Admin Panel - Main Blueprint
====================================
Secure, comprehensive admin interface for MindMend platform management
"""
from flask import Blueprint

# Create the main admin blueprint
admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin',
    template_folder='../templates/admin',
    static_folder='../static'
)

# Import all admin modules to register their routes
from . import dashboard
from . import auth
from . import users
from . import subscriptions
from . import finance
from . import ai_management
from . import marketing
from . import api_management
from . import system
from . import compliance

__all__ = ['admin_bp']