from utils.db import run_query, run_procedure

def handle_manage_payments(request):
    message = None
    alert_class = "info"

    if request.method == "POST":
        pay_id = request.form.get("pay_id")
        action = request.form.get("action")
        
        try:
            current_status_result = run_query(
                "SELECT status FROM Payment WHERE pay_id = %s", 
                (pay_id,), 
                fetch=True
            )
            
            current_status = current_status_result[0]['status'] if current_status_result else None
            
            if not current_status:
                 raise Exception("Payment ID not found.")

            if action == "update_status":
                new_status = request.form.get("new_status")
                
                if current_status in ["Completed", "Refunded"]:
                    raise Exception(f"Cannot update status for finalized payment ({current_status}).")
                
                run_procedure("UpdatePaymentStatus", (pay_id, new_status))
                message = f"Status for Payment #{pay_id} updated to {new_status} successfully."
                alert_class = "success"

            elif action == "update_method":
                new_method = request.form.get("new_method")
            
                if current_status in ["Completed", "Refunded"]:
                    raise Exception(f"Cannot change method for finalized payment ({current_status}).")
                
                run_procedure("UpdatePaymentMethod", (pay_id, new_method))
                message = f"Payment Method for #{pay_id} updated to {new_method} successfully."
                alert_class = "success"
            
            else:
                message = "Invalid action received."
                alert_class = "warning"

        except Exception as e:
            message = f"Error updating payment #{pay_id}: {e}"
            alert_class = "danger"

    filter_status = request.args.get('status')
    if not filter_status or filter_status == 'All':
        filter_status = None

    query = """
        SELECT 
            p.pay_id, p.method, p.amount, p.status, p.date,
            u.name AS user_name,
            a.pet_id, a.status AS app_status
        FROM Payment p
        JOIN User u ON p.user_id = u.user_id
        LEFT JOIN AdoptionApplication a 
            ON p.adoption_app_id = a.adopt_app_id
    """
    params = []

    if filter_status:
        query += " WHERE p.status = %s"
        params.append(filter_status)

    query += " ORDER BY p.date DESC"

    try:
        payments = run_query(query, tuple(params), fetch=True)

    except Exception as e:
        payments = []
        if not message or alert_class == "info":
            message = f"Error loading payments: {e}"
            alert_class = "danger"

    return {
        "payments": payments,
        "message": message,
        "alert_class": alert_class,
        "filter_status": filter_status
    }