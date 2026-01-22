import os
from os import environ
import logging

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO
)

class Config(object):
    # ------------------
    # SENSITIVE DATA (Load from Environment Variables)
    # ------------------
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    API_ID = int(os.environ.get("API_ID", 0)) 
    API_HASH = os.environ.get("API_HASH")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    
    # ------------------
    # CONFIGURATION
    # ------------------
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))
    HTTP_PROXY = os.environ.get("HTTP_PROXY", "")
    
    # File Size Limits
    MAX_FILE_SIZE = 2194304000 # ~2 GB
    TG_MAX_FILE_SIZE = 2194304000
    FREE_USER_MAX_FILE_SIZE = 2194304000
    
    # FIXED: Was set to 2GB, meaning it would reject small files. Set to 0.
    TG_MIN_FILE_SIZE = int(os.environ.get("TG_MIN_FILE_SIZE", 0))

    # Images
    DEF_THUMB_NAIL_VID_S = os.environ.get("DEF_THUMB_NAIL_VID_S", "https://placehold.it/90x90")
    DEF_WATER_MARK_FILE = "@Universal_url_downloader_bot"

    # Other API Keys
    OUO_IO_API_KEY = os.environ.get("OUO_IO_API_KEY", "")
    
    # System settings
    MAX_MESSAGE_LENGTH = 4096
    PROCESS_MAX_TIMEOUT = 3600
    
    # User Management
    ADMIN = set(
        int(x) for x in environ.get("ADMIN", "").split()
        if x.isdigit()
    )

    BANNED_USERS = set(
        int(x) for x in environ.get("BANNED_USERS", "").split()
        if x.isdigit()
    )

    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))
    LOGGER = logging
    
    # FIXED: Removed double quote at end of string
    SESSION_NAME = "Universal_url_downloader_bot"
    UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "")

    BOT_USERNAME = os.environ.get("BOT_USERNAME", "uploadLinkToFileBot")
    ADL_BOT_RQ = {}

    # Boolean Check
    TRUE_OR_FALSE = os.environ.get("TRUE_OR_FALSE", "").lower() == "true"

    # Shortlink settings
    SHORT_DOMAIN = environ.get("SHORT_DOMAIN", "")
    SHORT_API = environ.get("SHORT_API", "")

    # Verification
    VERIFICATION = os.environ.get("VERIFICATION", "")
