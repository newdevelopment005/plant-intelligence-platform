
from app.core.celery import celery_app
from app.database import async_session_factory
from app.modules.auth.infrastructure.password_reset_repository import PasswordResetRepository
from app.modules.auth.infrastructure.token_repository import TokenRepository


@celery_app.task(name="app.modules.auth.tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    import asyncio

    async def _cleanup():
        async with async_session_factory() as db:
            token_repo = TokenRepository(db)
            reset_repo = PasswordResetRepository(db)

            revoked = await token_repo.cleanup_expired_tokens()
            cleaned = await reset_repo.cleanup_expired()

            await db.commit()

            return {"revoked_tokens": revoked, "cleaned_resets": cleaned}

    return asyncio.run(_cleanup())
