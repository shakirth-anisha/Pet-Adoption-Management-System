from flask import session, redirect, url_for, request, render_template
from utils.db import run_query

def handle_login(request):
    """Handle user login"""
    message = None
    alert_class = "info"
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            message = "Please provide both email and password."
            alert_class = "danger"
            return {"message": message, "alert_class": alert_class}
        
        # First, get the user by email
        query = """
            SELECT user_id, name, email, role, password_hash
            FROM User
            WHERE email = %s
        """
        user_result = run_query(query, (email,), fetch=True)
        
        if user_result and len(user_result) > 0:
            user = user_result[0]
            verify_query = """
                SELECT CASE 
                    WHEN password_hash = SHA2(%s, 256) THEN 1 
                    ELSE 0 
                END AS password_match
            """
            try:
                verify_result = run_query(verify_query, (password,), fetch=True)
                if verify_result and verify_result[0].get('password_match') == 1:
                    session['user_id'] = user['user_id']
                    session['user_name'] = user['name']
                    session['user_email'] = user['email']
                    session['user_role'] = user['role']
                    message = f"Welcome back, {user['name']}!"
                    alert_class = "success"
                    return {"message": message, "alert_class": alert_class, "redirect": url_for("render_page", page_name="dashboard")}
                else:
                    message = "Invalid email or password."
                    alert_class = "danger"
            except Exception as e:
                alt_query = """
                    SELECT user_id, name, email, role
                    FROM User
                    WHERE email = %s AND password_hash = SHA2(%s, 256)
                """
                try:
                    alt_result = run_query(alt_query, (email, password), fetch=True)
                    if alt_result and len(alt_result) > 0:
                        user = alt_result[0]
                        session['user_id'] = user['user_id']
                        session['user_name'] = user['name']
                        session['user_email'] = user['email']
                        session['user_role'] = user['role']
                        message = f"Welcome back, {user['name']}!"
                        alert_class = "success"
                        return {"message": message, "alert_class": alert_class, "redirect": url_for("render_page", page_name="dashboard")}
                    else:
                        message = "Invalid email or password."
                        alert_class = "danger"
                except Exception as e2:
                    message = f"Database error: {str(e2)}. Please ensure the User table has a password_hash column."
                    alert_class = "danger"
        else:
            message = "Invalid email or password."
            alert_class = "danger"
    
    return {"message": message, "alert_class": alert_class}

def handle_logout():
    """Handle user logout"""
    session.clear()
    return {"redirect": url_for("login")}

def require_auth(required_role=None):
    """Decorator to check authentication and role"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for("login"))
            
            if required_role:
                user_role = session.get('user_role')
                if user_role != required_role and required_role != 'admin':
                    # Admin has access to everything
                    if required_role == 'shelter_worker' and user_role not in ['admin', 'shelter_worker']:
                        return redirect(url_for("render_page", page_name="dashboard"))
                    elif required_role == 'general' and user_role not in ['admin', 'shelter_worker', 'general']:
                        return redirect(url_for("render_page", page_name="dashboard"))
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def get_user_role():
    """Get current user's role from session"""
    return session.get('user_role', None)

def is_authenticated():
    """Check if user is authenticated"""
    return 'user_id' in session

def refresh_user_session():
    """Refresh user session data from database (especially role)"""
    if 'user_id' not in session:
        return False
    
    try:
        query = """
            SELECT user_id, name, email, role
            FROM User
            WHERE user_id = %s
        """
        user_result = run_query(query, (session.get('user_id'),), fetch=True)
        
        if user_result and len(user_result) > 0:
            user = user_result[0]
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            old_role = session.get('user_role')
            session['user_role'] = user['role']
            
            # Return True if role changed
            return old_role != user['role']
        return False
    except Exception:
        return False

