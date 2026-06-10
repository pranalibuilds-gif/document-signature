import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def start_scheduler():
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled in settings.")
        return

    from app.jobs.expiration_jobs import expire_documents_job
    from app.jobs.reminder_jobs import send_signer_reminders_job
    from app.jobs.cleanup_jobs import cleanup_tokens_job

    # Job: Expire documents (Every hour)
    scheduler.add_job(
        expire_documents_job,
        "interval",
        hours=1,
        id="expire_documents",
        replace_existing=True
    )

    # Job: Send reminders (Once a day)
    scheduler.add_job(
        send_signer_reminders_job,
        "cron",
        hour=9, # 9 AM
        id="send_reminders",
        replace_existing=True
    )

    # Job: Cleanup tokens (Once a day)
    scheduler.add_job(
        cleanup_tokens_job,
        "cron",
        hour=2, # 2 AM
        id="cleanup_tokens",
        replace_existing=True
    )

    scheduler.start()
    logger.info("APScheduler started successfully.")

def stop_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler shut down.")
