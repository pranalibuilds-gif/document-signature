import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, require_admin
from app.modules.admin.service import AdminService
from app.modules.admin.schemas import DashboardMetrics, SchedulerStatus, NotificationMetrics, HealthDetails
from app.modules.users.schemas import UserRead
from app.modules.users.repository import UserRepository
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditLogRead

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _admin: any = Depends(require_admin)
):
    service = AdminService(db)
    return await service.get_dashboard_metrics()

@router.get("/jobs", response_model=SchedulerStatus)
async def get_jobs(
    db: AsyncSession = Depends(get_db),
    _admin: any = Depends(require_admin)
):
    service = AdminService(db)
    return service.get_scheduler_status()

@router.get("/notifications", response_model=NotificationMetrics)
async def get_notification_metrics(
    db: AsyncSession = Depends(get_db),
    _admin: any = Depends(require_admin)
):
    service = AdminService(db)
    return await service.get_notification_health()

@router.get("/audit", response_model=List[AuditLogRead])
async def search_audit_logs(
    user_id: uuid.UUID | None = None,
    document_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _admin: any = Depends(require_admin)
):
    repo = AuditRepository(db)
    if document_id:
        return await repo.list_by_document(document_id, skip, limit)
    if user_id:
        return await repo.list_by_user(user_id, skip, limit)

    # Generic list if no filter
    from sqlalchemy import select
    from app.modules.audit.models import AuditLog
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit))
    return list(result.scalars().all())

@router.get("/users", response_model=List[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _admin: any = Depends(require_admin)
):
    repo = UserRepository(db)
    return await repo.list(skip, limit)

@router.get("/health-details", response_model=HealthDetails)
async def get_health_details(
    db: AsyncSession = Depends(get_db),
    _admin: any = Depends(require_admin)
):
    from sqlalchemy import text
    from app.core.config import settings
    from app.jobs.scheduler import scheduler
    import os

    db_alive = False
    try:
        await db.execute(text("SELECT 1"))
        db_alive = True
    except:
        pass

    storage_ok = os.path.exists(settings.STORAGE_BASE_PATH)

    return HealthDetails(
        database=db_alive,
        storage=storage_ok,
        scheduler=scheduler.running
    )
