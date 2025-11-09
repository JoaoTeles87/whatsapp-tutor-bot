"""
Cost monitoring and API usage tracking
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class CostMonitor:
    """Monitor API usage and costs"""
    
    # Approximate costs (update based on actual pricing)
    COSTS = {
        "groq": {
            "llama-3.3-70b-versatile": 0.0,  # Free tier
            "llama-3.1-8b-instant": 0.0,  # Free tier
        },
        "openai": {
            "gpt-3.5-turbo": 0.0015,  # per 1K tokens (input + output)
            "gpt-4": 0.03,  # per 1K tokens
        }
    }
    
    def __init__(self, stats_file: str = "api_stats.json"):
        """
        Initialize cost monitor
        
        Args:
            stats_file: File to store statistics
        """
        self.stats_file = stats_file
        self.stats = self._load_stats()
        logger.info("CostMonitor initialized")
    
    def _load_stats(self) -> Dict:
        """Load statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading stats: {e}")
        
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "by_provider": {},
            "by_user": {},
            "daily": {}
        }
    
    def _save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
    
    def log_request(self, provider: str, model: str, tokens: int, user_id: str):
        """
        Log an API request
        
        Args:
            provider: LLM provider (groq/openai)
            model: Model name
            tokens: Estimated tokens used
            user_id: User phone number
        """
        # Update totals
        self.stats["total_requests"] += 1
        self.stats["total_tokens"] += tokens
        
        # Calculate cost
        cost = self._calculate_cost(provider, model, tokens)
        self.stats["total_cost"] += cost
        
        # Update by provider
        if provider not in self.stats["by_provider"]:
            self.stats["by_provider"][provider] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0
            }
        self.stats["by_provider"][provider]["requests"] += 1
        self.stats["by_provider"][provider]["tokens"] += tokens
        self.stats["by_provider"][provider]["cost"] += cost
        
        # Update by user
        if user_id not in self.stats["by_user"]:
            self.stats["by_user"][user_id] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0
            }
        self.stats["by_user"][user_id]["requests"] += 1
        self.stats["by_user"][user_id]["tokens"] += tokens
        self.stats["by_user"][user_id]["cost"] += cost
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily"]:
            self.stats["daily"][today] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0
            }
        self.stats["daily"][today]["requests"] += 1
        self.stats["daily"][today]["tokens"] += tokens
        self.stats["daily"][today]["cost"] += cost
        
        # Save stats
        self._save_stats()
        
        logger.info(f"API call logged: {provider}/{model} - {tokens} tokens - ${cost:.4f}")
    
    def _calculate_cost(self, provider: str, model: str, tokens: int) -> float:
        """Calculate cost for API call"""
        if provider in self.COSTS and model in self.COSTS[provider]:
            cost_per_1k = self.COSTS[provider][model]
            return (tokens / 1000) * cost_per_1k
        return 0.0
    
    def get_summary(self) -> Dict:
        """Get usage summary"""
        return {
            "total_requests": self.stats["total_requests"],
            "total_tokens": self.stats["total_tokens"],
            "total_cost": f"${self.stats['total_cost']:.4f}",
            "by_provider": self.stats["by_provider"]
        }
    
    def get_user_usage(self, user_id: str) -> Dict:
        """Get usage for specific user"""
        if user_id in self.stats["by_user"]:
            return self.stats["by_user"][user_id]
        return {"requests": 0, "tokens": 0, "cost": 0.0}
    
    def check_user_limit(self, user_id: str, max_requests: int = 100) -> Tuple[bool, str]:
        """
        Check if user exceeded limits
        
        Args:
            user_id: User phone number
            max_requests: Maximum requests per user
            
        Returns:
            (within_limit, message)
        """
        usage = self.get_user_usage(user_id)
        
        if usage["requests"] >= max_requests:
            return False, f"Você atingiu o limite de {max_requests} mensagens. Entre em contato com o administrador."
        
        return True, ""
