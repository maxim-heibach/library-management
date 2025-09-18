# library_app/decorators.py
# Enthält benutzerdefinierte Decorators zur Überprüfung von Benutzerrollen und Zugriffsrechten.

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('Für diese Aktion haben Sie nicht die erforderlichen Rechte.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

admin_required = role_required(['admin'])
librarian_required = role_required(['admin', 'librarian'])