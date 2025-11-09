# 🔧 Troubleshooting Guide - Nino Educational Agent

## Table of Contents
1. [Webhook Connection Issues](#webhook-connection-issues)
2. [WhatsApp Not Responding](#whatsapp-not-responding)
3. [Docker Networking Problems](#docker-networking-problems)
4. [Analytics Not Working](#analytics-not-working)
5. [Dashboard Issues](#dashboard-issues)
6. [Common Error Messages](#common-error-messages)

---

## 🚨 Webhook Connection Issues

### Problem: Evolution API can't reach Nino Agent

**Symptoms:**
- Evolution API logs show: `ECONNREFUSED 192.168.1.114:5000`
- WhatsApp messages not triggering responses
- Webhook retries failing

**Root Cause:**
Evolution API runs inside Docker and cannot reach the host machine's IP address directly.

**Solution:**

#### ✅ Use `host.docker.internal` (Recommended)

```powershell
# Update webhook URL to use Docker's special DNS
$body = @{
    webhook=@{
        url="http://host.docker.internal:5000/webhook"
        events=@("MESSAGES_UPSERT")
        enabled=$true
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8080/webhook/set/Pro%20Letras" `
    -Method Post `
    -Body $body `
    -ContentType "application/json" `
    -Headers @{"apikey"="YOUR_API_KEY"}
```

#### Alternative: Use Docker Network

If `host.docker.internal` doesn't work:

1. **Find your Docker network gateway:**
```powershell
docker network inspect bridge | Select-String "Gateway"
```

2. **Use the gateway IP** (usually `172.17.0.1`):
```powershell
# Update webhook URL
url="http://172.17.0.1:5000/webhook"
```

#### Verification:

Test if Evolution API can reach Nino:
```powershell
# Should return: {"status":"healthy"}
docker exec evolution_api wget -qO- http://host.docker.internal:5000/health
```

---

## 📱 WhatsApp Not Responding

### Problem: Messages sent but no response received

**Diagnostic Steps:**

#### 1. Check if Nino Agent is Running
```powershell
# Should show uvicorn process
Get-Process | Where-Object {$_.ProcessName -like "*uvicorn*"}

# Check if port 5000 is listening
netstat -an | Select-String "5000"
# Should show: TCP    0.0.0.0:5000    LISTENING
```

#### 2. Verify Evolution API Connection
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/instance/connectionState/Pro%20Letras" `
    -Headers @{"apikey"="YOUR_API_KEY"}
# Should return: state=open
```

#### 3. Check Webhook Configuration
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/webhook/find/Pro%20Letras" `
    -Headers @{"apikey"="YOUR_API_KEY"}
```

Expected output:
```json
{
  "url": "http://host.docker.internal:5000/webhook",
  "enabled": true,
  "events": ["MESSAGES_UPSERT"]
}
```

#### 4. Test Webhook Manually
```powershell
$body = @{
    event="messages.upsert"
    instance="Pro Letras"
    data=@{
        key=@{
            remoteJid="YOUR_NUMBER@s.whatsapp.net"
            fromMe=$false
        }
        message=@{
            conversation="Test message"
        }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:5000/webhook" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

#### 5. Monitor Logs

**Nino Agent Logs:**
Look for these messages in the PowerShell window running uvicorn:
```
INFO - Received webhook event: messages.upsert
INFO - Processing message from YOUR_NUMBER
INFO - Generated response for YOUR_NUMBER
INFO - Message sent successfully to YOUR_NUMBER
```

**Evolution API Logs:**
```powershell
docker logs evolution_api --tail 50 --follow
```

Look for:
- Incoming message from your number
- Webhook POST to host.docker.internal:5000
- Response being sent back

---

## 🐳 Docker Networking Problems

### Problem: Services can't communicate

#### Issue A: Evolution API can't reach host machine

**Symptoms:**
- Connection refused errors
- Webhook timeouts

**Solutions:**

1. **Use `host.docker.internal`** (Windows/Mac)
   ```
   http://host.docker.internal:5000/webhook
   ```

2. **Use Docker gateway IP** (Linux)
   ```bash
   # Find gateway
   docker network inspect bridge | grep Gateway
   # Use: http://172.17.0.1:5000/webhook
   ```

3. **Use host network mode** (Linux only)
   ```yaml
   # docker-compose.yml
   services:
     evolution_api:
       network_mode: "host"
   ```

#### Issue B: Firewall blocking connections

**Windows Firewall:**
```powershell
# Allow Python through firewall
New-NetFirewallRule -DisplayName "Python Nino Agent" `
    -Direction Inbound `
    -Program "C:\Path\To\Python\python.exe" `
    -Action Allow
```

**Check if port is accessible:**
```powershell
Test-NetConnection -ComputerName localhost -Port 5000
```

---

## 📊 Analytics Not Working

### Problem: Dashboard shows only mock data

**Symptoms:**
- No real conversation data in dashboard
- `alertas.json` not updating
- Analytics not running

**Diagnostic Steps:**

#### 1. Verify Analytics Agent is Initialized
Check `main.py` logs for:
```
INFO - AgenteAnalista initialized with Fredricks framework
```

#### 2. Check Conversation Length
Analytics only runs after **4+ messages** (2 exchanges):
```
User: "Oi Nino"
Nino: "E aí! 😊..."
User: "Preciso de ajuda"
Nino: "Claro! Como posso ajudar?"
← Analytics runs here
```

#### 3. Verify Analytics is Called
Check logs for:
```
INFO - Running engagement analysis for YOUR_NUMBER
INFO - Analysis complete for YOUR_NUMBER: risk=0.XX
INFO - Alert saved for YOUR_NUMBER
```

#### 4. Check alertas.json
```powershell
# Count records
(Get-Content alertas.json | ConvertFrom-Json).Count

# View latest
Get-Content alertas.json | ConvertFrom-Json | Select-Object -Last 1
```

#### 5. Manual Test
```powershell
venv\Scripts\activate
python test_analytics.py
```

---

## 🎨 Dashboard Issues

### Problem: Dashboard not loading data

#### Issue A: File not found
```
FileNotFoundError: alertas.json
```

**Solution:**
```powershell
# Create empty file
echo "[]" > alertas.json
```

#### Issue B: Timestamp parsing error
```
Error: unconverted data remains when parsing
```

**Solution:** Already fixed in dashboard code using `format='ISO8601'`

#### Issue C: Dashboard not updating

**Solutions:**

1. **Clear cache:**
   - Click "🔄 Atualizar Dados" button in sidebar
   - Or press F5 to reload page

2. **Check cache TTL:**
   ```python
   # In dashboard.py
   @st.cache_data(ttl=5)  # Updates every 5 seconds
   ```

3. **Restart dashboard:**
   ```powershell
   # Stop current dashboard (Ctrl+C)
   venv\Scripts\activate
   streamlit run src/dashboard/dashboard.py
   ```

---

## ⚠️ Common Error Messages

### 1. "ECONNREFUSED 192.168.1.114:5000"

**Meaning:** Evolution API can't reach Nino agent

**Fix:** Use `host.docker.internal:5000` instead of IP address

**Command:**
```powershell
# Update webhook URL
$body = @{webhook=@{url="http://host.docker.internal:5000/webhook";events=@("MESSAGES_UPSERT");enabled=$true}} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Uri "http://localhost:8080/webhook/set/Pro%20Letras" -Method Post -Body $body -ContentType "application/json" -Headers @{"apikey"="YOUR_KEY"}
```

---

### 2. "No module named 'langchain_community'"

**Meaning:** Missing dependency

**Fix:**
```powershell
venv\Scripts\activate
pip install langchain-community
```

---

### 3. "Could not import faiss python package"

**Meaning:** FAISS not installed

**Fix:**
```powershell
venv\Scripts\activate
pip install faiss-cpu
```

---

### 4. "Invalid comparison between dtype=datetime64[ns] and Timestamp"

**Meaning:** Timezone mismatch in dashboard

**Fix:** Already fixed in dashboard code (removes timezone)

---

### 5. "Rate limit exceeded"

**Meaning:** Too many messages sent too quickly

**Current Limits:**
- 2 seconds between messages
- 30 messages per hour per user
- 100 total messages per user

**Fix:** Wait before sending next message

---

## 🔍 Complete Flow Verification

### Step-by-Step Test:

1. **Start Nino Agent:**
   ```powershell
   venv\Scripts\activate
   uvicorn main:app --reload --host 0.0.0.0 --port 5000
   ```

2. **Verify Health:**
   ```powershell
   curl http://localhost:5000/health
   # Should return: {"status":"healthy"}
   ```

3. **Check Evolution API:**
   ```powershell
   docker ps | Select-String "evolution"
   # Should show 3 containers running
   ```

4. **Verify Webhook:**
   ```powershell
   docker exec evolution_api wget -qO- http://host.docker.internal:5000/health
   # Should return: {"status":"healthy"}
   ```

5. **Send Test Message:**
   ```powershell
   python test_complete_loop.py
   ```

6. **Check Logs:**
   - Nino Agent: Look in PowerShell window
   - Evolution API: `docker logs evolution_api --tail 50`

7. **Send Real WhatsApp Message:**
   - Open WhatsApp on your phone
   - Send message to bot number
   - Wait for response

---

## 📞 Quick Reference

### Important URLs:
- **Nino Agent**: http://localhost:5000
- **Evolution API**: http://localhost:8080
- **Dashboard**: http://localhost:8501

### Important Files:
- **Webhook**: `src/webhook.py`
- **Agent**: `src/leo_agent.py`
- **Analytics**: `src/analytics_agent.py`
- **Dashboard**: `src/dashboard/dashboard.py`
- **Data**: `alertas.json`

### Important Commands:

**Start Nino:**
```powershell
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

**Start Dashboard:**
```powershell
venv\Scripts\activate
streamlit run src/dashboard/dashboard.py
```

**Check Evolution API:**
```powershell
docker ps
docker logs evolution_api --tail 50
```

**Update Webhook:**
```powershell
$body = @{webhook=@{url="http://host.docker.internal:5000/webhook";events=@("MESSAGES_UPSERT");enabled=$true}} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Uri "http://localhost:8080/webhook/set/Pro%20Letras" -Method Post -Body $body -ContentType "application/json" -Headers @{"apikey"="YOUR_KEY"}
```

---

## 🆘 Still Having Issues?

### Diagnostic Script:
```powershell
venv\Scripts\activate
python diagnose_flow.py
```

### Collect Information:
1. Nino Agent logs (PowerShell window)
2. Evolution API logs: `docker logs evolution_api --tail 100`
3. Webhook configuration
4. Network connectivity test results

### Common Solutions Checklist:
- [ ] Nino agent running on 0.0.0.0:5000
- [ ] Evolution API containers running
- [ ] Webhook URL uses `host.docker.internal`
- [ ] WhatsApp instance connected (state: open)
- [ ] Firewall allows port 5000
- [ ] All dependencies installed
- [ ] Virtual environment activated

---

**Last Updated**: 2025-11-09
**Version**: 1.0
