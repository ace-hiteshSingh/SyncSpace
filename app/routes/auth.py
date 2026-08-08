from datetime import datetime

from app.services.dashboard_service import DashboardService

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

from app.services.auth_service import (
    register_user,
    login_user_service,
)

auth = Blueprint(
    "auth",
    __name__,
)


# ===========================
# Register
# ===========================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validate empty fields
        if not username or not email or not password or not confirm_password:
            flash("Please fill all fields.", "error")
            return redirect(url_for("auth.register"))

        # Validate passwords
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        # Register user
        success, message = register_user(
            username,
            email,
            password,
        )

        if success:
            flash(message, "success")
            return redirect(url_for("auth.login"))

        flash(message, "error")
        return redirect(url_for("auth.register"))

    return render_template("auth/register.html")


# ===========================
# Login
# ===========================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = login_user_service(email, password)

        if user:

            login_user(user)

            flash(
                f"Welcome back, {user.username}!",
                "success",
            )

            return redirect(url_for("dashboard.dashboard_home"))

        flash("Invalid email or password.", "error")

        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")





# ===========================
# Logout
# ===========================

@auth.route("/logout")
@login_required
def logout():

    if current_user.is_authenticated:
        current_user.is_online = False
        current_user.last_seen = datetime.utcnow()
        from app.extensions import db
        db.session.commit()

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("auth.login"))
