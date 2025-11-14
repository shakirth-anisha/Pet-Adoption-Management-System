from datetime import datetime
from utils.db import run_query
import json

def handle_test_procedural_extensions(request):
    """
    Single-handler style (no blueprints) that:
    - Presents forms to run procedures/functions from your SQL file.
    - Captures 'before' and 'after' snapshots of related tables for auditing.
    - Returns a context dict for rendering the template.
    """

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
        "before": {},
        "after": {},
        "message": message,
        "alert_class": alert_class,
        "error": error
    }

    # helper: snapshot given list of tables (simple SELECT *)
    def snapshot_tables(table_list):
        snaps = {}
        for t in table_list:
            try:
                # Limit to 1000 rows for performance
                snaps[t] = run_query(f"SELECT * FROM {t} ORDER BY 1 LIMIT 1000", fetch=True) or []
            except Exception as e:
                snaps[t] = []
        return snaps

    # Known triggers (from your SQL) - Keep all, as they might still be active
    context["all_triggers"] = [
        {"name": "trg_log_pet_status_change", "event": "BEFORE UPDATE", "table": "Pet", "description": "Logs pet status changes into PetStatusLog."},
        {"name": "trg_prevent_duplicate_adoption", "event": "BEFORE INSERT", "table": "AdoptionApplication", "description": "Prevents application if pet is already Adopted."},
        {"name": "trg_update_pet_status_on_approval", "event": "AFTER UPDATE", "table": "AdoptionApplication", "description": "Updates Pet and Payment status upon application approval."},
    ]

    # Always show recent trigger logs
    try:
        logs = run_query("SELECT pet_id, old_status, new_status, changed_at FROM PetStatusLog ORDER BY changed_at DESC LIMIT 10", fetch=True) or []
        # ensure changed_at is string
        for r in logs:
            if isinstance(r.get("changed_at"), datetime):
                r["changed_at"] = r["changed_at"].strftime("%Y-%m-%d %H:%M:%S")
        context["trigger_logs"] = logs
    except Exception:
        context["trigger_logs"] = []

    # available actions triggered by POST forms
    action = request.form.get("action") if request.method == "POST" else None

    # Map each action to the tables we want to snapshot for before/after comparison.
    # Only keep UpdatePaymentStatus, GetAdoptedPetsByUsers, and FunctionsSummary
    SNAPSHOT_MAP = {
        "UpdatePaymentStatus": ["Payment"],
        "GetAdoptedPetsByUsers": ["AdoptionApplication", "User", "Pet"],  # read-only proc
        "FunctionsSummary": ["Pet", "AdoptionApplication"]
    }

    # If no action, we still want to render basic snapshots (small subset)
    # capture a default before snapshot for display purposes
    try:
        context["before"] = snapshot_tables(["Pet", "Payment", "AdoptionApplication"])
    except Exception as e:
        context["before"] = {}
        context["error"] = str(e)

    # Execute requested action and capture before/after snapshots for that action
    if action:
        # Default snapshot to keep it from breaking if action is not in map
        tables = SNAPSHOT_MAP.get(action, ["Payment"])
        
        # BEFORE
        before_snap = snapshot_tables(tables)
        context["before"] = before_snap

        try:
            # Drop RegisterPet, AddAdoptionApplication, ApproveApplication, RejectApplication, AutoRejectOtherApplications, AddUser
            
            # ---------- UpdatePaymentStatus ----------
            if action == "UpdatePaymentStatus":
                pay_id = request.form.get("pay_id")
                status_val = request.form.get("pay_status")
                if not pay_id or not status_val:
                    raise Exception("pay_id and pay_status are required.")
                run_query("CALL UpdatePaymentStatus(%s, %s)", (int(pay_id), status_val))
                message = f"UpdatePaymentStatus called for Pay {pay_id} -> {status_val}."
                alert_class = "success"

            # ---------- GetAdoptedPetsByUsers (read-only procedure) ----------
            elif action == "GetAdoptedPetsByUsers":
                rows = run_query("CALL GetAdoptedPetsByUsers()", fetch=True)
                # store as a procedure result for display
                context["procedure_results"].append({
                    "name": "GetAdoptedPetsByUsers",
                    "description": "List of approved adoptions with user & pet.",
                    "output_format": "Table",
                    "output_data": rows
                })
                message = "GetAdoptedPetsByUsers executed (results shown)."
                alert_class = "info"

            # ---------- Functions Summary (read-only) ----------
            elif action == "FunctionsSummary":
                shelter_id = request.form.get("shelter_id") or 1
                user_id = request.form.get("user_id") or 1
                try:
                    available = run_query("SELECT CountAvailablePets(%s) AS val", (int(shelter_id),), fetch=True)[0]["val"]
                except Exception:
                    available = "ERR"
                try:
                    total = run_query("SELECT TotalAdoptionsByUser(%s) AS val", (int(user_id),), fetch=True)[0]["val"]
                except Exception:
                    total = "ERR"
                try:
                    avg_age = run_query("SELECT AvgPetAgeInShelter(%s) AS val", (int(shelter_id),), fetch=True)[0]["val"]
                except Exception:
                    avg_age = "ERR"

                context["function_results"].append({
                    "name": f"CountAvailablePets(shelter={shelter_id})",
                    "description": "Available pets in shelter",
                    "output_data": available
                })
                context["function_results"].append({
                    "name": f"TotalAdoptionsByUser(user={user_id})",
                    "description": "Total approved adoptions by user",
                    "output_data": total
                })
                context["function_results"].append({
                    "name": f"AvgPetAgeInShelter(shelter={shelter_id})",
                    "description": "Average pet age in shelter",
                    "output_data": avg_age
                })

            else:
                # If an action was performed but it was one of the removed ones (shouldn't happen with the new HTML, but for safety)
                raise Exception(f"Action '{action}' is not supported in this test version.")

        except Exception as e:
            error = f"Error executing {action}: {e}"
            alert_class = "danger"

        # AFTER snapshot
        after_snap = snapshot_tables(tables)
        context["after"] = after_snap
        
        # put message, alert_class, and error into context
        context["message"] = message
        context["alert_class"] = alert_class
        context["error"] = error

    # If no POST action, ensure "after" has a default (same as before)
    if not context.get("after"):
        context["after"] = context["before"]

    return context