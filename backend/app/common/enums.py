"""
Global Enumerations for the application.
Defines valid states, roles, and event types to ensure data consistency.
"""
from enum import Enum

class DocumentStatus(str, Enum):
    """Lifecycle states of a document."""
    DRAFT = "DRAFT" # Initial state, owner can edit fields
    PENDING = "PENDING" # Sent for signing, no fields signed yet
    PARTIALLY_SIGNED = "PARTIALLY_SIGNED" # At least one (but not all) signers signed
    COMPLETED = "COMPLETED" # All signers signed, final PDF generated
    REJECTED = "REJECTED" # At least one signer rejected the document
    EXPIRED = "EXPIRED" # Document was not signed within the deadline
    CANCELED = "CANCELED" # Owner manually canceled the request

class UserRole(str, Enum):
    """Access control levels."""
    USER = "USER"
    ADMIN = "ADMIN"

class SignerStatus(str, Enum):
    """The current state of an individual recipient."""
    PENDING = "PENDING"
    SIGNED = "SIGNED"
    REJECTED = "REJECTED"

class FieldType(str, Enum):
    """Types of data that can be captured on a document."""
    SIGNATURE = "SIGNATURE"
    TEXT = "TEXT"
    DATE = "DATE"

class NotificationType(str, Enum):
    """Categories of automated emails sent by the system."""
    INVITATION = "INVITATION"
    REMINDER = "REMINDER"
    COMPLETION = "COMPLETION"
    REJECTION = "REJECTION"

class NotificationStatus(str, Enum):
    """Delivery status of a notification."""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

class AuditActorType(str, Enum):
    """The source of an action in the audit trail."""
    USER = "USER" # Action performed by a person
    SYSTEM = "SYSTEM" # Action performed by background jobs or automated logic

class AuditEventType(str, Enum):
    """Catalog of all loggable system events."""
    USER_REGISTERED = "USER_REGISTERED"
    USER_LOGIN = "USER_LOGIN"
    DOCUMENT_CREATED = "DOCUMENT_CREATED"
    DOCUMENT_UPDATED = "DOCUMENT_UPDATED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    SIGNER_ADDED = "SIGNER_ADDED"
    SIGNER_REMOVED = "SIGNER_REMOVED"
    FIELD_CREATED = "FIELD_CREATED"
    FIELD_REMOVED = "FIELD_REMOVED"
    INVITATION_SENT = "INVITATION_SENT"
    DOCUMENT_VIEWED = "DOCUMENT_VIEWED"
    FIELD_COMPLETED = "FIELD_COMPLETED"
    DOCUMENT_SIGNED = "DOCUMENT_SIGNED"
    DOCUMENT_REJECTED = "DOCUMENT_REJECTED"
    DOCUMENT_COMPLETED = "DOCUMENT_COMPLETED"
    LINK_EXPIRED = "LINK_EXPIRED"
    FINAL_PDF_GENERATED = "FINAL_PDF_GENERATED"
    EMAIL_VERIFICATION_SENT = "EMAIL_VERIFICATION_SENT"
    EMAIL_VERIFIED = "EMAIL_VERIFIED"
    NOTIFICATION_SENT = "NOTIFICATION_SENT"
    NOTIFICATION_FAILED = "NOTIFICATION_FAILED"
