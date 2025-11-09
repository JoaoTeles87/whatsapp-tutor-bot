"""
Analytics Agent using Fredricks (2004) Engagement Framework
"""
import logging
import json
import os
from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class AnaliseEngajamento(BaseModel):
    """Engagement analysis based on Fredricks (2004) framework"""
    
    # Fredricks 3 Pillars
    engajamento_comportamental: float = Field(
        ...,
        description="Score de 0.0 (passivo/não fez) a 1.0 (fez o quiz/participou)"
    )
    engajamento_emocional: float = Field(
        ...,
        description="Score de 0.0 (frustrado/entediado) a 1.0 (curioso/positivo)"
    )
    engajamento_cognitivo: float = Field(
        ...,
        description="Score de 0.0 (respostas superficiais) a 1.0 (fez perguntas profundas/críticas)"
    )
    
    # Calculated metric
    score_desmotivacao: float = Field(
        ...,
        description="Score de Risco de 0.0 (engajado) a 1.0 (alto risco de evasão)"
    )
    
    observacoes_chave: List[str] = Field(
        ...,
        description="1-2 frases EXATAS do aluno que justificam os scores"
    )
    
    # Location data for heatmap
    escola: str = Field(..., description="Nome da escola/instituição")
    cidade: str = Field(..., description="Cidade da escola, ex: João Pessoa")
    lat: float = Field(..., description="Latitude da escola")
    lon: float = Field(..., description="Longitude da escola")


class AgenteAnalista:
    """Analytics agent for student engagement analysis"""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize analytics agent
        
        Args:
            api_key: Groq API key
            model: LLM model name
        """
        self.llm = ChatGroq(
            model=model,
            temperature=0.3,  # Lower temperature for more consistent analysis
            groq_api_key=api_key
        )
        
        self.system_prompt = """Você é um analista educacional sênior. Seu trabalho é analisar a transcrição de uma conversa
e preencher um JSON, usando o framework de engajamento de Fredricks (2004).

[REGRAS DE CLASSIFICAÇÃO]
1. **engajamento_comportamental (0.0-1.0):** O aluno está fazendo? (Participou, respondeu quiz, etc.)
2. **engajamento_emocional (0.0-1.0):** O aluno está sentindo? (Curioso, positivo vs. Frustrado, "que saco")
3. **engajamento_cognitivo (0.0-1.0):** O aluno está pensando? (Fez perguntas extras, criticou vs. Só respondeu "sim/não")

[REGRAS DE CÁLCULO]
1. **score_desmotivacao**: Deve ser calculado como (1.0 - a MÉDIA dos três pilares).
   Ex: Se a média dos 3 pilares for 0.2, o score de desmotivação é 0.8.
2. **observacoes_chave**: Extraia 1 ou 2 frases exatas do aluno que justificam sua análise.
3. **Localização**: Use "João Pessoa" como cidade, lat: -7.1195, lon: -34.845

[IMPORTANTE - CONTEXTO DE CONVERSA]
- Mensagens curtas de saudação ("Oi", "Olá", apresentações) NÃO devem ser interpretadas como desmotivação
- Considere o CONTEXTO COMPLETO da conversa, não apenas mensagens isoladas
- Se o aluno está iniciando a conversa de forma educada, isso é NEUTRO (score ~0.5), não negativo
- Só classifique como alta desmotivação (>0.7) se houver EVIDÊNCIAS CLARAS de frustração, desistência ou desinteresse

