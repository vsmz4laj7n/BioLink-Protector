from pyrogram import Client, enums, filters
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from colorama import Fore, Back, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

from config import (
    MONGO_URI,
    DEFAULT_CONFIG,
    DEFAULT_PUNISHMENT,
    DEFAULT_WARNING_LIMIT
)

# Verbose logging functions
def log_info(message: str):
    """Log informational message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.CYAN}[{timestamp}] ℹ️  INFO: {message}{Style.RESET_ALL}")

def log_success(message: str):
    """Log success message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.GREEN}[{timestamp}] ✅ SUCCESS: {message}{Style.RESET_ALL}")

def log_warning(message: str):
    """Log warning message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.YELLOW}[{timestamp}] ⚠️  WARNING: {message}{Style.RESET_ALL}")

def log_error(message: str):
    """Log error message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.RED}[{timestamp}] ❌ ERROR: {message}{Style.RESET_ALL}")

def log_debug(message: str):
    """Log debug message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.MAGENTA}[{timestamp}] 🔍 DEBUG: {message}{Style.RESET_ALL}")

def log_user_action(user_name: str, user_id: int, action: str, details: str = ""):
    """Log user action with formatting"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = f"{user_name} [{user_id}]"
    if details:
        print(f"{Fore.BLUE}[{timestamp}] 👤 USER: {user_info} | {action} | {details}{Style.RESET_ALL}")
    else:
        print(f"{Fore.BLUE}[{timestamp}] 👤 USER: {user_info} | {action}{Style.RESET_ALL}")

def log_channel_info(channel_name: str, channel_id: int, info: str):
    """Log channel information"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.LIGHTCYAN_EX}[{timestamp}] 📢 CHANNEL: {channel_name} [{channel_id}] | {info}{Style.RESET_ALL}")

def log_separator(title: str = ""):
    """Print separator line"""
    if title:
        print(f"\n{Fore.WHITE}{Back.BLUE}{'='*20} {title} {'='*20}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.WHITE}{'='*60}{Style.RESET_ALL}")

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client['telegram_bot_db']
warnings_collection = db['warnings']
punishments_collection = db['punishments']
whitelists_collection = db['whitelists']
activity_collection = db['user_activity']

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    async for member in client.get_chat_members(
        chat_id,
        filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        if member.user.id == user_id:
            return True
    return False

async def get_config(chat_id: int):
    doc = await punishments_collection.find_one({'chat_id': chat_id})
    if doc:
        return doc.get('mode', 'warn'), doc.get('limit', DEFAULT_WARNING_LIMIT), doc.get('penalty', DEFAULT_PUNISHMENT)
    return DEFAULT_CONFIG

async def update_config(chat_id: int, mode=None, limit=None, penalty=None):
    update = {}
    if mode is not None:
        update['mode'] = mode
    if limit is not None:
        update['limit'] = limit
    if penalty is not None:
        update['penalty'] = penalty
    if update:
        await punishments_collection.update_one(
            {'chat_id': chat_id},
            {'$set': update},
            upsert=True
        )

async def increment_warning(chat_id: int, user_id: int) -> int:
    await warnings_collection.update_one(
        {'chat_id': chat_id, 'user_id': user_id},
        {'$inc': {'count': 1}},
        upsert=True
    )
    doc = await warnings_collection.find_one({'chat_id': chat_id, 'user_id': user_id})
    return doc['count']

async def reset_warnings(chat_id: int, user_id: int):
    await warnings_collection.delete_one({'chat_id': chat_id, 'user_id': user_id})

async def is_whitelisted(chat_id: int, user_id: int) -> bool:
    doc = await whitelists_collection.find_one({'chat_id': chat_id, 'user_id': user_id})
    return bool(doc)

async def add_whitelist(chat_id: int, user_id: int):
    await whitelists_collection.update_one(
        {'chat_id': chat_id, 'user_id': user_id},
        {'$set': {'user_id': user_id}},
        upsert=True
    )

async def remove_whitelist(chat_id: int, user_id: int):
    await whitelists_collection.delete_one({'chat_id': chat_id, 'user_id': user_id})

async def get_whitelist(chat_id: int) -> list:
    cursor = whitelists_collection.find({'chat_id': chat_id})
    docs = await cursor.to_list(length=None)
    return [doc['user_id'] for doc in docs]

# New activity tracking functions
async def track_user_activity(chat_id: int, user_id: int, activity_type: str, details: str = ""):
    """
    Track user activity in the group

    Args:
        chat_id: Chat ID where activity occurred
        user_id: User ID who performed the activity
        activity_type: Type of activity (message, reaction, join, etc.)
        details: Additional details about the activity
    """
    try:
        activity_doc = {
            'chat_id': chat_id,
            'user_id': user_id,
            'activity_type': activity_type,
            'details': details,
            'timestamp': datetime.now()
        }

        await activity_collection.insert_one(activity_doc)
        log_debug(f"Tracked activity: User {user_id} | {activity_type} | {details}")

        # Clean up old activities (keep only last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted = await activity_collection.delete_many({
            'chat_id': chat_id,
            'timestamp': {'$lt': cutoff_date}
        })
        if deleted.deleted_count > 0:
            log_debug(f"Cleaned up {deleted.deleted_count} old activity records")

    except Exception as e:
        log_error(f"Error tracking user activity: {e}")

async def get_recent_activity(chat_id: int, hours: int = 24, user_id: int = None):
    """
    Get recent user activity from the group

    Args:
        chat_id: Chat ID to query
        hours: Number of hours to look back (default 24)
        user_id: Optional specific user ID to filter by

    Returns:
        list: List of activity documents
    """
    try:
        cutoff_date = datetime.now() - timedelta(hours=hours)

        query = {
            'chat_id': chat_id,
            'timestamp': {'$gte': cutoff_date}
        }

        if user_id:
            query['user_id'] = user_id

        cursor = activity_collection.find(query).sort('timestamp', -1)
        activities = await cursor.to_list(length=100)  # Limit to 100 most recent

        return activities

    except Exception as e:
        print(f"Error getting recent activity: {e}")
        return []

async def get_user_activity_stats(chat_id: int, user_id: int, days: int = 7):
    """
    Get activity statistics for a specific user

    Args:
        chat_id: Chat ID
        user_id: User ID to check
        days: Number of days to analyze (default 7)

    Returns:
        dict: Statistics including message count, reaction count, etc.
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)

        activities = await activity_collection.find({
            'chat_id': chat_id,
            'user_id': user_id,
            'timestamp': {'$gte': cutoff_date}
        }).to_list(length=None)

        stats = {
            'total_activities': len(activities),
            'messages': 0,
            'reactions': 0,
            'joins': 0,
            'first_seen': None,
            'last_seen': None
        }

        for activity in activities:
            activity_type = activity.get('activity_type', '')

            if activity_type == 'message':
                stats['messages'] += 1
            elif activity_type == 'reaction':
                stats['reactions'] += 1
            elif activity_type == 'join':
                stats['joins'] += 1

            # Track first and last seen
            timestamp = activity.get('timestamp')
            if timestamp:
                if stats['first_seen'] is None or timestamp < stats['first_seen']:
                    stats['first_seen'] = timestamp
                if stats['last_seen'] is None or timestamp > stats['last_seen']:
                    stats['last_seen'] = timestamp

        return stats

    except Exception as e:
        print(f"Error getting user activity stats: {e}")
        return None

