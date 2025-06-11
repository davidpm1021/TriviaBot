import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import List, Dict

from src.database.database import db_manager
from src.utils.scoring import scoring_system
from src.personality.response_generator import personality_engine
from src.personality.personas import ResponseType
from src.trivia.generator import trivia_generator

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('TriviaBot.Stats')
    
    @app_commands.command(name="stats", description="View your trivia statistics")
    async def stats(self, interaction: discord.Interaction):
        """Display user's trivia statistics."""
        try:
            await interaction.response.defer()
            
            user = await db_manager.get_user_stats(str(interaction.user.id))
            
            if not user or user['total_games'] == 0:
                embed = discord.Embed(
                    title="📊 Your Trivia Stats",
                    description="You haven't played any trivia games yet! Use `/trivia` to get started.",
                    color=0x0099ff
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Calculate derived stats
            win_rate = user['win_rate']
            avg_score = user['avg_score_per_game']
            performance_rating = scoring_system.get_performance_rating(
                win_rate, avg_score, user['total_games']
            )
            
            # Create stats embed
            embed = discord.Embed(
                title=f"📊 {interaction.user.display_name}'s Trivia Stats",
                color=0x00ff00
            )
            
            # Main stats
            embed.add_field(
                name="🎮 Games Overview",
                value=f"**Games Played:** {user['total_games']}\n"
                      f"**Games Won:** {user['total_wins']}\n"
                      f"**Win Rate:** {win_rate:.1f}%",
                inline=True
            )
            
            embed.add_field(
                name="🏆 Scoring",
                value=f"**Total Score:** {scoring_system.format_score(user['total_score'])}\n"
                      f"**Avg Score:** {scoring_system.format_score(avg_score)}\n"
                      f"**Performance:** {performance_rating}",
                inline=True
            )
            
            embed.add_field(
                name="🔥 Streaks",
                value=f"**Current Streak:** {user['current_streak']}\n"
                      f"**Best Streak:** {user['best_streak']}\n"
                      f"**Avg Response:** {user['avg_response_time']:.1f}s",
                inline=True
            )
            
            # Persona info
            embed.add_field(
                name="🎭 Current Persona",
                value=user['preferred_persona'].replace('_', ' ').title(),
                inline=False
            )
            
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_footer(text=f"Member since {user['created_at'].strftime('%B %Y')}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            await interaction.followup.send("Error retrieving stats.", ephemeral=True)
    
    @app_commands.command(name="leaderboard", description="View the global trivia leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """Display the trivia leaderboard."""
        try:
            await interaction.response.defer()
            
            # Get leaderboard data
            users = await db_manager.get_leaderboard("global", None, limit=10)
            
            if not users:
                embed = discord.Embed(
                    title="🏆 Trivia Leaderboard",
                    description="No players found! Be the first to play some trivia!",
                    color=0x0099ff
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create leaderboard embed
            embed = discord.Embed(title="🏆 Global Trivia Leaderboard", color=0xffd700)
            
            leaderboard_text = ""
            medals = ["🥇", "🥈", "🥉"]
            
            for i, user in enumerate(users):
                rank = i + 1
                medal = medals[i] if i < 3 else f"{rank}."
                
                # Calculate normalized score for fair comparison
                normalized_score = scoring_system.normalize_score_for_leaderboard(
                    user.total_score, user.total_games, user.win_rate
                )
                
                leaderboard_text += (
                    f"{medal} **{user.username}**\n"
                    f"    Score: {scoring_system.format_score(normalized_score)} "
                    f"({user.total_games} games, {user.win_rate:.1f}% win rate)\n\n"
                )
            
            embed.description = leaderboard_text
            embed.set_footer(text="Scores are normalized for fair comparison based on games played and win rate")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Failed to get leaderboard: {e}")
            await interaction.followup.send("Error retrieving leaderboard.", ephemeral=True)
    
    @app_commands.command(name="roast", description="Get roasted by your trivia host based on your stats")
    async def roast_me(self, interaction: discord.Interaction):
        """Generate a playful roast based on user's stats."""
        try:
            await interaction.response.defer()
            
            user = await db_manager.get_user_stats(str(interaction.user.id))
            
            if not user or user['total_games'] == 0:
                await interaction.followup.send(
                    "I can't roast you if you haven't played any games! Use `/trivia` to give me some material to work with! 😏",
                    ephemeral=True
                )
                return
            
            # Prepare stats for roast
            user_stats = {
                "win_rate": user['win_rate'],
                "games_played": user['total_games'],
                "avg_score": user['avg_score_per_game'],
                "current_streak": user['current_streak'],
                "best_streak": user['best_streak'],
                "avg_response_time": user['avg_response_time']
            }
            
            # Generate custom roast
            roast = await personality_engine.generate_custom_roast(
                user['preferred_persona'],
                user_stats
            )
            
            embed = discord.Embed(
                title="🔥 You've Been Roasted! 🔥",
                description=roast,
                color=0xff6b35
            )
            
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_footer(text="All in good fun! Use /trivia to prove me wrong! 😈")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Failed to generate roast: {e}")
            await interaction.followup.send("Error generating roast.", ephemeral=True)
    
    @app_commands.command(name="compare", description="Compare your stats with another player")
    @app_commands.describe(user="The user to compare stats with")
    async def compare_stats(self, interaction: discord.Interaction, user: discord.Member):
        """Compare stats between two users."""
        try:
            await interaction.response.defer()
            
            if user.id == interaction.user.id:
                await interaction.followup.send("You can't compare with yourself! 🤔", ephemeral=True)
                return
            
            # Get both users' stats
            user1 = await db_manager.get_user_stats(str(interaction.user.id))
            user2 = await db_manager.get_user_stats(str(user.id))
            
            if not user1 or user1['total_games'] == 0:
                await interaction.followup.send(
                    "You need to play some games first! Use `/trivia` to get started.",
                    ephemeral=True
                )
                return
            
            if not user2 or user2['total_games'] == 0:
                await interaction.followup.send(
                    f"{user.display_name} hasn't played any games yet!",
                    ephemeral=True
                )
                return
            
            # Create comparison embed
            embed = discord.Embed(
                title="⚔️ Stats Comparison",
                color=0x9932cc
            )
            
            # Helper function to format comparison
            def format_comparison(value1, value2, format_func=lambda x: str(x), reverse=False):
                if value1 == value2:
                    return f"{format_func(value1)} 🤝 {format_func(value2)}"
                elif (value1 > value2) != reverse:
                    return f"**{format_func(value1)}** 🏆 {format_func(value2)}"
                else:
                    return f"{format_func(value1)} 🏆 **{format_func(value2)}**"
            
            # Games played
            embed.add_field(
                name="🎮 Games Played",
                value=format_comparison(user1['total_games'], user2['total_games']),
                inline=True
            )
            
            # Win rate
            embed.add_field(
                name="📊 Win Rate",
                value=format_comparison(
                    user1['win_rate'], user2['win_rate'],
                    lambda x: f"{x:.1f}%"
                ),
                inline=True
            )
            
            # Average score
            embed.add_field(
                name="💯 Avg Score",
                value=format_comparison(
                    user1['avg_score_per_game'], user2['avg_score_per_game'],
                    lambda x: scoring_system.format_score(x)
                ),
                inline=True
            )
            
            # Best streak
            embed.add_field(
                name="🔥 Best Streak",
                value=format_comparison(user1['best_streak'], user2['best_streak']),
                inline=True
            )
            
            # Response time (lower is better)
            embed.add_field(
                name="⚡ Avg Response Time",
                value=format_comparison(
                    user1['avg_response_time'], user2['avg_response_time'],
                    lambda x: f"{x:.1f}s",
                    reverse=True
                ),
                inline=True
            )
            
            # Overall performance
            perf1 = scoring_system.get_performance_rating(
                user1['win_rate'], user1['avg_score_per_game'], user1['total_games']
            )
            perf2 = scoring_system.get_performance_rating(
                user2['win_rate'], user2['avg_score_per_game'], user2['total_games']
            )
            
            embed.add_field(
                name="🎖️ Performance Rating",
                value=f"{interaction.user.display_name}: **{perf1}**\n{user.display_name}: **{perf2}**",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Failed to compare stats: {e}")
            await interaction.followup.send("Error comparing stats.", ephemeral=True)
    
    @app_commands.command(name="categories", description="View available trivia categories")
    async def categories(self, interaction: discord.Interaction):
        """Display available trivia categories."""
        try:
            categories = trivia_generator.get_available_categories()
            
            embed = discord.Embed(
                title="📚 Available Trivia Categories",
                description="Here are the built-in categories you can use with `/trivia`:",
                color=0x3498db
            )
            
            # Format categories nicely
            category_list = ""
            for category in categories:
                if category != "random":
                    category_list += f"• **{category.title()}**\n"
            
            category_list += "\n• **Random** - Mixed topics from all categories"
            category_list += "\n\n**Custom Categories:** You can also use any custom category like \"star trek\", \"physics\", \"marvel\", etc!"
            
            embed.add_field(
                name="Categories",
                value=category_list,
                inline=False
            )
            
            embed.set_footer(text="Example: /trivia category:science difficulty:medium")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            await interaction.response.send_message("Error retrieving categories.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(StatsCog(bot))