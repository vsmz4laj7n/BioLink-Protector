# BioLink Protector Bot - Enhanced Edition

## 🆕 New Features

This updated version includes enhanced monitoring capabilities for detecting suspicious users through reactions and recent messages, plus comprehensive verbose terminal logging.

### Enhanced Monitoring Features

1. **Reaction Monitoring**
   - Automatically scans users who add reactions to messages
   - Checks reactor profiles for suspicious channels
   - Tracks reaction activity across the group

2. **Recent Message Scanning**
   - Monitors all group messages for suspicious activity
   - Periodically checks message senders' profiles
   - Tracks user messaging patterns

3. **User Activity Tracking**
   - Records all user activities (messages, reactions, joins)
   - Provides activity statistics and reports
   - Identifies most active users in the group

4. **Profile Scanning Through Reactions**
   - When users react to messages, their profiles are analyzed
   - Detects suspicious channels even if user hasn't posted yet
   - Helps catch lurkers with promotional channels

5. **Verbose Terminal Logging**
   - Color-coded terminal output for easy reading
   - Detailed timestamps and user tracking
   - Multiple log levels (INFO, SUCCESS, WARNING, ERROR, DEBUG)
   - Comprehensive operation logging
   - See VERBOSE_OUTPUT_EXAMPLES.md for examples

## 📋 Updated Commands

### New Commands

- `/checkfull` - Comprehensive check: recent joins, messages, reactions, and channels (reply to user)
- `/scanreactions` - Scan recent message reactions for suspicious users
- `/recentactivity` - Show recent user activity in the group (last 24 hours)

### Existing Commands

- `/start` - Start the bot and get welcome message
- `/help` - Show all available commands
- `/config` - Configure warning limits and punishment mode
- `/free <user>` - Whitelist a user (reply to message or mention)
- `/unfree <user>` - Remove user from whitelist
- `/freelist` - List all whitelisted users
- `/checkuser` - Check a user's channels and profile (reply to their message)

## 🔍 How It Works

### Reaction Monitoring

When enabled, the bot:
1. Monitors reactions added to messages in the group
2. Randomly samples reactor profiles (configurable probability)
3. Analyzes their channels for suspicious content
4. Issues warnings or bans based on configuration

### Message Monitoring

For every message sent:
1. Bot tracks the activity in database
2. Periodically samples user profiles (configurable probability)
3. Checks for suspicious channels
4. Takes action if violations are found

### Activity Tracking

The bot maintains a database of:
- Message counts per user
- Reaction counts per user
- Join timestamps
- First and last seen timestamps
- Activity patterns over time

## ⚙️ Configuration

### New Config Options in `config.py`

```python
# Reaction Monitoring Settings
MONITOR_REACTIONS = True  # Monitor reactions to detect suspicious users
REACTION_SCAN_PROBABILITY = 0.2  # 20% chance to check reactor's profile

# Message Monitoring Settings
MESSAGE_SCAN_PROBABILITY = 0.1  # 10% chance to check message sender's profile

# Activity Tracking Settings
TRACK_USER_ACTIVITY = True  # Track user messages, reactions, and joins
ACTIVITY_RETENTION_DAYS = 7  # Keep activity records for 7 days
```

## 📊 Checking List Implementation

The bot now checks:

### ✅ Recent Reactions
- Monitors all reactions added to messages
- Scans reactor profiles for suspicious channels
- Even checks users already in the group
- Detects promotional channels through reaction activity

### ✅ Recent Messages
- Tracks all messages sent in the group
- Periodically scans message senders
- Monitors user activity patterns
- Identifies suspicious behavior over time

### ✅ User Profile Scanning
- Analyzes channels through reactions
- Checks bio for keywords
- Detects NSFW content
- Monitors recent channel activity

## 🚀 Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Dependencies:
   - `pyrofork` - Telegram client library
   - `tgcrypto` - Encryption for Pyrogram
   - `motor` - Async MongoDB driver
   - `colorama` - Colored terminal output for verbose logging

2. **Configure Settings**
   - Edit `config.py`
   - Add your API credentials
   - Set your MongoDB URI
   - Adjust monitoring probabilities

3. **Create Directory Structure**
   ```
   BioLink-Protector/
   ├── bio.py
   ├── config.py
   ├── requirements.txt
   └── helper/
       ├── channel_checker.py
       └── utils.py
   ```

4. **Run the Bot**
   ```bash
   python bio.py
   ```

## 📝 Database Collections

The bot uses the following MongoDB collections:

1. **warnings** - User warning counts
2. **punishments** - Group punishment configurations
3. **whitelists** - Whitelisted users per group
4. **user_activity** - Activity tracking (NEW)

## 🎯 Use Cases

### Scenario 1: Silent Spammer Detection
A user joins the group and stays quiet, but reacts to messages to appear active. The bot detects their promotional channel through reaction monitoring and takes action.

### Scenario 2: Activity Pattern Analysis
View recent activity to identify users who only join to spam and leave, or those who react excessively without genuine participation.

### Scenario 3: Proactive Monitoring
Instead of waiting for users to post, the bot actively scans reactions and identifies suspicious accounts before they can spam the group.

## ⚠️ Important Notes

1. **Performance Considerations**
   - Adjust scan probabilities based on group size
   - Higher probabilities = more thorough checking but more API calls
   - Monitor bot performance and adjust as needed

2. **Privacy**
   - All activity tracking is group-specific
   - Data is retained based on ACTIVITY_RETENTION_DAYS setting
   - Old data is automatically cleaned up

3. **Rate Limiting**
   - Telegram has API rate limits
   - Random sampling helps avoid hitting limits
   - Adjust probabilities if you get rate limit errors

## 🔧 Troubleshooting

**Issue**: Too many API calls / rate limits
- **Solution**: Reduce REACTION_SCAN_PROBABILITY and MESSAGE_SCAN_PROBABILITY

**Issue**: Not detecting enough suspicious users
- **Solution**: Increase scan probabilities or add more keywords to SUSPICIOUS_CHANNEL_KEYWORDS

**Issue**: Activity data growing too large
- **Solution**: Reduce ACTIVITY_RETENTION_DAYS or implement data cleanup

## 📈 Future Enhancements

Potential additions:
- Machine learning-based detection
- Pattern recognition for spam behavior
- Advanced analytics dashboard
- Multi-group coordination
- Reputation scoring system

## 🤝 Support

For issues or questions:
- Channel: https://t.me/itsSmartDev
- Author: @BisnuRay

## 📄 License

This is a modified version of the original BioLink Protector Bot with enhanced monitoring capabilities.
