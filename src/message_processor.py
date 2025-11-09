import logging
from src.leo_agent import LeoAgent
from src.evolution_client import EvolutionAPIClient

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Processes incoming messages and coordinates response generation"""
    
    def __init__(self, leo_agent: LeoAgent, evolution_client: EvolutionAPIClient):
        """
        Initialize message processor
        
        Args:
            leo_agent: LeoAgent instance for generating responses
            evolution_client: EvolutionAPIClient for sending messages
        """
        self.leo_agent = leo_agent
        self.evolution_client = evolution_client
        logger.info("MessageProcessor initialized")
    
    async def process_message(self, phone_number: str, message_text: str) -> None:
        """
        Process incoming message and send response
        
        Args:
            phone_number: User's phone number
            message_text: Message text from user
        """
        try:
            logger.info(f"Processing message from {phone_number}: {message_text[:50]}...")
            
            # Generate response using Leo agent
            response = await self.leo_agent.generate_response(phone_number, message_text)
            
            # Send response via Evolution API
            success = await self.evolution_client.send_message(phone_number, response)
            
            if success:
                logger.info(f"Successfully processed and responded to {phone_number}")
            else:
                logger.error(f"Failed to send response to {phone_number}")
                
        except Exception as e:
            logger.error(f"Error processing message from {phone_number}: {e}")
            # Try to send error message to user
            try:
                await self.evolution_client.send_message(
                    phone_number,
                    "Opa, tive um probleminha aqui 😅 Pode tentar de novo?"
                )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
