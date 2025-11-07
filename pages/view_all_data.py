from utils.db import run_query

def handle_view_all_data(request):
    try:
        available_pets = run_query("SELECT * FROM AvailablePets", fetch=True)
        adoption_summary = run_query("SELECT * FROM AdoptionSummary", fetch=True)
        shelters = run_query("SELECT shelter_id, name, location, contact FROM Shelter", fetch=True)
        pet_types = run_query("SELECT type_id, species, breed, life_span FROM PetType", fetch=True)

    except Exception as e:
        print(f"Database Error fetching view data: {e}")
        available_pets = []
        adoption_summary = []
        shelters = []
        pet_types = []
    
    return {
        "available_pets": available_pets,
        "adoption_summary": adoption_summary,
        "shelters": shelters,
        "pet_types": pet_types,
        "error_message": None
    }