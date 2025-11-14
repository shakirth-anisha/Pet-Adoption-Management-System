from datetime import datetime
from utils.db import run_query
import json

def handle_test_procedural_extensions(request):
    message = None
    alert_class = "info"
    error = None

    # default context pieces
    context = {
        "page_title": "Procedural Extensions Testing",
        "procedure_results": [],
        "function_results": [],
        "trigger_logs": [],
        "all_triggers": [],
        "message": message,
        "alert_class": alert_class,
        "error": error
    }

    context["all_triggers"] = [
        {"name": "trg_log_pet_status_change", "event": "BEFORE UPDATE", "table": "Pet", "description": "Logs pet status changes into PetStatusLog."},
        {"name": "trg_prevent_duplicate_adoption", "event": "BEFORE INSERT", "table": "AdoptionApplication", "description": "Prevents application if pet is already Adopted."},
        {"name": "trg_update_pet_status_on_approval", "event": "AFTER UPDATE", "table": "AdoptionApplication", "description": "Updates Pet and Payment status upon application approval."},
    ]

    try:
        logs = run_query("SELECT pet_id, old_status, new_status, changed_at FROM PetStatusLog ORDER BY changed_at DESC LIMIT 10", fetch=True) or []
        for r in logs:
            if isinstance(r.get("changed_at"), datetime):
                r["changed_at"] = r["changed_at"].strftime("%Y-%m-%d %H:%M:%S")
        context["trigger_logs"] = logs
    except Exception:
        context["trigger_logs"] = []

    action = request.form.get("action") if request.method == "POST" else None

    if action:
        try:
            
            # GetAdoptedPetsByUsers 
            if action == "GetAdoptedPetsByUsers":
                rows = run_query("CALL GetAdoptedPetsByUsers()", fetch=True)
                context["procedure_results"].append({
                    "name": "GetAdoptedPetsByUsers",
                    "description": "List of approved adoptions with user & pet.",
                    "output_format": "Table",
                    "output_data": rows
                })
                message = "GetAdoptedPetsByUsers executed (results shown)."
                alert_class = "info"

            #  RunCountAvailablePets (Function) 
            elif action == "RunCountAvailablePets":
                shelter_id = request.form.get("shelter_id")
                if not shelter_id:
                    raise Exception("Shelter ID is required.")
                
                available = run_query("SELECT CountAvailablePets(%s) AS val", (int(shelter_id),), fetch=True)[0]["val"]
                
                context["function_results"].append({
                    "name": f"CountAvailablePets(shelter={shelter_id})",
                    "description": "Available pets in shelter",
                    "output_data": available
                })
                message = f"CountAvailablePets executed (Shelter ID: {shelter_id})."
                alert_class = "success"

            #  RunTotalAdoptionsByUser (Function) 
            elif action == "RunTotalAdoptionsByUser":
                user_id = request.form.get("user_id")
                if not user_id:
                    raise Exception("User ID is required.")

                total = run_query("SELECT TotalAdoptionsByUser(%s) AS val", (int(user_id),), fetch=True)[0]["val"]
                
                context["function_results"].append({
                    "name": f"TotalAdoptionsByUser(user={user_id})",
                    "description": "Total approved adoptions by user",
                    "output_data": total
                })
                message = f"TotalAdoptionsByUser executed (User ID: {user_id})."
                alert_class = "success"

            #  RunAvgPetAgeInShelter (Function) 
            elif action == "RunAvgPetAgeInShelter":
                shelter_id = request.form.get("shelter_id")
                if not shelter_id:
                    raise Exception("Shelter ID is required.")
                
                avg_age = run_query("SELECT AvgPetAgeInShelter(%s) AS val", (int(shelter_id),), fetch=True)[0]["val"]
                
                context["function_results"].append({
                    "name": f"AvgPetAgeInShelter(shelter={shelter_id})",
                    "description": "Average pet age in shelter",
                    "output_data": avg_age
                })
                message = f"AvgPetAgeInShelter executed (Shelter ID: {shelter_id})."
                alert_class = "success"

            else:
                raise Exception(f"Unknown action requested: {action}")

        except Exception as e:
            error = f"Error executing {action}: {e}"
            alert_class = "danger"

        context["message"] = message
        context["alert_class"] = alert_class
        context["error"] = error

    return context