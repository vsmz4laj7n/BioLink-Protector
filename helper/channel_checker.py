"""
Helper functions for checking user channels and activity
Enhanced with reaction monitoring and user activity tracking
Includes verbose logging for detailed terminal output
"""

from pyrogram import Client, errors, enums
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.types import InputPeerChannel, InputPeerUser
from datetime import datetime, timedelta

# Import logging functions from utils (will be available when imported together)
try:
    from helper.utils import log_info, log_success, log_warning, log_error, log_debug, log_channel_info
except ImportError:
    # Fallback if utils not available
    def log_info(msg): print(f"INFO: {msg}")
    def log_success(msg): print(f"SUCCESS: {msg}")
    def log_warning(msg): print(f"WARNING: {msg}")
    def log_error(msg): print(f"ERROR: {msg}")
    def log_debug(msg): print(f"DEBUG: {msg}")
    def log_channel_info(name, id, info): print(f"CHANNEL: {name} [{id}] | {info}")


async def get_personal_channel_from_profile(client: Client, user_id: int):
    """Get personal channel ID from user's profile"""
    try:
        result = await client.invoke(
            GetFullUser(id=await client.resolve_peer(user_id))
        )
        if hasattr(result, 'full_user') and hasattr(result.full_user, 'personal_channel_id'):
            return result.full_user.personal_channel_id
    except Exception as e:
        print(f"Error getting personal channel from profile: {e}")
    return None


async def get_user_common_chats(client: Client, user_id: int):
    """Get common chats between bot and user"""
    try:
        common_chats = await client.get_common_chats(user_id)
        return common_chats
    except Exception as e:
        print(f"Error getting common chats: {e}")
        return []


async def check_if_channel_owner(client: Client, channel_id: int, user_id: int):
    """Check if user is the owner of a channel"""
    try:
        async for admin in client.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if admin.user.id == user_id and admin.status == enums.ChatMemberStatus.OWNER:
                return True
    except Exception as e:
        print(f"Error checking channel ownership: {e}")
    return False


async def get_recent_reactions(client: Client, channel_id: int, limit: int = 10):
    """
    Get recent reactions from a channel
    Returns list of messages with their reaction counts
    """
    reactions_data = []
    try:
        async for message in client.get_chat_history(channel_id, limit=limit):
            if message.reactions:
                reaction_info = {
                    'message_id': message.id,
                    'date': message.date,
                    'reaction_count': sum(r.count for r in message.reactions.reactions),
                    'reactions': [{'emoji': r.emoji, 'count': r.count} for r in message.reactions.reactions]
                }
                reactions_data.append(reaction_info)
    except Exception as e:
        print(f"Error getting recent reactions: {e}")

    return reactions_data


async def get_recent_joins(client: Client, channel_id: int, days: int = 7):
    """
    Get recent member joins in a channel (requires admin rights)
    Returns list of user IDs who joined recently
    """
    recent_joins = []
    try:
        cutoff_date = datetime.now() - timedelta(days=days)

        async for member in client.get_chat_members(channel_id):
            if hasattr(member, 'joined_date') and member.joined_date:
                if member.joined_date >= cutoff_date:
                    recent_joins.append({
                        'user_id': member.user.id,
                        'joined_date': member.joined_date
                    })
    except Exception as e:
        print(f"Error getting recent joins: {e}")

    return recent_joins


async def get_channel_stats(client: Client, channel_id: int):
    """Get comprehensive channel statistics"""
    try:
        chat = await client.get_chat(channel_id)

        stats = {
            'title': chat.title,
            'username': chat.username,
            'type': chat.type.value,
            'description': chat.description,
            'members_count': 0
        }

        # Try to get member count
        if chat.type.value == 'channel':
            try:
                full_chat = await client.invoke(
                    GetFullChannel(
                        channel=InputPeerChannel(
                            channel_id=abs(channel_id) if channel_id < 0 else channel_id,
                            access_hash=0
                        )
                    )
                )
                if hasattr(full_chat, 'full_chat'):
                    stats['members_count'] = full_chat.full_chat.participants_count
            except Exception as e:
                print(f"Could not get member count: {e}")
                stats['members_count'] = 0

        return stats

    except Exception as e:
        print(f"Error getting channel stats for {channel_id}: {e}")
        return None


