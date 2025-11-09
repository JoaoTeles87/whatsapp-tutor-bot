# Analytics False Positive Fix

## Problem Identified

The system was flagging simple greeting messages like "Oi" and "Meu nome é João" as high-risk students (score_desmotivacao > 0.9). This was happening because:

1. **Short conversations were being analyzed**: The LLM was analyzing conversations with only 1-2 student messages
2. **Lack of context**: Greeting messages don't provide enough information for meaningful engagement analysis
3. **LLM interpretation**: The AI was interpreting minimal engagement in greetings as disengagement/demotivation

## Example False Positives

From `alertas.json`:
```json
{
  "aluno_id": "558195741999",
  "observacoes_chave": ["Oi", "Pedro"],
  "score_desmotivacao": 0.93  // ❌ FALSE POSITIVE
}

{
  "aluno_id": "558198991001",
  "observacoes_chave": ["Oi", "Oi"],
  "score_desmotivacao": 0.9  // ❌ FALSE POSITIVE
}
```

## Solution Implemented

### 1. Minimum Message Threshold
Added logic to skip analysis for conversations with fewer than 3 student messages:

```python
student_messages = [msg for msg in historico if msg['role'] == 'user']

if len(student_messages) < 3:
    logger.info(f"Skipping analysis: conversation too short")
    return None
```

### 2. Minimum Content Length
Skip analysis if total student content is less than 20 characters:

```python
total_content = " ".join([msg['content'] for msg in student_messages])
if len(total_content.strip()) < 20:
    logger.info(f"Skipping analysis: content too minimal")
    return None
```

### 3. Improved LLM Prompt
Updated the system prompt to explicitly handle greetings:

```
[IMPORTANTE - CONTEXTO DE CONVERSA]
- Mensagens curtas de saudação ("Oi", "Olá", apresentações) NÃO devem ser interpretadas como desmotivação
- Considere o CONTEXTO COMPLETO da conversa, não apenas mensagens isoladas
- Se o aluno está iniciando a conversa de forma educada, isso é NEUTRO (score ~0.5), não negativo
- Só classifique como alta desmotivação (>0.7) se houver EVIDÊNCIAS CLARAS de frustração, desistência ou desinteresse
```

## Files Modified

1. **src/analytics_agent.py**
   - Added conversation length validation
   - Added content length validation
   - Improved system prompt with context awareness
   - Returns `None` for conversations too short to analyze

2. **src/message_processor.py**
   - Updated to handle `None` return from analytics
   - Added logging for skipped analyses

## Testing Recommendations

Test with these scenarios:

1. ✅ **Short greeting**: "Oi" → Should NOT be analyzed
2. ✅ **Name introduction**: "Meu nome é João" → Should NOT be analyzed
3. ✅ **Brief exchange**: "Oi" + "Tudo bem?" → Should NOT be analyzed
4. ✅ **Meaningful conversation**: 3+ messages with real content → Should be analyzed
5. ✅ **Actual demotivation**: "Não aguento mais, vou desistir" → Should be flagged

## Expected Behavior

- **Before fix**: Every message analyzed, many false positives
- **After fix**: Only meaningful conversations (3+ messages, 20+ chars) analyzed
- **Result**: More accurate engagement scores, fewer false alarms
