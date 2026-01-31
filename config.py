"""
Configuration file for BioLink Protector Bot
"""

# Bot credentials (Get from BotFather)
API_ID = "xxxx"  # Your Telegram API ID
API_HASH = "xxxxxxxxxxxxxxxxxxxxxxx"  # Your Telegram API Hash
BOT_TOKEN = "xxxxxxxxxxxxxxxxxxxxx"  # Your Bot Token

# MongoDB URI for database (Get free MongoDB from mongodb.com)
MONGO_URI = "xxxxxxxxxxxxxxxxxxxxx"  # Replace with your MongoDB URI
# Default configuration
DEFAULT_CONFIG = ("penalty")  # (mode, warning_limit, penalty)
DEFAULT_PUNISHMENT = "kick"  # Options: "mute" or "ban"
DEFAULT_WARNING_LIMIT = 0  # Number of warnings before punishment

# Suspicious channel keywords to detect
# Add keywords that indicate promotional or spam channels
SUSPICIOUS_CHANNEL_KEYWORDS = [
    # Promotional/Marketing
    "promo",
    "promotion",
    "marketing",
    "advertisement",
    "ads",
    "sponsored",
    # Dating/Romance
    "dating",
    "girls",
    "boys",
    "relationship",
    "love",
    "meet",
    # Gambling/Finance
    "casino",
    "lottery",
    "betting",
    "crypto",
    "bitcoin",
    "investment",
    # NSFW related keywords (automatically detected separately)
    "nsfw",
    "18+",
    "adult",
    "onlyfans",
    "+18",
    "sussy",
    "secret place",
    # Add your own keywords here
]

# Check if channel name/username is mentioned in user's bio
CHECK_BIO_FOR_CHANNELS = True  # Set to False to disable bio checking

# NSFW Detection Settings
ENABLE_NSFW_DETECTION = True  # Set to False to disable NSFW channel detection
NSFW_AUTO_BAN = True  # Set to True to automatically ban users with NSFW channels (ignores warning limit)

# New Member Checking
CHECK_NEW_MEMBERS = True  # Check members immediately when they join (before they send messages)
AUTO_BAN_NSFW_ON_JOIN = True  # Automatically ban/kick/mute new members with NSFW channels
AUTO_BAN_SUSPICIOUS_ON_JOIN = True  # Automatically ban/kick/mute new members matching SUSPICIOUS_CHANNEL_KEYWORDS
AUTO_BAN_ACTION = "ban"  # Options: "ban" (permanent), "kick" (remove but can rejoin), "mute" (restrict messaging)
SILENT_MODE = True  # If True, no checking message appears in chat (only terminal logs)

# Reaction Monitoring Settings
MONITOR_REACTIONS = True  # Monitor reactions to detect suspicious users
REACTION_SCAN_PROBABILITY = 0.2  # 20% chance to check reactor's profile (0.0 to 1.0)

# Message Monitoring Settings
MESSAGE_SCAN_PROBABILITY = 0.1  # 10% chance to check message sender's profile (0.0 to 1.0)

# Activity Tracking Settings
TRACK_USER_ACTIVITY = True  # Track user messages, reactions, and joins
ACTIVITY_RETENTION_DAYS = 7  # Keep activity records for 7 days

