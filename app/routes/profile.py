from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from app.services.dashboard_service import DashboardService
from app.services.profile_service import ProfileService

profile = Blueprint(
    "profile",
    __name__,
    url_prefix="/profile"
)


@profile.route("/")
@login_required
def view_profile():

    completion = DashboardService.profile_completion(current_user)

    return render_template(
        "profile/profile.html",
        user=current_user,
        profile_completion=completion
    )


@profile.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        ProfileService.update_profile(
            current_user,
            request.form
        )

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("profile.view_profile")
        )

    return render_template(
        "profile/edit_profile.html",
        user=current_user
    )

@profile.route("/avatar", methods=["POST"])
@login_required
def upload_avatar():

    file = request.files.get("avatar")

    success = ProfileService.update_avatar(
        current_user,
        file
    )

    if success:

        flash(
            "Avatar updated successfully!",
            "success"
        )

    else:

        flash(
            "Please upload a valid image.",
            "error"
        )

    return redirect(
        url_for("profile.view_profile")
    )