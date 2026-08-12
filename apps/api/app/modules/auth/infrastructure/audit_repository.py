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

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: str | None = None,
        action: str | None = None,
    ) -> tuple[list[dict], int]:
        from sqlalchemy import func, select, text

        conditions = []
        params: dict = {}
        if user_id:
            conditions.append("user_id = :user_id")
            params["user_id"] = user_id
        if action:
            conditions.append("action = :action")
            params["action"] = action
        where_sql = f" WHERE {' AND '.join(conditions)}" if conditions else ""

        rows = await self.db.execute(
            text(
                f"""
                SELECT id, user_id, action, resource_type, resource_id, ip_address, metadata, created_at
                FROM admin.audit_log{where_sql}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :skip
                """
            ),
            {**params, "limit": limit, "skip": skip},
        )
        items = [dict(r._mapping) for r in rows]

        total = await self.db.execute(
            text(f"SELECT count(*) FROM admin.audit_log{where_sql}"),
            params,
        )
        count = total.scalar() or 0

        return items, count
