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
    try:
        available_pets = run_query("SELECT * FROM AvailablePets", fetch=True)
        adoption_summary = run_query("SELECT * FROM AdoptionSummary", fetch=True)
        shelters = run_query("SELECT shelter_id, name, location, contact FROM Shelter", fetch=True)
        pet_types = run_query("SELECT type_id, species, breed, life_span FROM PetType", fetch=True)
        popular_pets = run_query(nested_sql, fetch=True) # Fetch results from the new query

    except Exception as e:
        print(f"Database Error fetching view data: {e}")
        available_pets = []
        adoption_summary = []
        shelters = []
        pet_types = []
        popular_pets = []
    
    return {
        "available_pets": available_pets,
        "adoption_summary": adoption_summary,
        "shelters": shelters,
        "pet_types": pet_types,
        "popular_pets": popular_pets, # Include the new data set
        "error_message": None
    }