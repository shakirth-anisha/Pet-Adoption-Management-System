from flask import Flask, render_template, redirect, url_for
from utils.db import run_query, run_procedure

app = Flask(__name__)

nav_options = {
    "Dashboard": "dashboard",
    "View Pets": "view_pets",
    "Add Adoption Application": "add_application",
    "Manage Applications": "manage_applications",
    "Register Pet": "register_pet",
    "Manage Pets": "manage_pets",
    "Analytics": "analytics",
    "View All Data": "view_all_data",
    "Test Functions": "test_functions"
}

@app.route("/")
def home():
    return redirect(url_for("render_page", page_name="dashboard"))

@app.route("/page/<page_name>")
def render_page(page_name):
    if page_name not in nav_options.values():
        return "Page not found", 404

    # Prepare chart data only for dashboard
    charts = {}
    if page_name == "dashboard":
        # Total pets by species
        pets_data = run_query("SELECT species, COUNT(*) AS count FROM PetType GROUP BY species;", fetch=True)
        charts['pets_data'] = {
            'labels': [row['species'] for row in pets_data],
            'values': [row['count'] for row in pets_data]
        }

        # Adoption applications status
        apps_data = run_query("SELECT status, COUNT(*) AS count FROM AdoptionApplication GROUP BY status;", fetch=True)
        charts['applications_data'] = {
            'labels': [row['status'] for row in apps_data],
            'values': [row['count'] for row in apps_data]
        }

        # Users by role
        users_data = run_query("SELECT role, COUNT(*) AS count FROM User GROUP BY role;", fetch=True)
        charts['users_data'] = {
            'labels': [row['role'] for row in users_data],
            'values': [row['count'] for row in users_data]
        }

        # Pets per shelter
        shelters_data = run_query("""
            SELECT s.name, COUNT(p.pet_id) AS count
            FROM Shelter s
            LEFT JOIN Pet p ON s.shelter_id = p.shelter_id
            GROUP BY s.shelter_id;
        """, fetch=True)
        charts['shelters_data'] = {
            'labels': [row['name'] for row in shelters_data],
            'values': [row['count'] for row in shelters_data]
        }

    return render_template(
        f"{page_name}.html",
        nav_options=nav_options,
        current_page=page_name,
        **charts  # pass chart data if dashboard
    )

if __name__ == "__main__":
    app.run(debug=True)
