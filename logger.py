from pathlib import Path
from loguru import logger

logs_path = Path(".logs")
logs_path.mkdir(parents=True, exist_ok=True)

logger.remove() # Remove the default console logger
logger.add(
    logs_path / "log_{time:YYYY-MM-DD}.log",  # File name with date
    rotation="00:00",                  # Rotate daily at midnight
    retention="2 months",                # Keep 7 days of logs
    compression="zip",                 # Compress old logs
    level="INFO",                      # Only log INFO and above
    enqueue=True                       # Thread-safe logging
)