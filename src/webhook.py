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
    id: Optional[str] = None
    participant: Optional[str] = None


class MessageContent(BaseModel):
    """Evolution API message content structure"""
    conversation: Optional[str] = None
    extendedTextMessage: Optional[Dict[str, Any]] = None
    imageMessage: Optional[Dict[str, Any]] = None
    videoMessage: Optional[Dict[str, Any]] = None


class MessageData(BaseModel):
    """Evolution API data structure"""
    key: MessageKey
    message: MessageContent
    pushName: Optional[str] = None
    messageType: Optional[str] = None
    messageTimestamp: Optional[int] = None


class WebhookPayload(BaseModel):
    """Evolution API webhook payload structure"""
    event: str
    instance: str
    data: MessageData
    destination: Optional[str] = None
    date_time: Optional[str] = None
    sender: Optional[str] = None


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
            logger.info(f"Received webhook event: {body.get('event')}")
            
            # Parse payload
            payload = WebhookPayload(**body)
            
            # Only process message events
            if payload.event != "messages.upsert":
                logger.info(f"Ignoring non-message event: {payload.event}")
                return {"status": "ignored", "reason": "not_message_event"}
            
            # Ignore messages sent by the bot itself
            if payload.data.key.fromMe:
                logger.info("Ignoring message from bot itself (fromMe=true)")
                return {"status": "ignored", "reason": "fromMe"}
            
            # Extract phone number from remoteJid
            phone_number = extract_phone_number(payload.data.key.remoteJid)
            
            # Extract message text from different possible fields
            message_text = None
            
            # Try conversation field first
            if payload.data.message.conversation:
                message_text = payload.data.message.conversation
                logger.info(f"Message extracted from 'conversation' field")
            # Try extendedTextMessage
            elif payload.data.message.extendedTextMessage:
                message_text = payload.data.message.extendedTextMessage.get("text")
                logger.info(f"Message extracted from 'extendedTextMessage' field")
            
            # Validate message text exists
            if not message_text:
                logger.warning(f"No text message in payload from {phone_number}. Message type: {payload.data.messageType}")
                logger.warning(f"Full message object: {payload.data.message}")
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
