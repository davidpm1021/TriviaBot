import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
import time
from typing import Dict, Optional, Any
from datetime import datetime

from src.trivia.generator import trivia_generator, TriviaQuestion
from src.personality.response_generator import personality_engine
from src.personality.personas import ResponseType
from src.utils.scoring import scoring_system
from src.database.database import db_manager

class TriviaGame:
    """Represents an active trivia game session."""
    
    def __init__(self, user_id: int, channel_id: int, persona: str = "sarcastic_host"):
        self.user_id = user_id
        self.channel_id = channel_id
        self.persona = persona
        self.current_question: Optional[TriviaQuestion] = None
        self.start_time: Optional[float] = None
        self.is_active = False
        self.timeout_task: Optional[asyncio.Task] = None

class TriviaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('TriviaBot.Trivia')
        self.active_games: Dict[int, TriviaGame] = {}  # user_id -> TriviaGame
        
        # Initialize database on cog load
        self.bot.loop.create_task(self._initialize_database())
    
    async def _initialize_database(self):
        """Initialize database tables."""
        try:
            await db_manager.create_tables()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
    
    @app_commands.command(name="trivia", description="Start a trivia question")
    @app_commands.describe(
        category="Category of trivia question",
        difficulty="Difficulty level (easy/medium/hard)",
        era="Time period for the question"
    )
    async def trivia(
        self,
        interaction: discord.Interaction,
        category: Optional[str] = "random",
        difficulty: Optional[str] = "medium",
        era: Optional[str] = "any"
    ):
        """Start a new trivia question."""
        user_id = interaction.user.id
        
        # Check if user already has an active game
        if user_id in self.active_games and self.active_games[user_id].is_active:
            await interaction.response.send_message(
                "You already have an active trivia question! Answer it first or use `/skip` to skip it.",
                ephemeral=True
            )
            return
        
        try:
            await interaction.response.defer()
            
            # Get or create user in database
            user = await db_manager.get_or_create_user(str(user_id), interaction.user.display_name)
            
            # Generate question
            question = await trivia_generator.generate_question(category, difficulty, era)
            
            # Create game session
            game = TriviaGame(user_id, interaction.channel.id, user.preferred_persona)
            game.current_question = question
            game.start_time = time.time()
            game.is_active = True
            
            self.active_games[user_id] = game
            
            # Generate personality response
            intro_response = await personality_engine.generate_response(
                ResponseType.QUESTION_INTRO,
                user.preferred_persona,
                {"category": question.category, "difficulty": question.difficulty}
            )
            
            # Create embed
            embed = self._create_question_embed(question, intro_response)
            
            # Send question and start timeout
            await interaction.followup.send(embed=embed)
            
            # Set up timeout
            game.timeout_task = asyncio.create_task(
                self._handle_question_timeout(user_id, interaction.channel)
            )
            
            self.logger.info(f"Started trivia for user {user_id}: {question.category}/{question.difficulty}")
            
        except Exception as e:
            self.logger.error(f"Failed to start trivia: {e}")
            await interaction.followup.send(
                "Sorry, I couldn't generate a trivia question right now. Please try again!",
                ephemeral=True
            )
    
    @app_commands.command(name="answer", description="Answer the current trivia question")
    @app_commands.describe(answer="Your answer (A, B, C, or D)")
    async def answer(self, interaction: discord.Interaction, answer: str):
        """Submit an answer to the current trivia question."""
        user_id = interaction.user.id
        
        # Check if user has an active game
        if user_id not in self.active_games or not self.active_games[user_id].is_active:
            await interaction.response.send_message(
                "You don't have an active trivia question! Use `/trivia` to start one.",
                ephemeral=True
            )
            return
        
        try:
            await interaction.response.defer()
            
            game = self.active_games[user_id]
            question = game.current_question
            response_time = time.time() - game.start_time
            
            # Cancel timeout task
            if game.timeout_task:
                game.timeout_task.cancel()
            
            # Validate answer format
            answer = answer.upper().strip()
            if answer not in ['A', 'B', 'C', 'D']:
                await interaction.followup.send(
                    "Please provide a valid answer: A, B, C, or D",
                    ephemeral=True
                )
                return
            
            # Check if answer is correct
            is_correct = answer == question.correct_answer.upper()
            
            # Calculate score
            base_score, speed_bonus, total_score = scoring_system.calculate_score(
                is_correct, response_time, question.difficulty
            )
            
            # Get user from database
            user = await db_manager.get_or_create_user(str(user_id), interaction.user.display_name)
            
            # Save game session to database
            game_data = {
                "user_id": user.id,
                "question_text": question.question,
                "category": question.category,
                "difficulty": question.difficulty,
                "era": question.era,
                "correct_answer": question.correct_answer,
                "user_answer": answer,
                "is_correct": is_correct,
                "response_time": response_time,
                "base_score": base_score,
                "speed_bonus": speed_bonus,
                "total_score": total_score,
                "persona_used": game.persona,
                "completed_at": datetime.utcnow()
            }
            
            await db_manager.save_game_session(game_data)
            
            # Generate personality response
            response_type = ResponseType.CORRECT_ANSWER if is_correct else ResponseType.WRONG_ANSWER
            response_context = {
                "score": total_score,
                "user_name": interaction.user.display_name,
                "response_time": response_time
            }
            
            personality_response = await personality_engine.generate_response(
                response_type, game.persona, response_context
            )
            
            # Create result embed
            embed = self._create_result_embed(
                question, answer, is_correct, total_score, response_time, personality_response
            )
            
            await interaction.followup.send(embed=embed)
            
            # Check for streak bonus
            if is_correct and user.current_streak > 1:
                streak_response = await personality_engine.generate_response(
                    ResponseType.STREAK_BONUS,
                    game.persona,
                    {"streak": user.current_streak}
                )
                await interaction.followup.send(streak_response)
            
            # Clean up game
            game.is_active = False
            del self.active_games[user_id]
            
            self.logger.info(f"User {user_id} answered: {answer} ({'correct' if is_correct else 'wrong'})")
            
        except Exception as e:
            self.logger.error(f"Failed to process answer: {e}")
            await interaction.followup.send(
                "Sorry, there was an error processing your answer. Please try again!",
                ephemeral=True
            )
    
    @app_commands.command(name="skip", description="Skip the current trivia question")
    async def skip(self, interaction: discord.Interaction):
        """Skip the current trivia question."""
        user_id = interaction.user.id
        
        if user_id not in self.active_games or not self.active_games[user_id].is_active:
            await interaction.response.send_message(
                "You don't have an active trivia question to skip!",
                ephemeral=True
            )
            return
        
        try:
            game = self.active_games[user_id]
            
            # Cancel timeout task
            if game.timeout_task:
                game.timeout_task.cancel()
            
            # Show correct answer
            question = game.current_question
            correct_option = question.options[ord(question.correct_answer.upper()) - ord('A')]
            
            embed = discord.Embed(
                title="Question Skipped",
                description=f"The correct answer was **{question.correct_answer}: {correct_option}**",
                color=0xffff00
            )
            
            if question.explanation:
                embed.add_field(name="Explanation", value=question.explanation, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Clean up game
            game.is_active = False
            del self.active_games[user_id]
            
            self.logger.info(f"User {user_id} skipped question")
            
        except Exception as e:
            self.logger.error(f"Failed to skip question: {e}")
            await interaction.response.send_message("Error skipping question.", ephemeral=True)
    
    @app_commands.command(name="persona", description="Change your trivia host personality")
    @app_commands.describe(persona="Choose your trivia host personality")
    async def set_persona(self, interaction: discord.Interaction, persona: str):
        """Change the user's preferred persona."""
        try:
            available_personas = personality_engine.get_available_personas()
            
            if persona.lower() not in available_personas:
                embed = discord.Embed(
                    title="Available Personas",
                    description="Choose from these available personalities:",
                    color=0x0099ff
                )
                
                for name, description in available_personas.items():
                    embed.add_field(name=name.title(), value=description, inline=False)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Update user's preferred persona in database
            user = await db_manager.get_or_create_user(str(interaction.user.id), interaction.user.display_name)
            
            async with db_manager.get_session() as session:
                user.preferred_persona = persona.lower()
            
            # Update active game if exists
            if interaction.user.id in self.active_games:
                self.active_games[interaction.user.id].persona = persona.lower()
            
            await interaction.response.send_message(
                f"Your trivia host is now **{persona.title()}**! 🎭",
                ephemeral=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to set persona: {e}")
            await interaction.response.send_message("Error setting persona.", ephemeral=True)
    
    async def _handle_question_timeout(self, user_id: int, channel):
        """Handle question timeout."""
        try:
            await asyncio.sleep(30)  # 30 second timeout
            
            if user_id in self.active_games and self.active_games[user_id].is_active:
                game = self.active_games[user_id]
                question = game.current_question
                
                # Show timeout message
                correct_option = question.options[ord(question.correct_answer.upper()) - ord('A')]
                
                embed = discord.Embed(
                    title="⏰ Time's Up!",
                    description=f"The correct answer was **{question.correct_answer}: {correct_option}**",
                    color=0xff6b6b
                )
                
                if question.explanation:
                    embed.add_field(name="Explanation", value=question.explanation, inline=False)
                
                await channel.send(embed=embed)
                
                # Clean up game
                game.is_active = False
                del self.active_games[user_id]
                
        except asyncio.CancelledError:
            pass  # Task was cancelled, ignore
        except Exception as e:
            self.logger.error(f"Error in timeout handler: {e}")
    
    def _create_question_embed(self, question: TriviaQuestion, intro_text: str) -> discord.Embed:
        """Create embed for trivia question."""
        embed = discord.Embed(
            title="🧠 Trivia Question",
            description=intro_text,
            color=0x0099ff
        )
        
        embed.add_field(name="Question", value=question.question, inline=False)
        
        # Add options
        options_text = ""
        for i, option in enumerate(question.options):
            letter = chr(ord('A') + i)
            options_text += f"**{letter}:** {option}\n"
        
        embed.add_field(name="Options", value=options_text, inline=False)
        
        # Add metadata
        metadata = f"Category: {question.category} | Difficulty: {question.difficulty.title()}"
        if question.era:
            metadata += f" | Era: {question.era.title()}"
        
        embed.set_footer(text=f"{metadata} | Use /answer [A/B/C/D] to respond")
        
        return embed
    
    def _create_result_embed(
        self,
        question: TriviaQuestion,
        user_answer: str,
        is_correct: bool,
        score: float,
        response_time: float,
        personality_response: str
    ) -> discord.Embed:
        """Create embed for answer result."""
        color = 0x00ff00 if is_correct else 0xff0000
        title = "✅ Correct!" if is_correct else "❌ Incorrect!"
        
        embed = discord.Embed(
            title=title,
            description=personality_response,
            color=color
        )
        
        # Show correct answer
        correct_option = question.options[ord(question.correct_answer.upper()) - ord('A')]
        embed.add_field(
            name="Correct Answer",
            value=f"**{question.correct_answer}: {correct_option}**",
            inline=False
        )
        
        if question.explanation:
            embed.add_field(name="Explanation", value=question.explanation, inline=False)
        
        # Show score and time
        if is_correct:
            embed.add_field(
                name="Score",
                value=f"{scoring_system.format_score(score)} points",
                inline=True
            )
        
        embed.add_field(
            name="Response Time",
            value=f"{response_time:.1f}s",
            inline=True
        )
        
        return embed

async def setup(bot):
    await bot.add_cog(TriviaCog(bot))