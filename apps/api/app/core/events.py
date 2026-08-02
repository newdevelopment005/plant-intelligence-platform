import structlog

logger = structlog.get_logger()


async def startup_event():
    logger.info("Application startup events triggered")


async def shutdown_event():
    logger.info("Application shutdown events triggered")
