from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import DashboardMetrics, SchedulerStatus, JobInfo, NotificationMetrics
from app.common.enums import DocumentStatus, NotificationStatus
from app.jobs.scheduler import scheduler

class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AdminRepository(session)

    async def get_dashboard_metrics(self) -> DashboardMetrics:
        return DashboardMetrics(
            users=await self.repo.count_users(),
            verified_users=await self.repo.count_users(verified_only=True),
            documents_total=await self.repo.count_documents(),
            draft_documents=await self.repo.count_documents(DocumentStatus.DRAFT),
            pending_documents=await self.repo.count_documents(DocumentStatus.PENDING),
            partially_signed_documents=await self.repo.count_documents(DocumentStatus.PARTIALLY_SIGNED),
            completed_documents=await self.repo.count_documents(DocumentStatus.COMPLETED),
            rejected_documents=await self.repo.count_documents(DocumentStatus.REJECTED),
            expired_documents=await self.repo.count_documents(DocumentStatus.EXPIRED),
            canceled_documents=await self.repo.count_documents(DocumentStatus.CANCELED)
        )

    def get_scheduler_status(self) -> SchedulerStatus:
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append(JobInfo(
                id=job.id,
                next_run=str(job.next_run_time) if job.next_run_time else None,
                last_run=None # APScheduler doesn't store this easily without a job store
            ))

        return SchedulerStatus(
            scheduler_running=scheduler.running,
            jobs=jobs
        )

    async def get_notification_health(self) -> NotificationMetrics:
        return NotificationMetrics(
            total_sent=await self.repo.count_notifications(NotificationStatus.SENT),
            total_failed=await self.repo.count_notifications(NotificationStatus.FAILED)
        )
