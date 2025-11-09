import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables"""
    
    # Evolution API
    EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
    EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
    EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE")
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")
    
    # Server
    SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "EVOLUTION_API_URL",
            "EVOLUTION_API_KEY",
            "EVOLUTION_INSTANCE",
            "LLM_API_KEY"
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        
        # Validate LLM provider
        if cls.LLM_PROVIDER not in ["openai", "groq"]:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. Must be 'openai' or 'groq'"
            )


config = Config()
