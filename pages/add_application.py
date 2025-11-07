from utils.db import run_query, run_procedure

def get_add_application_data():
    """Fetch all users and pets to populate dropdowns."""
    users = run_query("SELECT user_id, name FROM User WHERE role='adopter';", fetch=True)
    pets = run_query("SELECT pet_id, name FROM Pet WHERE status='Available';", fetch=True)
    return {"users": users, "pets": pets}

def add_application(user_id, pet_id, reason):
    """Insert a new adoption application."""
    try:
        run_query(
            "INSERT INTO AdoptionApplication (status, reason, pet_id, user_id) VALUES ('Pending', %s, %s, %s);",
            (reason, pet_id, user_id)
        )
        return "Adoption application submitted successfully!"
    except Exception as e:
        return f"Error submitting application: {e}"
