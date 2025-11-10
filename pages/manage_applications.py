from utils.db import run_query, run_procedure
import pymysql

def handle_manage_applications(request):
    """Fetch and manage adoption applications."""
    data = {}
    
    # Handle form submission for approve/reject actions
    if request.method == "POST":
        action = request.form.get("action")
        app_id = request.form.get("app_id")
        
        if action == "approve":
            worker_id = request.form.get("worker_id")
            result = approve_application(app_id, worker_id)
            data["message"] = result["message"]
            data["alert_class"] = "success" if result["success"] else "danger"
            
        elif action == "reject":
            reject_reason = request.form.get("reject_reason")
            result = reject_application(app_id, reject_reason)
            data["message"] = result["message"]
            data["alert_class"] = "success" if result["success"] else "danger"
    
    # Filter option
    filter_status = request.args.get("filter", "all")
    
    # Fetch all applications with details
    query = """
        SELECT a.adopt_app_id, a.status, a.reason, a.date, a.approved_by,
               u.user_id, u.name AS adopter_name,
               p.pet_id, p.name AS pet_name, p.status AS pet_status,
               s.name AS shelter_name,
               w.name AS worker_name
        FROM AdoptionApplication a
        JOIN User u ON a.user_id = u.user_id
        JOIN Pet p ON a.pet_id = p.pet_id
        JOIN Shelter s ON p.shelter_id = s.shelter_id
        LEFT JOIN User w ON a.approved_by = w.user_id
    """
    
    if filter_status == "pending":
        query += " WHERE a.status = 'Pending'"
    
    query += " ORDER BY a.adopt_app_id DESC;"
    
    applications = run_query(query, fetch=True)
    data["applications"] = applications or []
    
    # Fetch workers for the approve dropdown
    workers = run_query("SELECT user_id, name FROM User WHERE role IN ('worker', 'shelter_worker', 'admin');", fetch=True)
    data["workers"] = workers or []
    data["current_filter"] = filter_status
    
    return data

def approve_application(app_id, worker_id):
    """Approve an adoption application using stored procedure."""
    try:
        # Call the stored procedure ApproveApplication
        run_procedure("ApproveApplication", (app_id, worker_id), fetch=False)
        return {
            "success": True,
            "message": "✅ Application approved successfully! Pet status updated to 'Adopted' and payment record initialized."
        }
    except pymysql.err.IntegrityError as e:
        return {
            "success": False,
            "message": f"❌ Database Error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error approving application: {str(e)}"
        }

def reject_application(app_id, reject_reason):
    """Reject an adoption application using stored procedure."""
    try:
        # Call the stored procedure RejectApplication
        run_procedure("RejectApplication", (app_id, reject_reason), fetch=False)
        return {
            "success": True,
            "message": "✅ Application rejected successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error rejecting application: {str(e)}"
        }
