# 🏗️ System Architecture

## Overview

Nino is a microservices-based educational AI system designed for scalability, reliability, and real-time analytics.

## High-Level Architecture

```
┌─────────────────┐
│  WhatsApp User  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   Evolution API         │
│   (Docker Container)    │
│   - WhatsApp Gateway    │
│   - Message Queue       │
└────────┬────────────────┘
         │ HTTP Webhook
         ▼
┌─────────────────────────┐
│   Nino Agent (FastAPI)  │
│   ┌──────────────────┐  │
│   │  Webhook Handler │  │
│   └────────┬─────────┘  │
│            │             │
│   ┌────────▼─────────┐  │
│   │ Message Processor│  │
│   └────────┬─────────┘  │
│            │             │
│   ┌────────▼─────────┐  │
│   │   LLM Agent      │  │
│   │   (LangChain)    │  │
│   └────────┬─────────┘  │
│            │             │
│   ┌────────▼─────────┐  │
│   │  Analytics Agent │  │
│   └────────┬─────────┘  │
│            │             │
│   ┌────────▼─────────┐  │
│   │   RAG Service    │  │
│   └──────────────────┘  │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Data Layer            │
│   - alertas.json        │
│   - FAISS Index         │
│   - Conversation Memory │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Dashboard (Streamlit) │
│   - Real-time Analytics │
│   - Visualizations      │
└─────────────────────────┘
```

## Component Details

### 1. Evolution API (External)
- **Technology**: Node.js, Baileys
- **Purpose**: WhatsApp Business API integration
- **Deployment**: Docker containers
- **Communication**: HTTP webhooks

### 2. Nino Agent (Core)
- **Technology**: FastAPI, Python 3.8+
- **Purpose**: Main application logic
- **Components**:
  - Webhook Handler
  - Message Processor
  - LLM Agent
  - Analytics Engine
  - RAG Service

### 3. LLM Integration
- **Provider**: Groq (free tier)
- **Model**: llama-3.3-70b-versatile
- **Framework**: LangChain
- **Features**:
  - Conversation memory
  - Dual-mode prompts
  - Context management

### 4. Analytics System
- **Framework**: Fredricks (2004)
- **Metrics**:
  - Behavioral engagement
  - Emotional engagement
  - Cognitive engagement
- **Output**: Risk scores (0.0-1.0)

### 5. RAG System
- **Embeddings**: HuggingFace (sentence-transformers)
- **Vector DB**: FAISS
- **Purpose**: School document retrieval

### 6. Dashboard
- **Technology**: Streamlit, Plotly
- **Features**:
  - Real-time metrics
  - Interactive maps
  - Risk visualization

## Data Flow

### Incoming Message Flow

```
1. User sends WhatsApp message
   ↓
2. Evolution API receives message
   ↓
3. Evolution API sends webhook POST
   {
     "event": "messages.upsert",
     "data": {
       "key": {"remoteJid": "phone@s.whatsapp.net"},
       "message": {"conversation": "text"}
     }
   }
   ↓
4. Webhook Handler validates & parses
   ↓
5. Message Processor routes message
   ├─→ Professor Agent (if teacher)
   ├─→ Alert Detector (if critical)
   └─→ LLM Agent (regular message)
   ↓
6. LLM Agent processes
   ├─→ Retrieves conversation history
   ├─→ Checks RAG for context
   ├─→ Generates response
   └─→ Stores in memory
   ↓
7. Response sent via Evolution API
   ↓
8. Analytics Agent analyzes (if ≥4 messages)
   ↓
9. Data saved to alertas.json
   ↓
10. Dashboard updates (5s cache)
```

## Security Architecture

### Layers of Protection

1. **Input Validation**
   - Pydantic models
   - Type checking
   - Length limits

2. **Prompt Injection Detection**
   - Pattern matching
   - Keyword filtering
   - Sanitization

3. **Rate Limiting**
   - Per-user limits
   - Time-based throttling
   - Cost monitoring

4. **Data Privacy**
   - Anonymous IDs in dashboard
   - No PII storage
   - Secure memory management

## Scalability Considerations

### Current Capacity
- **Concurrent Users**: 100+
- **Messages/Second**: 10+
- **Response Time**: <2s average

### Bottlenecks
1. **LLM API**: Groq rate limits
2. **Memory**: In-memory conversation storage
3. **File I/O**: JSON-based data storage

### Future Improvements
1. **Database**: PostgreSQL for persistence
2. **Cache**: Redis for conversation memory
3. **Queue**: RabbitMQ for message processing
4. **Load Balancer**: Multiple Nino instances

## Deployment Architecture

### Development
```
Local Machine
├── Nino Agent (Python)
├── Evolution API (Docker)
└── Dashboard (Streamlit)
```

### Production (Recommended)
```
Cloud Infrastructure
├── Nino Agent (Container)
│   ├── Auto-scaling
│   └── Load balancer
├── Evolution API (Container)
├── PostgreSQL (Managed)
├── Redis (Managed)
└── Dashboard (Container)
```

## Technology Stack

### Backend
- **FastAPI**: Async web framework
- **LangChain**: LLM orchestration
- **Pydantic**: Data validation
- **HTTPX**: Async HTTP client

### AI/ML
- **Groq**: LLM inference
- **HuggingFace**: Embeddings
- **FAISS**: Vector search
- **Sentence Transformers**: Text encoding

### Frontend
- **Streamlit**: Dashboard framework
- **Plotly**: Interactive charts
- **Pandas**: Data manipulation

### Infrastructure
- **Docker**: Containerization
- **Evolution API**: WhatsApp gateway

## Performance Metrics

### Response Times
- Webhook processing: <100ms
- LLM generation: 1-2s
- Analytics: 2-3s
- Dashboard update: 5s cache

### Resource Usage
- **CPU**: 2-4 cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB for indexes + logs
- **Network**: 10Mbps minimum

## Monitoring & Logging

### Log Levels
- **INFO**: Normal operations
- **WARNING**: Rate limits, retries
- **ERROR**: Failed operations
- **CRITICAL**: System failures

### Key Metrics
- Message processing rate
- LLM response time
- Error rate
- User engagement scores

## API Endpoints

### Public Endpoints
- `POST /webhook` - Receive Evolution API messages
- `GET /health` - Health check

### Internal Services
- LLM Agent (in-process)
- Analytics Agent (in-process)
- RAG Service (in-process)

## Configuration Management

### Environment Variables
- API keys (Evolution, Groq)
- Server settings
- Feature flags
- Rate limits

### Runtime Configuration
- Conversation memory size
- Analytics thresholds
- Security rules

---

**Version**: 1.0
**Last Updated**: 2025-11-09
