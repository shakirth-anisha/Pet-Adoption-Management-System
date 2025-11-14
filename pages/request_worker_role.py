from utils.db import run_query
from flask import session

def handle_request_worker_role(request):
    message = None
    alert_class = "info"
    user_id = session.get('user_id')
    
    if not user_id:
        return {
            "message": "You must be logged in to request a role upgrade.",
            "alert_class": "danger"
        }
    
    # 1. Check current role
    role_query = "SELECT role FROM User WHERE user_id = %s"
    user_role_result = run_query(role_query, (user_id,), fetch=True)
    current_role = user_role_result[0]['role'] if user_role_result else None
    
    if current_role == 'admin':
        return {
            "message": "You are already an admin. No upgrade needed.",
            "alert_class": "info",
            "already_upgraded": True
        }
    
    # 2. Check for existing pending request
    pending = []
    try:
        pending_query = """
            SELECT request_id, status, requested_role
            FROM WorkerRequest 
            WHERE user_id = %s AND status = 'Pending'
        """
        pending = run_query(pending_query, (user_id,), fetch=True)
    except Exception:
        pending_query = """
            SELECT request_id, status
            FROM WorkerRequest 
            WHERE user_id = %s AND status = 'Pending'
        """
        pending = run_query(pending_query, (user_id,), fetch=True)
    
    if pending and len(pending) > 0:
        pending_request = pending[0]
        
        pending_role = pending_request.get('requested_role', 'shelter_worker')
        
        if current_role == pending_role:
            try:
                cancel_query = "UPDATE WorkerRequest SET status = 'Rejected' WHERE request_id = %s"
                run_query(cancel_query, (pending_request['request_id'],))
            except Exception:
                pass
        
        if pending and len(pending) > 0:
            role_name = "Shelter Worker" if pending_role == 'shelter_worker' else "Admin"
            return {
                "message": f"You already have a pending request to become a {role_name}. Please wait for admin approval.",
                "alert_class": "warning",
                "has_pending": True,
                "pending_role": pending_role
            }
    
    # 3. Handle POST submission for a new request
    if request.method == "POST":
        requested_role = request.form.get("requested_role", "shelter_worker")
        message_text = request.form.get("message", "")
        
        if requested_role not in ['shelter_worker', 'admin']:
            requested_role = 'shelter_worker'
            
        role_name = "Shelter Worker" if requested_role == 'shelter_worker' else "Admin"

        if not message_text:
            message_text = f"Request to become a {role_name}"
        
        try:
            insert_query = """
                INSERT INTO WorkerRequest (user_id, message, requested_role, status)
                VALUES (%s, %s, %s, 'Pending')
            """
            run_query(insert_query, (user_id, message_text, requested_role))
            
            message = f"Your request to become a {role_name} has been submitted successfully. An admin will review it soon."
            alert_class = "success"
            
        except Exception as col_error:
            if "Unknown column 'requested_role'" in str(col_error):
                try:
                    insert_query_fallback = """
                        INSERT INTO WorkerRequest (user_id, message, status)
                        VALUES (%s, %s, 'Pending')
                    """
                    run_query(insert_query_fallback, (user_id, message_text))
                    message = "Your request has been submitted successfully (defaulted to Shelter Worker request)."
                    alert_class = "success"
                except Exception as fallback_error:
                    message = f"Error submitting request (Fallback failed): {str(fallback_error)}"
                    alert_class = "danger"
            else:
                message = f"Error submitting request: {str(col_error)}"
                alert_class = "danger"
    
    
    return {
        "message": message,
        "alert_class": alert_class,
        "has_pending": pending and len(pending) > 0 if pending else False,
        "current_role": current_role,
    }