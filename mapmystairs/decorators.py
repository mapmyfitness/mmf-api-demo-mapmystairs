"""
    Decorators
    ~~~~~~~~~~
"""
from functools import wraps
from flask import g, request, redirect, session, url_for


# decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if user is None:
            return redirect(url_for('auth_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
