import structlog
import os
import logging
from structlog.processors import CallsiteParameter

lvl = os.environ.get('LOG_LEVEL', 'INFO')

structlog.configure(
    wrapper_class = structlog.make_filtering_bound_logger( logging.getLevelNamesMapping()[lvl] ),
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
