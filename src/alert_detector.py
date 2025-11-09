"""
Critical Alert Detector - Identifies urgent student situations
"""
import logging
import json
import os
from datetime import datetime
from typing import Tuple, Optional
import re

logger = logging.getLogger(__name__)


class AlertDetector:
    """Detects critical situations requiring immediate intervention"""
    
    # Critical patterns indicating serious issues
    CRITICAL_PATTERNS = {
        "dropout_risk": [
            r"vou\s+sair\s+da\s+escola",
            r"vou\s+desistir",
            r"não\s+quero\s+mais\s+estudar",
            r"vou\s+parar\s+de\s+estudar",
            r"vou\s+abandonar",
            r"se\s+tirar\s+nota\s+baixa.*vou\s+sair",
        ],
        "self_harm": [
            r"vou\s+embora\s+para\s+sempre",
            r"quero\s+sumir",
            r"quero\s+desaparecer",
            r"não\s+aguento\s+mais",
            r"preferia\s+não\s+existir",
            r"ninguém\s+vai\s+sentir\s+minha\s+falta",
        ],
        "bullying": [
            r"todo\s+mundo\s+me\s+odeia",
            r"ninguém\s+gosta\s+de\s+mim",
            r"sofro\s+bullying",
            r"me\s+xingam\s+todo\s+dia",
            r"tenho\s+medo\s+dos?\s+colegas",
            r"me\s+batem",
        ],
        "family_issues": [
            r"meus\s+pais\s+brigam\s+muito",
            r"apanho\s+em\s+casa",
            r"meu\s+pai.*bate",
            r"minha\s+mãe.*bate",
            r"não\s+tenho\s+comida",
            r"passo\s+fome",
        ],
        "severe_anxiety": [
            r"tenho\s+muito\s+medo\s+da\s+prova",
            r"não\s+consigo\s+dormir.*prova",
            r"fico\s+tremendo.*escola",
            r"tenho\s+pavor\s+de",
            r"entro\s+em\s+pânico",
        ]
    }
    
    # Alert severity levels
    SEVERITY = {
        "self_harm": "CRITICAL",
        "dropout_risk": "HIGH",
        "bullying": "HIGH",
        "family_issues": "HIGH",
        "severe_anxiety": "MEDIUM"
    }
    
    def __init__(self, alerts_file: str = "critical_alerts.json"):
        """
        Initialize alert detector
        
        Args:
            alerts_file: File to store critical alerts
        """
        self.alerts_file = alerts_file
        logger.info("AlertDetector initialized")
    
    def detect_critical_situation(self, message: str, user_id: str) -> Tuple[bool, Optional[dict]]:
        """
        Detect if message indicates a critical situation
        
        Args:
            message: Student's message
            user_id: Student's phone number
            
        Returns:
            (is_critical, alert_data)
        """
        message_lower = message.lower()
        
        for category, patterns in self.CRITICAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    alert = self._create_alert(
                        user_id=user_id,
                        message=message,
                        category=category,
                        pattern=pattern,
                        severity=self.SEVERITY[category]
                    )
                    
                    self._save_alert(alert)
                    logger.critical(f"CRITICAL ALERT: {category} detected for user {user_id}")
                    
                    return True, alert
        
        return False, None
    
    def _create_alert(self, user_id: str, message: str, category: str, 
                     pattern: str, severity: str) -> dict:
        """Create alert data structure"""
        return {
            "alert_id": f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "severity": severity,
            "category": category,
            "message": message,
            "pattern_matched": pattern,
            "status": "NEW",
            "requires_immediate_action": severity in ["CRITICAL", "HIGH"]
        }
    
    def _save_alert(self, alert: dict):
        """Save critical alert to file"""
        try:
            # Load existing alerts
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, "r", encoding="utf-8") as f:
                    alerts = json.load(f)
            else:
                alerts = []
            
            # Add new alert
            alerts.append(alert)
            
            # Save back
            with open(self.alerts_file, "w", encoding="utf-8") as f:
                json.dump(alerts, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Critical alert saved: {alert['alert_id']}")
            
        except Exception as e:
            logger.error(f"Error saving critical alert: {e}")
    
    def get_response_for_critical_situation(self, category: str) -> str:
        """
        Get appropriate response for critical situation
        
        Args:
            category: Alert category
            
        Returns:
            Empathetic response message
        """
        responses = {
            "self_harm": """Ei, percebi que você está passando por um momento muito difícil. 😔

Quero que saiba que você é importante e que existem pessoas que se importam com você.

🆘 Por favor, converse com:
- Seus pais ou responsável
- Um professor de confiança
- CVV (Centro de Valorização da Vida): 188 (24h, gratuito)

Você não está sozinho. Vamos conversar mais sobre isso?""",
            
            "dropout_risk": """Ei, entendo que você está pensando em sair da escola. 😔

Antes de tomar essa decisão, vamos conversar sobre o que está acontecendo?

Às vezes as coisas parecem impossíveis, mas existem pessoas que podem ajudar:
- Converse com seus pais
- Fale com a coordenação da escola
- Me conte mais sobre o que está te fazendo pensar nisso

O que está te deixando assim?""",
            
            "bullying": """Sinto muito que você esteja passando por isso. 😔 Ninguém merece ser tratado assim.

🛡️ Isso é sério e precisa ser resolvido:
- Conte para seus pais HOJE
- Fale com um professor ou coordenador
- Isso não é culpa sua

Você quer me contar mais sobre o que está acontecendo? Estou aqui para te ouvir.""",
            
            "family_issues": """Percebi que as coisas em casa não estão fáceis. 😔

Isso é muito sério e você precisa de ajuda de um adulto de confiança:
- Fale com um professor
- Converse com a coordenação da escola
- Disque 100 (Direitos Humanos) se precisar

Você está seguro agora? Quer conversar sobre isso?""",
            
            "severe_anxiety": """Entendo que você está com muito medo. 😔 Ansiedade antes de provas é normal, mas quando é muito forte, precisa de atenção.

💙 Algumas coisas que podem ajudar:
- Respire fundo algumas vezes
- Converse com seus pais sobre como está se sentindo
- Fale com um professor sobre sua ansiedade

Quer conversar sobre o que te deixa tão nervoso?"""
        }
        
        return responses.get(category, "Percebi que você está passando por um momento difícil. Quer conversar sobre isso? 💙")
    
    def get_pending_alerts(self, status: str = "NEW") -> list:
        """Get alerts by status"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, "r", encoding="utf-8") as f:
                    alerts = json.load(f)
                return [a for a in alerts if a.get("status") == status]
            return []
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
            return []
    
    def mark_alert_handled(self, alert_id: str):
        """Mark alert as handled"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, "r", encoding="utf-8") as f:
                    alerts = json.load(f)
                
                for alert in alerts:
                    if alert["alert_id"] == alert_id:
                        alert["status"] = "HANDLED"
                        alert["handled_at"] = datetime.now().isoformat()
                
                with open(self.alerts_file, "w", encoding="utf-8") as f:
                    json.dump(alerts, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Alert marked as handled: {alert_id}")
        except Exception as e:
            logger.error(f"Error marking alert as handled: {e}")