async def get_active_users(chat_id: int, hours: int = 24, limit: int = 20):
    """
    Get most active users in the group

    Args:
        chat_id: Chat ID
        hours: Number of hours to look back (default 24)
        limit: Maximum number of users to return (default 20)

    Returns:
        list: List of user IDs sorted by activity count
    """
    try:
        cutoff_date = datetime.now() - timedelta(hours=hours)

        pipeline = [
            {
                '$match': {
                    'chat_id': chat_id,
                    'timestamp': {'$gte': cutoff_date}
                }
            },
            {
                '$group': {
                    '_id': '$user_id',
                    'activity_count': {'$sum': 1}
                }
            },
            {
                '$sort': {'activity_count': -1}
            },
            {
                '$limit': limit
            }
        ]

        results = await activity_collection.aggregate(pipeline).to_list(length=None)

        return [{'user_id': r['_id'], 'count': r['activity_count']} for r in results]

    except Exception as e:
        log_error(f"Error getting active users: {e}")
        return []

async def get_recent_joins(chat_id: int, hours: int = 24):
    """
    Get users who recently joined the group

    Args:
        chat_id: Chat ID
        hours: Number of hours to look back (default 24)

    Returns:
        list: List of recent join activities
    """
    try:
        cutoff_date = datetime.now() - timedelta(hours=hours)

        joins = await activity_collection.find({
            'chat_id': chat_id,
            'activity_type': 'join',
            'timestamp': {'$gte': cutoff_date}
        }).sort('timestamp', -1).to_list(length=None)

        log_info(f"Found {len(joins)} recent joins in last {hours} hours")
        return joins

    except Exception as e:
        log_error(f"Error getting recent joins: {e}")
        return []

