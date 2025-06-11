import openai
import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config.settings import settings
import random

@dataclass
class TriviaQuestion:
    question: str
    options: List[str]
    correct_answer: str
    category: str
    difficulty: str
    era: Optional[str] = None
    explanation: Optional[str] = None

class TriviaGenerator:
    def __init__(self):
        self.logger = logging.getLogger('TriviaBot.TriviaGenerator')
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Predefined categories and their subcategories
        self.categories = {
            "science": ["Physics", "Chemistry", "Biology", "Astronomy", "Earth Science"],
            "history": ["Ancient History", "Modern History", "World Wars", "American History", "European History"],
            "geography": ["World Geography", "Capitals", "Mountains", "Rivers", "Countries"],
            "entertainment": ["Movies", "Music", "TV Shows", "Celebrities", "Games"],
            "sports": ["Football", "Basketball", "Baseball", "Soccer", "Olympics"],
            "literature": ["Classic Literature", "Poetry", "Authors", "Nobel Prize Winners"],
            "technology": ["Computer Science", "Internet", "Inventions", "Software"],
            "art": ["Painting", "Sculpture", "Architecture", "Famous Artists"],
            "food": ["Cuisine", "Cooking", "Restaurants", "Ingredients"],
            "random": ["Mixed Topics"]
        }
        
        self.difficulties = ["easy", "medium", "hard"]
        self.eras = ["ancient", "medieval", "renaissance", "modern", "contemporary", "any"]
    
    def generate_question(
        self, 
        category: str = "random", 
        difficulty: str = "medium", 
        era: str = "any"
    ) -> TriviaQuestion:
        """Generate a trivia question using OpenAI."""
        try:
            # Normalize inputs
            category = category.lower()
            difficulty = difficulty.lower()
            era = era.lower()
            
            # Validate inputs
            if category not in self.categories and category != "random":
                category = "random"
            if difficulty not in self.difficulties:
                difficulty = "medium"
            if era not in self.eras:
                era = "any"
            
            # Get specific subcategory if applicable
            specific_category = self._get_specific_category(category)
            
            # Create the prompt
            prompt = self._create_trivia_prompt(specific_category, difficulty, era)
            
            # Temporarily use fallback questions to debug the OpenAI issue
            question = self._get_fallback_question(category, difficulty)
            
            # TODO: Re-enable OpenAI generation after fixing the issue
            # response = self._call_openai(prompt)
            # question = self._parse_response(response, specific_category, difficulty, era)
            
            self.logger.info(f"Generated question: {category}/{difficulty}/{era}")
            return question
            
        except Exception as e:
            self.logger.error(f"Failed to generate question: {e}")
            # Return a fallback question
            return self._get_fallback_question(category, difficulty)
    
    def _get_specific_category(self, category: str) -> str:
        """Get a specific subcategory or return the category itself."""
        if category == "random":
            # Pick a random category and subcategory
            random_cat = random.choice(list(self.categories.keys()))
            if random_cat != "random":
                return random.choice(self.categories[random_cat])
            return "General Knowledge"
        elif category in self.categories:
            return random.choice(self.categories[category])
        return category.title()
    
    def _create_trivia_prompt(self, category: str, difficulty: str, era: str) -> str:
        """Create a prompt for OpenAI to generate trivia questions."""
        era_context = ""
        if era != "any":
            era_context = f" from the {era} era"
        
        difficulty_context = {
            "easy": "suitable for beginners, with well-known facts",
            "medium": "moderately challenging, requiring some knowledge",
            "hard": "challenging, requiring specialized or detailed knowledge"
        }
        
        prompt = f"""Generate a multiple-choice trivia question about {category}{era_context}.

Requirements:
- Difficulty: {difficulty} ({difficulty_context[difficulty]})
- Provide exactly 4 answer choices (A, B, C, D)
- Only one correct answer
- Question should be clear and unambiguous
- Avoid questions that require extremely specific dates or obscure facts
- Include a brief explanation of the correct answer

Format your response as JSON:
{{
    "question": "Your question here?",
    "options": {{
        "A": "First option",
        "B": "Second option", 
        "C": "Third option",
        "D": "Fourth option"
    }},
    "correct_answer": "A",
    "explanation": "Brief explanation of why this is correct"
}}

Generate the question now:"""
        
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Make API call to OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a trivia question generator. Always respond with valid JSON in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_response(self, response: str, category: str, difficulty: str, era: str) -> TriviaQuestion:
        """Parse OpenAI response into TriviaQuestion object."""
        try:
            # Clean the response - remove markdown code blocks if present
            response = re.sub(r'```json\s*', '', response)
            response = re.sub(r'```\s*$', '', response)
            
            # Parse JSON
            data = json.loads(response)
            
            # Extract data
            question_text = data["question"]
            options_dict = data["options"]
            correct_answer = data["correct_answer"]
            explanation = data.get("explanation", "")
            
            # Convert options to list
            options = [
                options_dict["A"],
                options_dict["B"], 
                options_dict["C"],
                options_dict["D"]
            ]
            
            return TriviaQuestion(
                question=question_text,
                options=options,
                correct_answer=correct_answer,
                category=category,
                difficulty=difficulty,
                era=era if era != "any" else None,
                explanation=explanation
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Failed to parse OpenAI response: {e}")
            self.logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid response format from AI: {e}")
    
    def _get_fallback_question(self, category: str, difficulty: str) -> TriviaQuestion:
        """Return a fallback question if AI generation fails."""
        fallback_questions = {
            "easy": {
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": "C",
                "explanation": "Paris has been the capital of France since ancient times."
            },
            "medium": {
                "question": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct_answer": "B", 
                "explanation": "Mars appears red due to iron oxide (rust) on its surface."
            },
            "hard": {
                "question": "What is the smallest prime number?",
                "options": ["0", "1", "2", "3"],
                "correct_answer": "C",
                "explanation": "2 is the smallest and only even prime number."
            }
        }
        
        fallback = fallback_questions.get(difficulty, fallback_questions["medium"])
        
        return TriviaQuestion(
            question=fallback["question"],
            options=fallback["options"],
            correct_answer=fallback["correct_answer"],
            category=category,
            difficulty=difficulty,
            explanation=fallback["explanation"]
        )
    
    def get_available_categories(self) -> List[str]:
        """Get list of available categories."""
        return list(self.categories.keys())
    
    def get_available_difficulties(self) -> List[str]:
        """Get list of available difficulties."""
        return self.difficulties.copy()
    
    def get_available_eras(self) -> List[str]:
        """Get list of available eras."""
        return self.eras.copy()

# Global trivia generator instance
trivia_generator = TriviaGenerator()