async def scan_message_reactions(client: Client, chat_id: int, message_id: int):
    """
    Scan a specific message for reactions and return user IDs who reacted

    Args:
        client: Pyrogram client
        chat_id: Chat ID where the message is
        message_id: Message ID to scan

    Returns:
        list: User IDs who reacted to the message
    """
    reactor_ids = []
    try:
        message = await client.get_messages(chat_id, message_id)

        if message and message.reactions:
            for reaction in message.reactions.reactions:
                try:
                    # Get users who reacted with this specific emoji
                    async for user in client.get_message_reactions(chat_id, message_id, reaction.emoji):
                        if not user.is_bot:
                            reactor_ids.append(user.id)
                except Exception as e:
                    print(f"Error getting reactors for emoji {reaction.emoji}: {e}")
    except Exception as e:
        print(f"Error scanning message reactions: {e}")

    return list(set(reactor_ids))  # Remove duplicates


async def check_user_channels(client: Client, user_id: int):
    """
    Main function to check user's personal channels
    Returns detailed information about channels owned by the user

    This function checks:
    1. Personal channel ID from user profile (UserFull.personal_channel_id)
    2. Common chats where user is the owner
    """
    try:
        user_channels = []
        checked_channel_ids = set()

        # Method 1: Get personal channel from user profile (PRIMARY METHOD)
        personal_channel_id = await get_personal_channel_from_profile(client, user_id)

        if personal_channel_id:
            try:
                # Convert to proper channel ID format
                channel_id = abs(personal_channel_id)
                if personal_channel_id < 0:
                    channel_id = personal_channel_id
                else:
                    channel_id = -1000000000000 - channel_id

                # Get channel info
                stats = await get_channel_stats(client, channel_id)

                if stats and stats['type'] == 'channel':
                    # Get recent reactions
                    reactions = await get_recent_reactions(client, channel_id)

                    # Get recent joins (if bot has admin rights)
                    recent_joins = await get_recent_joins(client, channel_id)

                    channel_info = {
                        'channel_id': channel_id,
                        'title': stats['title'],
                        'username': stats['username'],
                        'members_count': stats['members_count'],
                        'description': stats['description'],
                        'recent_reactions': reactions,
                        'recent_joins': recent_joins,
                        'source': 'profile'
                    }

                    user_channels.append(channel_info)
                    checked_channel_ids.add(channel_id)

            except Exception as e:
                print(f"Error getting personal channel info: {e}")

        # Method 2: Check common chats (FALLBACK METHOD)
        common_chats = await get_user_common_chats(client, user_id)

        for chat in common_chats:
            if chat.id in checked_channel_ids:
                continue

            if chat.type.value == "channel":
                is_owner = await check_if_channel_owner(client, chat.id, user_id)

                if is_owner:
                    stats = await get_channel_stats(client, chat.id)

                    if stats:
                        reactions = await get_recent_reactions(client, chat.id)
                        recent_joins = await get_recent_joins(client, chat.id)

                        channel_info = {
                            'channel_id': chat.id,
                            'title': stats['title'],
                            'username': stats['username'],
                            'members_count': stats['members_count'],
                            'description': stats['description'],
                            'recent_reactions': reactions,
                            'recent_joins': recent_joins,
                            'source': 'common_chats'
                        }

                        user_channels.append(channel_info)
                        checked_channel_ids.add(chat.id)

        return user_channels

    except Exception as e:
        print(f"Error in check_user_channels: {e}")
        return []


