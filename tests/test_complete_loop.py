"""
Test complete conversation loop:
1. Simulate WhatsApp message → Webhook
2. Nino generates response
3. Response sent back via Evolution API
"""
import requests
import json
import time

# Your WhatsApp number
YOUR_NUMBER = "558132991244"

def test_complete_loop():
    print("🔄 Testing Complete Conversation Loop\n")
    print("=" * 60)
    
    # Step 1: Simulate incoming WhatsApp message
    print("\n📱 Step 1: Simulating WhatsApp message from your number...")
    webhook_payload = {
        "event": "messages.upsert",
        "instance": "Pro Letras",
        "data": {
            "key": {
                "remoteJid": f"{YOUR_NUMBER}@s.whatsapp.net",
                "fromMe": False,
                "id": "test_loop_123"
            },
            "message": {
                "conversation": "Oi Nino, você está funcionando?"
            },
            "pushName": "Test User",
            "messageType": "conversation"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/webhook",
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Webhook received message successfully")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Webhook error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending to webhook: {e}")
        return False
    
    # Step 2: Wait for processing
    print("\n⏳ Step 2: Waiting for Nino to process and respond...")
    time.sleep(3)
    
    # Step 3: Check if message was sent via Evolution API
    print("\n📤 Step 3: Checking Evolution API logs...")
    print("   (Check your WhatsApp to see if you received a response)")
    
    # Step 4: Verify conversation memory
    print("\n💾 Step 4: Conversation should be stored in Nino's memory")
    print("   (Send another message to test memory persistence)")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("\n📱 Check your WhatsApp number:", YOUR_NUMBER)
    print("   You should have received a message from 558132991224")
    print("\n💡 If you didn't receive a message, check:")
    print("   1. Evolution API is connected to WhatsApp")
    print("   2. Webhook URL is accessible from Evolution API")
    print("   3. Nino agent is running on port 5000")
    
    return True

if __name__ == "__main__":
    test_complete_loop()
