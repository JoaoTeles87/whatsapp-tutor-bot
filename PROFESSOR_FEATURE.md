# 👨‍🏫 Professor Feature - Update RAG via WhatsApp

## Overview

Professors can now send messages directly through WhatsApp to update the RAG system. Leo automatically detects professor messages and saves them as documents that students can query.

## How It Works

### 1. Professor Detection

Leo uses multiple methods to identify professors:

**Method A: Known Numbers** (Instant recognition)
- Add professor numbers to `src/professor_agent.py`:
```python
PROFESSOR_NUMBERS = [
    "558132991244",  # Professor Carlos
    "5581999887766",  # Add more here
]
```

**Method B: Keyword Detection** (Fast check)
- "sou professor"
- "aqui é o professor"
- "tarefa para os alunos"
- "aviso aos alunos"
- "atenção turma"
- "atenção 6º ano"

**Method C: LLM Analysis** (Smart detection)
- Analyzes message context
- Detects formal communication style
- Confidence score > 0.7 required

### 2. Message Flow

```
Professor sends message
    ↓
Leo detects it's a professor (confidence > 0.7)
    ↓
Saves message to documentos_escola/professor_msg_TIMESTAMP.txt
    ↓
Sends confirmation to professor
    ↓
Professor can type "reindexar" to update RAG immediately
```

## Usage Examples

### Example 1: New Assignment

**Professor sends**:
```
Atenção, 6º ano! Aqui é o Professor Carlos.

Nova tarefa de Português para esta semana:

1. Ler o capítulo 5 do livro
2. Fazer resumo de 10 linhas
3. Entregar na sexta-feira

Qualquer dúvida, perguntem para o Leo!
```

**Leo responds**:
```
✅ Mensagem recebida e salva, Professor(a)!

Sua mensagem foi adicionada aos documentos da escola e os alunos poderão consultá-la através do Leo.

📁 Arquivo: professor_msg_20251108_233045.txt
⏰ Salvo em: 08/11/2025 às 23:30

Para que os alunos vejam a atualização, é necessário reindexar o sistema RAG.
Digite "reindexar" para atualizar agora, ou isso será feito automaticamente em breve.

Obrigado por usar o sistema! 📚
```

### Example 2: Reindexing

**Professor sends**:
```
reindexar
```

**Leo responds**:
```
✅ Sistema atualizado com sucesso!

Os alunos já podem consultar sua nova mensagem através do Leo.

Tudo pronto! 🎉
```

### Example 3: Student Query

**Student asks**:
```
Qual é a tarefa de português?
```

**Leo responds** (using RAG):
```
Opa! O Professor Carlos mandou avisar que a tarefa de Português desta semana é:

1. Ler o capítulo 5 do livro
2. Fazer resumo de 10 linhas  
3. Entregar na sexta-feira

Precisa de ajuda com alguma parte? 📚
```

## Configuration

### Add Known Professors

Edit `src/professor_agent.py`:

```python
PROFESSOR_NUMBERS = [
    "558132991244",  # Professor Carlos - Matemática
    "5581999887766",  # Professora Maria - Português
    "5581988776655",  # Professor João - Ciências
]
```

### Customize Keywords

Edit `src/professor_agent.py`:

```python
PROFESSOR_KEYWORDS = [
    "sou professor",
    "sou o professor", 
    "aqui é o professor",
    # Add more keywords
]
```

## File Structure

```
documentos_escola/
├── tarefa_semana_professor.txt (manual)
├── calendario_escolar.txt (manual)
├── professor_msg_20251108_233045.txt (auto-generated)
├── professor_msg_20251108_234512.txt (auto-generated)
└── ... (more auto-generated files)
```

Each auto-generated file includes:
- Timestamp
- Professor's phone number
- Original message content

## Benefits

✅ **No Technical Knowledge Required**: Professors just send WhatsApp messages
✅ **Instant Updates**: Messages saved immediately
✅ **Automatic Detection**: No special commands needed
✅ **Audit Trail**: All messages timestamped and logged
✅ **Student Access**: Students can query via Leo instantly

## Security

- Only detected professors can update documents
- All messages are logged with phone numbers
- Reindexing requires explicit command
- Failed attempts are logged

## Troubleshooting

### Professor Message Not Detected?

1. **Add to known numbers** in `professor_agent.py`
2. **Use clear keywords**: "Atenção turma", "Sou o professor"
3. **Check logs** for detection confidence score

### Reindexing Failed?

1. Check `prep_rag.py` runs without errors
2. Verify `documentos_escola/` folder exists
3. Check file permissions
4. Review logs for specific error

### Students Can't See Updates?

1. Professor must type "reindexar" after sending message
2. Or manually run: `python prep_rag.py`
3. Restart server if needed

## Future Enhancements

- [ ] Automatic reindexing (scheduled)
- [ ] Professor dashboard
- [ ] Message editing/deletion
- [ ] Multi-language support
- [ ] Rich media support (images, PDFs)

## Example Workflow

**Monday Morning**:
1. Professor Carlos sends assignment via WhatsApp
2. Leo saves and confirms
3. Professor types "reindexar"
4. System updates

**Monday Afternoon**:
5. Student asks "qual a tarefa?"
6. Leo retrieves from RAG
7. Student gets instant answer

**No more**: Email chains, lost messages, or confusion! 🎉