async def is_suspicious_channel(channel_info: dict, threshold_members: int = 100):
    """
    Determine if a channel is suspicious based on criteria

    Args:
        channel_info: Dictionary with channel information
        threshold_members: Minimum members to not be flagged (default 100)

    Returns:
        tuple: (is_suspicious: bool, reasons: list)
    """
    reasons = []

    # Check if channel has very few members
    if channel_info['members_count'] < threshold_members:
        reasons.append(f"Low member count ({channel_info['members_count']})")

    # Check if there are unusual reaction patterns
    if len(channel_info['recent_reactions']) > 0:
        avg_reactions = sum(r['reaction_count'] for r in channel_info['recent_reactions']) / len(channel_info['recent_reactions'])
        if avg_reactions > channel_info['members_count'] * 0.5:
            reasons.append("Unusually high reaction rate")

    # Check for rapid member growth
    if len(channel_info['recent_joins']) > channel_info['members_count'] * 0.3:
        reasons.append("Rapid member growth detected")

    is_suspicious = len(reasons) > 0

    return is_suspicious, reasons


async def check_bio_for_channel_mentions(bio: str, suspicious_keywords: list):
    """
    Check if user's bio contains channel mentions or suspicious keywords

    Args:
        bio: User's bio text
        suspicious_keywords: List of keywords to check for

    Returns:
        tuple: (has_mentions: bool, found_keywords: list)
    """
    import re

    if not bio:
        return False, []

    bio_lower = bio.lower()
    found_keywords = []

    # Check for suspicious keywords
    for keyword in suspicious_keywords:
        if keyword.lower() in bio_lower:
            found_keywords.append(keyword)

    # Check for channel/group links
    channel_patterns = [
        r'@([a-zA-Z0-9_]{5,})',
        r't\.me/([a-zA-Z0-9_]{5,})',
        r'telegram\.me/([a-zA-Z0-9_]{5,})',
    ]

    has_channel_mention = False
    for pattern in channel_patterns:
        if re.search(pattern, bio):
            has_channel_mention = True
            break

    return (has_channel_mention or len(found_keywords) > 0), found_keywords


async def check_if_nsfw_channel(client: Client, channel_id: int):
    """
    Check if a channel is NSFW based on various indicators

    Returns:
        dict with: is_nsfw (bool), reasons (list), confidence (low/medium/high)
    """
    reasons = []
    confidence_score = 0

    try:
        chat = await client.get_chat(channel_id)

        nsfw_keywords = [
            'nsfw', '18+', 'adult', 'porn', 'sex', 'xxx', 'nude', 'naked',
            'onlyfans', 'premium content', 'hot girls', 'sexy', 'leaked',
            'nudes', 'explicit', 'adult content', 'mature', 'erotic'
        ]

        title_lower = (chat.title or "").lower()
        desc_lower = (chat.description or "").lower()

        # Check title
        for keyword in nsfw_keywords:
            if keyword in title_lower:
                reasons.append(f"Title contains: '{keyword}'")
                confidence_score += 2

        # Check description
        for keyword in nsfw_keywords:
            if keyword in desc_lower:
                reasons.append(f"Description contains: '{keyword}'")
                confidence_score += 1

        # Check protected content
        if hasattr(chat, 'has_protected_content') and chat.has_protected_content:
            reasons.append("Protected content enabled")
            confidence_score += 1

        # Check recent messages
        try:
            nsfw_message_count = 0
            total_checked = 0

            async for message in client.get_chat_history(channel_id, limit=20):
                total_checked += 1

                # Check for media
                if message.photo or message.video:
                    nsfw_message_count += 1

                # Check text for NSFW keywords
                if message.text or message.caption:
                    text = (message.text or message.caption or "").lower()
                    for keyword in nsfw_keywords:
                        if keyword in text:
                            nsfw_message_count += 1
                            break

            if total_checked > 0:
                nsfw_ratio = nsfw_message_count / total_checked
                if nsfw_ratio > 0.5:
                    reasons.append(f"High NSFW content ratio ({int(nsfw_ratio*100)}%)")
                    confidence_score += 3
                elif nsfw_ratio > 0.3:
                    reasons.append(f"Moderate NSFW content ratio ({int(nsfw_ratio*100)}%)")
                    confidence_score += 1

        except Exception as e:
            print(f"Could not check messages: {e}")

        # Determine confidence level
        if confidence_score >= 5:
            confidence = "high"
        elif confidence_score >= 3:
            confidence = "medium"
        elif confidence_score >= 1:
            confidence = "low"
        else:
            confidence = "none"

        return {
            'is_nsfw': confidence_score > 0,
            'reasons': reasons,
            'confidence': confidence,
            'score': confidence_score
        }

    except Exception as e:
        print(f"Error checking NSFW status: {e}")
        return {
            'is_nsfw': False,
            'reasons': [],
            'confidence': 'none',
            'score': 0
        }


