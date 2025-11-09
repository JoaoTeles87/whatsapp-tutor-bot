"""
Security module for prompt injection protection and input sanitization
"""
import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)


class SecurityGuard:
    """Security guard for prompt injection and malicious input detection"""
    
    # Dangerous patterns that indicate prompt injection attempts
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|above|all)\s+instructions?",
        r"disregard\s+(previous|above|all)\s+instructions?",
        r"forget\s+(previous|above|all)\s+instructions?",
        r"you\s+are\s+now\s+a",
        r"act\s+as\s+(a\s+)?(?!aluno|estudante)",  # Allow "act as student"
        r"pretend\s+to\s+be",
        r"roleplay\s+as",
        r"system\s*:\s*",
        r"<\s*system\s*>",
        r"\[system\]",
        r"sudo\s+",
        r"admin\s+mode",
        r"developer\s+mode",
        r"jailbreak",
        r"dan\s+mode",
        r"do\s+anything\s+now",
    ]
    
    # Suspicious repetition patterns
    MAX_REPEATED_CHARS = 50
    MAX_REPEATED_WORDS = 10
    
    # Token limits
    MAX_MESSAGE_TOKENS = 500  # Approximate (1 token ≈ 4 chars)
    
    def __init__(self):
        """Initialize security guard"""
        self.blocked_count = 0
        logger.info("SecurityGuard initialized")
    
    def check_prompt_injection(self, message: str) -> Tuple[bool, str]:
        """
        Check if message contains prompt injection attempts
        
        Args:
            message: User message to check
            
        Returns:
            (is_safe, reason) - False if injection detected
        """
        message_lower = message.lower()
        
        # Check for injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                logger.warning(f"Prompt injection detected: {pattern}")
                self.blocked_count += 1
                return False, "Mensagem bloqueada por segurança. Evite comandos especiais."
        
        # Check for excessive repetition (spam/DOS attempt)
        if self._has_excessive_repetition(message):
            logger.warning("Excessive repetition detected")
            self.blocked_count += 1
            return False, "Mensagem com muito texto repetido. Tente ser mais claro."
        
        # Check for suspicious special characters
        if self._has_suspicious_chars(message):
            logger.warning("Suspicious characters detected")
            self.blocked_count += 1
            return False, "Mensagem contém caracteres suspeitos."
        
        return True, ""
    
    def _has_excessive_repetition(self, message: str) -> bool:
        """Check for excessive character or word repetition"""
        # Check repeated characters
        for char in set(message):
            if message.count(char * 10) > 0:  # 10+ same chars in a row
                return True
        
        # Check repeated words
        words = message.split()
        if len(words) > 5:
            for word in set(words):
                if words.count(word) > self.MAX_REPEATED_WORDS:
                    return True
        
        return False
    
    def _has_suspicious_chars(self, message: str) -> bool:
        """Check for suspicious special characters"""
        # Count special chars
        special_chars = sum(1 for c in message if not c.isalnum() and not c.isspace() and c not in ".,!?;:-'\"()áéíóúãõâêôàèìòùçÁÉÍÓÚÃÕÂÊÔÀÈÌÒÙÇ")
        
        # If more than 20% special chars, suspicious
        if len(message) > 0 and special_chars / len(message) > 0.2:
            return True
        
        return False
    
    def sanitize_input(self, message: str) -> str:
        """
        Sanitize user input
        
        Args:
            message: Raw user message
            
        Returns:
            Sanitized message
        """
        # Remove null bytes
        message = message.replace('\x00', '')
        
        # Remove excessive whitespace
        message = ' '.join(message.split())
        
        # Limit length
        if len(message) > 2000:  # Hard limit
            message = message[:2000]
            logger.warning("Message truncated to 2000 chars")
        
        return message.strip()
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation)
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters for English
        # For Portuguese, slightly different but close enough
        return len(text) // 4
    
    def get_stats(self) -> dict:
        """Get security statistics"""
        return {
            "blocked_messages": self.blocked_count
        }
