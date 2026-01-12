from flask import Blueprint, request, session, redirect, url_for, render_template

auth_routes = Blueprint("auth", __name__)

# Hardcoded demo users (enough for shortlisting)
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "editor": {"password": "editor123", "role": "editor"},
    "viewer": {"password": "viewer123", "role": "viewer"},
}

@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = USERS.get(username)
        if user and user["password"] == password:
            session["user"] = username
            session["role"] = user["role"]
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@auth_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
