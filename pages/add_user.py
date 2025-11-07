from utils.db import run_query

def handle_add_user(request):
    message = None
    alert_class = "info"

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        role = request.form.get("role")

        if not all([name, email, role]):
            message = "Please fill in all required fields (Name, Email, Role)."
            alert_class = "danger"
            return {"message": message, "alert_class": alert_class}

        try:
            query = "CALL AddUser(%s, %s, %s, %s);"
            params = (name, email, phone, role)
            run_query(query, params)
            message = f"User '{name}' has been successfully registered!"
            alert_class = "success"

        except Exception as e:
            if "Email already exists" in str(e):
                message = "Email already exists. Please use a different one."
                alert_class = "warning"
            else:
                message = f"Error registering user: {str(e)}"
                alert_class = "danger"

    return {"message": message, "alert_class": alert_class}
