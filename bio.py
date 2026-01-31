"""
Author: Bisnu Ray (Modified)
User: https://t.me/BisnuRay
Channel: https://t.me/itsSmartDev
Modified to check personal channels instead of bio URLs
UPDATED: Enhanced reaction monitoring and user profile scanning through reactions
FURTHER UPDATED: Fixed auto-ban/kick/mute on join + unified logic
FIXED: Corrected ban on join execution
"""

from pyrogram import Client, filters, errors, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.raw.types import UpdateMessageReactions
from datetime import datetime, timedelta

from helper.utils import (
    is_admin,
    get_config, update_config,
    increment_warning, reset_warnings,
    is_whitelisted, add_whitelist, remove_whitelist, get_whitelist,
    track_user_activity, get_recent_activity,
    log_info, log_success, log_warning, log_error, log_debug,
    log_user_action, log_channel_info, log_separator,
    get_recent_joins, get_user_recent_messages, get_user_recent_reactions,
    get_all_recent_reactions, check_user_comprehensive
)

from helper.channel_checker import (
    check_user_channels,
    get_recent_reactions,
    get_recent_joins,
    analyze_user_profile,
    scan_message_reactions
)

from config import (
    API_ID, API_HASH, BOT_TOKEN,
    SUSPICIOUS_CHANNEL_KEYWORDS,
    CHECK_BIO_FOR_CHANNELS,
    CHECK_NEW_MEMBERS,
    AUTO_BAN_NSFW_ON_JOIN,
    AUTO_BAN_SUSPICIOUS_ON_JOIN,
    AUTO_BAN_ACTION,
    SILENT_MODE,
    ENABLE_NSFW_DETECTION,
    NSFW_AUTO_BAN,
    REACTION_SCAN_PROBABILITY,
    MESSAGE_SCAN_PROBABILITY
)

import random

