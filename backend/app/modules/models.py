# Import all models here for Alembic to discover them
from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.modules.audit.models import AuditLog
from app.modules.notifications.models import Notification
from app.modules.documents.models import Document, DocumentFile
from app.modules.signers.models import DocumentSigner
from app.modules.fields.models import SignatureField

# This list will grow as we add more modules
__all__ = ["User", "RefreshToken", "AuditLog", "Notification", "Document", "DocumentFile", "DocumentSigner", "SignatureField"]
