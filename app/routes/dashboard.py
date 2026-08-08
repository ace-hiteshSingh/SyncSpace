from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.dashboard_service import DashboardService
from app.services.profile_service import ProfileService

dashboard = Blueprint(
    "dashboard",
    __name__,
)


@dashboard.route("/dashboard")
@login_required
def dashboard_home():

    dashboard_data = DashboardService.get_dashboard(current_user)

    profile_completion = DashboardService.profile_completion(current_user)

    return render_template(
        "dashboard/dashboard.html",
        user=current_user,
        dashboard=dashboard_data,
        profile_completion=profile_completion,
    )


@dashboard.route("/dashboard/workspaces")
@login_required
def workspaces_page():
    dashboard_data = DashboardService.get_dashboard(current_user)
    profile_completion = DashboardService.profile_completion(current_user)
    return render_template(
        "dashboard/workspaces.html",
        user=current_user,
        dashboard=dashboard_data,
        profile_completion=profile_completion,
    )


@dashboard.route("/dashboard/tasks-page")
@login_required
def tasks_page():
    dashboard_data = DashboardService.get_dashboard(current_user)
    profile_completion = DashboardService.profile_completion(current_user)
    return render_template(
        "dashboard/tasks.html",
        user=current_user,
        dashboard=dashboard_data,
        profile_completion=profile_completion,
    )


@dashboard.route("/dashboard/settings-page")
@login_required
def settings_page():
    dashboard_data = DashboardService.get_dashboard(current_user)
    profile_completion = DashboardService.profile_completion(current_user)
    return render_template(
        "dashboard/settings.html",
        user=current_user,
        dashboard=dashboard_data,
        profile_completion=profile_completion,
    )


@dashboard.route("/dashboard/tasks", methods=["POST"])
@login_required
def create_task():
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    priority = (request.form.get("priority") or "medium").strip().lower() or "medium"

    if title:
        DashboardService.create_task(current_user, title, description, priority)
        flash("Task added successfully.", "success")
    else:
        flash("Please enter a task title.", "error")

    return redirect(url_for("dashboard.dashboard_home"))


@dashboard.route("/dashboard/tasks/<task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    DashboardService.toggle_task(current_user, task_id)
    return redirect(url_for("dashboard.dashboard_home"))


@dashboard.route("/dashboard/tasks/<task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    DashboardService.delete_task(current_user, task_id)
    return redirect(url_for("dashboard.dashboard_home"))


@dashboard.route("/dashboard/workspaces", methods=["POST"])
@login_required
def create_workspace():
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    category = (request.form.get("category") or "Personal").strip() or "Personal"

    if name:
        DashboardService.create_workspace(current_user, name, description, category)
        flash("Workspace created successfully.", "success")
    else:
        flash("Please enter a workspace name.", "error")

    return redirect(url_for("dashboard.dashboard_home"))


@dashboard.route("/dashboard/workspaces/<workspace_id>/delete", methods=["POST"])
@login_required
def delete_workspace(workspace_id):
    DashboardService.delete_workspace(current_user, workspace_id)
    flash("Workspace removed.", "success")
    return redirect(url_for("dashboard.dashboard_home"))


@dashboard.route("/dashboard/settings", methods=["POST"])
@login_required
def update_settings():
    settings = {
        "theme": request.form.get("theme", "dark"),
        "notifications_enabled": request.form.get("notifications_enabled") == "on",
        "compact_mode": request.form.get("compact_mode") == "on",
    }
    DashboardService.save_settings(current_user, settings)
    flash("Settings saved successfully.", "success")
    return redirect(url_for("dashboard.dashboard_home"))


@dashboard.route("/dashboard/avatar", methods=["POST"])
@login_required
def upload_dashboard_avatar():
    success = ProfileService.update_avatar(current_user, request.files.get("avatar"))
    if success:
        flash("Avatar updated successfully.", "success")
    else:
        flash("Please upload a valid image.", "error")
    return redirect(url_for("dashboard.dashboard_home"))
