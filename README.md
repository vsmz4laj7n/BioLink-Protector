# BioLink Protector Bot - UPDATED VERSION

## 🎉 What's Fixed in This Version

This updated version fixes critical issues with **auto-ban** and **silent mode** functionality, plus adds new features:

### ✅ Fixed Issues:

1. **Auto-Ban Not Working**
   - Previously checked generic `is_suspicious` flag
   - Now specifically checks for NSFW channels
   - Auto-ban now triggers immediately when NSFW channels are detected

2. **Silent Mode Not Working**
   - Check messages are now properly deleted for clean profiles
   - Works correctly across all code paths
   - Ban notifications still appear (only check message is deleted)

3. **Better Logic Flow**
   - Clear separation between NSFW and suspicious content
   - More accurate detection and response
   - Improved message handling

### ✨ NEW Features:

4. **Kick vs Ban Option**
   - Choose between permanent ban or kick (user can rejoin)
   - Configurable via `AUTO_BAN_ACTION` setting
   - Options: `"ban"` (permanent) or `"kick"` (can rejoin)

5. **True Silent Mode**
   - When enabled, NO checking messages appear in chat
   - Only terminal/console logs are shown
   - Completely silent for clean users
   - Notifications still appear for NSFW/suspicious users

---

## ⚡ Quick Configuration Guide

### Most Common Settings

**1. Strict Mode (Kick NSFW users, silent checking):**
```python
CHECK_NEW_MEMBERS = True
AUTO_BAN_NSFW_ON_JOIN = True
AUTO_BAN_ACTION = "kick"  # They can rejoin if cleaned up
SILENT_MODE = True  # No checking messages in chat
```

**2. Stealth Mode (Ban NSFW users, completely silent):**
```python
CHECK_NEW_MEMBERS = True
AUTO_BAN_NSFW_ON_JOIN = True
AUTO_BAN_ACTION = "ban"  # Permanent ban
SILENT_MODE = True  # No messages at all
```

**3. Visible Mode (Show all checks to users):**
```python
CHECK_NEW_MEMBERS = True
AUTO_BAN_NSFW_ON_JOIN = True
AUTO_BAN_ACTION = "kick"
SILENT_MODE = False  # All checks visible in chat
```

**4. Manual Mode (No auto-actions, warnings only):**
```python
CHECK_NEW_MEMBERS = True
AUTO_BAN_NSFW_ON_JOIN = False  # No auto-action
SILENT_MODE = False
DEFAULT_PUNISHMENT = "warn"  # Admins handle manually
```

---

## 📋 Features

- ✅ Automatic detection of personal channels
- ✅ NSFW channel detection with confidence scoring
- ✅ Auto-ban for NSFW channels on join
- ✅ Silent mode for clean user checks
- ✅ Customizable warning system
- ✅ Whitelist management
- ✅ Suspicious keyword detection
- ✅ Bio checking for channel mentions

---

## 🚀 Installation

### Prerequisites

1. Python 3.8 or higher
2. MongoDB (local or cloud)
3. Telegram Bot Token
4. Telegram API ID and Hash

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure MongoDB

Make sure MongoDB is running:

```bash
# For local MongoDB
mongod

# Or use MongoDB Atlas (cloud)
# Update MONGO_URI in config.py with your connection string
```

### Step 3: Edit Configuration

Edit `config.py` and add your credentials:

```python
API_ID = "YOUR_API_ID"  # Get from https://my.telegram.org
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Get from @BotFather
```

### Step 4: Run the Bot

```bash
python bio.py
```

---

## ⚙️ Configuration Options

In `config.py`, you can customize:

### Auto-Ban Settings
```python
# NSFW Detection Settings
ENABLE_NSFW_DETECTION = True  # Enable/disable NSFW detection
NSFW_AUTO_BAN = True  # Auto-ban users with NSFW channels

# New Member Checking
CHECK_NEW_MEMBERS = True  # Check members when they join
AUTO_BAN_NSFW_ON_JOIN = True  # Auto-ban/kick new members with NSFW
AUTO_BAN_ACTION = "kick"  # "kick" (can rejoin) or "ban" (permanent)
SILENT_MODE = True  # True = No check messages in chat (terminal only)
```

