import discord
from discord.ext import commands
import logging
from typing import Optional
from config.settings import settings

class TriviaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # Only enable what we actually need - no privileged intents required
        intents.guilds = True
        intents.guild_messages = True
        intents.dm_messages = True
        intents.reactions = True
        # Remove message_content as it's privileged and not needed for slash commands
        
        super().__init__(
            command_prefix=settings.BOT_PREFIX,
            intents=intents,
            help_command=None
        )
        
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration."""
        import os
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Set up handlers - prefer console logging for containers
        handlers = [logging.StreamHandler()]
        
        # Only add file handler if we can write to the logs directory
        try:
            handlers.append(logging.FileHandler('logs/bot.log'))
        except (PermissionError, OSError):
            # If we can't write to file, just use console logging
            pass
        
        logging.basicConfig(
            level=logging.INFO if not settings.DEBUG_MODE else logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger('TriviaBot')
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        self.logger.info("Setting up bot...")
        
        # Load cogs
        try:
            await self.load_extension('src.bot.cogs.trivia')
            await self.load_extension('src.bot.cogs.admin')
            await self.load_extension('src.bot.cogs.stats')
            self.logger.info("All cogs loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load cogs: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        self.logger.info(f'{self.user} has connected to Discord!')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot activity
        activity = discord.Game(name="Trivia | Use /trivia to start!")
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Global error handler."""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Invalid argument provided.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            self.logger.error(f"Unhandled error in {ctx.command}: {error}")
            await ctx.send("An unexpected error occurred. Please try again later.")
    
    async def close(self):
        """Clean shutdown."""
        self.logger.info("Shutting down bot...")
        await super().close()