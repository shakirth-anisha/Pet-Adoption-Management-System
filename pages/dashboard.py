from utils.db import run_query

def get_dashboard_data():
    # Total Pets by Type
    pets_query = """
        SELECT pt.species AS label, COUNT(p.pet_id) AS value
        FROM Pet p
        JOIN PetType pt ON p.type_id = pt.type_id
        GROUP BY pt.species
    """
    pets = run_query(pets_query, fetch=True)
    pets_data = {
        "labels": [row['label'] for row in pets],
        "values": [row['value'] for row in pets]
    }

    # Adoption Status
    adoption_query = """
        SELECT status AS label, COUNT(adopt_app_id) AS value
        FROM AdoptionApplication
        GROUP BY status
    """
    adoption = run_query(adoption_query, fetch=True)
    applications_data = {
        "labels": [row['label'] for row in adoption],
        "values": [row['value'] for row in adoption]
    }

    # Users by Role
    users_query = """
        SELECT role AS label, COUNT(user_id) AS value
        FROM User
        GROUP BY role
    """
    users = run_query(users_query, fetch=True)
    users_data = {
        "labels": [row['label'] for row in users],
        "values": [row['value'] for row in users]
    }

    # Pets per Shelter
    shelter_query = """
        SELECT s.name AS label, COUNT(p.pet_id) AS value
        FROM Pet p
        JOIN Shelter s ON p.shelter_id = s.shelter_id
        GROUP BY s.name
    """
    shelters = run_query(shelter_query, fetch=True)
    shelters_data = {
        "labels": [row['label'] for row in shelters],
        "values": [row['value'] for row in shelters]
    }

    # Top 5 Adopters (by approved adoptions)
    adopters_query = """
        SELECT u.name AS label, COUNT(a.adopt_app_id) AS value
        FROM AdoptionApplication a
        JOIN User u ON a.user_id = u.user_id
        WHERE a.status = 'Approved'
        GROUP BY u.user_id
        ORDER BY value DESC
        LIMIT 5
    """
    adopters = run_query(adopters_query, fetch=True)
    adopters_data = {
        "labels": [row['label'] for row in adopters],
        "values": [row['value'] for row in adopters]
    }

    # Payments by Method
    payments_query = """
        SELECT method AS label, SUM(amount) AS value
        FROM Payment
        WHERE status = 'Completed'
        GROUP BY method
    """
    payments = run_query(payments_query, fetch=True)
    payments_data = {
        "labels": [row['label'] for row in payments],
        "values": [float(row['value']) for row in payments]
    }

    return {
        "pets_data": pets_data,
        "applications_data": applications_data,
        "users_data": users_data,
        "shelters_data": shelters_data,
        "payments_data": payments_data,
        "adopters_data": adopters_data
    }
