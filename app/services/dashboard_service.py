import json
from datetime import datetime

from app.extensions import db
from app.models.friend import Friend
from app.models.message import Message


class DashboardService:

    @staticmethod
    def _read_json_field(user, field_name, default):
        value = getattr(user, field_name, None) if hasattr(user, field_name) else None
        if isinstance(value, (dict, list)):
            return value
        if not value:
            return default
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _write_json_field(user, field_name, value):
        setattr(user, field_name, json.dumps(value, ensure_ascii=False))
        db.session.commit()
        return value

    @staticmethod
    def get_dashboard(user):
        tasks = DashboardService.get_tasks(user)
        settings = DashboardService.get_settings(user)
        workspaces = DashboardService.get_workspaces(user)
        friends_count = Friend.query.filter(
            ((Friend.sender_id == user.id) | (Friend.receiver_id == user.id)) & (Friend.status == "accepted")
        ).count()
        conversation_ids = set()
        for message in Message.query.filter((Message.sender_id == user.id) | (Message.receiver_id == user.id)).all():
            other_user_id = message.receiver_id if message.sender_id == user.id else message.sender_id
            conversation_ids.add(other_user_id)

        data = {
            "friends_count": friends_count,
            "chat_count": len(conversation_ids),
            "workspace_count": len(workspaces),
            "task_count": len(tasks),
            "tasks": tasks,
            "workspaces": workspaces,
            "settings": settings,
            "recent_activity": [
                "Welcome to SyncSpace 🎉",
                "Complete your profile",
                "Create your first workspace"
            ]
        }

        return data

    @staticmethod
    def get_tasks(user):
        tasks = DashboardService._read_json_field(user, "tasks_json", [])
        return tasks if isinstance(tasks, list) else []

    @staticmethod
    def get_settings(user):
        settings = DashboardService._read_json_field(user, "settings_json", {})
        return settings if isinstance(settings, dict) else {}

    @staticmethod
    def get_workspaces(user):
        workspaces = DashboardService._read_json_field(user, "workspaces_json", [])
        return workspaces if isinstance(workspaces, list) else []

    @staticmethod
    def create_task(user, title, description="", priority="medium"):
        title = (title or "").strip()
        if not title:
            return None
        tasks = DashboardService.get_tasks(user)
        task = {
            "id": f"task-{int(datetime.utcnow().timestamp() * 1000)}",
            "title": title,
            "description": (description or "").strip(),
            "done": False,
            "priority": (priority or "medium").strip().lower() or "medium",
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        }
        tasks.append(task)
        DashboardService._write_json_field(user, "tasks_json", tasks)
        return task

    @staticmethod
    def toggle_task(user, task_id):
        tasks = DashboardService.get_tasks(user)
        updated = False
        for task in tasks:
            if task.get("id") == task_id:
                task["done"] = not task.get("done", False)
                updated = True
                break
        if updated:
            DashboardService._write_json_field(user, "tasks_json", tasks)
        return updated

    @staticmethod
    def delete_task(user, task_id):
        tasks = DashboardService.get_tasks(user)
        filtered = [task for task in tasks if task.get("id") != task_id]
        DashboardService._write_json_field(user, "tasks_json", filtered)
        return True

    @staticmethod
    def save_settings(user, settings):
        payload = {key: value for key, value in (settings or {}).items() if key in {"theme", "notifications_enabled", "compact_mode"}}
        payload.setdefault("theme", "dark")
        payload.setdefault("notifications_enabled", True)
        payload.setdefault("compact_mode", False)
        return DashboardService._write_json_field(user, "settings_json", payload)

    @staticmethod
    def create_workspace(user, name, description="", category="Personal"):
        name = (name or "").strip()
        if not name:
            return None
        workspaces = DashboardService.get_workspaces(user)
        workspace = {
            "id": f"workspace-{int(datetime.utcnow().timestamp() * 1000)}",
            "name": name,
            "description": (description or "").strip(),
            "category": (category or "Personal").strip() or "Personal",
            "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        }
        workspaces.append(workspace)
        DashboardService._write_json_field(user, "workspaces_json", workspaces)
        return workspace

    @staticmethod
    def delete_workspace(user, workspace_id):
        workspaces = DashboardService.get_workspaces(user)
        filtered = [workspace for workspace in workspaces if workspace.get("id") != workspace_id]
        DashboardService._write_json_field(user, "workspaces_json", filtered)
        return True

    @staticmethod
    def profile_completion(user):

        score = 0

        if user.username:
            score += 20

        if user.email:
            score += 20

        if user.bio:
            score += 20

        if user.location:
            score += 20

        if user.website:
            score += 20

        if getattr(user, "avatar", None) and user.avatar != "default-avatar.png":
            score += 20

        return score