### Warning System
```python
DEFAULT_WARNING_LIMIT = 3  # Number of warnings before action
DEFAULT_PUNISHMENT = "mute"  # Options: "mute" or "ban"
```

### Detection Keywords
```python
SUSPICIOUS_CHANNEL_KEYWORDS = [
    "earn", "money", "crypto", "investment",
    "trading", "forex", "bitcoin", "signals",
    # Add your own keywords
]
```

---

## 📖 How It Works

### New Member Joins (Silent Mode ON)

1. **User joins group** → Bot checks profile (no message in chat, only terminal logs)
2. **NSFW channel detected** → Immediate kick/ban + notification shown
3. **Suspicious channel detected** → Warning message shown
4. **Clean profile** → No messages at all (completely silent)

### New Member Joins (Silent Mode OFF)

1. **User joins group** → "🔍 Checking..." message appears
2. **NSFW channel detected** → Immediate kick/ban, check msg deleted, notification shown
3. **Suspicious channel detected** → Check message updated with warning
4. **Clean profile** → Check message updated to "✅ Clean"

### Kick vs Ban

- **KICK** (`AUTO_BAN_ACTION = "kick"`): User is removed but can rejoin via invite link
- **BAN** (`AUTO_BAN_ACTION = "ban"`): User is permanently banned, cannot rejoin

### User Sends Message

1. **Message sent** → Bot analyzes profile
2. **NSFW/suspicious content found** → Message deleted, warning issued
3. **Warnings exceed limit** → Mute or ban based on config
4. **Clean profile** → Warnings reset

---

## 🎮 Bot Commands

### Admin Commands

- `/config` - Configure warning limit and punishment mode
- `/free @user` - Whitelist a user (no checking)
- `/unfree @user` - Remove from whitelist
- `/freelist` - Show all whitelisted users
- `/checkuser` - Check user's profile (reply to message)

### User Commands

- `/start` - Show welcome message
- `/help` - Show help and commands

---

## 🔍 Expected Behavior

### Scenario 1: User with NSFW Channel Joins (Silent Mode ON)
```
1. No message appears in chat
2. Terminal shows: "🔍 Checking new member..."
3. User is kicked/banned immediately
4. "🚫 KICKED/BANNED: [User] - NSFW channel detected" (appears in chat)
```

### Scenario 2: User with NSFW Channel Joins (Silent Mode OFF)
```
1. "🔍 Checking new member..." (appears in chat)
2. User is kicked/banned immediately
3. Check message is deleted
4. "🚫 KICKED/BANNED: [User] - NSFW channel detected" (appears in chat)
```

### Scenario 3: Clean User Joins (Silent Mode ON)
```
1. No message appears in chat at all
2. Terminal shows: "✅ Profile is clean"
3. Completely silent - no trace in chat
```

### Scenario 4: Clean User Joins (Silent Mode OFF)
```
1. "🔍 Checking new member..." (appears)
2. "✅ [User] profile checked - Clean" (stays in chat)
```

### Scenario 5: Suspicious (Non-NSFW) User Joins
```
1. "🔍 Checking new member..." (if silent mode OFF)
2. "⚠️ Warning: New member has suspicious channels..." (appears)
3. User is monitored but NOT kicked/banned
```

### Terminal Output Example (Silent Mode ON)
```
==================================================
🔍 Checking new member: John Doe (ID: 123456789)
==================================================
🔇 Silent mode: No message sent to chat
🔎 Starting profile analysis...
🔞 NSFW channels detected: 1 channel(s)
  • Adult Content 18+ - Confidence: high

⚠️  AUTO-KICK TRIGGERED for NSFW content
✅ User kicked from group (can rejoin)
🔇 Silent mode: Sending notification only
✅ KICKED notification sent to chat
==================================================
```

---

## 📊 Terminal Logging

