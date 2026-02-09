import logging
from datetime import datetime

from app.core.config import get_settings
from app.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self, user_id: str = "user_001") -> None:
        self._settings = get_settings()
        self._reminder_service = ReminderService()
        self._user_id = user_id
        self._enabled = self._settings.REMINDER_ENABLE_SCHEDULER
        self._last_trigger_date: str | None = None

    def check_and_run(self) -> None:
        if not self._enabled:
            return

        now = datetime.now(self._settings.reminder_timezone)
        hhmm = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")
        if hhmm != self._settings.REMINDER_TIME:
            return

        if self._last_trigger_date == today:
            return

        result = self._reminder_service.list_tomorrow_reminders(user_id=self._user_id, now=now)
        self._last_trigger_date = today
        logger.info(
            "reminder_scan user_id=%s remind_date=%s target_date=%s total=%s",
            self._user_id,
            result["remind_date"],
            result["target_date"],
            result["total"],
        )


class ReminderSchedulerRunner:
    def __init__(self, scheduler: ReminderScheduler | None = None) -> None:
        self._scheduler = scheduler or ReminderScheduler()
        self._enabled = get_settings().REMINDER_ENABLE_SCHEDULER
        self._task = None
        self._running = False

    async def start(self) -> None:
        import asyncio

        if not self._enabled:
            logger.info("reminder_scheduler_skipped enabled=false")
            return

        if self._running:
            return

        self._running = True
        logger.info("reminder_scheduler_started enabled=true")

        async def loop() -> None:
            while self._running:
                try:
                    self._scheduler.check_and_run()
                except Exception as exc:  # noqa: BLE001
                    logger.exception("reminder_scheduler_error=%s", exc)
                await asyncio.sleep(30)

        self._task = asyncio.create_task(loop())

    async def stop(self) -> None:
        import asyncio

        if not self._running:
            return

        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("reminder_scheduler_stopped")
