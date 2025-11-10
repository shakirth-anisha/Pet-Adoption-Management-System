from utils.db import run_query

def handle_view_pets(request):
    """Fetch and display pets with filtering and stats."""
    data = {}
    
    # Get filter parameters
    status_filter = request.args.get("status", "all")
    shelter_filter = request.args.get("shelter", "all")
    pet_id_for_history = request.args.get("history", None)
    
    # Build query with filters
    query = """
        SELECT p.pet_id, p.name AS pet_name, pt.species, pt.breed,
               p.gender, p.age, p.status, p.shelter_id,
               s.name AS shelter_name, s.location
        FROM Pet p
        JOIN PetType pt ON p.type_id = pt.type_id
        JOIN Shelter s ON p.shelter_id = s.shelter_id
        WHERE 1=1
    """
    
    params = []
    
    # Apply status filter
    if status_filter != "all":
        query += " AND p.status = %s"
        params.append(status_filter)
    
    # Apply shelter filter
    if shelter_filter != "all":
        query += " AND p.shelter_id = %s"
        params.append(shelter_filter)
    
    query += " ORDER BY p.created_at DESC;"
    
    pets = run_query(query, tuple(params) if params else None, fetch=True)
    data["pets"] = pets or []
    
    # Fetch all shelters for filter dropdown
    shelters = run_query("SELECT shelter_id, name FROM Shelter ORDER BY name;", fetch=True)
    data["shelters"] = shelters or []
    
    # Get shelter stats using database functions
    shelter_stats = []
    for shelter in shelters or []:
        stats = get_shelter_stats(shelter["shelter_id"], shelter["name"])
        shelter_stats.append(stats)
    
    data["shelter_stats"] = shelter_stats
    data["current_status"] = status_filter
    data["current_shelter"] = shelter_filter
    
    # Get overall stats
    data["total_pets"] = len(pets) if pets else 0
    data["available_count"] = len([p for p in pets if p["status"] == "Available"]) if pets else 0
    data["adopted_count"] = len([p for p in pets if p["status"] == "Adopted"]) if pets else 0
    data["medical_count"] = len([p for p in pets if p["status"] == "Medical Hold"]) if pets else 0
    
    # If history requested, get pet history
    if pet_id_for_history:
        data["pet_history"] = get_pet_history(pet_id_for_history)
        data["history_pet_id"] = pet_id_for_history
        # Get pet name
        pet_info = run_query("SELECT name FROM Pet WHERE pet_id = %s;", (pet_id_for_history,), fetch=True)
        data["history_pet_name"] = pet_info[0]["name"] if pet_info else "Unknown"
    
    return data

def get_shelter_stats(shelter_id, shelter_name):
    """Get statistics for a specific shelter using database functions."""
    stats = {"shelter_id": shelter_id, "shelter_name": shelter_name}
    
    # Use CountAvailablePets function
    result = run_query("SELECT CountAvailablePets(%s) AS available_count;", (shelter_id,), fetch=True)
    stats["available_count"] = result[0]["available_count"] if result else 0
    
    # Use AvgPetAgeInShelter function
    result = run_query("SELECT AvgPetAgeInShelter(%s) AS avg_age;", (shelter_id,), fetch=True)
    stats["avg_age"] = float(result[0]["avg_age"]) if result and result[0]["avg_age"] else 0.0
    
    # Get total pets in shelter
    result = run_query("SELECT COUNT(*) AS total FROM Pet WHERE shelter_id = %s;", (shelter_id,), fetch=True)
    stats["total_pets"] = result[0]["total"] if result else 0
    
    return stats

def get_pet_history(pet_id):
    """Get status change history for a specific pet from PetStatusLog."""
    query = """
        SELECT log_id, old_status, new_status, changed_at
        FROM PetStatusLog
        WHERE pet_id = %s
        ORDER BY changed_at DESC;
    """
    history = run_query(query, (pet_id,), fetch=True)
    return history or []
