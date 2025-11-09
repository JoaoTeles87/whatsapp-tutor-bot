"""
Test Groq API connectivity and functionality
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

def test_groq_api():
    """Test if Groq API is working"""
    
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    
    print("🔍 Testing Groq API Connection...")
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"Model: {model}")
    print()
    
    try:
        # Initialize Groq client
        llm = ChatGroq(
            model=model,
            temperature=0.7,
            max_tokens=100,
            groq_api_key=api_key
        )
        
        print("✅ Groq client initialized")
        print()
        
        # Test simple message
        print("📤 Sending test message...")
        messages = [HumanMessage(content="Say 'Hello, I am working!' in Portuguese")]
        
        response = llm.invoke(messages)
        
        print("✅ Response received!")
        print(f"📥 Response: {response.content}")
        print()
        
        # Test with Nino's personality
        print("📤 Testing Nino's personality...")
        messages = [HumanMessage(content="Oi! Eu sou o Nino. Me apresente como um colega de classe do 6º ano.")]
        
        response = llm.invoke(messages)
        
        print("✅ Response received!")
        print(f"📥 Response: {response.content}")
        print()
        
        print("🎉 Groq API is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Possible issues:")
        print("1. API key is invalid or expired")
        print("2. Groq service is down")
        print("3. Rate limit exceeded")
        print("4. Network connectivity issue")
        return False

if __name__ == "__main__":
    test_groq_api()
