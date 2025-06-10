# TriviaBot 🧠🤖

An AI-powered Discord trivia bot with personality! Generate endless trivia questions using OpenAI, compete with friends, and enjoy sarcastic banter from multiple host personalities.

## Features

### 🎯 Core Functionality
- **AI-Generated Questions**: Unlimited trivia questions powered by OpenAI
- **Smart Scoring**: Score calculation with speed bonuses and difficulty multipliers
- **Multiple Categories**: Science, History, Geography, Entertainment, Sports, and more
- **Difficulty Levels**: Easy, Medium, and Hard questions
- **Time Periods**: Questions from different historical eras

### 🎭 Personality System
- **Multiple Personas**: Choose from different trivia host personalities
  - **Sarcastic Host** (Default): Smug and condescending with witty remarks
  - **Einstein**: Wise physicist with scientific curiosity
  - **Gordon Ramsay**: Fiery chef applying kitchen intensity to trivia
  - **Oprah**: Inspirational and celebrating every answer
  - **Yoda**: Wise Jedi master speaking in riddles
- **Dynamic Responses**: AI-generated personality-driven feedback
- **Custom Roasts**: Get roasted based on your performance

### 📊 Statistics & Competition
- **Detailed Stats**: Track wins, streaks, response times, and scores
- **Leaderboards**: Global rankings with normalized scoring
- **Performance Ratings**: From "Learning" to "Grandmaster"
- **Stat Comparisons**: Compare your performance with other players
- **Streak Bonuses**: Rewards for consecutive correct answers

### 🎮 Game Features
- **Individual Play**: Personal trivia sessions
- **Question Timeout**: 30-second time limit per question
- **Skip Function**: Skip difficult questions
- **Response Validation**: Proper answer format checking

## Installation & Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token
- OpenAI API Key

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/TriviaBot.git
cd TriviaBot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your credentials:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (SQLite default)
DATABASE_URL=sqlite:///trivia_bot.db

# Bot Configuration
BOT_PREFIX=!
DEFAULT_PERSONA=sarcastic_host
DEBUG_MODE=false
```

### 4. Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token to your `.env` file
4. Enable the following bot permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History
   - Add Reactions

### 5. OpenAI API Setup
1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Add it to your `.env` file
3. Ensure you have credits/billing set up

### 6. Run the Bot
```bash
python main.py
```

### 7. Sync Commands (First Time)
After the bot starts, use the owner command to sync slash commands:
```
!sync
```

## Usage

### Basic Commands

- `/trivia [category] [difficulty] [era]` - Start a trivia question
- `/answer <A/B/C/D>` - Answer the current question
- `/skip` - Skip the current question
- `/stats` - View your statistics
- `/leaderboard [type] [category]` - View leaderboards
- `/persona <name>` - Change trivia host personality
- `/roast` - Get roasted based on your performance
- `/compare <user>` - Compare stats with another player
- `/ping` - Check bot responsiveness
- `/status` - View bot status

### Examples

```
/trivia science medium modern
/trivia random hard
/trivia history easy ancient
/answer C
/persona gordon_ramsay
/stats
/leaderboard global
/compare @friend
/roast
```

## Database

The bot uses SQLite by default for simplicity. For production deployment, consider PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@localhost/trivia_bot
```

The database automatically creates all necessary tables on first run.

## Project Structure

```
TriviaBot/
├── main.py                    # Bot entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── project-plan.md           # Development plan
├── config/
│   └── settings.py           # Configuration management
├── src/
│   ├── bot/
│   │   ├── bot.py           # Main bot class
│   │   └── cogs/            # Bot commands
│   │       ├── admin.py     # Admin commands
│   │       ├── trivia.py    # Trivia game logic
│   │       └── stats.py     # Statistics commands
│   ├── database/
│   │   ├── models.py        # Database models
│   │   └── database.py      # Database manager
│   ├── trivia/
│   │   └── generator.py     # AI trivia generation
│   ├── personality/
│   │   ├── personas.py      # Personality definitions
│   │   └── response_generator.py # AI response generation
│   └── utils/
│       └── scoring.py       # Scoring system
└── logs/                    # Log files
```

## Security Features

- Environment variables for sensitive data
- Comprehensive `.gitignore` 
- Input validation and sanitization
- Error handling with logging
- Database session management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include relevant logs and error messages

## Roadmap

Future features planned:
- Tournament brackets
- Daily challenges
- Category mastery badges
- Custom question submission
- Multi-server leaderboards
- Voice channel integration