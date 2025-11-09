# 📚 RAG & Analytics Setup Guide

## New Features Added

### 1. 📖 RAG System (Document Retrieval)
Leo can now answer questions about:
- Teacher assignments
- School calendar
- Homework tasks

### 2. 📊 Analytics with Fredricks Framework
Automatic engagement analysis based on Fredricks (2004) framework:
- Behavioral engagement
- Emotional engagement  
- Cognitive engagement
- Risk score calculation

## Setup Instructions

### Step 1: Install New Dependencies

```bash
pip install -r requirements.txt
```

New packages:
- `faiss-cpu` - Vector database for RAG
- `pydantic` - Data validation

### Step 2: Prepare RAG Index

```bash
python prep_rag.py
```

This will:
- Load documents from `./documentos_escola/`
- Create embeddings
- Build FAISS index
- Save to `./faiss_index/`

### Step 3: Add More Documents (Optional)

Add `.txt` files to `./documentos_escola/`:
- Teacher messages
- School calendar
- Study materials
- Homework assignments

Then re-run: `python prep_rag.py`

### Step 4: Restart Server

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## How It Works

### RAG System

**Trigger Keywords**: tarefa, calendario, prova, trabalho, professor, quando

**Example**:
- **Student**: "Qual é a tarefa da semana?"
- **Leo**: Searches documents → Finds teacher message → Responds with task details

### Analytics Agent

**Automatic Analysis**: Runs in background after conversations

**Output**: `alertas.json` with:
```json
{
  "aluno_id": "5581998991001",
  "timestamp": "2025-11-08T23:30:00",
  "engajamento_comportamental": 0.7,
  "engajamento_emocional": 0.8,
  "engajamento_cognitivo": 0.6,
  "score_desmotivacao": 0.3,
  "observacoes_chave": ["Fez perguntas sobre frações"],
  "cidade": "João Pessoa",
  "lat": -7.1195,
  "lon": -34.845
}
```

## Testing

### Test RAG

Send WhatsApp message:
```
"Qual é a tarefa da semana?"
"Quando é a prova de matemática?"
"O que o professor mandou?"
```

### Test Analytics

After a conversation, check `alertas.json`:
```bash
cat alertas.json
```

## Files Created

```
documentos_escola/
├── tarefa_semana_professor.txt
└── calendario_escolar.txt

src/
├── rag_service.py
└── analytics_agent.py

prep_rag.py
alertas.json (generated)
faiss_index/ (generated)
```

## Fredricks Framework

Based on Fredricks, J. A., Blumenfeld, P. C., & Paris, A. H. (2004)

**3 Pillars of Engagement**:

1. **Behavioral** (0.0-1.0)
   - Is the student doing? (participating, completing tasks)

2. **Emotional** (0.0-1.0)
   - Is the student feeling? (curious, positive vs frustrated)

3. **Cognitive** (0.0-1.0)
   - Is the student thinking? (asking deep questions vs superficial)

**Risk Score** = 1.0 - (average of 3 pillars)
- 0.0-0.3: Low risk (engaged)
- 0.3-0.7: Medium risk (needs attention)
- 0.7-1.0: High risk (intervention needed)

## Troubleshooting

### RAG Not Working?

1. Check if `faiss_index/` exists
2. Run `python prep_rag.py`
3. Restart server

### Analytics Not Saving?

1. Check `alertas.json` permissions
2. Check logs for errors
3. Verify Groq API key

## Next Steps

- Add more school documents
- Create dashboard to visualize analytics
- Set up alerts for high-risk students
- Export data to CSV for reports
