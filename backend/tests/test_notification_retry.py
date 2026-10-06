from unittest.mock import AsyncMock

import pytest

from app.common.enums import NotificationStatus, NotificationType
from app.modules.notifications.models import Notification
from app.modules.notifications.service import NotificationService


@pytest.mark.asyncio
async def test_retry_failed_notifications_redelivers_and_commits():
    service = NotificationService.__new__(NotificationService)
    service.repo = type("Repo", (), {})()
    service.session = type("Session", (), {"commit": AsyncMock()})()
    service.provider = type("Provider", (), {"send_email": AsyncMock(return_value=True)})()

    failed_notification = Notification(
        id="11111111-1111-4111-8111-111111111111",
        recipient_email="owner@example.com",
        subject="Retry me",
        body="Body",
        type=NotificationType.INVITATION,
        status=NotificationStatus.FAILED,
    )
    service.repo.get_by_status = AsyncMock(return_value=[failed_notification])
    service.repo.update_status = AsyncMock()

    count = await service.retry_failed_notifications()

    assert count == 1
    service.provider.send_email.assert_awaited_once_with(
        "owner@example.com",
        "Retry me",
        "Body",
    )
    service.repo.update_status.assert_awaited_once_with(failed_notification.id, NotificationStatus.SENT)
    service.session.commit.assert_awaited_once()
