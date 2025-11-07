# pages/dashboard.py
from utils.db import run_query

def get_dashboard_data():
    """
    Fetch and process data for dashboard charts.
    Returns a dictionary with all chart data.
    """
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

    return {
        "pets_data": pets_data,
        "applications_data": applications_data,
        "users_data": users_data,
        "shelters_data": shelters_data
    }
