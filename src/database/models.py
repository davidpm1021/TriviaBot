from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(String(20), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    total_games = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    preferred_persona = Column(String(50), default='sarcastic_host')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game_sessions = relationship("GameSession", back_populates="user")
    user_stats = relationship("UserStats", back_populates="user")
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_games == 0:
            return 0.0
        return (self.total_wins / self.total_games) * 100
    
    @property
    def avg_score_per_game(self) -> float:
        """Calculate average score per game."""
        if self.total_games == 0:
            return 0.0
        return self.total_score / self.total_games

class GameSession(Base):
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String(100))
    difficulty = Column(String(20))
    era = Column(String(50))
    correct_answer = Column(String(500), nullable=False)
    user_answer = Column(String(500))
    is_correct = Column(Boolean, default=False)
    response_time = Column(Float)  # in seconds
    base_score = Column(Float, default=0.0)
    speed_bonus = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
    persona_used = Column(String(50), default='sarcastic_host')
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="game_sessions")

class UserStats(Base):
    __tablename__ = 'user_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category = Column(String(100), nullable=False)
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    avg_response_time = Column(Float, default=0.0)
    mastery_level = Column(Float, default=0.0)  # 0-100 scale
    
    # Relationships
    user = relationship("User", back_populates="user_stats")
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate for this category."""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

class Leaderboard(Base):
    __tablename__ = 'leaderboard'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    leaderboard_type = Column(String(50), nullable=False)  # 'global', 'weekly', 'category'
    category = Column(String(100))  # null for global leaderboards
    rank = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class PersonaSettings(Base):
    __tablename__ = 'persona_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    guild_id = Column(String(20))  # null for DM settings
    persona_name = Column(String(50), nullable=False)
    custom_prompts = Column(Text)  # JSON string of custom persona prompts
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")