from utils.db import run_query, run_procedure
from flask import session
import pymysql

def get_add_application_data(request=None):
    data = {}
    user_role = session.get('user_role', 'general')
    current_user_id = session.get('user_id')
    
    if user_role in ['admin', 'shelter_worker']:
        users = run_query("SELECT user_id, name FROM User;", fetch=True)
        data["users"] = users or []
        data["show_user_dropdown"] = True
    else:
        data["users"] = []
        data["show_user_dropdown"] = False
        data["current_user_id"] = current_user_id
    
    pets = run_query("SELECT pet_id, name, status FROM Pet ORDER BY status, name;", fetch=True)
    data["pets"] = pets or []
    
    if request and request.method == "POST":
        if user_role in ['admin', 'shelter_worker']:
            user_id = request.form.get("user_id")
        else:
            user_id = current_user_id
        
        pet_id = request.form.get("pet_id")
        reason = request.form.get("reason")
        
        if not user_id:
            data["message"] = "User ID is required."
            data["success"] = False
        else:
            result = add_application(user_id, pet_id, reason)
            data["message"] = result["message"]
            data["success"] = result["success"]
        
        data["pets"] = run_query("SELECT pet_id, name, status FROM Pet ORDER BY status, name;", fetch=True) or []
    
    return data

def add_application(user_id, pet_id, reason):
    """Insert a new adoption application using stored procedure."""
    try:
        run_procedure("AddAdoptionApplication", (user_id, pet_id, reason), fetch=False)
        return {
            "success": True,
            "message": "Adoption application submitted successfully!"
        }
    except pymysql.err.InternalError as e:
        error_code, error_msg = e.args
        if error_code == 1644:
            if "already been adopted" in str(error_msg):
                return {
                    "success": False,
                    "message": f"Application could not be submitted: This pet has already been adopted. The trigger prevented this action to maintain data integrity."
                }
            else:
                return {
                    "success": False,
                    "message": f"Application Denied: {error_msg}"
                }
        return {
            "success": False,
            "message": f"Database Error: {error_msg}"
        }
    except pymysql.err.OperationalError as e:
        error_code, error_msg = e.args
        if "already been adopted" in str(error_msg):
            return {
                "success": False,
                "message": f"Application could not be submitted: This pet has already been adopted. The trigger prevented this action to maintain data integrity."
            }
        return {
            "success": False,
            "message": f"Database Error: {error_msg}"
        }
    except Exception as e:
        error_str = str(e)
        if "already been adopted" in error_str:
            return {
                "success": False,
                "message": f"Application could not be submitted: This pet has already been adopted. The trigger prevented this action to maintain data integrity."
            }
        return {
            "success": False,
            "message": f"Error submitting application: {error_str}"
        }
