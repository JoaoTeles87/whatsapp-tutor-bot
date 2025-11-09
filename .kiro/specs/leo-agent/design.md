# Design Document - Leo Educational Agent

## Overview

The Leo Educational Agent is a Python-based WhatsApp chatbot that integrates with an existing Evolution API instance. The system receives messages via webhook, processes them using LangChain with OpenAI LLM, maintains conversation context in memory, and sends responses back through the Evolution API.

**Core Design Principles:**
- FastAPI for modern async webhook handling
- LangChain for flexible LLM orchestration and conversation management
- Dual-mode interaction: empathetic conversation and academic support
- In-memory session storage for conversation history
- Environment-based configuration for easy deployment

## Architecture

### High-Level Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│  WhatsApp   │◄───────►│  Evolution API   │◄───────►│  Leo Agent  │
│   Users     │         │   (External)     │         │   System    │
└─────────────┘         └──────────────────┘         └─────────────┘
                                                             │
                                                             ▼
                                                      ┌─────────────┐
                                                      │  OpenAI API │
                                                      └─────────────┘
```

### Component Architecture

```
┌────────────────────────────────────────────────────┐
│              Leo Agent System                      │
│                                                    │
│  ┌──────────────┐    ┌─────────────────┐         │
│  │   Webhook    │───►│  Message        │         │
│  │   Handler    │    │  Processor      │         │
│  │  (FastAPI)   │    │                 │         │
│  └──────────────┘    └────────┬────────┘         │
│                               │                   │
│                               ▼                   │
│                      ┌─────────────────┐          │
│                      │  LangChain      │          │
│                      │  Agent          │          │
│                      │  - Memory       │          │
│                      │  - Prompts      │          │
│                      └────────┬────────┘          │
│                               │                   │
│                               ▼                   │
│                      ┌─────────────────┐          │
│                      │  OpenAI LLM     │          │
│                      │  (via LangChain)│          │
│                      └────────┬────────┘          │
│                               │                   │
│                               ▼                   │
│                      ┌─────────────────┐          │
│                      │  Evolution API  │          │
│                      │  Client         │          │
│                      └─────────────────┘          │
└────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Webhook Handler (FastAPI Server)

**Responsibility:** Receive incoming messages from Evolution API

**Interface:**
```python
POST /webhook
Content-Type: application/json

Request Body (Evolution API format):
{
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": false
  },
  "message": {
    "conversation": "Oi Leo, preciso de ajuda com matemática"
  }
}

Response:
200 OK
```

**Key Functions:**
- `create_app()`: Initialize FastAPI application
- `webhook_endpoint()`: Async POST handler
- `extract_message_data(payload)`: Parse Evolution API payload
- `validate_payload(payload)`: Ensure required fields exist

### 2. Message Processor

**Responsibility:** Orchestrate message flow between components

**Interface:**
```python
class MessageProcessor:
    async def process_message(self, phone_number: str, message_text: str) -> None:
        """Process incoming message and send response"""
        
    async def _handle_message(self, phone_number: str, message_text: str) -> str:
        """Generate response using LangChain agent"""
```

**Key Functions:**
- Retrieve conversation memory from LangChain
- Invoke LangChain agent with message
- Send response via Evolution API
- Handle async processing

### 3. LangChain Agent with Memory

**Responsibility:** Manage conversation context and generate responses

**Components:**
- **ConversationBufferWindowMemory**: LangChain memory to store last 10 message exchanges per user
- **ChatOpenAI**: LLM instance configured for Leo's personality
- **Prompt Templates**: Dual-mode prompts for empathetic and academic responses

**Interface:**
```python
class LeoAgent:
    def __init__(self):
        self.memories = {}  # phone_number -> ConversationBufferWindowMemory
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        
    def get_memory(self, phone_number: str) -> ConversationBufferWindowMemory:
        """Get or create memory for a phone number"""
        
    async def generate_response(self, phone_number: str, message: str) -> str:
        """Generate response using LangChain with conversation memory"""
```

**Memory Configuration:**
- Window size: 10 (last 10 exchanges = 20 messages)
- Memory key: "chat_history"
- Return messages: True
- Indexed by phone number

### 4. Prompt Templates (Dual-Mode)

**Responsibility:** Define Leo's behavior for different interaction types