async def analyze_user_profile(client: Client, user_id: int, suspicious_keywords: list):
    """
    Comprehensive analysis of user profile including channels and bio

    Args:
        client: Pyrogram client
        user_id: User ID to analyze
        suspicious_keywords: List of suspicious keywords

    Returns:
        dict: Analysis results with channels, bio info, and suspicion level
    """
    try:
        log_debug(f"Starting profile analysis for user {user_id}")

        user = await client.get_chat(user_id)
        bio = user.bio or ""

        if bio:
            log_debug(f"User has bio: {bio[:50]}...")

        # Check channels
        log_debug("Checking user channels...")
        channels_info = await check_user_channels(client, user_id)
        log_info(f"Found {len(channels_info)} channels for user {user_id}")

        # Check bio for channel mentions and keywords
        has_bio_mentions, found_keywords = await check_bio_for_channel_mentions(bio, suspicious_keywords)

        if has_bio_mentions:
            log_warning(f"Bio contains suspicious content: {found_keywords}")

        # Check channel names for suspicious keywords and NSFW content
        suspicious_channels = []
        nsfw_channels = []

        for channel in channels_info:
            channel_name_lower = channel['title'].lower()
            channel_username_lower = (channel['username'] or "").lower()

            log_debug(f"Analyzing channel: {channel['title']}")

            # Check for suspicious keywords
            is_suspicious = False
            matched_keyword = None
            for keyword in suspicious_keywords:
                if keyword.lower() in channel_name_lower or keyword.lower() in channel_username_lower:
                    is_suspicious = True
                    matched_keyword = keyword
                    log_warning(f"Channel '{channel['title']}' matched keyword: {keyword}")
                    break

            # Check for NSFW content
            log_debug(f"Checking NSFW status for channel: {channel['title']}")
            nsfw_result = await check_if_nsfw_channel(client, channel['channel_id'])

            if nsfw_result['is_nsfw']:
                log_warning(f"NSFW channel detected: {channel['title']} (confidence: {nsfw_result['confidence']})")
                nsfw_channels.append({
                    'channel': channel,
                    'nsfw_info': nsfw_result
                })
                # NSFW channels are also suspicious
                if not is_suspicious:
                    is_suspicious = True
                    matched_keyword = f"NSFW ({nsfw_result['confidence']})"

            if is_suspicious:
                suspicious_channels.append({
                    'channel': channel,
                    'matched_keyword': matched_keyword,
                    'is_nsfw': nsfw_result['is_nsfw'],
                    'nsfw_info': nsfw_result
                })

        # Count total recent joins across all channels
        total_recent_joins = sum(len(ch.get('recent_joins', [])) for ch in channels_info)

        log_info(f"Analysis complete: {len(suspicious_channels)} suspicious, {len(nsfw_channels)} NSFW")

        analysis = {
            'user_id': user_id,
            'bio': bio,
            'has_bio_mentions': has_bio_mentions,
            'bio_keywords': found_keywords,
            'total_channels': len(channels_info),
            'channels': channels_info,
            'suspicious_channels': suspicious_channels,
            'nsfw_channels': nsfw_channels,
            'total_recent_joins': total_recent_joins,
            'is_suspicious': has_bio_mentions or len(suspicious_channels) > 0 or len(nsfw_channels) > 0
        }

        return analysis

    except Exception as e:
        log_error(f"Error in analyze_user_profile: {e}")
        import traceback
        traceback.print_exc()
        return None