async def get_user_recent_messages(chat_id: int, user_id: int, hours: int = 24):
    """
    Get recent messages from a specific user

    Args:
        chat_id: Chat ID
        user_id: User ID
        hours: Number of hours to look back (default 24)

    Returns:
        list: List of message activities
    """
    try:
        cutoff_date = datetime.now() - timedelta(hours=hours)

        messages = await activity_collection.find({
            'chat_id': chat_id,
            'user_id': user_id,
            'activity_type': 'message',
            'timestamp': {'$gte': cutoff_date}
        }).sort('timestamp', -1).to_list(length=None)

        log_debug(f"User {user_id} has {len(messages)} messages in last {hours} hours")
        return messages

    except Exception as e:
        log_error(f"Error getting user messages: {e}")
        return []

async def get_user_recent_reactions(chat_id: int, user_id: int, hours: int = 24):
    """
    Get recent reactions from a specific user

    Args:
        chat_id: Chat ID
        user_id: User ID
        hours: Number of hours to look back (default 24)

    Returns:
        list: List of reaction activities
    """
    try:
        cutoff_date = datetime.now() - timedelta(hours=hours)

        reactions = await activity_collection.find({
            'chat_id': chat_id,
            'user_id': user_id,
            'activity_type': 'reaction',
            'timestamp': {'$gte': cutoff_date}
        }).sort('timestamp', -1).to_list(length=None)

        log_debug(f"User {user_id} has {len(reactions)} reactions in last {hours} hours")
        return reactions

    except Exception as e:
        log_error(f"Error getting user reactions: {e}")
        return []

async def get_all_recent_reactions(chat_id: int, hours: int = 24):
    """
    Get all recent reactions in the group

    Args:
        chat_id: Chat ID
        hours: Number of hours to look back (default 24)

    Returns:
        list: List of all reaction activities
    """
    try:
        cutoff_date = datetime.now() - timedelta(hours=hours)

        reactions = await activity_collection.find({
            'chat_id': chat_id,
            'activity_type': 'reaction',
            'timestamp': {'$gte': cutoff_date}
        }).sort('timestamp', -1).to_list(length=None)

        log_info(f"Found {len(reactions)} total reactions in last {hours} hours")
        return reactions

    except Exception as e:
        log_error(f"Error getting all reactions: {e}")
        return []

async def check_user_comprehensive(client: Client, chat_id: int, user_id: int, hours: int = 24):
    """
    Comprehensive check of user activity including joins, messages, and reactions

    Args:
        client: Pyrogram client
        chat_id: Chat ID
        user_id: User ID
        hours: Hours to look back (default 24)

    Returns:
        dict: Comprehensive user activity data
    """
    try:
        log_separator(f"COMPREHENSIVE CHECK: User {user_id}")

        # Get user info
        try:
            user = await client.get_users(user_id)
            user_name = f"{user.first_name} {user.last_name or ''}".strip()
            log_user_action(user_name, user_id, "Starting comprehensive check", f"Looking back {hours} hours")
        except:
            user_name = f"User {user_id}"
            log_warning(f"Could not fetch user info for {user_id}")

        # Check join activity
        joins = await activity_collection.find({
            'chat_id': chat_id,
            'user_id': user_id,
            'activity_type': 'join',
            'timestamp': {'$gte': datetime.now() - timedelta(hours=hours)}
        }).to_list(length=None)

        if joins:
            join_time = joins[0]['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            log_info(f"User joined at: {join_time}")
        else:
            log_info("No recent join recorded (may be old member)")

        # Check messages
        messages = await get_user_recent_messages(chat_id, user_id, hours)
        log_info(f"Recent messages: {len(messages)}")

        # Check reactions
        reactions = await get_user_recent_reactions(chat_id, user_id, hours)
        log_info(f"Recent reactions: {len(reactions)}")

        # Get activity stats
        stats = await get_user_activity_stats(chat_id, user_id, days=7)

        if stats:
            log_info(f"7-day stats: {stats['messages']} messages, {stats['reactions']} reactions")
            if stats['first_seen']:
                log_info(f"First seen: {stats['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
            if stats['last_seen']:
                log_info(f"Last seen: {stats['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}")

        result = {
            'user_id': user_id,
            'user_name': user_name,
            'recent_joins': joins,
            'recent_messages': messages,
            'recent_reactions': reactions,
            'stats': stats
        }

        log_separator()
        return result

    except Exception as e:
        log_error(f"Error in comprehensive check: {e}")
        return None