app = Client(
    "channel_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ... (keeping all other handlers the same) ...

# Monitor new members - FIXED VERSION
@app.on_message(filters.new_chat_members)
async def new_member_handler(client: Client, message):
    chat_id = message.chat.id

    if not CHECK_NEW_MEMBERS:
        log_debug("CHECK_NEW_MEMBERS is disabled, skipping new member check")
        return

    for new_user in message.new_chat_members:
        if new_user.is_bot:
            log_debug(f"Skipping bot user: {new_user.first_name}")
            continue

        user_id = new_user.id
        user_name = f"{new_user.first_name} {new_user.last_name or ''}".strip()

        log_separator("NEW MEMBER JOINED")
        log_user_action(user_name, user_id, "Joined group", f"Chat: {chat_id}")

        # Track join activity
        await track_user_activity(chat_id, user_id, 'join', f"Joined group")

        # Skip whitelisted
        if await is_whitelisted(chat_id, user_id):
            log_info(f"User {user_name} is whitelisted, skipping check")
            log_separator()
            continue

        try:
            log_info(f"Running comprehensive analysis on new member {user_name}")

            # Run comprehensive check
            comp_check = await check_user_comprehensive(client, chat_id, user_id, hours=1)

            # Analyze profile
            log_info(f"Analyzing user profile for {user_name}")
            analysis = await analyze_user_profile(client, user_id, SUSPICIOUS_CHANNEL_KEYWORDS)

            if not analysis:
                log_warning(f"Could not analyze profile for {user_name} - profile may be private or inaccessible")
                log_separator()
                continue

            log_info(f"Profile analysis complete:")
            log_info(f"  - Total channels: {analysis['total_channels']}")
            log_info(f"  - Suspicious channels: {len(analysis['suspicious_channels'])}")
            log_info(f"  - NSFW channels: {len(analysis['nsfw_channels'])}")
            log_info(f"  - Is suspicious: {analysis.get('is_suspicious', False)}")

            # FIXED: Unified decision logic with proper execution
            should_instant_action = False
            action_reason = ""

            # Check NSFW first (highest priority)
            if ENABLE_NSFW_DETECTION and AUTO_BAN_NSFW_ON_JOIN and len(analysis['nsfw_channels']) > 0:
                should_instant_action = True
                action_reason = f"NSFW channels detected ({len(analysis['nsfw_channels'])})"
                log_warning(f"NSFW Auto-ban triggered: {action_reason}")
                for nsfw_ch in analysis['nsfw_channels'][:3]:  # Log first 3
                    ch = nsfw_ch['channel']
                    log_channel_info(ch['title'], ch['channel_id'], f"NSFW - {nsfw_ch['nsfw_info']['confidence']} confidence")

            # Check suspicious channels (second priority)
            elif AUTO_BAN_SUSPICIOUS_ON_JOIN and len(analysis['suspicious_channels']) > 0:
                should_instant_action = True
                action_reason = f"Suspicious channels detected ({len(analysis['suspicious_channels'])})"
                log_warning(f"Suspicious Auto-ban triggered: {action_reason}")
                for susp_ch in analysis['suspicious_channels'][:3]:  # Log first 3
                    ch = susp_ch['channel']
                    log_channel_info(ch['title'], ch['channel_id'], f"Matched: {susp_ch['matched_keyword']}")

            # EXECUTE ACTION IF NEEDED
            if should_instant_action:
                log_warning(f"Executing instant action on {user_name} [{user_id}]")
                log_info(f"Action type: {AUTO_BAN_ACTION}")
                
                action_executed = False
                action_text = ""
                
                try:
                    if AUTO_BAN_ACTION == "ban":
                        await client.ban_chat_member(chat_id, user_id)
                        action_text = "banned"
                        action_executed = True
                        log_success(f"✅ User {user_name} has been BANNED")
                        
                    elif AUTO_BAN_ACTION == "kick":
                        await client.ban_chat_member(chat_id, user_id)
                        await client.unban_chat_member(chat_id, user_id)
                        action_text = "kicked"
                        action_executed = True
                        log_success(f"✅ User {user_name} has been KICKED")
                        
                    elif AUTO_BAN_ACTION == "mute":
                        await client.restrict_chat_member(
                            chat_id, user_id,
                            ChatPermissions(can_send_messages=False)
                        )
                        action_text = "muted"
                        action_executed = True
                        log_success(f"✅ User {user_name} has been MUTED")
                    else:
                        log_error(f"Invalid AUTO_BAN_ACTION: {AUTO_BAN_ACTION}")
                        
                except errors.ChatAdminRequired:
                    log_error(f"❌ Failed to {AUTO_BAN_ACTION} {user_name}: Bot lacks admin permissions")
                except errors.UserAdminInvalid:
                    log_error(f"❌ Failed to {AUTO_BAN_ACTION} {user_name}: Cannot restrict admin user")
                except Exception as e:
                    log_error(f"❌ Failed to {AUTO_BAN_ACTION} {user_name}: {str(e)}")

                # Send notification if action was executed and not in silent mode
                if action_executed and not SILENT_MODE:
                    full_name = f"{new_user.first_name}{(' ' + new_user.last_name) if new_user.last_name else ''}"
                    mention = f"[{full_name}](tg://user?id={user_id})"
                    
                    notification_text = f"**🚫 {mention} has been {action_text} on join!**\n"
                    notification_text += f"**Reason:** {action_reason}\n"
                    
                    if len(analysis['suspicious_channels']) > 0:
                        notification_text += f"**Suspicious Channels:** {len(analysis['suspicious_channels'])}\n"
                        if analysis['suspicious_channels']:
                            notification_text += f"**Example:** {analysis['suspicious_channels'][0]['channel']['title']}"
                    
                    try:
                        await client.send_message(chat_id, notification_text)
                    except Exception as e:
                        log_error(f"Failed to send notification: {e}")
                        
            elif analysis.get('is_suspicious', False):
                log_warning(f"⚠️ User {user_name} has suspicious activity but auto-ban is disabled")
                log_info("User will be monitored for violations in future messages")
            else:
                log_success(f"✅ User {user_name} profile is clean")

        except errors.UserNotParticipant:
            log_warning(f"User {user_name} left before check completed")
        except errors.PeerIdInvalid:
            log_error(f"Invalid peer ID for user {user_name}")
        except Exception as e:
            log_error(f"Error checking new member {user_name}: {e}")
            import traceback
            log_error(traceback.format_exc())

        log_separator()

# ... (rest of the code remains the same) ...

if __name__ == "__main__":
    log_separator("BOT STARTUP")
    log_info("Initializing BioLink Protector Bot (FIXED VERSION)...")
    log_info(f"CHECK_NEW_MEMBERS: {CHECK_NEW_MEMBERS}")
    log_info(f"AUTO_BAN_NSFW_ON_JOIN: {AUTO_BAN_NSFW_ON_JOIN}")
    log_info(f"AUTO_BAN_SUSPICIOUS_ON_JOIN: {AUTO_BAN_SUSPICIOUS_ON_JOIN}")
    log_info(f"AUTO_BAN_ACTION: {AUTO_BAN_ACTION}")
    log_info(f"SILENT_MODE: {SILENT_MODE}")
    log_info(f"Monitoring reactions: True")
    log_info(f"Tracking user activity: True")
    log_separator()
    
    app.run()
