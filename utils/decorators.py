"""
Decorators for protecting routes by login status and role.
Usage:
    @app.route('/admin/dashboard')
    @login_required
    @role_required('admin')
    def admin_dashboard():
        ...
"""

from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*allowed_roles):
    """Restrict a route to one or more roles, e.g. @role_required('teacher', 'admin')."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator
