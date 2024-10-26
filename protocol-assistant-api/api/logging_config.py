# logging_config.py
import logging
import os

# Set up logging configuration
LOG_LEVEL = logging.DEBUG if os.getenv("DEBUG_MODE", "false").lower() == "true" else logging.INFO
LOG_FILE = "app.log"

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # For console output
    ]
)

# Get the logger instance
logger = logging.getLogger("chat")