When `SILENT_MODE = True`, all checking activity is logged to the terminal/console instead of the chat. This allows admins to monitor bot activity without cluttering the group.

### What's Logged:

- ✅ New member details (name, ID)
- ✅ Profile analysis status
- ✅ NSFW channel detection results
- ✅ Suspicious channel findings
- ✅ Actions taken (kick/ban/warning)
- ✅ Message sending status
- ✅ Errors and exceptions

### Example Terminal Output:
```
==================================================
🔍 Checking new member: John Doe (ID: 123456789)
==================================================
🔇 Silent mode: No message sent to chat
🔎 Starting profile analysis...
✅ Profile is clean - No violations found
🔇 Silent mode: No messages sent (clean profile)
==================================================
```

This makes it easy to monitor the bot's activity through server logs or console while keeping the group chat clean.

---

## 🛠️ Troubleshooting

### Auto-ban not working?

1. Check bot has ban permission in group
2. Verify `AUTO_BAN_NSFW_ON_JOIN = True` in config.py
3. Check console logs for errors
4. Ensure NSFW detection is enabled

### Kick not working / User still banned permanently?

1. Verify `AUTO_BAN_ACTION = "kick"` in config.py (not "ban")
2. Check bot has both ban AND unban permissions
3. Kick = ban + immediate unban (allows rejoin)
4. Check terminal logs for "User kicked" confirmation

### Silent mode not working?

1. Verify `SILENT_MODE = True` in config.py
2. Check that no checking messages appear in chat
3. Check terminal/console for log output
4. Notifications for NSFW/suspicious users should still appear

### NSFW detection too sensitive/loose?

Adjust confidence thresholds in `helper/channel_checker.py`:

```python
# In check_if_nsfw_channel function
if confidence_score >= 5:  # High confidence (default)
    confidence = "high"
elif confidence_score >= 3:  # Medium confidence
    confidence = "medium"
```

Increase numbers for stricter detection, decrease for more sensitive.

---

## 📁 Project Structure

```
BioLink-Protector/
├── bio.py                    # Main bot file (UPDATED)
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
└── helper/
    ├── channel_checker.py    # Channel analysis functions
    └── utils.py              # Database utilities
```

---

## 🔐 Required Bot Permissions

In your Telegram group, the bot needs:

- ✅ Delete messages (for removing violating messages)
- ✅ Ban users (for both ban and kick actions)
- ✅ Unban users (required for kick feature to work)
- ✅ Restrict members (for mute functionality)
- ✅ Read message history

**Note**: The "kick" feature works by banning then immediately unbanning, which allows the user to rejoin.

---

## 📝 Notes

- The bot uses MongoDB to store warnings, punishments, and whitelist
- Personal channel detection uses Telegram's official API
- NSFW detection uses keyword matching and content analysis
- All checks are non-intrusive and respect user privacy

---

## 💡 Tips

1. **Test in a test group first** before deploying to production
2. **Whitelist trusted users** to avoid false positives
3. **Adjust keywords** based on your group's needs
4. **Monitor logs** regularly for debugging
5. **Keep MongoDB backed up** to preserve settings

---

## 📞 Support

- Channel: https://t.me/itsSmartDev
- Original Author: @BisnuRay
- Modified by: BioLink Protector Team

---

## ⚖️ License

This is a modified version of the original BioLink Protector bot.
Use at your own discretion and comply with Telegram's Terms of Service.

---

## 🎯 Key Changes in This Update

| Feature | Before | After |
|---------|--------|-------|
| Auto-ban trigger | Generic `is_suspicious` | Specific `nsfw_channels` check |
| Silent mode | Temporarily shows message | No message at all (true silent) |
| Check message on ban | Not deleted | Always deleted |
| NSFW vs suspicious | Mixed together | Clearly separated |
| Detection accuracy | Lower | Higher |
| Ban action | Ban only | **NEW: Kick or Ban (configurable)** |
| Terminal logging | Minimal | **NEW: Detailed logs** |

---

**Version**: 2.1 (Updated)  
**Last Updated**: January 2026
