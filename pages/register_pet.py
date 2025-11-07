from utils.db import run_query

def handle_register_pet(request):
    message = None
    alert_class = "info"

    pet_types = run_query("SELECT type_id, species, breed FROM PetType ORDER BY species, breed", fetch=True)
    shelters = run_query("SELECT shelter_id, name FROM Shelter ORDER BY name", fetch=True)

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        type_id_form = request.form.get("type_id")  
        new_species = request.form.get("new_species") 
        shelter_id = request.form.get("shelter_id")
        reason = request.form.get("reason", "Pet registered into the shelter.")
        status = request.form.get("status", "Available")
        
        if not all([name, age, gender, shelter_id, type_id_form]):
            message = "Please fill in all required fields."
            alert_class = "danger"
            return {
                "pet_types": pet_types, "shelters": shelters, 
                "message": message, "alert_class": alert_class
            }
        
        final_type_id = None
        
        if type_id_form == "other":
            if not new_species or new_species.strip() == "":
                message = "You selected 'Other' for Species/Type. Please provide the new species name."
                alert_class = "warning"
                return {
                    "pet_types": pet_types, "shelters": shelters, 
                    "message": message, "alert_class": alert_class
                }
            
            try:
                parts = [p.strip() for p in new_species.split('-', 1)]
                species = parts[0]
                breed = parts[1] if len(parts) > 1 else 'N/A'
                
                insert_type_query = "INSERT INTO PetType (species, breed) VALUES (%s, %s)"
                run_query(insert_type_query, (species, breed)) 
                
                newly_inserted_type = run_query(
                    "SELECT type_id FROM PetType WHERE species = %s AND breed = %s ORDER BY type_id DESC LIMIT 1",
                    (species, breed),
                    fetch=True
                )
                
                if newly_inserted_type and newly_inserted_type[0]:
                    final_type_id = newly_inserted_type[0]['type_id']
                else:
                    raise Exception("Failed to retrieve ID for new species after insertion.")
                    
            except Exception as e:
                message = f"Error creating new species type: {str(e)}"
                alert_class = "danger"
                return {
                    "pet_types": pet_types, "shelters": shelters, 
                    "message": message, "alert_class": alert_class
                }
        
        else:
            final_type_id = type_id_form 
        
        # --- Pet Registration
        
        try:
            age_int = int(age)
            final_type_id_int = int(final_type_id)
            shelter_id_int = int(shelter_id)

            query = """
                CALL RegisterPet(%s, %s, %s, %s, %s, %s, %s);
            """
            
            params = (
                name, 
                gender, 
                age_int, 
                reason, 
                status, 
                shelter_id_int, 
                final_type_id_int
            )
            
            run_query(query, params) 
            message = f"Pet '{name}' has been successfully registered!"
            alert_class = "success"
            
            pet_types = run_query("SELECT type_id, species, breed FROM PetType ORDER BY species, breed", fetch=True)
            
        except Exception as e:
            message = f"Error registering pet: {str(e)}"
            alert_class = "danger"

    return {
        "pet_types": pet_types,
        "shelters": shelters,
        "message": message,
        "alert_class": alert_class
    }