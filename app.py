from flask import Flask, render_template, redirect, url_for, request
from pages import (
    dashboard, add_user, manage_pets, view_pets,
    register_pet, add_application, manage_applications, 
    manage_payments, view_all_data, test_procedural_extensions
)

app = Flask(__name__)

nav_options = {
    "Dashboard": "dashboard",
    "Add User": "add_user",
    "Register Pet": "register_pet",
    "Add Adoption Application": "add_application",
    "View Pets": "view_pets",
    "Manage Pets": "manage_pets",
    "Manage Applications": "manage_applications",
    "Manage Payements": "manage_payments",
    "View All Data": "view_all_data",
    "Test Procedural Extensions": "test_procedural_extensions"
}

# Map page names to (handler_function, template_name)
page_registry = {
    "dashboard": (dashboard.get_dashboard_data, "dashboard.html"),
    "add_user": (add_user.handle_add_user, "add_user.html"),
    "view_pets": (view_pets.handle_view_pets, "view_pets.html"),
    "add_application": (add_application.get_add_application_data, "add_application.html"),
    "manage_applications": (manage_applications.handle_manage_applications, "manage_applications.html"),
    "manage_payments": (manage_payments.handle_manage_payments, "manage_payments.html"),
    "register_pet": (register_pet.handle_register_pet, "register_pet.html"),
    "manage_pets": (manage_pets.handle_manage_pets, "manage_pets.html"),
    "view_all_data": (view_all_data.handle_view_all_data, "view_all_data.html"),
    "test_procedural_extensions": (test_procedural_extensions.handle_test_procedural_extensions, "test_procedural_extensions.html")
}


@app.route("/")
def home():
    return redirect(url_for("render_page", page_name="dashboard"))


@app.route("/page/<page_name>", methods=["GET", "POST"])
def render_page(page_name):
    context = {"nav_options": nav_options, "current_page": page_name}

    if page_name in page_registry:
        handler, template_name = page_registry[page_name]
        try:
            data = handler(request)
        except TypeError:
            data = handler()
        context.update(data)
        return render_template(template_name, **context)

    elif page_name in nav_options.values():
        context["message"] = f"Page '{page_name}' is not implemented yet."
        return render_template("placeholder.html", **context)

    return f"Page '{page_name}' does not exist.", 404


if __name__ == "__main__":
    app.run(debug=True)
