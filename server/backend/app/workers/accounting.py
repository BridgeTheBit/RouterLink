import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import SessionLocal
from app.models.session import Session as VPNSession
from app.models.user import User
from app.models.audit import AuditLog

logger = logging.getLogger("routerlink.accounting")


class AccountingWorker:
    def __init__(self, interval_seconds: int = 10):
        self._interval = interval_seconds
        self._running = False
        self._task: asyncio.Task = None

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("RouterLink Accounting & Quota Worker started.")

    def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            logger.info("RouterLink Accounting & Quota Worker stopped.")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                self.enforce_quotas_and_expirations()
            except Exception as e:
                logger.error(f"Error in quota enforcement loop: {e}", exc_info=True)
            await asyncio.sleep(self._interval)

    def enforce_quotas_and_expirations(self) -> int:
        """Enforces limits on all active sessions. Returns count of terminated sessions."""
        db: Session = SessionLocal()
        terminated_count = 0
        try:
            active_sessions = db.query(VPNSession).filter(VPNSession.is_active == True).all()
            now = datetime.now(timezone.utc)

            for session in active_sessions:
                user = session.user
                should_terminate = False
                reason = ""

                if not user.is_active:
                    should_terminate = True
                    reason = "USER_DISABLED"
                elif user.is_expired:
                    should_terminate = True
                    reason = "SUBSCRIPTION_EXPIRED"
                elif user.is_quota_depleted:
                    should_terminate = True
                    reason = "QUOTA_EXHAUSTED"

                if should_terminate:
                    session.is_active = False
                    session.disconnected_at = now
                    terminated_count += 1

                    # Log to audit trail
                    audit = AuditLog(
                        actor_type="system",
                        actor_id="accounting_worker",
                        action=f"SESSION_TERMINATED_{reason}",
                        target_entity=f"user:{user.username},session:{session.id}",
                        ip_address=session.client_ip,
                        metadata_json=f'{{"reason": "{reason}", "used_bytes": {user.used_traffic_bytes}, "limit_bytes": {user.traffic_limit_bytes}}}',
                        created_at=now
                    )
                    db.add(audit)
                    logger.warning(
                        f"Killed session {session.id} for user '{user.username}'. Reason: {reason}"
                    )

            if terminated_count > 0:
                db.commit()
            return terminated_count
        finally:
            db.close()


accounting_worker = AccountingWorker(interval_seconds=settings.ACCOUNTING_INTERVAL_SECONDS)

