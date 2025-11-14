from utils.db import run_query, run_procedure
from flask import flash
import pymysql

def handle_manage_applications(request):
    """Handle manage applications page with filtering and actions"""
    # Get filter parameter
    status_filter = request.args.get('status', 'all')
    
    # Build query with filter
    query = """
        SELECT 
            a.adopt_app_id, a.status, a.reason, a.date,
            u.name AS adopter_name, u.email AS adopter_email,
            p.pet_id, p.name AS pet_name, p.age AS pet_age,
            pt.species AS pet_type, pt.breed AS pet_breed,
            s.name AS shelter_name,
            a.approved_by AS approved_by_worker_id,
            worker_user.name AS approved_by_name
        FROM AdoptionApplication a
        JOIN User u ON a.user_id = u.user_id
        JOIN Pet p ON a.pet_id = p.pet_id
        JOIN PetType pt ON p.type_id = pt.type_id
        JOIN Shelter s ON p.shelter_id = s.shelter_id
        LEFT JOIN ShelterWorker sw ON a.approved_by = sw.worker_id
        LEFT JOIN User worker_user ON sw.user_id = worker_user.user_id
    """
    
    if status_filter != 'all':
        query += f" WHERE a.status = '{status_filter}'"
    
    query += " ORDER BY a.date DESC, a.adopt_app_id DESC"
    
    applications = run_query(query, fetch=True)
    
    # Get all workers for the dropdown
    workers_query = """
        SELECT sw.worker_id, u.name, s.name AS shelter_name
        FROM ShelterWorker sw
        JOIN User u ON sw.user_id = u.user_id
        JOIN Shelter s ON sw.shelter_id = s.shelter_id
        ORDER BY u.name
    """
    workers = run_query(workers_query, fetch=True)
    
    return {
        "applications": applications,
        "workers": workers,
        "status_filter": status_filter
    }

def approve_application(app_id, worker_id):
    """Approve an adoption application using stored procedure"""
    try:
        run_procedure("ApproveApplication", (app_id, worker_id))
        flash(f"Application #{app_id} approved successfully! Pet status updated and payment completed.", "success")
        return True
    except pymysql.Error as e:
        error_msg = str(e)
        if "already been adopted" in error_msg.lower():
            flash(f"Cannot approve: This pet has already been adopted.", "error")
        else:
            flash(f"Error approving application: {error_msg}", "error")
        return False
    except Exception as e:
        flash(f"Unexpected error: {str(e)}", "error")
        return False

def reject_application(app_id, reason):
    """Reject an adoption application using stored procedure"""
    try:
        run_procedure("RejectApplication", (app_id, reason))
        flash(f"Application #{app_id} rejected. Reason: {reason}", "warning")
        return True
    except Exception as e:
        flash(f"Error rejecting application: {str(e)}", "error")
        return False
