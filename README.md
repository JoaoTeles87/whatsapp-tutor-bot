# Nino Educational Agent

> ⚠️ **Status**: MVP/Protótipo de Hackathon - Funcional mas não pronto para produção

Chatbot educacional para WhatsApp que atua como tutor virtual para alunos do 6º ano, integrando com Evolution API.

## Características

- 🤖 Agente conversacional com personalidade de colega de classe
- 💬 Dois modos de interação: empático (desabafos) e acadêmico (dúvidas escolares)
- 🧠 Memória de conversação usando LangChain
- 📱 Integração com WhatsApp via Evolution API
- ⚡ API assíncrona com FastAPI
- 🛡️ Proteção contra prompt injection
- 💰 Monitoramento de custos e uso de API
- 📚 Sistema RAG para documentos escolares
- 📊 Analytics com Framework de Fredricks (2004)

## Requisitos

- Python 3.8+
- Evolution API configurada e rodando
- Chave de API de LLM (Groq GRÁTIS ou OpenAI)

## Instalação

### 1. Criar ambiente virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Obter chave de API do LLM (GRÁTIS)

**Opção 1: Groq (RECOMENDADO - GRÁTIS e RÁPIDO)**

1. Acesse: https://console.groq.com/keys
2. Crie uma conta (grátis)
3. Clique em "Create API Key"
4. Copie a chave que começa com `gsk_...`

**Opção 2: OpenAI (PAGO)**

1. Acesse: https://platform.openai.com/api-keys
2. Crie uma conta e adicione créditos
3. Crie uma API key

### 4. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

**Para Groq (GRÁTIS):**
```env
EVOLUTION_API_URL=http://seu-servidor:8080
EVOLUTION_API_KEY=sua_chave_evolution_api
EVOLUTION_INSTANCE=nome_da_instancia
LLM_PROVIDER=groq
LLM_API_KEY=gsk_sua_chave_groq_aqui
LLM_MODEL=llama-3.1-70b-versatile
```

**Para OpenAI:**
```env
EVOLUTION_API_URL=http://seu-servidor:8080
EVOLUTION_API_KEY=sua_chave_evolution_api
EVOLUTION_INSTANCE=nome_da_instancia
LLM_PROVIDER=openai
LLM_API_KEY=sk-sua-chave-openai
LLM_MODEL=gpt-3.5-turbo
```

## Executar

### Modo desenvolvimento (com reload automático)

```bash
uvicorn main:app --reload --port 5000
```

### Modo produção

```bash
uvicorn main:app --host 0.0.0.0 --port 5000
```

## Modelos LLM Disponíveis

### Groq (GRÁTIS) - Recomendado
- `llama-3.1-70b-versatile` - Melhor qualidade (padrão)
- `llama-3.1-8b-instant` - Mais rápido
- `mixtral-8x7b-32768` - Contexto longo

### OpenAI (PAGO)
- `gpt-3.5-turbo` - Rápido e barato
- `gpt-4` - Melhor qualidade

## Configurar Webhook na Evolution API

Configure a Evolution API para enviar webhooks para:

```
http://seu-servidor:5000/webhook
```

## Estrutura do Projeto

```
.
├── src/
│   ├── config.py           # Configurações e variáveis de ambiente
│   ├── evolution_client.py # Cliente para Evolution API
│   ├── leo_agent.py        # Agente LangChain com prompts
│   └── message_processor.py # Processador de mensagens
├── main.py                 # Aplicação FastAPI
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de variáveis de ambiente
└── README.md              # Este arquivo
```

## Como Funciona

1. Evolution API recebe mensagem do WhatsApp e envia para o webhook
2. FastAPI recebe a mensagem no endpoint `/webhook`
3. MessageProcessor processa a mensagem
4. LeoAgent usa LangChain para gerar resposta contextualizada
5. Resposta é enviada de volta via Evolution API
6. Aluno recebe a mensagem no WhatsApp

## Modos de Interação do Nino

### Modo 1: Conversa Empática
Quando o aluno desabafa ou fala sobre sentimentos:
- Escuta ativa e empática
- Perguntas abertas para entender melhor
- Validação de sentimentos
- Sem conselhos não solicitados

### Modo 2: Suporte Acadêmico
Quando o aluno tem dúvidas escolares:
- Explicações claras e simples
- Exemplos do cotidiano
- Perguntas para verificar entendimento
- Ajuda a pensar, não dá respostas prontas

## Endpoints

- `POST /webhook` - Recebe mensagens da Evolution API
- `GET /health` - Health check do servidor

## 🛡️ Segurança e Otimização

### Proteção contra Prompt Injection
- Detecta e bloqueia tentativas de manipulação do AI
- Sanitização automática de entrada
- Proteção contra spam e repetição excessiva

### Monitoramento de Custos
- Rastreamento de uso de API
- Estatísticas por usuário
- Limites configuráveis

### Rate Limiting
- 2 segundos entre mensagens
- 30 mensagens por hora
- 100 mensagens totais por usuário

📖 **Documentação completa**: [SECURITY_AND_OPTIMIZATION.md](SECURITY_AND_OPTIMIZATION.md)

## 📚 Documentação Adicional

- [FAQ](FAQ.md) - **LEIA PRIMEIRO** - Perguntas frequentes e limitações conhecidas
- [RAG & Analytics Setup](RAG_ANALYTICS_SETUP.md) - Sistema de documentos e análise de engajamento
- [Professor Feature](PROFESSOR_FEATURE.md) - Como professores podem enviar tarefas
- [Security & Optimization](SECURITY_AND_OPTIMIZATION.md) - Segurança e otimização de custos
- [Deployment Success](DEPLOYMENT_SUCCESS.md) - Status e configuração atual

## ⚠️ Limitações Conhecidas

- Sem banco de dados (tudo em memória)
- Perde histórico ao reiniciar
- Não escala horizontalmente
- Segurança básica (não production-ready)
- Sem testes automatizados
- Estimativas de custo aproximadas
- Suporta apenas texto (sem áudio/imagem)

Ver [FAQ.md](FAQ.md) para lista completa.

## Licença

MIT
