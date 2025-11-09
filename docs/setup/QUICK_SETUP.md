# ⚡ Quick Setup Checklist - Nino Educational Agent

## 🎯 Complete Setup in 10 Minutes

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] Evolution API running in Docker
- [ ] Groq API key (free from https://console.groq.com/keys)

---

## Step 1: Clone and Setup (2 min)

```powershell
# Clone repository
git clone https://github.com/JoaoTeles87/whatsapp-tutor-bot.git
cd whatsapp-tutor-bot

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure Environment (1 min)

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your settings
notepad .env
```

**Required settings:**
```env
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=your_evolution_api_key
EVOLUTION_INSTANCE=Pro Letras
LLM_PROVIDER=groq
LLM_API_KEY=gsk_your_groq_key_here
LLM_MODEL=llama-3.3-70b-versatile
```

---

## Step 3: Prepare RAG System (2 min)

```powershell
# Install additional dependencies
pip install sentence-transformers faiss-cpu

# Create FAISS index
python prep_rag.py
```

Expected output:
```
📚 Loading documents from ./documentos_escola...
✅ Loaded 4 documents
✅ Split into 5 chunks
🔄 Creating embeddings...
✅ FAISS index saved to ./faiss_index
🎉 RAG preparation complete!
```

---

## Step 4: Start Nino Agent (1 min)

```powershell
# Start server (IMPORTANT: use 0.0.0.0 for Docker compatibility)
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Expected output:
```
INFO - Nino Educational Agent initialized successfully
INFO - Server will run on port 5000
INFO - Using LLM provider: groq
```

**Keep this window open!**

---

## Step 5: Configure Webhook (2 min)

⚠️ **CRITICAL**: Use `host.docker.internal` for Docker!

```powershell
# In a NEW PowerShell window
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
    -Headers @{"apikey"="YOUR_EVOLUTION_API_KEY"}
```

Expected output:
```json
{
  "url": "http://host.docker.internal:5000/webhook",
  "enabled": true,
  "events": ["MESSAGES_UPSERT"]
}
```

---

## Step 6: Verify Connection (1 min)

```powershell
# Test if Evolution API can reach Nino
docker exec evolution_api wget -qO- http://host.docker.internal:5000/health
```

Expected output:
```json
{"status":"healthy"}
```

✅ If you see this, the connection is working!

---

## Step 7: Test Complete Flow (1 min)

```powershell
# Run test script
python test_complete_loop.py
```

Expected output:
```
✅ Webhook received message successfully
✅ Test complete!
```

---

## Step 8: Send Real WhatsApp Message

1. Open WhatsApp on your phone
2. Send message to the bot number (check Evolution API for number)
3. Wait for Nino's response

**Expected response:**
```
E aí! 😊 Eu sou o Nino, tô aqui pra te ajudar! 
Qual é o seu nome?
```

---

## Step 9: Start Dashboard (Optional)

```powershell
# In a NEW PowerShell window
venv\Scripts\activate
streamlit run src/dashboard/dashboard.py
```

Access: http://localhost:8501

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Nino agent running on port 5000
- [ ] Evolution API containers running (`docker ps`)
- [ ] Webhook configured with `host.docker.internal`
- [ ] Health check passes
- [ ] Test message works
- [ ] Real WhatsApp message gets response
- [ ] Dashboard loads (optional)

---

## 🚨 Common Issues

### Issue 1: "ECONNREFUSED"
**Solution:** Make sure webhook URL uses `host.docker.internal`, not IP address

### Issue 2: "No module named X"
**Solution:** 
```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue 3: No response on WhatsApp
**Solution:** Check both:
1. Nino agent logs (PowerShell window)
2. Evolution API logs: `docker logs evolution_api --tail 50`

### Issue 4: Dashboard not loading
**Solution:**
```powershell
# Create empty alerts file if missing
echo "[]" > alertas.json
```

---

## 📚 Next Steps

After successful setup:

1. **Test conversation memory**: Send multiple messages
2. **Test analytics**: Send 4+ messages to trigger analysis
3. **Check dashboard**: View engagement data
4. **Add school documents**: Place .txt files in `documentos_escola/`
5. **Customize prompts**: Edit `src/leo_agent.py`

---

## 🆘 Need Help?

- **Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Full Documentation**: [README.md](README.md)
- **Test Scripts**: 
  - `test_complete_loop.py` - Test full flow
  - `test_groq_api.py` - Test Groq API
  - `test_analytics.py` - Test analytics

---

## 🎯 Success Criteria

You'll know setup is complete when:

✅ Nino responds to WhatsApp messages
✅ Conversation memory works (remembers previous messages)
✅ Analytics runs after 4+ messages
✅ Dashboard shows data
✅ No errors in logs

**Estimated Total Time: 10 minutes**

---

**Last Updated**: 2025-11-09
**Version**: 1.0
