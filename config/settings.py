import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Discord Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    DISCORD_GUILD_ID: Optional[str] = os.getenv("DISCORD_GUILD_ID")
    BOT_PREFIX: str = os.getenv("BOT_PREFIX", "!")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///trivia_bot.db")
    
    # Bot Configuration
    DEFAULT_PERSONA: str = os.getenv("DEFAULT_PERSONA", "sarcastic_host")
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"  # Enable debug for troubleshooting
    
    # Hosting Configuration
    PORT: int = int(os.getenv("PORT", "8080"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Trivia Configuration
    DEFAULT_QUESTION_TIMEOUT: int = 30
    BASE_POINTS: int = 100
    MAX_SPEED_BONUS: float = 1.0
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required environment variables are set."""
        required_vars = [
            ("DISCORD_TOKEN", cls.DISCORD_TOKEN),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

settings = Settings()