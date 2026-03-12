import os
import logging
from logging.handlers import TimedRotatingFileHandler

# Set up logger
logger = logging.getLogger('discord_bot')
logger.setLevel(logging.ERROR)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Rotating file handler - rotates monthly
file_handler = TimedRotatingFileHandler(
    filename='logs/bot_errors.log',
    when='midnight',
    interval=30,
    backupCount=12,
    encoding='utf-8'
)

# Format: [2025-01-29 14:30:45] ERROR - message
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
