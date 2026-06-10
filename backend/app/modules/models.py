# Import all models here for Alembic to discover them
from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.modules.audit.models import AuditLog
from app.modules.notifications.models import Notification

# This list will grow as we add more modules
__all__ = ["User", "RefreshToken", "AuditLog", "Notification"]
