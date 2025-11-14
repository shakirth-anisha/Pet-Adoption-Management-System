from utils.db import run_query, run_procedure

def handle_manage_applications(request):
    message = None
    alert_class = "info"
    filter_status = request.args.get('status') 
    if not filter_status or filter_status == 'All':
        filter_status = None

    if request.method == "POST":
        action = request.form.get("action")
        app_id = request.form.get("app_id")
        worker_id = request.form.get("worker_id")
        reject_reason = request.form.get("reject_reason")

        try:
            if action == "approve":
                if not worker_id:
                    raise ValueError("Worker ID is required for approval.")
                
                run_procedure("ApproveApplication", (app_id, worker_id))
                message = f"Application #{app_id} approved successfully."
                alert_class = "success"

            elif action == "reject":
                if not reject_reason:
                    raise ValueError("Rejection reason is required.")
                    
                run_procedure("RejectApplication", (app_id, reject_reason))
                message = f"Application #{app_id} rejected."
                alert_class = "warning"
            
            else:
                 message = "Invalid action received."
                 alert_class = "warning"

        except Exception as e:
            message = f"Error performing action on application #{app_id}: {e}"
            alert_class = "danger"

    query = """
        SELECT 
            a.adopt_app_id,
            a.status,
            a.reason,
            u.name AS user_name,
            u.email,
            p.pet_id,
            p.name AS pet_name,
            p.status AS pet_status,
            a.approved_by
        FROM AdoptionApplication a
        JOIN User u ON a.user_id = u.user_id
        JOIN Pet p ON a.pet_id = p.pet_id
    """
    params = []

    if filter_status:
        query += " WHERE a.status = %s"
        params.append(filter_status)
    
    query += " ORDER BY a.adopt_app_id DESC"

    try:
        applications = run_query(query, tuple(params), fetch=True)

    except Exception as e:
        applications = []
        if not message or alert_class == "info":
            message = f"Failed to load applications: {e}"
            alert_class = "danger"

    return {
        "applications": applications,
        "message": message,
        "alert_class": alert_class,
        "filter_status": filter_status 
    }