"""
Test script to simulate real WhatsApp messages
"""
import requests
import json

# Your real WhatsApp number
PHONE_NUMBER = "558132991244"

# Test messages
test_messages = [
    "Oi Nino!",
    "Preciso de ajuda com matematica",
    "Qual e a tarefa de hoje?",
]

def send_test_message(message: str):
    """Send a test message to the webhook"""
    payload = {
        "event": "messages.upsert",
        "instance": "Pro Letras",
        "data": {
            "key": {
                "remoteJid": f"{PHONE_NUMBER}@s.whatsapp.net",
                "fromMe": False,
                "id": "test123"
            },
            "message": {
                "conversation": message
            },
            "pushName": "Test User",
            "messageType": "conversation"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/webhook",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Sent: {message}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

if __name__ == "__main__":
    print("🧪 Testing Nino webhook with real message format\n")
    print(f"📱 Phone: {PHONE_NUMBER}\n")
    
    for msg in test_messages:
        send_test_message(msg)
        input("Press Enter to send next message...")
    
    print("✅ All tests complete!")
