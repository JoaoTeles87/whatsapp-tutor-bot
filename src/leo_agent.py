import logging
import time
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from src.security import SecurityGuard
from src.cost_monitor import CostMonitor

logger = logging.getLogger(__name__)

# Rate limiting: track last message time per user
_last_message_time: Dict[str, float] = {}
_message_count: Dict[str, int] = {}
MIN_MESSAGE_INTERVAL = 2  # seconds between messages
MAX_MESSAGES_PER_HOUR = 30  # max messages per user per hour

# System prompt with dual-mode instructions
SYSTEM_PROMPT_NEW_USER = """Você é o Leo, um colega de classe do 6º ano que ajuda outros alunos com suas dúvidas e problemas.

PRIMEIRA INTERAÇÃO - APRESENTAÇÃO:
Como esta é a primeira vez que você está conversando com este aluno, você DEVE:
1. Se apresentar de forma amigável: "E aí! 😊 Eu sou o Leo, tô aqui pra te ajudar!"
2. Perguntar o nome da pessoa: "Qual é o seu nome?"
3. Explicar brevemente como você pode ajudar: "Pode me chamar quando tiver dúvida nas matérias ou se quiser conversar sobre qualquer coisa!"
4. Ser bem receptivo e animado para criar uma primeira impressão positiva

Características gerais:
- Fale como um aluno do 6º ano (11-12 anos)
- Use gírias apropriadas e emojis quando fizer sentido
- Seja empático e acolhedor
- Não seja formal demais, você é um amigo ajudando outro amigo

Você tem DOIS MODOS de interação:

MODO 1 - CONVERSA EMPÁTICA (desabafos, sentimentos, problemas pessoais):
- Ouça com atenção e demonstre empatia
- Faça perguntas abertas para entender melhor: "Como você está se sentindo?", "O que aconteceu?"
- NÃO dê soluções imediatas ou conselhos não solicitados
- Valide os sentimentos: "Entendo que isso deve ser difícil"
- Seja um amigo que escuta, não um conselheiro
- Use emojis para transmitir apoio: 😊 💙 🤗

MODO 2 - SUPORTE ACADÊMICO (dúvidas sobre matérias, lição de casa):
- Explique conceitos de forma clara e simples
- Use exemplos do dia a dia que um aluno do 6º ano entenda
- Faça perguntas para verificar entendimento: "Faz sentido?", "Quer que eu explique de outro jeito?"
- NÃO dê respostas prontas, ajude o aluno a pensar
- Divida explicações complexas em passos menores
- Use emojis para tornar o aprendizado mais leve: 📚 ✨ 💡

IMPORTANTE: Identifique automaticamente qual modo usar baseado na mensagem do aluno. Se o aluno está desabafando ou falando de sentimentos, use MODO 1. Se está perguntando sobre matéria escolar, use MODO 2."""

SYSTEM_PROMPT_RETURNING_USER = """Você é o Leo, um colega de classe do 6º ano que ajuda outros alunos com suas dúvidas e problemas.

CONVERSA CONTÍNUA:
Você já conhece este aluno! Aja naturalmente como se vocês já fossem amigos. Use o histórico da conversa para:
- Lembrar do nome dele se ele já te contou
- Fazer referência a conversas anteriores quando relevante
- Ser mais informal e próximo, como amigos de verdade

Características gerais:
- Fale como um aluno do 6º ano (11-12 anos)
- Use gírias apropriadas e emojis quando fizer sentido
- Seja empático e acolhedor
- Não seja formal demais, você é um amigo ajudando outro amigo

Você tem DOIS MODOS de interação:

MODO 1 - CONVERSA EMPÁTICA (desabafos, sentimentos, problemas pessoais):
- Ouça com atenção e demonstre empatia
- Faça perguntas abertas para entender melhor: "Como você está se sentindo?", "O que aconteceu?"
- NÃO dê soluções imediatas ou conselhos não solicitados
- Valide os sentimentos: "Entendo que isso deve ser difícil"
- Seja um amigo que escuta, não um conselheiro
- Use emojis para transmitir apoio: 😊 💙 🤗

MODO 2 - SUPORTE ACADÊMICO (dúvidas sobre matérias, lição de casa):
- Explique conceitos de forma clara e simples
- Use exemplos do dia a dia que um aluno do 6º ano entenda
- Faça perguntas para verificar entendimento: "Faz sentido?", "Quer que eu explique de outro jeito?"
- NÃO dê respostas prontas, ajude o aluno a pensar
- Divida explicações complexas em passos menores
- Use emojis para tornar o aprendizado mais leve: 📚 ✨ 💡

IMPORTANTE: Identifique automaticamente qual modo usar baseado na mensagem do aluno. Se o aluno está desabafando ou falando de sentimentos, use MODO 1. Se está perguntando sobre matéria escolar, use MODO 2."""


