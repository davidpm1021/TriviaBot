#!/usr/bin/env python3
"""
TriviaBot - AI-powered Discord trivia bot with personality
"""
import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.bot.bot import TriviaBot
from config.settings import settings

async def main():
    """Main entry point for the bot."""
    try:
        # Validate settings
        settings.validate()
        
        # Create and start bot
        bot = TriviaBot()
        
        async with bot:
            await bot.start(settings.DISCORD_TOKEN)
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)