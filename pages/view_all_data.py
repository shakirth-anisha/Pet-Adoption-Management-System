from flask import session
from utils.db import run_query

def handle_view_all_data(request):
    nested_sql = """
        SELECT p.pet_id, p.name, COALESCE(COUNT(a.adopt_app_id), 0) AS app_count
        FROM Pet p
        LEFT JOIN AdoptionApplication a ON p.pet_id = a.pet_id
        GROUP BY p.pet_id, p.name
        HAVING COUNT(a.adopt_app_id) > (
            SELECT AVG(pet_app_counts.app_count) FROM (
                SELECT COUNT(adopt_app_id) AS app_count
                FROM AdoptionApplication
                GROUP BY pet_id
            ) AS pet_app_counts
        )
        ORDER BY app_count DESC;
        """
    worker_mappings = []
    user_role = session.get('user_role')

    try:
        available_pets = run_query("SELECT * FROM AvailablePets", fetch=True)
        adoption_summary = run_query("SELECT * FROM AdoptionSummary", fetch=True)
        shelters = run_query("SELECT shelter_id, name, location, contact FROM Shelter", fetch=True)
        pet_types = run_query("SELECT type_id, species, breed, life_span FROM PetType", fetch=True)
        popular_pets = run_query(nested_sql, fetch=True) # Fetch results from the new query
        if user_role == 'admin':
            worker_mapping_sql = """
                SELECT 
                    u.user_id,
                    u.email,
                    u.name,
                    (
                        SELECT sw_inner.worker_id
                        FROM ShelterWorker sw_inner
                        WHERE sw_inner.user_id = u.user_id
                    ) AS worker_id
                FROM User u
                WHERE EXISTS (
                    SELECT 1 
                    FROM ShelterWorker sw 
                    WHERE sw.user_id = u.user_id
                )
                ORDER BY u.user_id
            """
            worker_mappings = run_query(worker_mapping_sql, fetch=True) or []

    except Exception as e:
        print(f"Database Error fetching view data: {e}")
        available_pets = []
        adoption_summary = []
        shelters = []
        pet_types = []
        popular_pets = []
        worker_mappings = []
    
    return {
        "available_pets": available_pets,
        "adoption_summary": adoption_summary,
        "shelters": shelters,
        "pet_types": pet_types,
        "popular_pets": popular_pets, # Include the new data set
        "worker_mappings": worker_mappings,
        "error_message": None
    }