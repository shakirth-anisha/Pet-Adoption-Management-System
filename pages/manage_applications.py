from utils.db import run_query

def get_manage_applications_data():
    """Fetch all adoption applications with related info."""
    query = """
        SELECT a.adopt_app_id, a.status, a.reason, u.name AS adopter_name,
               p.name AS pet_name, s.name AS shelter_name, a.date
        FROM AdoptionApplication a
        JOIN User u ON a.user_id = u.user_id
        JOIN Pet p ON a.pet_id = p.pet_id
        JOIN Shelter s ON p.shelter_id = s.shelter_id
        ORDER BY a.adopt_app_id DESC;
    """
    applications = run_query(query, fetch=True)
    return {"applications": applications}
