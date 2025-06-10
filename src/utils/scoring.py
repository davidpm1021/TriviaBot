import math
from typing import Tuple
from config.settings import settings

class ScoringSystem:
    """Handles score calculation and normalization."""
    
    @staticmethod
    def calculate_score(
        is_correct: bool,
        response_time: float,
        difficulty: str = "medium",
        max_time: float = None
    ) -> Tuple[float, float, float]:
        """
        Calculate score with speed bonus.
        
        Args:
            is_correct: Whether the answer was correct
            response_time: Time taken to answer (seconds)
            difficulty: Question difficulty (easy/medium/hard)
            max_time: Maximum time allowed (defaults to config)
            
        Returns:
            Tuple of (base_score, speed_bonus, total_score)
        """
        if not is_correct:
            return 0.0, 0.0, 0.0
        
        # Base score based on difficulty
        difficulty_multipliers = {
            "easy": 1.0,
            "medium": 1.5,
            "hard": 2.0
        }
        
        base_score = settings.BASE_POINTS * difficulty_multipliers.get(difficulty.lower(), 1.5)
        
        # Speed bonus calculation
        max_time = max_time or settings.DEFAULT_QUESTION_TIMEOUT
        speed_bonus = ScoringSystem._calculate_speed_bonus(response_time, max_time, base_score)
        
        total_score = base_score + speed_bonus
        
        return base_score, speed_bonus, total_score
    
    @staticmethod
    def _calculate_speed_bonus(response_time: float, max_time: float, base_score: float) -> float:
        """
        Calculate speed bonus based on response time.
        
        Formula: bonus = base_score * max_bonus * (max(0, max_time - response_time) / max_time)
        """
        if response_time >= max_time:
            return 0.0
        
        # Time remaining as percentage of max time
        time_factor = max(0, max_time - response_time) / max_time
        
        # Apply diminishing returns using square root
        time_factor = math.sqrt(time_factor)
        
        speed_bonus = base_score * settings.MAX_SPEED_BONUS * time_factor
        
        return round(speed_bonus, 2)
    
    @staticmethod
    def calculate_streak_bonus(streak: int, base_score: float) -> float:
        """
        Calculate bonus points for answer streaks.
        
        Args:
            streak: Current correct answer streak
            base_score: Base score for the question
            
        Returns:
            Streak bonus points
        """
        if streak <= 1:
            return 0.0
        
        # Streak bonus: 10% of base score per streak level (capped at 100%)
        streak_multiplier = min((streak - 1) * 0.1, 1.0)
        streak_bonus = base_score * streak_multiplier
        
        return round(streak_bonus, 2)
    
    @staticmethod
    def normalize_score_for_leaderboard(
        total_score: float,
        games_played: int,
        win_rate: float
    ) -> float:
        """
        Normalize score for fair leaderboard comparison.
        
        Considers both total score and consistency (win rate).
        """
        if games_played == 0:
            return 0.0
        
        # Average score per game
        avg_score = total_score / games_played
        
        # Consistency bonus: reward high win rates
        consistency_multiplier = 1.0 + (win_rate / 100 * 0.5)  # Up to 50% bonus
        
        # Experience factor: slight bonus for more games played (diminishing returns)
        experience_factor = 1.0 + (math.log(games_played + 1) / 20)  # Small logarithmic bonus
        
        normalized_score = avg_score * consistency_multiplier * experience_factor
        
        return round(normalized_score, 2)
    
    @staticmethod
    def get_performance_rating(win_rate: float, avg_score: float, games_played: int) -> str:
        """
        Get a performance rating based on stats.
        
        Returns:
            Performance rating string
        """
        if games_played < 5:
            return "Novice"
        
        # Calculate overall performance score
        performance_score = (win_rate * 0.6) + (min(avg_score / 200, 1.0) * 40)
        
        if performance_score >= 85:
            return "Grandmaster"
        elif performance_score >= 75:
            return "Expert"
        elif performance_score >= 65:
            return "Advanced"
        elif performance_score >= 50:
            return "Intermediate"
        elif performance_score >= 35:
            return "Beginner"
        else:
            return "Learning"
    
    @staticmethod
    def format_score(score: float) -> str:
        """Format score for display."""
        if score == int(score):
            return str(int(score))
        return f"{score:.1f}"

# Global scoring system instance
scoring_system = ScoringSystem()