"""
Professor Agent - Allows teachers to update RAG documents via WhatsApp
"""
import logging
import os
from datetime import datetime
from typing import Optional, Tuple
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class ProfessorAgent:
    """Agent to detect and handle professor messages"""
    
    # Known professor numbers (can be configured)
    PROFESSOR_NUMBERS = [
        # "558132991244",  # Temporarily disabled for testing
        "558195435686",  # Professor João
        # Add more professor numbers here
    ]
    
    # Track professor conversation state
    professor_sessions = {}  # phone_number -> {"state": "awaiting_content", "buffer": []}
    
    # Keywords that indicate professor identity
    PROFESSOR_KEYWORDS = [
        "sou professor",
        "sou o professor",
        "aqui é o professor",
        "professor carlos",
        "professora",
        "tarefa para",
        "aviso aos alunos",
        "comunicado",
        "atenção turma",
        "atenção 6º ano"
    ]
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize professor agent
        
        Args:
            api_key: Groq API key
            model: LLM model name
        """
        self.llm = ChatGroq(
            model=model,
            temperature=0.2,
            groq_api_key=api_key
        )
        
        self.system_prompt = """Você é um assistente que identifica se uma mensagem é de um professor.

Analise a mensagem e responda APENAS com JSON:
{
  "is_professor": true/false,
  "confidence": 0.0-1.0,
  "reason": "breve explicação"
}

Indicadores de que é professor:
- Se identifica como professor/professora
- Usa linguagem formal de comunicado
- Menciona "tarefa para os alunos", "aviso", "comunicado"
- Fala sobre conteúdo didático de forma autoritativa
- Usa frases como "Atenção turma", "Atenção 6º ano"

Indicadores de que NÃO é professor:
- Faz perguntas sobre matéria (aluno com dúvida)
- Usa linguagem informal de colega
- Pede ajuda ou explicação
- Conversa casual"""
        
        logger.info("ProfessorAgent initialized")
    
    def is_known_professor(self, phone_number: str) -> bool:
        """Check if phone number is a known professor"""
        return phone_number in self.PROFESSOR_NUMBERS
    
    def has_professor_keywords(self, message: str) -> bool:
        """Quick check for professor keywords"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.PROFESSOR_KEYWORDS)
    
    async def detect_professor(self, phone_number: str, message: str) -> Tuple[bool, float]:
        """
        Detect if message is from a professor
        
        Args:
            phone_number: Sender's phone number
            message: Message text
            
        Returns:
            (is_professor, confidence)
        """
        # Quick check: known professor number
        if self.is_known_professor(phone_number):
            logger.info(f"Known professor detected: {phone_number}")
            return True, 1.0
        
        # Quick check: professor keywords
        if not self.has_professor_keywords(message):
            return False, 0.0
        
        # LLM analysis for uncertain cases
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Mensagem: {message}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse response
            import json
            result = json.loads(response.content)
            
            is_prof = result.get("is_professor", False)
            confidence = result.get("confidence", 0.0)
            
            if is_prof and confidence > 0.7:
                logger.info(f"Professor detected via LLM: {phone_number} (confidence: {confidence})")
            
            return is_prof, confidence
            
        except Exception as e:
            logger.error(f"Error detecting professor: {e}")
            return False, 0.0
    
    def save_professor_message(self, message: str, phone_number: str) -> str:
        """
        Save professor message as a RAG document
        
        Args:
            message: Professor's message
            phone_number: Professor's phone number
            
        Returns:
            Filename of saved document
        """
        try:
            # Create documentos_escola folder if it doesn't exist
            os.makedirs("documentos_escola", exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"documentos_escola/professor_msg_{timestamp}.txt"
            
            # Add metadata header
            content = f"""[Mensagem do Professor - {datetime.now().strftime("%d/%m/%Y %H:%M")}]
[Enviado por: {phone_number}]

{message}
"""
            
            # Save to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"Professor message saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving professor message: {e}")
            raise
    
    def start_professor_session(self, phone_number: str) -> str:
        """Start a new professor session"""
        self.professor_sessions[phone_number] = {
            "state": "awaiting_content",
            "buffer": [],
            "started_at": datetime.now()
        }
        
        return """👨‍🏫 Olá, Professor(a)!

Detectei que você quer criar um novo comunicado para os alunos.

Por favor, envie a mensagem completa que deseja compartilhar com a turma. Pode incluir:
- Tarefas de casa
- Avisos importantes
- Datas de provas
- Conteúdo de estudo

Quando terminar, envie: "PUBLICAR"
Para cancelar, envie: "CANCELAR"

Aguardando sua mensagem... 📝"""
    
    def add_to_buffer(self, phone_number: str, message: str) -> Optional[str]:
        """
        Add message to professor's buffer
        
        Returns:
            Response message or None if still collecting
        """
        if phone_number not in self.professor_sessions:
            return None
        
        session = self.professor_sessions[phone_number]
        
        # Check for commands
        if message.upper() == "PUBLICAR":
            if not session["buffer"]:
                return "❌ Nenhuma mensagem para publicar. Envie o conteúdo primeiro."
            
            # Combine all buffered messages
            full_message = "\n\n".join(session["buffer"])
            
            # Save and return confirmation
            filename = self.save_professor_message(full_message, phone_number)
            
            # Clear session
            del self.professor_sessions[phone_number]
            
            return self.generate_confirmation_message(filename)
        
        elif message.upper() == "CANCELAR":
            del self.professor_sessions[phone_number]
            return "❌ Operação cancelada. Nenhuma mensagem foi publicada."
        
        else:
            # Add to buffer
            session["buffer"].append(message)
            
            # Show preview
            preview = "\n\n".join(session["buffer"])
            return f"""📝 Mensagem adicionada ao rascunho:

---
{preview}
---

Continue enviando mais conteúdo ou:
- Digite "PUBLICAR" para salvar e compartilhar com os alunos
- Digite "CANCELAR" para descartar"""
    
    def is_in_session(self, phone_number: str) -> bool:
        """Check if professor has an active session"""
        return phone_number in self.professor_sessions
    
    def generate_confirmation_message(self, filename: str) -> str:
        """Generate confirmation message for professor"""
        return f"""✅ Mensagem publicada com sucesso, Professor(a)!

Sua mensagem foi adicionada aos documentos da escola e os alunos poderão consultá-la através do Leo.

📁 Arquivo: {os.path.basename(filename)}
⏰ Publicado em: {datetime.now().strftime("%d/%m/%Y às %H:%M")}

⚠️ IMPORTANTE: Para que os alunos vejam a atualização imediatamente, digite:
"REINDEXAR"

Ou aguarde a reindexação automática (ocorre a cada hora).

Obrigado por usar o sistema! 📚"""
    
    async def handle_reindex_request(self) -> Tuple[bool, str]:
        """
        Handle request to reindex RAG
        
        Returns:
            (success, message)
        """
        try:
            # Import here to avoid circular dependency
            import subprocess
            
            logger.info("Starting RAG reindexing...")
            
            # Run prep_rag.py
            result = subprocess.run(
                ["python", "prep_rag.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("RAG reindexing successful")
                return True, """✅ Sistema atualizado com sucesso!

Os alunos já podem consultar sua nova mensagem através do Leo.

Tudo pronto! 🎉"""
            else:
                logger.error(f"RAG reindexing failed: {result.stderr}")
                return False, """❌ Erro ao atualizar o sistema.

Por favor, contate o administrador do sistema.

Erro técnico registrado nos logs."""
                
        except Exception as e:
            logger.error(f"Error reindexing RAG: {e}")
            return False, f"❌ Erro ao atualizar: {str(e)}"
