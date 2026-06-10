from pydantic import BaseModel
from typing import Dict, List, Any
from app.modules.users.schemas import UserRead

class DashboardMetrics(BaseModel):
    users: int
    verified_users: int
    documents_total: int
    draft_documents: int
    pending_documents: int
    partially_signed_documents: int
    completed_documents: int
    rejected_documents: int
    expired_documents: int
    canceled_documents: int

class JobInfo(BaseModel):
    id: str
    next_run: str | None
    last_run: str | None

class SchedulerStatus(BaseModel):
    scheduler_running: bool
    jobs: List[JobInfo]

class NotificationMetrics(BaseModel):
    total_sent: int
    total_failed: int
    # recent_failures: List[Dict[str, Any]] # simplified for V1

class HealthDetails(BaseModel):
    database: bool
    storage: bool
    scheduler: bool