class LeoAgent:
    """LangChain-based agent for Leo educational chatbot"""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile", 
                 max_messages: int = 20, provider: str = "groq", rag_service=None):
        """
        Initialize Leo agent with LangChain
        
        Args:
            api_key: LLM API key (OpenAI or Groq)
            model: LLM model name
            max_messages: Maximum messages to keep in memory per user
            provider: LLM provider ('openai' or 'groq')
            rag_service: Optional RAG service for document retrieval
        """
        self.rag_service = rag_service
        self.provider = provider
        self.model = model
        
        # Initialize security and monitoring
        self.security = SecurityGuard()
        self.cost_monitor = CostMonitor()
        # Initialize LLM based on provider
        if provider == "groq":
            self.llm = ChatGroq(
                model=model,
                temperature=0.7,
                max_tokens=500,
                groq_api_key=api_key
            )
        else:  # openai
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.7,
                max_tokens=500,
                openai_api_key=api_key
            )
        
        # Memory storage per phone number
        self.memories: Dict[str, ChatMessageHistory] = {}
        self.max_messages = max_messages
        
        # Create prompt templates for new and returning users
        self.prompt_new_user = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_NEW_USER),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        self.prompt_returning_user = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_RETURNING_USER),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        logger.info(f"LeoAgent initialized with {provider} provider and model {model}")
    
    def get_or_create_memory(self, phone_number: str) -> ChatMessageHistory:
        """
        Get existing memory or create new one for phone number
        
        Args:
            phone_number: User's phone number
            
        Returns:
            ChatMessageHistory instance
        """
        if phone_number not in self.memories:
            self.memories[phone_number] = ChatMessageHistory()
            logger.info(f"Created new memory for {phone_number}")
        
        return self.memories[phone_number]
    
    def is_new_user(self, phone_number: str) -> bool:
        """
        Check if this is a new user (no conversation history)
        
        Args:
            phone_number: User's phone number
            
        Returns:
            True if new user, False if returning user
        """
        if phone_number not in self.memories:
            return True
        return len(self.memories[phone_number].messages) == 0
    
    def check_rate_limit(self, phone_number: str) -> tuple[bool, str]:
        """
        Check if user is within rate limits
        
        Returns:
            (allowed, message) - True if allowed, False with reason if not
        """
        current_time = time.time()
        
        # Check minimum interval between messages
        if phone_number in _last_message_time:
            time_since_last = current_time - _last_message_time[phone_number]
            if time_since_last < MIN_MESSAGE_INTERVAL:
                return False, "Calma aí! Espera só um pouquinho antes de mandar outra mensagem 😅"
        
        # Check hourly message count
        if phone_number not in _message_count:
            _message_count[phone_number] = 0
        
        if _message_count[phone_number] >= MAX_MESSAGES_PER_HOUR:
            return False, "Opa, você já mandou muitas mensagens hoje! Vamos conversar mais amanhã? 😊"
        
        return True, ""
    
    def update_rate_limit(self, phone_number: str):
        """Update rate limit counters"""
        _last_message_time[phone_number] = time.time()
        _message_count[phone_number] = _message_count.get(phone_number, 0) + 1
    
    async def generate_response(self, phone_number: str, message: str) -> str:
        """
        Generate response using LangChain with conversation memory
        
        Args:
            phone_number: User's phone number
            message: User's message text
            
        Returns:
            Generated response text
        """
        try:
            # Check rate limits
            allowed, limit_message = self.check_rate_limit(phone_number)
            if not allowed:
                logger.warning(f"Rate limit exceeded for {phone_number}")
                return limit_message
            
            # Security check: prompt injection
            is_safe, security_msg = self.security.check_prompt_injection(message)
            if not is_safe:
                logger.warning(f"Security block for {phone_number}: {security_msg}")
                return security_msg
            
            # Sanitize input
            message = self.security.sanitize_input(message)
            
            # Input validation
            if len(message) > 500:
                return "Opa, sua mensagem tá muito grande! Tenta resumir um pouco? 😅"
            
            if not message.strip():
                return "Não entendi... pode mandar de novo? 🤔"
            
            # Check user API limits
            within_limit, limit_msg = self.cost_monitor.check_user_limit(phone_number, max_requests=100)
            if not within_limit:
                return limit_msg
            
            # Check if this is a new user
            is_new = self.is_new_user(phone_number)
            
            # Get or create memory for this user
            memory = self.get_or_create_memory(phone_number)
            
            # Get chat history (limit to last 20 messages)
            messages = memory.messages[-20:] if len(memory.messages) > 20 else memory.messages
            
            # Check if RAG context is needed (keywords: tarefa, calendario, prova, trabalho)
            rag_context = None
            if self.rag_service and any(keyword in message.lower() for keyword in 
                                       ["tarefa", "calendario", "prova", "trabalho", "professor", "quando"]):
                rag_context = self.rag_service.search(message)
                if rag_context:
                    logger.info(f"RAG context found for: {message[:50]}...")
            
            # Choose prompt based on user status
            if is_new:
                chain = self.prompt_new_user | self.llm
                logger.info(f"New user detected: {phone_number} - Using introduction prompt")
            else:
                chain = self.prompt_returning_user | self.llm
                logger.info(f"Returning user: {phone_number} - Using regular prompt")
            
            # Prepare input with RAG context if available
            input_message = message
            if rag_context:
                input_message = f"[CONTEXTO DOS DOCUMENTOS DA ESCOLA]:\n{rag_context}\n\n[PERGUNTA DO ALUNO]: {message}"
            
            # Generate response
            response = await chain.ainvoke({
                "chat_history": messages,
                "input": input_message
            })
            
            # Add messages to memory
            memory.add_user_message(message)
            memory.add_ai_message(response.content)
            
            # Update rate limit
            self.update_rate_limit(phone_number)
            
            # Log API usage for cost monitoring
            estimated_tokens = self.security.estimate_tokens(message + response.content)
            self.cost_monitor.log_request(self.provider, self.model, estimated_tokens, phone_number)
            
            logger.info(f"Generated response for {phone_number}")
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response for {phone_number}: {e}")
            # Fallback message
            return "Opa, tive um probleminha aqui 😅 Pode tentar de novo?"
