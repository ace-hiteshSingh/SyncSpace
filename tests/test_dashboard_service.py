from types import SimpleNamespace

from app.services.dashboard_service import DashboardService


def test_dashboard_service_exposes_tasks_and_settings():
    user = SimpleNamespace(
        tasks_json='[{"id": "task-1", "title": "Ship MVP", "done": false}]',
        settings_json='{"theme": "dark", "notifications_enabled": true, "compact_mode": false}',
    )

    dashboard = DashboardService.get_dashboard(user)

    assert dashboard["task_count"] == 1
    assert dashboard["settings"]["theme"] == "dark"
    assert dashboard["settings"]["notifications_enabled"] is True


def test_dashboard_service_can_create_task_payloads():
    user = SimpleNamespace(tasks_json="[]", settings_json="{}")

    task = DashboardService.create_task(user, "Write release notes", "Share summary")

    assert task["title"] == "Write release notes"
    assert task["done"] is False
    assert task["priority"] == "medium"
