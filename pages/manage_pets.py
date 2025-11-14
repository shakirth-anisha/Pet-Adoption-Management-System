from utils.db import run_query

def handle_manage_pets(request):
    if request.method == "POST":
        pet_id = request.form.get("pet_id")
        action = request.form.get("action")

        if action == "delete":
            run_query("DELETE FROM Pet WHERE pet_id=%s", (pet_id,))
        elif action == "update_status":
            new_status = request.form.get("status")
            current = run_query("SELECT status FROM Pet WHERE pet_id=%s", (pet_id,), fetch=True)
            if current and current[0]["status"] != "Adopted":
                run_query("UPDATE Pet SET status=%s WHERE pet_id=%s", (new_status, pet_id))

    filter_status = request.args.get('status')
    if not filter_status or filter_status == 'All':
        filter_status = None

    query = """
        SELECT p.pet_id, p.name, p.age, p.gender, p.status, pt.species, pt.breed, s.name AS shelter_name
        FROM Pet p
        JOIN PetType pt ON p.type_id = pt.type_id
        JOIN Shelter s ON p.shelter_id = s.shelter_id
    """
    params = []

    if filter_status:
        query += " WHERE p.status = %s"
        params.append(filter_status)

    query += " ORDER BY p.pet_id"

    pets = run_query(query, tuple(params), fetch=True)

    return {
        "pets": pets,
        "filter_status": filter_status
    }