Responda APENAS com o objeto JSON válido, sem markdown ou explicações."""
        
        logger.info("AgenteAnalista initialized with Fredricks framework")
    
    async def analisar_conversa(self, aluno_id: str, historico: List[Dict[str, str]]) -> AnaliseEngajamento:
        """
        Analyze conversation and generate engagement scores
        
        Args:
            aluno_id: Student phone number
            historico: Conversation history
            
        Returns:
            AnaliseEngajamento with scores
        """
        try:
            # Skip analysis for very short conversations (less than 3 student messages)
            student_messages = [msg for msg in historico if msg['role'] == 'user']
            
            if len(student_messages) < 3:
                logger.info(f"Skipping analysis for {aluno_id}: conversation too short ({len(student_messages)} messages)")
                return None  # Don't analyze yet
            
            # Skip if total conversation content is too short (greeting only)
            total_content = " ".join([msg['content'] for msg in student_messages])
            if len(total_content.strip()) < 20:  # Less than 20 characters total
                logger.info(f"Skipping analysis for {aluno_id}: content too minimal")
                return None
            
            # Format conversation for analysis
            conversa_texto = "\n".join([
                f"{'Aluno' if msg['role'] == 'user' else 'Nino'}: {msg['content']}"
                for msg in historico
            ])
            
            # Create analysis prompt
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Analise esta conversa:\n\n{conversa_texto}")
            ]
            
            # Get analysis from LLM
            response = await self.llm.ainvoke(messages)
            
            # Clean response content (remove markdown if present)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            # Parse JSON response
            analise_dict = json.loads(content)
            
            # Ensure location data is present
            if "escola" not in analise_dict:
                analise_dict["escola"] = "Vista Alegre Park, Haras e Hípica"
            if "cidade" not in analise_dict:
                analise_dict["cidade"] = "João Pessoa"
            if "lat" not in analise_dict:
                analise_dict["lat"] = -7.1195
            if "lon" not in analise_dict:
                analise_dict["lon"] = -34.845
            
            # Calculate score_desmotivacao if not provided
            if "score_desmotivacao" not in analise_dict:
                media_pilares = (
                    analise_dict["engajamento_comportamental"] +
                    analise_dict["engajamento_emocional"] +
                    analise_dict["engajamento_cognitivo"]
                ) / 3
                analise_dict["score_desmotivacao"] = 1.0 - media_pilares
            
            # Create Pydantic model
            analise = AnaliseEngajamento(**analise_dict)
            
            # Save to alerts file
            self._save_alert(aluno_id, analise)
            
            logger.info(f"Analysis complete for {aluno_id}: risk={analise.score_desmotivacao:.2f}")
            return analise
            
        except Exception as e:
            logger.error(f"Error analyzing conversation for {aluno_id}: {e}")
            # Return default analysis on error
            return AnaliseEngajamento(
                engajamento_comportamental=0.5,
                engajamento_emocional=0.5,
                engajamento_cognitivo=0.5,
                score_desmotivacao=0.5,
                observacoes_chave=["Análise não disponível"],
                escola="Vista Alegre Park, Haras e Hípica",
                cidade="João Pessoa",
                lat=-7.1195,
                lon=-34.845
            )
    
    def _save_alert(self, aluno_id: str, analise: AnaliseEngajamento):
        """Save analysis to alerts.json file"""
        try:
            alerts_file = "alertas.json"
            
            # Load existing alerts
            if os.path.exists(alerts_file):
                with open(alerts_file, "r", encoding="utf-8") as f:
                    alerts = json.load(f)
            else:
                alerts = []
            
            # Add new alert
            alert = {
                "aluno_id": aluno_id,
                "timestamp": datetime.now().isoformat(),
                "engajamento_comportamental": analise.engajamento_comportamental,
                "engajamento_emocional": analise.engajamento_emocional,
                "engajamento_cognitivo": analise.engajamento_cognitivo,
                "score_desmotivacao": analise.score_desmotivacao,
                "observacoes_chave": analise.observacoes_chave,
                "escola": analise.escola,
                "cidade": analise.cidade,
                "lat": analise.lat,
                "lon": analise.lon
            }
            
            alerts.append(alert)
            
            # Save back to file
            with open(alerts_file, "w", encoding="utf-8") as f:
                json.dump(alerts, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Alert saved for {aluno_id}")
            
        except Exception as e:
            logger.error(f"Error saving alert: {e}")
