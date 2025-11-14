from utils.db import run_query

def handle_manage_users(request):
    """Admin page to manage users and their roles"""
    message = None
    alert_class = "info"
    
    if request.method == "POST":
        action = request.form.get("action")
        user_id = request.form.get("user_id")
        new_role = request.form.get("new_role")
        
        if action == "update_role" and user_id and new_role:
            try:
                query = "UPDATE User SET role = %s WHERE user_id = %s"
                run_query(query, (new_role, user_id))
                message = f"User role updated successfully."
                alert_class = "success"
            except Exception as e:
                message = f"Error updating user role: {str(e)}"
                alert_class = "danger"
    
    query = """
        SELECT 
            u.user_id,
            u.name,
            u.email,
            u.phone,
            u.role,
            u.created_at,
            (SELECT COUNT(*) 
             FROM AdoptionApplication aa 
             WHERE aa.user_id = u.user_id 
             AND aa.status = 'Approved') AS approved_applications,
            (SELECT COUNT(*) 
             FROM AdoptionApplication aa 
             WHERE aa.user_id = u.user_id) AS total_applications
        FROM User u
        ORDER BY u.created_at DESC
    """
    
    try:
        users = run_query(query, fetch=True) or []
    except Exception as e:
        users = []
        if not message:
            message = f"Error loading users: {str(e)}"
            alert_class = "danger"
    
    return {
        "users": users,
        "message": message,
        "alert_class": alert_class
    }

