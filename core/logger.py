import json
import logging
from datetime import datetime

try:
    # optional: enable proper ANSI handling on Windows
    import colorama
    colorama.init()
    _COLORAMA = True
except Exception:
    _COLORAMA = False


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',
        'INFO': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'CRITICAL': '\033[95m',
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        label = f"{level}:"
        # pad label to a fixed width for alignment
        padded = f"{label:<9}"
        color = self.COLORS.get(level, '')
        if color:
            record.levelname = f"{color}{padded}{self.RESET}"
        else:
            record.levelname = padded
        try:
            return super().format(record)
        finally:
            # restore original to avoid side effects
            record.levelname = level


logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)
logger.propagate = False
logger.handlers.clear()

handler = logging.StreamHandler()
formatter = ColoredFormatter("%(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def format_body(body: dict) -> str:
    try:
        return json.dumps(body, indent=2, ensure_ascii=False)
    except Exception:
        return str(body)


def log_request(method: str, path: str, query: dict, body: dict | None):
    print("\n\n")
    logger.debug("==================== START LOGGER ====================")
    logger.info(f"[REQUEST]    : {method} {path}")
    logger.info(f"Query        : {json.dumps(query, ensure_ascii=False)}")
    logger.info("Body         :")
    logger.info(format_body(body or {}))


def log_response(method: str, path: str, status_code: int):
    logger.info(f"[RESPONSE]   : {method} {path} | Status: {status_code}")
    logger.debug("==================== END LOGGER ====================")
