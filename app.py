from flask import Flask, render_template, redirect, url_for
from pages import dashboard

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
    context = {"nav_options": nav_options, "current_page": page_name}

    if page_name == "dashboard":
        context.update(dashboard.get_dashboard_data())
        return render_template("dashboard.html", **context)

    elif page_name in nav_options.values():
        # Page exists but not yet implemented
        context["message"] = f"Page '{page_name}' is not implemented yet."
        return render_template("placeholder.html", **context)

    else:
        # Page does not exist at all
        return f"Page '{page_name}' does not exist.", 404

if __name__ == "__main__":
    app.run(debug=True)
