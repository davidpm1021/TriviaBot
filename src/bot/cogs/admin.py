import discord
from discord.ext import commands
from discord import app_commands
import logging

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('TriviaBot.Admin')
    
    @app_commands.command(name="ping", description="Check if the bot is responsive")
    async def ping(self, interaction: discord.Interaction):
        """Simple ping command to test bot responsiveness."""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency: {latency}ms")
    
    @app_commands.command(name="status", description="Get bot status information")
    async def status(self, interaction: discord.Interaction):
        """Get bot status and statistics."""
        embed = discord.Embed(title="TriviaBot Status", color=0x00ff00)
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_commands(self, ctx):
        """Sync slash commands (owner only)."""
        try:
            synced = await self.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands.")
            self.logger.info(f"Synced {len(synced)} commands")
        except Exception as e:
            await ctx.send(f"Failed to sync commands: {e}")
            self.logger.error(f"Failed to sync commands: {e}")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))