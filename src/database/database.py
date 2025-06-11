from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator, Optional
from config.settings import settings
from .models import Base, User, GameSession, UserStats, Leaderboard, PersonaSettings

class DatabaseManager:
    def __init__(self):
        self.logger = logging.getLogger('TriviaBot.Database')
        self.engine = None
        self.async_session = None
        self._setup_database()
    
    def _setup_database(self):
        """Set up database connection and session."""
        try:
            # Handle different database URLs
            db_url = settings.DATABASE_URL
            
            if db_url.startswith('sqlite'):
                # For SQLite, use synchronous engine
                self.engine = create_engine(db_url, echo=settings.DEBUG_MODE)
                self.SessionLocal = sessionmaker(bind=self.engine)
            else:
                # For PostgreSQL, use async engine
                if not db_url.startswith('postgresql+asyncpg'):
                    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
                
                self.engine = create_async_engine(db_url, echo=settings.DEBUG_MODE)
                self.async_session = async_sessionmaker(self.engine, class_=AsyncSession)
            
            self.logger.info("Database connection established")
            
        except Exception as e:
            self.logger.error(f"Failed to setup database: {e}")
            raise
    
    async def create_tables(self):
        """Create all database tables."""
        try:
            if hasattr(self, 'async_session') and self.async_session:
                # PostgreSQL async
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            else:
                # SQLite sync
                Base.metadata.create_all(bind=self.engine)
            
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Failed to create tables: {e}")
            raise
    
    def get_session(self):
        """Get database session context manager."""
        if hasattr(self, 'async_session') and self.async_session:
            return self._async_session_context()
        else:
            return self._sync_session_context()
    
    @asynccontextmanager
    async def _async_session_context(self):
        """Async session context manager."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    @asynccontextmanager
    async def _sync_session_context(self):
        """Sync session context manager for SQLite."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def get_or_create_user(self, discord_id: str, username: str) -> User:
        """Get existing user or create new one."""
        # For SQLite, we need to handle this synchronously
        if hasattr(self, 'async_session') and self.async_session:
            # PostgreSQL async path
            async with self._async_session_context() as session:
                user = await self._find_user_by_discord_id(session, discord_id)
                
                if not user:
                    user = User(discord_id=discord_id, username=username)
                    session.add(user)
                    await session.flush()
                    self.logger.info(f"Created new user: {username} ({discord_id})")
                else:
                    if user.username != username:
                        user.username = username
                        self.logger.info(f"Updated username for {discord_id}: {username}")
                
                return user
        else:
            # SQLite sync path - run in thread
            import asyncio
            return await asyncio.to_thread(self._get_or_create_user_sync, discord_id, username)
    
    def _get_or_create_user_sync(self, discord_id: str, username: str) -> User:
        """Synchronous version for SQLite."""
        session = self.SessionLocal()
        try:
            user = session.query(User).filter(User.discord_id == discord_id).first()
            
            if not user:
                user = User(discord_id=discord_id, username=username)
                session.add(user)
                session.flush()  # Get the ID
                self.logger.info(f"Created new user: {username} ({discord_id})")
            else:
                if user.username != username:
                    user.username = username
                    self.logger.info(f"Updated username for {discord_id}: {username}")
            
            session.commit()
            
            # Detach from session to avoid issues when using outside the session
            session.expunge(user)
            return user
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def _find_user_by_discord_id(self, session: Session, discord_id: str) -> Optional[User]:
        """Find user by Discord ID."""
        if hasattr(session, 'execute'):
            # Async session
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.discord_id == discord_id))
            return result.scalar_one_or_none()
        else:
            # Sync session
            return session.query(User).filter(User.discord_id == discord_id).first()
    
    async def save_game_session(self, game_data: dict) -> GameSession:
        """Save a completed game session."""
        if hasattr(self, 'async_session') and self.async_session:
            # PostgreSQL async path
            async with self._async_session_context() as session:
                game_session = GameSession(**game_data)
                session.add(game_session)
                await session.flush()
                await self._update_user_stats(session, game_session)
                return game_session
        else:
            # SQLite sync path
            import asyncio
            return await asyncio.to_thread(self._save_game_session_sync, game_data)
    
    def _save_game_session_sync(self, game_data: dict) -> GameSession:
        """Synchronous version for SQLite."""
        session = self.SessionLocal()
        try:
            game_session = GameSession(**game_data)
            session.add(game_session)
            session.flush()
            
            # Update user stats
            self._update_user_stats_sync(session, game_session)
            
            session.commit()
            return game_session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def _update_user_stats(self, session: Session, game_session: GameSession):
        """Update user statistics after a game."""
        user = game_session.user
        
        # Update user totals
        user.total_games += 1
        user.total_score += game_session.total_score
        
        if game_session.is_correct:
            user.total_wins += 1
            user.current_streak += 1
            user.best_streak = max(user.best_streak, user.current_streak)
        else:
            user.current_streak = 0
        
        # Update average response time
        if user.total_games == 1:
            user.avg_response_time = game_session.response_time
        else:
            user.avg_response_time = (
                (user.avg_response_time * (user.total_games - 1) + game_session.response_time) 
                / user.total_games
            )
        
        # Update category stats
        await self._update_category_stats(session, game_session)
    
    def _update_user_stats_sync(self, session: Session, game_session: GameSession):
        """Synchronous version of update user statistics."""
        # Get user from database
        user = session.query(User).filter(User.id == game_session.user_id).first()
        
        # Update user totals
        user.total_games += 1
        user.total_score += game_session.total_score
        
        if game_session.is_correct:
            user.total_wins += 1
            user.current_streak += 1
            user.best_streak = max(user.best_streak, user.current_streak)
        else:
            user.current_streak = 0
        
        # Update average response time
        if user.total_games == 1:
            user.avg_response_time = game_session.response_time
        else:
            user.avg_response_time = (
                (user.avg_response_time * (user.total_games - 1) + game_session.response_time) 
                / user.total_games
            )
        
        # Update category stats
        self._update_category_stats_sync(session, game_session)
    
    def _update_category_stats_sync(self, session: Session, game_session: GameSession):
        """Synchronous version of update category statistics."""
        if not game_session.category:
            return
        
        # Find or create category stats
        stats = session.query(UserStats).filter(
            UserStats.user_id == game_session.user_id,
            UserStats.category == game_session.category
        ).first()
        
        if not stats:
            stats = UserStats(
                user_id=game_session.user_id,
                category=game_session.category
            )
            session.add(stats)
        
        # Update stats
        stats.games_played += 1
        stats.total_score += game_session.total_score
        
        if game_session.is_correct:
            stats.games_won += 1
        
        # Update average response time
        if stats.games_played == 1:
            stats.avg_response_time = game_session.response_time
        else:
            stats.avg_response_time = (
                (stats.avg_response_time * (stats.games_played - 1) + game_session.response_time)
                / stats.games_played
            )
        
        # Calculate mastery level
        win_rate = (stats.games_won / stats.games_played) * 100 if stats.games_played > 0 else 0
        games_factor = min(stats.games_played / 10, 1.0)
        stats.mastery_level = win_rate * games_factor
    
    async def _update_category_stats(self, session: Session, game_session: GameSession):
        """Update category-specific statistics."""
        if not game_session.category:
            return
        
        # Find or create category stats
        if hasattr(session, 'execute'):
            from sqlalchemy import select
            result = await session.execute(
                select(UserStats).where(
                    UserStats.user_id == game_session.user_id,
                    UserStats.category == game_session.category
                )
            )
            stats = result.scalar_one_or_none()
        else:
            stats = session.query(UserStats).filter(
                UserStats.user_id == game_session.user_id,
                UserStats.category == game_session.category
            ).first()
        
        if not stats:
            stats = UserStats(
                user_id=game_session.user_id,
                category=game_session.category
            )
            session.add(stats)
        
        # Update stats
        stats.games_played += 1
        stats.total_score += game_session.total_score
        
        if game_session.is_correct:
            stats.games_won += 1
        
        # Update average response time
        if stats.games_played == 1:
            stats.avg_response_time = game_session.response_time
        else:
            stats.avg_response_time = (
                (stats.avg_response_time * (stats.games_played - 1) + game_session.response_time)
                / stats.games_played
            )
        
        # Calculate mastery level (simplified: based on win rate and games played)
        win_rate = stats.win_rate
        games_factor = min(stats.games_played / 10, 1.0)  # Factor in experience
        stats.mastery_level = win_rate * games_factor
    
    async def get_user_stats(self, discord_id: str) -> Optional[User]:
        """Get user statistics."""
        async with self.get_session() as session:
            return await self._find_user_by_discord_id(session, discord_id)
    
    async def get_leaderboard(self, leaderboard_type: str = 'global', category: str = None, limit: int = 10):
        """Get leaderboard data."""
        async with self.get_session() as session:
            if hasattr(session, 'execute'):
                from sqlalchemy import select, desc
                query = select(User).order_by(desc(User.total_score)).limit(limit)
                result = await session.execute(query)
                return result.scalars().all()
            else:
                return session.query(User).order_by(User.total_score.desc()).limit(limit).all()

# Global database manager instance
db_manager = DatabaseManager()