import structlog
from structlog.processors import CallsiteParameter

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.CallsiteParameterAdder(
            [
                CallsiteParameter.FILENAME,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO
            ],
        ),
        structlog.dev.ConsoleRenderer()
        # structlog.processors.JSONRenderer()
    ]
)

logging = structlog.get_logger()
