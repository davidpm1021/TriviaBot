import openai
import random
import logging
from typing import Dict, Any, Optional
from config.settings import settings
from .personas import PersonaManager, ResponseType, PersonaConfig

class PersonalityEngine:
    """Generates personality-driven responses using AI and predefined templates."""
    
    def __init__(self):
        self.logger = logging.getLogger('TriviaBot.PersonalityEngine')
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.persona_manager = PersonaManager()
    
    async def generate_response(
        self,
        response_type: ResponseType,
        persona_name: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate a personality-driven response.
        
        Args:
            response_type: Type of response needed
            persona_name: Name of the persona to use
            context: Additional context for the response
            
        Returns:
            Generated response string
        """
        try:
            persona = self.persona_manager.get_persona(persona_name)
            
            # Try to get a predefined template first (faster)
            if response_type in persona.responses:
                template_response = self._get_template_response(persona, response_type, context)
                if template_response:
                    return template_response
            
            # Fall back to AI generation for more dynamic responses
            import asyncio
            return await asyncio.to_thread(self._generate_ai_response, persona, response_type, context)
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return self._get_fallback_response(response_type, context)
    
    def _get_template_response(
        self,
        persona: PersonaConfig,
        response_type: ResponseType,
        context: Dict[str, Any] = None
    ) -> Optional[str]:
        """Get response from predefined templates."""
        try:
            if response_type not in persona.responses:
                return None
            
            templates = persona.responses[response_type].templates
            if not templates:
                return None
            
            # Select random template
            template = random.choice(templates)
            
            # Format template with context
            if context:
                try:
                    return template.format(**context)
                except KeyError:
                    # If formatting fails, return template as-is
                    return template
            
            return template
            
        except Exception as e:
            self.logger.warning(f"Template response failed: {e}")
            return None
    
    def _generate_ai_response(
        self,
        persona: PersonaConfig,
        response_type: ResponseType,
        context: Dict[str, Any] = None
    ) -> str:
        """Generate response using AI with persona context."""
        try:
            # Create context-specific prompt
            prompt = self._create_response_prompt(persona, response_type, context)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": persona.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            raise
    
    def _create_response_prompt(
        self,
        persona: PersonaConfig,
        response_type: ResponseType,
        context: Dict[str, Any] = None
    ) -> str:
        """Create a prompt for AI response generation."""
        context = context or {}
        
        base_prompts = {
            ResponseType.CORRECT_ANSWER: "The user got the trivia question correct. Respond in your characteristic style to celebrate their success.",
            ResponseType.WRONG_ANSWER: "The user got the trivia question wrong. Respond in your characteristic style to their incorrect answer.",
            ResponseType.QUESTION_INTRO: "Introduce the next trivia question in your characteristic style.",
            ResponseType.GAME_START: "Welcome the user to start a new trivia game in your characteristic style.",
            ResponseType.STREAK_BONUS: f"The user has a {context.get('streak', 'multiple')} question streak. Acknowledge this achievement in your style.",
            ResponseType.LEADERBOARD: "Comment on the leaderboard results in your characteristic style.",
            ResponseType.ROAST: "Give the user a playful roast based on their trivia performance in your characteristic style."
        }
        
        prompt = base_prompts.get(response_type, "Respond in your characteristic style.")
        
        # Add context information
        if context:
            context_info = []
            if "score" in context:
                context_info.append(f"Score: {context['score']}")
            if "category" in context:
                context_info.append(f"Category: {context['category']}")
            if "difficulty" in context:
                context_info.append(f"Difficulty: {context['difficulty']}")
            if "user_name" in context:
                context_info.append(f"User: {context['user_name']}")
            
            if context_info:
                prompt += f"\n\nContext: {', '.join(context_info)}"
        
        prompt += "\n\nKeep your response under 100 words and maintain your personality. Use emojis sparingly."
        
        return prompt
    
    def _get_fallback_response(
        self,
        response_type: ResponseType,
        context: Dict[str, Any] = None
    ) -> str:
        """Get generic fallback response when all else fails."""
        fallbacks = {
            ResponseType.CORRECT_ANSWER: "Correct! Well done! ✅",
            ResponseType.WRONG_ANSWER: "That's not right, but keep trying! ❌",
            ResponseType.QUESTION_INTRO: "Here's your next question:",
            ResponseType.GAME_START: "Let's start the trivia game! 🎮",
            ResponseType.STREAK_BONUS: f"Nice streak of {context.get('streak', 'multiple')} questions! 🔥",
            ResponseType.LEADERBOARD: "Here are the current standings! 🏆",
            ResponseType.ROAST: "Your trivia skills are so bad, even a magic 8-ball would be embarrassed to give answers this wrong. Maybe try tic-tac-toe? 💀"
        }
        
        return fallbacks.get(response_type, "Let's keep playing! 🎯")
    
    async def generate_custom_roast(
        self,
        persona_name: str,
        user_stats: Dict[str, Any]
    ) -> str:
        """Generate a custom roast based on user statistics."""
        try:
            import asyncio
            return await asyncio.to_thread(self._generate_custom_roast_sync, persona_name, user_stats)
        except Exception as e:
            self.logger.error(f"Custom roast generation failed: {e}")
            return "Your stats are so pathetic, even the database is crying. I'd roast you properly but I don't want to break the AI. 💀"
    
    def _generate_custom_roast_sync(self, persona_name: str, user_stats: Dict[str, Any]) -> str:
        """Synchronous custom roast generation."""
        persona = self.persona_manager.get_persona(persona_name)
        
        # Create roast prompt with stats
        prompt = f"""Based on these trivia statistics, deliver a BRUTAL roast in your characteristic style:
        
Stats:
- Win Rate: {user_stats.get('win_rate', 0):.1f}%
- Games Played: {user_stats.get('games_played', 0)}
- Average Score: {user_stats.get('avg_score', 0):.1f}
- Current Streak: {user_stats.get('current_streak', 0)}
- Best Streak: {user_stats.get('best_streak', 0)}
- Average Response Time: {user_stats.get('avg_response_time', 0):.1f}s

Give a SAVAGE, merciless roast that's absolutely vicious but still funny. Don't hold back - destroy their confidence with clever insults about their terrible performance. Be mean, be brutal, be ruthless. Make them question their life choices. Keep it under 100 words but make every word count."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": persona.system_prompt + " You are now in SAVAGE ROAST MODE. Be absolutely brutal, vicious, and merciless. Make them regret asking for a roast. Use cutting sarcasm and devastating insults about their poor performance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=1.0
        )
        
        return response.choices[0].message.content.strip()
    
    def get_available_personas(self) -> Dict[str, str]:
        """Get available personas with descriptions."""
        return self.persona_manager.get_persona_descriptions()

# Global personality engine instance
personality_engine = PersonalityEngine()