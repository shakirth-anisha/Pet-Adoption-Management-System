from utils.db import run_query

def handle_view_worker_applications(request):
    """Admin page to view and manage worker role requests"""
    message = None
    alert_class = "info"
    
    if request.method == "POST":
        action = request.form.get("action")
        request_id = request.form.get("request_id")
        user_id = request.form.get("user_id")
        
        if action == "approve" and request_id and user_id:
            try:
                # Get the requested role from the request
                try:
                    role_query = "SELECT requested_role FROM WorkerRequest WHERE request_id = %s"
                    role_result = run_query(role_query, (request_id,), fetch=True)
                except Exception:
                    role_result = [{'requested_role': 'shelter_worker'}]
                
                if role_result and len(role_result) > 0:
                    requested_role = role_result[0].get('requested_role', 'shelter_worker')
                    update_query = "UPDATE User SET role = %s WHERE user_id = %s"
                    run_query(update_query, (requested_role, user_id))
                    
                    status_query = "UPDATE WorkerRequest SET status = 'Approved' WHERE request_id = %s"
                    run_query(status_query, (request_id,))
                    
                    role_name = "Shelter Worker" if requested_role == 'shelter_worker' else "Admin"
                    message = f"User role upgraded to {role_name} successfully."
                    alert_class = "success"
                else:
                    message = "Request not found."
                    alert_class = "danger"
            except Exception as e:
                message = f"Error approving request: {str(e)}"
                alert_class = "danger"
        
        elif action == "reject" and request_id:
            try:
                status_query = "UPDATE WorkerRequest SET status = 'Rejected' WHERE request_id = %s"
                run_query(status_query, (request_id,))
                
                message = f"Request rejected successfully."
                alert_class = "warning"
            except Exception as e:
                message = f"Error rejecting request: {str(e)}"
                alert_class = "danger"
    
    try:
        query = """
            SELECT 
                wr.request_id,
                wr.user_id,
                wr.message,
                wr.requested_role,
                wr.status,
                wr.created_at,
                u.name AS user_name,
                u.email,
                u.role AS current_role
            FROM WorkerRequest wr
            JOIN User u ON wr.user_id = u.user_id
            WHERE wr.status = 'Pending'
            ORDER BY wr.created_at DESC
        """
        requests = run_query(query, fetch=True) or []
    except Exception as e:
        error_str = str(e)
        if "Unknown column" in error_str and "requested_role" in error_str:
            try:
                query = """
                    SELECT 
                        wr.request_id,
                        wr.user_id,
                        wr.message,
                        'shelter_worker' AS requested_role,
                        wr.status,
                        wr.created_at,
                        u.name AS user_name,
                        u.email,
                        u.role AS current_role
                    FROM WorkerRequest wr
                    JOIN User u ON wr.user_id = u.user_id
                    WHERE wr.status = 'Pending'
                    ORDER BY wr.created_at DESC
                """
                requests = run_query(query, fetch=True) or []
            except Exception as e2:
                requests = []
                if not message:
                    message = f"Error loading requests: {str(e2)}"
                    alert_class = "danger"
        else:
            requests = []
            if not message:
                message = f"Error loading requests: {error_str}"
                alert_class = "danger"
    
    return {
        "requests": requests,
        "message": message,
        "alert_class": alert_class
    }

