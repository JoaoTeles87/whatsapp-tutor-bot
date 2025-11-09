import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.config import config
from src.leo_agent import LeoAgent
from src.evolution_client import EvolutionAPIClient
from src.message_processor import MessageProcessor
from src.webhook import create_webhook_app
from src.rag_service import RAGService
from src.analytics_agent import AgenteAnalista
from src.professor_agent import ProfessorAgent
from src.professor_agent import ProfessorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Nino Educational Agent...")
    
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nino Educational Agent...")


# Initialize components
logger.info("Initializing components...")

# Create RAG service (optional)
rag_service = RAGService(api_key=config.LLM_API_KEY)

# Create Analytics agent
analytics_agent = AgenteAnalista(api_key=config.LLM_API_KEY, model=config.LLM_MODEL)

# Create Professor agent
professor_agent = ProfessorAgent(api_key=config.LLM_API_KEY, model=config.LLM_MODEL)

# Create Nino agent with RAG
leo_agent = LeoAgent(
    api_key=config.LLM_API_KEY,
    model=config.LLM_MODEL,
    max_messages=config.MAX_HISTORY_MESSAGES,
    provider=config.LLM_PROVIDER,
    rag_service=rag_service
)

# Create Evolution API client
evolution_client = EvolutionAPIClient(
    api_url=config.EVOLUTION_API_URL,
    api_key=config.EVOLUTION_API_KEY,
    instance=config.EVOLUTION_INSTANCE
)

# Create message processor with professor agent and analytics
message_processor = MessageProcessor(
    leo_agent=leo_agent,
    evolution_client=evolution_client,
    professor_agent=professor_agent,
    analytics_agent=analytics_agent
)

# Create FastAPI app with webhook
app = create_webhook_app(message_processor)

# Update lifespan
app.router.lifespan_context = lifespan

logger.info("Nino Educational Agent initialized successfully")
logger.info(f"Server will run on port {config.SERVER_PORT}")
logger.info(f"Using LLM provider: {config.LLM_PROVIDER}")
logger.info(f"Using LLM model: {config.LLM_MODEL}")
logger.info(f"Evolution API URL: {config.EVOLUTION_API_URL}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.SERVER_PORT,
        reload=False
    )
