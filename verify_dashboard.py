from app import create_app
from app.models.user import User
from app.services.dashboard_service import DashboardService

app = create_app()
with app.app_context():
    user = User.query.first()
    if user is None:
        print('NO_USER')
    else:
        task = DashboardService.create_task(user, 'Verify dashboard flow', 'Automated smoke test')
        settings = DashboardService.save_settings(user, {'theme': 'dark', 'notifications_enabled': True, 'compact_mode': False})
        dashboard = DashboardService.get_dashboard(user)
        print('TASK_CREATED', bool(task))
        print('TASK_COUNT', dashboard['task_count'])
        print('SETTINGS_THEME', dashboard['settings']['theme'])
