from utils.db import run_query, run_procedure
from flask import session

def handle_manage_my_applications(request):
    """General user page to view and manage their own adoption applications"""
    message = None
    alert_class = "info"
    user_id = session.get('user_id')
    
    if not user_id:
        return {
            "applications": [],
            "message": "You must be logged in to view your applications.",
            "alert_class": "danger"
        }
    
    if request.method == "POST":
        action = request.form.get("action")
        app_id = request.form.get("app_id")
        
        if action == "withdraw" and app_id:
            try:
                run_procedure("RejectApplication", (app_id, 'User withdrew application'), fetch=False)
                message = f"Application #{app_id} withdrawn successfully."
                alert_class = "success"
            except Exception as e:
                message = f"Error withdrawing application: {str(e)}"
                alert_class = "danger"
    
    query = """
        SELECT 
            a.adopt_app_id,
            a.status,
            a.reason,
            a.date,
            a.approved_by,
            p.pet_id,
            p.name AS pet_name,
            p.status AS pet_status,
            pt.species,
            pt.breed,
            s.name AS shelter_name,
            (SELECT COUNT(*) 
             FROM Payment pay 
             WHERE pay.adoption_app_id = a.adopt_app_id 
             AND pay.status = 'Completed') AS completed_payments,
            (SELECT SUM(pay.amount) 
             FROM Payment pay 
             WHERE pay.adoption_app_id = a.adopt_app_id) AS total_amount
        FROM AdoptionApplication a
        JOIN Pet p ON a.pet_id = p.pet_id
        JOIN PetType pt ON p.type_id = pt.type_id
        JOIN Shelter s ON p.shelter_id = s.shelter_id
        WHERE a.user_id = %s
        ORDER BY a.date DESC
    """
    
    try:
        applications = run_query(query, (user_id,), fetch=True) or []
    except Exception as e:
        applications = []
        if not message:
            message = f"Error loading applications: {str(e)}"
            alert_class = "danger"
    
    return {
        "applications": applications,
        "message": message,
        "alert_class": alert_class
    }

