# 📡 API Reference

## Base URL

```
http://localhost:5000
```

---

## Endpoints

### 1. Health Check

Check if the Nino agent is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

**Example:**
```bash
curl http://localhost:5000/health
```

---

### 2. Webhook (Evolution API)

Receive incoming WhatsApp messages from Evolution API.

**Endpoint:** `POST /webhook`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "event": "messages.upsert",
  "instance": "Pro Letras",
  "data": {
    "key": {
      "remoteJid": "5581999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "message_id_123"
    },
    "message": {
      "conversation": "Oi Nino, preciso de ajuda"
    },
    "pushName": "Student Name",
    "messageType": "conversation",
    "messageTimestamp": 1699999999
  }
}
```

**Response:**
```json
{
  "status": "success"
}
```

**Status Codes:**
- `200 OK` - Message processed successfully
- `400 Bad Request` - Invalid payload
- `500 Internal Server Error` - Processing error

**Example:**
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "Pro Letras",
    "data": {
      "key": {
        "remoteJid": "5581999999999@s.whatsapp.net",
        "fromMe": false
      },
      "message": {
        "conversation": "Oi Nino"
      }
    }
  }'
```

---

## Webhook Payload Schema

### MessageKey
```typescript
{
  remoteJid: string;      // Phone number with @s.whatsapp.net
  fromMe: boolean;        // true if sent by bot, false if from user
  id?: string;            // Message ID
  participant?: string;   // Group participant (if group message)
}
```

### MessageContent
```typescript
{
  conversation?: string;              // Plain text message
  extendedTextMessage?: {             // Rich text message
    text: string;
  };
  imageMessage?: object;              // Image (not supported)
  videoMessage?: object;              // Video (not supported)
}
```

### MessageData
```typescript
{
  key: MessageKey;
  message: MessageContent;
  pushName?: string;                  // Sender's display name
  messageType?: string;               // "conversation", "image", etc.
  messageTimestamp?: number;          // Unix timestamp
}
```

### WebhookPayload
```typescript
{
  event: string;                      // "messages.upsert"
  instance: string;                   // Evolution API instance name
  data: MessageData;
  destination?: string;
  date_time?: string;
  sender?: string;
}
```

---

## Evolution API Integration

### Configure Webhook

**Endpoint:** `POST http://localhost:8080/webhook/set/{instance}`

**Headers:**
```
apikey: YOUR_EVOLUTION_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "webhook": {
    "url": "http://host.docker.internal:5000/webhook",
    "events": ["MESSAGES_UPSERT"],
    "enabled": true
  }
}
```

**PowerShell Example:**
```powershell
$body = @{
    webhook=@{
        url="http://host.docker.internal:5000/webhook"
        events=@("MESSAGES_UPSERT")
        enabled=$true
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://localhost:8080/webhook/set/Pro%20Letras" `
    -Method Post `
    -Body $body `
    -ContentType "application/json" `
    -Headers @{"apikey"="YOUR_KEY"}
```

---

### Send Message (Evolution API)

**Endpoint:** `POST http://localhost:8080/message/sendText/{instance}`

**Headers:**
```
apikey: YOUR_EVOLUTION_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "number": "5581999999999",
  "text": "Hello from Nino!"
}
```

**Used internally by:** `src/evolution_client.py`

---

## Internal Services

### Analytics Agent

**Function:** `analisar_conversa(aluno_id, historico)`

**Input:**
```python
aluno_id: str  # Phone number
historico: List[Dict[str, str]]  # Conversation history
# [
#   {"role": "user", "content": "message"},
#   {"role": "assistant", "content": "response"}
# ]
```

**Output:**
```python
AnaliseEngajamento(
    engajamento_comportamental=0.7,
    engajamento_emocional=0.6,
    engajamento_cognitivo=0.8,
    score_desmotivacao=0.3,
    observacoes_chave=["Fez perguntas relevantes"],
    escola="Vista Alegre Park, Haras e Hípica",
    cidade="João Pessoa",
    lat=-7.1195,
    lon=-34.845
)
```

---

### RAG Service

**Function:** `search(query, k=3)`

**Input:**
```python
query: str  # Search query
k: int      # Number of results
```

**Output:**
```python
str  # Concatenated relevant documents
```

**Example:**
```python
rag_service.search("qual a tarefa de matemática?", k=3)
# Returns: "Professor Carlos: A tarefa é sobre frações..."
```

---

## Data Models

### AnaliseEngajamento (Pydantic)

```python
class AnaliseEngajamento(BaseModel):
    engajamento_comportamental: float  # 0.0-1.0
    engajamento_emocional: float       # 0.0-1.0
    engajamento_cognitivo: float       # 0.0-1.0
    score_desmotivacao: float          # 0.0-1.0
    observacoes_chave: List[str]
    escola: str
    cidade: str
    lat: float
    lon: float
```

### Alert Data (JSON)

```json
{
  "aluno_id": "5581999999999",
  "timestamp": "2025-11-09T12:00:00",
  "engajamento_comportamental": 0.7,
  "engajamento_emocional": 0.6,
  "engajamento_cognitivo": 0.8,
  "score_desmotivacao": 0.3,
  "observacoes_chave": ["Participou ativamente"],
  "escola": "Vista Alegre Park, Haras e Hípica",
  "cidade": "João Pessoa",
  "lat": -7.1195,
  "lon": -34.845
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error: field 'fromMe' is required"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

### Per User
- **Minimum interval**: 2 seconds between messages
- **Hourly limit**: 30 messages
- **Total limit**: 100 messages per user

### Responses
```json
{
  "response": "Calma aí! Espera só um pouquinho antes de mandar outra mensagem 😅"
}
```

---

## Security

### Prompt Injection Detection

Blocked patterns:
- System commands
- Role manipulation
- Instruction overrides

**Response:**
```json
{
  "response": "Mensagem bloqueada por segurança. Evite comandos especiais."
}
```

---

## Testing

### Test Webhook
```bash
python tests/test_complete_loop.py
```

### Test Analytics
```bash
python tests/test_analytics.py
```

### Test Groq API
```bash
python tests/test_groq_api.py
```

---

**Version**: 1.0
**Last Updated**: 2025-11-09
