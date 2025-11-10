from flask import Flask, render_template, redirect, url_for, request
from pages import dashboard, add_user, manage_pets, view_pets, register_pet, add_application, manage_applications, view_all_data

app = Flask(__name__)

nav_options = {
    "Dashboard": "dashboard",
    "Add User": "add_user",
    "View Pets": "view_pets",
    "Add Adoption Application": "add_application",
    "Manage Applications": "manage_applications",
    "Register Pet": "register_pet",
    "Manage Pets": "manage_pets",
    "View All Data": "view_all_data",
    "Test Procedural Extensions": "test_procedural_extensions"
}


@app.route("/")
def home():
    return redirect(url_for("render_page", page_name="dashboard"))


@app.route("/page/<page_name>", methods=["GET", "POST"])
def render_page(page_name):
    context = {"nav_options": nav_options, "current_page": page_name}

    if page_name == "dashboard":
        context.update(dashboard.get_dashboard_data())
        return render_template("dashboard.html", **context)
    
    elif page_name == "add_user":
        context.update(add_user.handle_add_user(request))
        return render_template("add_user.html", **context)
    
    elif page_name == "view_pets":
        context.update(view_pets.get_view_pets_data())
        return render_template("view_pets.html", **context)
    
    elif page_name == "add_application":
        context.update(add_application.get_add_application_data(request))
        return render_template("add_application.html", **context)
    
    elif page_name == "manage_applications":
        context.update(manage_applications.get_manage_applications_data())
        return render_template("manage_applications.html", **context)   
    
    elif page_name == "register_pet":
        context.update(register_pet.handle_register_pet(request))
        return render_template("register_pet.html", **context)

    elif page_name == "manage_pets":
        context.update(manage_pets.handle_manage_pets(request))
        return render_template("manage_pets.html", **context)
    
    elif page_name == "view_all_data":
        context.update(view_all_data.handle_view_all_data(request))
        return render_template("view_all_data.html", **context)

    elif page_name in nav_options.values():
        context["message"] = f"Page '{page_name}' is not implemented yet."
        return render_template("placeholder.html", **context)

    else:
        return f"Page '{page_name}' does not exist.", 404


if __name__ == "__main__":
    app.run(debug=True)