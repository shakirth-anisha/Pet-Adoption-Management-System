from utils.db import run_query

def get_view_pets_data():
    query = """
        SELECT p.pet_id, p.name AS pet_name, pt.species, pt.breed,
               p.gender, p.age, p.status, s.name AS shelter_name
        FROM Pet p
        JOIN PetType pt ON p.type_id = pt.type_id
        JOIN Shelter s ON p.shelter_id = s.shelter_id
        ORDER BY p.created_at DESC;
    """
    pets = run_query(query, fetch=True)
    return {"pets": pets}
