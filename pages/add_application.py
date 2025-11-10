from utils.db import run_query, run_procedure
import pymysql

def get_add_application_data(request=None):
    """Fetch all users and pets to populate dropdowns and handle form submission."""
    data = {}
    
    # Fetch users (adopters only)
    users = run_query("SELECT user_id, name FROM User WHERE role='adopter';", fetch=True)
    data["users"] = users or []
    
    # Fetch available pets
    pets = run_query("SELECT pet_id, name FROM Pet WHERE status='Available';", fetch=True)
    data["pets"] = pets or []
    
    # Handle form submission
    if request and request.method == "POST":
        user_id = request.form.get("user_id")
        pet_id = request.form.get("pet_id")
        reason = request.form.get("reason")
        
        result = add_application(user_id, pet_id, reason)
        data["message"] = result["message"]
        data["success"] = result["success"]
        
        # Refresh the pet list after submission to reflect any status changes
        data["pets"] = run_query("SELECT pet_id, name FROM Pet WHERE status='Available';", fetch=True) or []
    
    return data

def add_application(user_id, pet_id, reason):
    """Insert a new adoption application using stored procedure."""
    try:
        # Call the stored procedure AddAdoptionApplication
        run_procedure("AddAdoptionApplication", (user_id, pet_id, reason), fetch=False)
        return {
            "success": True,
            "message": "✅ Adoption application submitted successfully! You can view its status in 'Manage Applications'."
        }
    except pymysql.err.InternalError as e:
        # Handle trigger error (SQLSTATE 45000)
        error_code, error_msg = e.args
        if error_code == 1644:  # Custom SIGNAL error from trigger
            return {
                "success": False,
                "message": f"❌ Application Denied: {error_msg}"
            }
        return {
            "success": False,
            "message": f"❌ Database Error: {error_msg}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error submitting application: {str(e)}"
        }
