# 👨‍🏫 Professor Workflow - Smart MVP Solution

## Problem Solved
❌ **Before**: System saved "Sou professor" immediately → useless for students
✅ **After**: Multi-turn conversation to collect complete message before saving

## How It Works

### Step 1: Professor Identification
Professor sends: `"Sou professor e quero fazer um novo dever de casa"`

System responds:
```
👨‍🏫 Olá, Professor(a)!

Detectei que você quer criar um novo comunicado para os alunos.

Por favor, envie a mensagem completa que deseja compartilhar com a turma...

Quando terminar, envie: "PUBLICAR"
Para cancelar, envie: "CANCELAR"
```

### Step 2: Content Collection
Professor sends multiple messages:
```
Message 1: "Atenção 6º ano!"
Message 2: "Tarefa de matemática para segunda-feira"
Message 3: "Resolver exercícios 1-10 da página 65"
```

System shows preview after each message:
```
📝 Mensagem adicionada ao rascunho:

---
Atenção 6º ano!

Tarefa de matemática para segunda-feira

Resolver exercícios 1-10 da página 65
---

Continue enviando ou digite "PUBLICAR"
```

### Step 3: Publication
Professor sends: `"PUBLICAR"`

System saves and confirms:
```
✅ Mensagem publicada com sucesso!

📁 Arquivo: professor_msg_20251108_235616.txt
⏰ Publicado em: 08/11/2025 às 23:56

⚠️ Para atualização imediata, digite: "REINDEXAR"
```

### Step 4: Reindexing
Professor sends: `"REINDEXAR"`

System updates RAG:
```
✅ Sistema atualizado com sucesso!

Os alunos já podem consultar sua nova mensagem através do Leo.
```

## Key Features

### 1. Session Management
- Tracks professor conversation state
- Buffers messages until "PUBLICAR"
- Can cancel with "CANCELAR"

### 2. Known Professors
Configured in `src/professor_agent.py`:
```python
PROFESSOR_NUMBERS = [
    "558132991244",  # Professor Carlos
    "558195435686",  # Professor João
]
```

### 3. Smart Detection
- Known number → Instant recognition
- Keywords → Quick check
- LLM analysis → For uncertain cases

### 4. Preview Before Save
- Shows accumulated content
- Allows editing (just send more messages)
- Confirms before publishing

## Testing

### Test as Professor (558195435686)

**Message 1:**
```
Sou professor e tenho um aviso
```

**Expected Response:**
```
👨‍🏫 Olá, Professor(a)!
Detectei que você quer criar um novo comunicado...
```

**Message 2:**
```
Atenção turma! Prova de ciências na sexta-feira.
Estudem os capítulos 3 e 4.
```

**Expected Response:**
```
📝 Mensagem adicionada ao rascunho:
---
Atenção turma! Prova de ciências na sexta-feira...
---
```

**Message 3:**
```
PUBLICAR
```

**Expected Response:**
```
✅ Mensagem publicada com sucesso!
```

**Message 4:**
```
REINDEXAR
```

**Expected Response:**
```
✅ Sistema atualizado com sucesso!
```

## Student Experience

After reindexing, students can ask:
```
Student: "Qual é a tarefa de matemática?"
Leo: "O Professor João mandou avisar que a tarefa é..."
```

## Architecture

```
Professor Message
    ↓
Detect Professor (LLM)
    ↓
Start Session
    ↓
Buffer Messages
    ↓
"PUBLICAR" command
    ↓
Save to documentos_escola/
    ↓
"REINDEXAR" command
    ↓
Run prep_rag.py
    ↓
Students can query via Leo
```

## Advantages of This Approach

✅ **No premature saves** - Waits for complete content
✅ **Preview & edit** - Professor sees what will be published
✅ **Explicit confirmation** - "PUBLICAR" command required
✅ **Cancellable** - Can abort with "CANCELAR"
✅ **Multi-message support** - Can send content in parts
✅ **Simple commands** - Just "PUBLICAR" and "REINDEXAR"

## Files Modified

- `src/professor_agent.py` - Added session management
- `src/message_processor.py` - Added workflow handling
- `main.py` - Already configured

## Next Steps

1. Restart server to load changes
2. Test with professor number
3. Verify students can query after reindex
4. Add more professor numbers if needed

## Configuration

Add professor numbers in `src/professor_agent.py`:
```python
PROFESSOR_NUMBERS = [
    "558132991244",
    "558195435686",
    "5581XXXXXXXX",  # Add more here
]
```
