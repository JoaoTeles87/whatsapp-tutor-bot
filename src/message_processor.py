import logging
from src.leo_agent import LeoAgent
from src.evolution_client import EvolutionAPIClient
from src.alert_detector import AlertDetector

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Processes incoming messages and coordinates response generation"""
    
    def __init__(self, leo_agent: LeoAgent, evolution_client: EvolutionAPIClient, professor_agent=None):
        """
        Initialize message processor
        
        Args:
            leo_agent: LeoAgent instance for generating responses
            evolution_client: EvolutionAPIClient for sending messages
            professor_agent: Optional ProfessorAgent for handling teacher messages
        """
        self.leo_agent = leo_agent
        self.evolution_client = evolution_client
        self.professor_agent = professor_agent
        self.alert_detector = AlertDetector()
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
            
            # Check if this is a professor message
            if self.professor_agent:
                # Check if professor is in an active session
                if self.professor_agent.is_in_session(phone_number):
                    logger.info(f"Professor {phone_number} in active session")
                    response = self.professor_agent.add_to_buffer(phone_number, message_text)
                    if response:
                        await self.evolution_client.send_message(phone_number, response)
                    return
                
                # Check for reindex command
                if "reindexar" in message_text.lower():
                    success, response = await self.professor_agent.handle_reindex_request()
                    await self.evolution_client.send_message(phone_number, response)
                    return
                
                # Detect if this is a new professor message
                is_professor, confidence = await self.professor_agent.detect_professor(
                    phone_number, message_text
                )
                
                if is_professor and confidence > 0.7:
                    logger.info(f"New professor detected from {phone_number}")
                    # Start professor session
                    response = self.professor_agent.start_professor_session(phone_number)
                    await self.evolution_client.send_message(phone_number, response)
                    return
            
            # Check for critical situations BEFORE generating response
            is_critical, alert_data = self.alert_detector.detect_critical_situation(
                message_text, phone_number
            )
            
            if is_critical:
                logger.critical(f"CRITICAL ALERT for {phone_number}: {alert_data['category']}")
                # Send immediate empathetic response
                crisis_response = self.alert_detector.get_response_for_critical_situation(
                    alert_data['category']
                )
                await self.evolution_client.send_message(phone_number, crisis_response)
                return
            
            # Regular student message - generate response using Leo agent
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
