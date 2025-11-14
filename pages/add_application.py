from utils.db import run_query, run_procedure
import pymysql

def get_add_application_data(request=None):
    """Fetch all users and pets to populate dropdowns and handle form submission."""
    data = {}
    
    users = run_query("SELECT user_id, name FROM User WHERE role='adopter';", fetch=True)
    data["users"] = users or []
    
    pets = run_query("SELECT pet_id, name FROM Pet;", fetch=True)
    data["pets"] = pets or []
    
    if request and request.method == "POST":
        user_id = request.form.get("user_id")
        pet_id = request.form.get("pet_id")
        reason = request.form.get("reason")
        
        result = add_application(user_id, pet_id, reason)
        data["message"] = result["message"]
        data["success"] = result["success"]
        
        data["pets"] = run_query("SELECT pet_id, name FROM Pet WHERE status='Available';", fetch=True) or []
    
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
            return {
                "success": False,
                "message": f"Application Denied: {error_msg}"
            }
        return {
            "success": False,
            "message": f"Database Error: {error_msg}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error submitting application: {str(e)}"
        }
