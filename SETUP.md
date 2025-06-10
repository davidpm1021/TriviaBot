# TriviaBot Setup Guide

## Quick Start

Your API keys have been configured! Follow these steps to get the bot running:

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using pip3
pip3 install -r requirements.txt

# Or using python module
python -m pip install -r requirements.txt
```

### 2. Test Configuration

```bash
python test_config.py
```

This will verify your setup and show any missing dependencies.

### 3. Run the Bot

```bash
python main.py
```

### 4. Setup Discord Commands

Once the bot is online:
1. In any Discord channel where the bot has access, type: `!sync`
2. This registers all slash commands with Discord

### 5. Start Playing!

Use these commands:
- `/trivia` - Start a random trivia question
- `/trivia science medium` - Science question, medium difficulty  
- `/answer A` - Answer with A, B, C, or D
- `/stats` - View your statistics
- `/persona gordon_ramsay` - Switch to Gordon Ramsay personality
- `/roast` - Get roasted by your trivia host

## Troubleshooting

### Common Issues:

**"ModuleNotFoundError: No module named 'discord'"**
- Install dependencies: `pip install discord.py`

**"ModuleNotFoundError: No module named 'openai'"**
- Install dependencies: `pip install openai`

**"Configuration error: Missing required environment variables"**
- Check that `.env` file exists and contains your API keys

**Bot doesn't respond to slash commands**
- Make sure you ran `!sync` after the bot started
- Check bot permissions in Discord (needs "Use Slash Commands")

### Discord Bot Permissions

Your bot needs these permissions:
- ✅ Send Messages
- ✅ Use Slash Commands  
- ✅ Embed Links
- ✅ Read Message History
- ✅ Add Reactions

### Bot Invite Link

Generate an invite link in Discord Developer Portal with these scopes:
- `bot`
- `applications.commands`

## API Keys Security

✅ **Your API keys are secure!**
- Stored in `.env` file (excluded from git)
- Never exposed in code
- Used only for authentication

## Support

If you encounter issues:
1. Check the console/logs for error messages
2. Verify all dependencies are installed
3. Ensure bot has proper Discord permissions
4. Check that API keys are valid and have credits

## Features Ready to Use

🧠 **AI-Generated Questions** - Unlimited trivia powered by OpenAI
🎭 **5 Personalities** - Sarcastic Host, Einstein, Gordon Ramsay, Oprah, Yoda  
📊 **Statistics** - Track performance, streaks, and rankings
🏆 **Leaderboards** - Compete with other players
🎯 **Smart Scoring** - Speed bonuses and difficulty multipliers
⚡ **Real-time** - Instant responses and feedback

Have fun with your new trivia bot! 🎉