**System Prompt (Base):**
```
Você é o Leo, um colega de classe do 6º ano que ajuda outros alunos com suas dúvidas e problemas.

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

IMPORTANTE: Identifique automaticamente qual modo usar baseado na mensagem do aluno. Se o aluno está desabafando ou falando de sentimentos, use MODO 1. Se está perguntando sobre matéria escolar, use MODO 2.
```

**LangChain Prompt Template:**
```python
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])
```

**LLM Configuration:**
- Model: gpt-3.5-turbo (or gpt-4 if specified)
- Temperature: 0.7 (balanced creativity)
- Max tokens: 500 (concise responses)

### 5. Evolution API Client

**Responsibility:** Send messages back to WhatsApp users

**Interface:**
```python
class EvolutionAPIClient:
    def send_message(self, phone_number: str, text: str) -> bool:
        """Send text message to WhatsApp number"""
```

**API Call:**
```python
POST {EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}
Headers:
  apikey: {EVOLUTION_API_KEY}
  Content-Type: application/json

Body:
{
  "number": "5511999999999",
  "text": "E aí! 😊 Como posso te ajudar?"
}
```

**Implementation:**
- Use httpx for async HTTP requests
- Async send_message method
- Log failed requests
- Return boolean success status

## Data Models

### Message Format (Internal)
```python
{
    "role": str,      # "user" or "assistant"
    "content": str    # Message text
}
```

### Configuration
```python
{
    "evolution_api_url": str,      # Base URL for Evolution API
    "evolution_api_key": str,      # API key for authentication
    "evolution_instance": str,     # Instance name
    "llm_api_key": str,           # OpenAI API key
    "llm_model": str,             # Model name (default: gpt-3.5-turbo)
    "server_port": int,           # Flask server port (default: 5000)
    "max_history_messages": int   # Max messages per user (default: 20)
}
```

## Error Handling

### Webhook Errors
- **Invalid payload**: Return 400 Bad Request with error message
- **Missing required fields**: Return 400 Bad Request
- **Processing exception**: Return 500 Internal Server Error, log error

### LLM Errors
- **API timeout**: Log error, send fallback message to user
- **Rate limit**: Log error, send "Estou um pouco ocupado, tenta de novo em um minutinho?"
- **Invalid API key**: Log error, system should not start

### Evolution API Errors
- **Send failure**: Log error with phone number and message
- **Network timeout**: Log error
- **Invalid credentials**: Log error on startup

### Fallback Message
When LLM fails:
```
"Opa, tive um probleminha aqui 😅 Pode tentar de novo?"
```

## Testing Strategy

### Unit Tests
- `test_message_history.py`: Test history storage, retrieval, and limits
- `test_payload_validation.py`: Test webhook payload parsing
- `test_phone_number_extraction.py`: Test phone number normalization

### Integration Tests
- `test_webhook_flow.py`: Test full webhook → response flow with mocked LLM
- `test_evolution_api_client.py`: Test API client with mocked HTTP responses

### Manual Testing
- Send test messages via Evolution API webhook simulator
- Verify conversation context is maintained across messages
- Test error scenarios (invalid payloads, API failures)

### Test Environment Setup
```bash
# Create test .env
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=test_key
EVOLUTION_INSTANCE=test_instance
LLM_API_KEY=sk-test-key
LLM_MODEL=gpt-3.5-turbo
SERVER_PORT=5001
```

## Deployment Considerations

### Environment Variables
Required:
- `EVOLUTION_API_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- `LLM_API_KEY`

Optional:
- `LLM_MODEL` (default: gpt-3.5-turbo)
- `SERVER_PORT` (default: 5000)
- `MAX_HISTORY_MESSAGES` (default: 20)

### Virtual Environment Setup
```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System
```bash
# Development
uvicorn main:app --reload --port 5000

# Production
uvicorn main:app --host 0.0.0.0 --port 5000
```

### Evolution API Webhook Configuration
Configure Evolution API to send webhooks to:
```
http://your-server:5000/webhook
```

## Security Considerations

- Store API keys in .env file (never commit to git)
- Add .env to .gitignore
- Validate webhook payloads to prevent injection
- Consider adding webhook signature verification (future enhancement)
- Rate limiting on webhook endpoint (future enhancement)

## Future Enhancements (Out of Scope)

- Persistent storage (database) for conversation history
- RAG integration for educational content
- Analytics and sentiment analysis
- Multi-language support
- Admin dashboard
- Message queue for async processing
