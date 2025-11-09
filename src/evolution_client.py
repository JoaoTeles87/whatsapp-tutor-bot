import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EvolutionAPIClient:
    """Client for sending messages via Evolution API"""
    
    def __init__(self, api_url: str, api_key: str, instance: str):
        """
        Initialize Evolution API client
        
        Args:
            api_url: Base URL of Evolution API
            api_key: API key for authentication
            instance: Instance name
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.instance = instance
        self.endpoint = f"{self.api_url}/message/sendText/{self.instance}"
        
    async def send_message(self, phone_number: str, text: str) -> bool:
        """
        Send text message to WhatsApp number via Evolution API
        
        Args:
            phone_number: Phone number to send message to
            text: Message text content
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "number": phone_number,
            "text": text
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.endpoint,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    logger.info(f"Message sent successfully to {phone_number}")
                    return True
                else:
                    logger.error(
                        f"Failed to send message to {phone_number}. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return False
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout sending message to {phone_number}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Request error sending message to {phone_number}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message to {phone_number}: {e}")
            return False
