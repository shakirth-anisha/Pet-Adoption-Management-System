from utils.db import run_query
from flask import request

def handle_add_user(request, is_registration=False):
    message = None
    alert_class = "info"

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        role = request.form.get("role")
        
        if is_registration:
            role = 'general'
            if not password:
                message = "Password is required for registration."
                alert_class = "danger"
                return {"message": message, "alert_class": alert_class, "is_registration": True}
        else:
            if not role:
                message = "Please fill in all required fields (Name, Email, Role)."
                alert_class = "danger"
                return {"message": message, "alert_class": alert_class, "is_registration": False}

        if not all([name, email]):
            message = "Please fill in all required fields (Name, Email)."
            alert_class = "danger"
            return {"message": message, "alert_class": alert_class, "is_registration": is_registration}

        if not password:
            password = "default123" 
        
        try:
            # Use SHA2 for password hashing (matching database)
            query = "CALL AddUser(%s, %s, SHA2(%s, 256), %s, %s);"
            params = (name, email, password, phone, role)
            run_query(query, params)
            message = f"User '{name}' has been successfully registered!"
            alert_class = "success"
            if is_registration:
                message += " Please login with your credentials."

        except Exception as e:
            if "Email already exists" in str(e):
                message = "Email already exists. Please use a different one."
                alert_class = "warning"
            else:
                message = f"Error registering user: {str(e)}"
                alert_class = "danger"

    return {"message": message, "alert_class": alert_class, "is_registration": is_registration}
