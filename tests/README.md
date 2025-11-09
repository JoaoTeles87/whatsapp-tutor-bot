# 🧪 Test Suite

## Overview

Comprehensive test scripts for validating Nino's functionality.

---

## Test Scripts

### 1. test_groq_api.py
**Purpose:** Verify Groq API connectivity and LLM functionality

**Usage:**
```bash
python tests/test_groq_api.py
```

**Tests:**
- API key validation
- Model initialization
- Response generation
- Portuguese language support

**Expected Output:**
```
✅ Groq client initialized
✅ Response received!
📥 Response: Olá, estou trabalhando!
🎉 Groq API is working perfectly!
```

---

### 2. test_complete_loop.py
**Purpose:** Test end-to-end conversation flow

**Usage:**
```bash
python tests/test_complete_loop.py
```

**Tests:**
- Webhook reception
- Message processing
- Response generation
- Evolution API integration

**Expected Output:**
```
✅ Webhook received message successfully
✅ Test complete!
📱 Check your WhatsApp number: 558132991244
```

---

### 3. test_analytics.py
**Purpose:** Validate engagement analytics system

**Usage:**
```bash
python tests/test_analytics.py
```

**Tests:**
- Conversation analysis
- Fredricks framework scoring
- Risk calculation
- Data persistence

**Expected Output:**
```
📊 RESULTADO DA ANÁLISE:
   Engajamento Comportamental: 0.20
   Engajamento Emocional: 0.10
   Engajamento Cognitivo: 0.30
   🚨 Score de Desmotivação: 0.80
🔴 ALERTA ALTO: Aluno em risco de evasão!
```

---

### 4. simulate_conversations.py
**Purpose:** Generate realistic conversation data for dashboard

**Usage:**
```bash
python tests/simulate_conversations.py
```

**Tests:**
- Multiple conversation scenarios
- Different engagement levels
- Data generation for dashboard

**Expected Output:**
```
📱 Seu número - Desmotivado (558132991244)
   Score: 0.70
   Status: 🔴 CRÍTICO

📱 Aluno engajado (5581987654322)
   Score: 0.10
   Status: 🟢 BAIXO
```

---

## Running All Tests

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run all tests
python tests/test_groq_api.py
python tests/test_complete_loop.py
python tests/test_analytics.py
python tests/simulate_conversations.py
```

---

## Test Data

### Mock Students
Located in `alertas.json`:
- 9 mock students from various schools
- Different engagement levels
- Geographic distribution across Paraíba

### School Documents
Located in `documentos_escola/`:
- Professor messages
- School calendar
- Assignments

---

## Continuous Testing

### Before Deployment
1. ✅ Test Groq API connection
2. ✅ Test webhook endpoint
3. ✅ Test complete message flow
4. ✅ Test analytics generation
5. ✅ Verify dashboard loads

### After Changes
1. Run relevant test script
2. Check logs for errors
3. Verify dashboard updates
4. Test with real WhatsApp message

---

## Troubleshooting Tests

### Test Fails: "Connection Refused"
**Solution:** Ensure Nino agent is running
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### Test Fails: "Module Not Found"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Test Fails: "API Key Invalid"
**Solution:** Check `.env` file
```env
LLM_API_KEY=gsk_your_groq_key_here
```

---

## Adding New Tests

### Template
```python
"""
Test description
"""
import asyncio
from src.your_module import YourClass

async def test_your_feature():
    print("🧪 Testing your feature...")
    
    # Setup
    instance = YourClass()
    
    # Test
    result = await instance.your_method()
    
    # Verify
    assert result is not None
    print("✅ Test passed!")

if __name__ == "__main__":
    asyncio.run(test_your_feature())
```

---

**Version**: 1.0
**Last Updated**: 2025-11-09
