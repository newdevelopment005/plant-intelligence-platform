from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        user_id: str | None,
        action: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        from sqlalchemy import text

        await self.db.execute(
            text(
                """
                INSERT INTO admin.audit_log (user_id, action, resource_type, resource_id, ip_address, metadata, created_at)
                VALUES (:user_id, :action, :resource_type, :resource_id, :ip_address, :metadata, :created_at)
                """
            ),
            {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "metadata": metadata,
                "created_at": datetime.now(UTC),
            },
        )
        await self.db.flush()
