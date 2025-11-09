import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from src.message_processor import MessageProcessor

logger = logging.getLogger(__name__)


class MessageKey(BaseModel):
    """Evolution API message key structure"""
    remoteJid: str
    fromMe: bool


class MessageContent(BaseModel):
    """Evolution API message content structure"""
    conversation: Optional[str] = None
    extendedTextMessage: Optional[Dict[str, Any]] = None
    imageMessage: Optional[Dict[str, Any]] = None
    videoMessage: Optional[Dict[str, Any]] = None


class WebhookPayload(BaseModel):
    """Evolution API webhook payload structure"""
    key: MessageKey
    message: MessageContent
    messageType: Optional[str] = None
    pushName: Optional[str] = None


def create_webhook_app(message_processor: MessageProcessor) -> FastAPI:
    """
    Create FastAPI application with webhook endpoint
    
    Args:
        message_processor: MessageProcessor instance
        
    Returns:
        FastAPI application
    """
    app = FastAPI(title="Leo Educational Agent")
    
    @app.post("/webhook")
    async def webhook_endpoint(request: Request):
        """
        Receive messages from Evolution API webhook
        
        Args:
            request: Raw request to log full payload
            
        Returns:
            Success response
        """
        try:
            # Get raw body for logging
            body = await request.json()
            logger.info(f"Received webhook payload: {body}")
            
            # Parse payload
            payload = WebhookPayload(**body)
            
            # Ignore messages sent by the bot itself
            if payload.key.fromMe:
                logger.info("Ignoring message from bot itself (fromMe=true)")
                return {"status": "ignored", "reason": "fromMe"}
            
            # Extract phone number from remoteJid
            phone_number = extract_phone_number(payload.key.remoteJid)
            
            # Extract message text from different possible fields
            message_text = None
            
            # Try conversation field first
            if payload.message.conversation:
                message_text = payload.message.conversation
            # Try extendedTextMessage
            elif payload.message.extendedTextMessage:
                message_text = payload.message.extendedTextMessage.get("text")
            
            # Validate message text exists
            if not message_text:
                logger.warning(f"No text message in payload from {phone_number}. Message type: {payload.messageType}")
                return {"status": "ignored", "reason": "no_text"}
            
            logger.info(f"Processing message from {phone_number}: {message_text[:50]}...")
            
            # Process message asynchronously
            await message_processor.process_message(phone_number, message_text)
            
            return {"status": "success"}
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    @app.post("/webhook/debug")
    async def webhook_debug(request: Request):
        """Debug endpoint to see raw webhook payloads"""
        body = await request.json()
        logger.info(f"DEBUG - Full webhook payload: {body}")
        return {"status": "received", "payload": body}
    
    return app


def extract_phone_number(remote_jid: str) -> str:
    """
    Extract phone number from Evolution API remoteJid format
    
    Args:
        remote_jid: Remote JID (e.g., "5511999999999@s.whatsapp.net")
        
    Returns:
        Phone number string
        
    Raises:
        ValueError: If remoteJid format is invalid
    """
    if not remote_jid:
        raise ValueError("remoteJid is empty")
    
    # Extract number before @ symbol
    if "@" in remote_jid:
        phone_number = remote_jid.split("@")[0]
        return phone_number
    else:
        raise ValueError(f"Invalid remoteJid format: {remote_jid}")
