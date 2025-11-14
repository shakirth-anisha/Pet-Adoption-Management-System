from flask import Flask, render_template, redirect, url_for, request, session, make_response
from pages import (
    dashboard, add_user, manage_pets, view_pets,
    register_pet, add_application, manage_applications, 
    manage_payments, view_all_data, test_procedural_extensions,
    auth, manage_users, view_worker_applications,
    manage_my_applications, request_worker_role
)
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Role-based page access permissions
ROLE_PERMISSIONS = {
    'admin': [
        'dashboard', 'add_user', 'register_pet', 'add_application', 'view_pets',
        'manage_pets', 'manage_applications', 'manage_payments', 'view_all_data',
        'test_procedural_extensions', 'manage_users', 'view_worker_applications',
        'manage_my_applications', 'request_worker_role'
    ],
    'shelter_worker': [
        'dashboard', 'register_pet', 'manage_pets', 'manage_payments',
        'manage_applications', 'add_application', 'view_all_data', 'view_pets',
        'request_worker_role'
    ],
    'general': [
        'dashboard', 'add_application', 'view_pets', 'manage_my_applications',
        'request_worker_role'
    ],
    'adopter': [
        'dashboard', 'add_application', 'view_pets', 'manage_my_applications',
        'request_worker_role'
    ]
}

# Navigation options based on role
def get_nav_options_for_role(role):
    """Get navigation options based on user role"""
    base_nav = {
        "Dashboard": "dashboard",
    }
    
    if role == 'admin':
        return {
            **base_nav,
            "Register User": "add_user",
            "Register Pet": "register_pet",
            "Add Adoption Application": "add_application",
            "View Pets": "view_pets",
            "Manage Pets": "manage_pets",
            "Manage Applications": "manage_applications",
            "Manage Payments": "manage_payments",
            "View All Data": "view_all_data",
            "Manage Users": "manage_users",
            "View Worker Applications": "view_worker_applications",
            "Manage My Applications": "manage_my_applications",
            "Request Role Upgrade": "request_worker_role",
            "Test Procedural Extensions": "test_procedural_extensions"
        }
    elif role == 'shelter_worker':
        return {
            **base_nav,
            "Register Pet": "register_pet",
            "Add Adoption Application": "add_application",
            "View Pets": "view_pets",
            "Manage Pets": "manage_pets",
            "Manage Applications": "manage_applications",
            "Manage Payments": "manage_payments",
            "View All Data": "view_all_data",
            "Request Role Upgrade": "request_worker_role"
        }
    elif role == 'general':
        return {
            **base_nav,
            "Add Adoption Application": "add_application",
            "View Pets": "view_pets",
            "Manage My Applications": "manage_my_applications",
            "Request Role Upgrade": "request_worker_role"
        }
    elif role == 'adopter':
        return {
            **base_nav,
            "Add Adoption Application": "add_application",
            "View Pets": "view_pets",
            "Manage My Applications": "manage_my_applications",
            "Request Role Upgrade": "request_worker_role"
        }
    return base_nav

# Map page names to (handler_function, template_name)
page_registry = {
    "dashboard": (dashboard.get_dashboard_data, "dashboard.html"),
    "add_user": (add_user.handle_add_user, "add_user.html"),
    "view_pets": (view_pets.handle_view_pets, "view_pets.html"),
    "add_application": (add_application.get_add_application_data, "add_application.html"),
    "manage_applications": (manage_applications.handle_manage_applications, "manage_applications.html"),
    "manage_payments": (manage_payments.handle_manage_payments, "manage_payments.html"),
    "register_pet": (register_pet.handle_register_pet, "register_pet.html"),
    "manage_pets": (manage_pets.handle_manage_pets, "manage_pets.html"),
    "view_all_data": (view_all_data.handle_view_all_data, "view_all_data.html"),
    "test_procedural_extensions": (test_procedural_extensions.handle_test_procedural_extensions, "test_procedural_extensions.html"),
    "manage_users": (manage_users.handle_manage_users, "manage_users.html"),
    "view_worker_applications": (view_worker_applications.handle_view_worker_applications, "view_worker_applications.html"),
    "manage_my_applications": (manage_my_applications.handle_manage_my_applications, "manage_my_applications.html"),
    "request_worker_role": (request_worker_role.handle_request_worker_role, "request_worker_role.html")
}

def check_role_access(page_name, user_role):
    """Check if user has access to a page based on their role"""
    if not user_role:
        return False
    allowed_pages = ROLE_PERMISSIONS.get(user_role, [])
    return page_name in allowed_pages

@app.route("/")
def home():
    """Redirect to login if not authenticated, otherwise to dashboard"""
    if 'user_id' not in session:
        return redirect(url_for("login"))
    return redirect(url_for("render_page", page_name="dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for("render_page", page_name="dashboard"))
    
    data = auth.handle_login(request)
    
    if "redirect" in data:
        return redirect(data["redirect"])
    
    return render_template("login.html", **data)

@app.route("/logout")
def logout():
    """Logout route"""
    result = auth.handle_logout()
    if "redirect" in result:
        return redirect(result["redirect"])
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page - reuses add_user logic"""
    if 'user_id' in session:
        return redirect(url_for("render_page", page_name="dashboard"))
    
    data = add_user.handle_add_user(request, is_registration=True)
    data["nav_options"] = {}
    data["current_page"] = "register"
    return render_template("add_user.html", **data)

@app.route("/page/<page_name>", methods=["GET", "POST"])
def render_page(page_name):
    """Render page with authentication and role-based access control"""
    # Check authentication
    if 'user_id' not in session:
        return redirect(url_for("login"))
    
    # Refresh user session from database to get latest role
    auth.refresh_user_session()
    
    user_role = session.get('user_role')
    
    # Check role-based access
    if not check_role_access(page_name, user_role):
        return render_template("access_denied.html", 
                             current_page=page_name,
                             user_role=user_role), 403
    
    # Get navigation options for current role
    nav_options = get_nav_options_for_role(user_role)
    context = {"nav_options": nav_options, "current_page": page_name, "user_role": user_role}
    
    if page_name in page_registry:
        handler, template_name = page_registry[page_name]
        try:
            data = handler(request)
        except TypeError:
            data = handler()
        context.update(data)
        
        # Create response with no-cache headers to ensure fresh data
        response = make_response(render_template(template_name, **context))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return f"Page '{page_name}' does not exist.", 404

if __name__ == "__main__":
    app.run(debug=True)
