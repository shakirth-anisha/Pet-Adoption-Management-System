from utils.db import run_query

def handle_register_pet(request):
    message = None
    alert_class = "info"

    # Fetch dropdown data
    # No changes here
    pet_types = run_query("SELECT type_id, species, breed FROM PetType ORDER BY species, breed", fetch=True)
    shelters = run_query("SELECT shelter_id, name FROM Shelter ORDER BY name", fetch=True)

    # Handle form submission
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        type_id_form = request.form.get("type_id")   
        new_species = request.form.get("new_species") 
        shelter_id = request.form.get("shelter_id")
        
        # --- Validation & Type Handling ---
        
        if not all([name, age, gender, shelter_id, type_id_form]):
            message = "Please fill in all required fields."
            alert_class = "danger"
            return {
                "pet_types": pet_types, "shelters": shelters, 
                "message": message, "alert_class": alert_class
            }
        
        final_type_id = None
        
        if type_id_form == "other":
            # 1. Handle 'Other' species: insert new type first
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
                
                # --- FIX APPLIED: Removed 'commit=True' ---
                # Execute INSERT. Must rely on run_query() committing internally.
                run_query(insert_type_query, (species, breed)) # Removed 'commit=True'
                
                # Execute SELECT to retrieve the type_id of the newly inserted row
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
            # 2. Use the existing type_id selected from the dropdown
            final_type_id = type_id_form
            
        # --- Pet Registration (Final Step) ---
        
        try:
            query = """
                INSERT INTO Pet (name, age, gender, status, type_id, shelter_id)
                VALUES (%s, %s, %s, 'Available', %s, %s)
            """
            age_int = int(age) 
            
            # --- FIX APPLIED: Removed 'commit=True' ---
            run_query(query, (name, age_int, gender, final_type_id, shelter_id)) # Removed 'commit=True'
            message = f"Pet '{name}' has been successfully registered!"
            alert_class = "success"
            
            # Re-fetch pet types to include the newly added type 
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