"""
Simula conversas completas para gerar dados reais no dashboard
"""
import asyncio
import os
from dotenv import load_dotenv
from src.analytics_agent import AgenteAnalista

load_dotenv()

async def simulate_multiple_conversations():
    """Simula várias conversas com diferentes perfis de alunos"""
    
    analytics = AgenteAnalista(
        api_key=os.getenv("LLM_API_KEY"),
        model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    )
    
    # Conversa 1: Aluno desmotivado (seu número)
    conversa1 = [
        {"role": "assistant", "content": "E aí! 😊 Eu sou o Nino, tô aqui pra te ajudar! Qual é o seu nome?"},
        {"role": "user", "content": "João"},
        {"role": "assistant", "content": "Legal, João! Como posso te ajudar hoje?"},
        {"role": "user", "content": "Tô meio desanimado com a escola, não tá dando certo"},
        {"role": "assistant", "content": "Entendo que você está se sentindo assim. Quer me contar o que está acontecendo?"},
        {"role": "user", "content": "Matemática tá muito difícil, não consigo acompanhar a turma"},
    ]
    
    # Conversa 2: Aluno engajado
    conversa2 = [
        {"role": "assistant", "content": "E aí! 😊 Eu sou o Nino, tô aqui pra te ajudar!"},
        {"role": "user", "content": "Oi Nino! Preciso de ajuda com frações"},
        {"role": "assistant", "content": "Claro! Vamos lá. O que você quer saber sobre frações?"},
        {"role": "user", "content": "Como somar frações com denominadores diferentes?"},
        {"role": "assistant", "content": "Boa pergunta! Primeiro você precisa encontrar o MMC..."},
        {"role": "user", "content": "Ah entendi! Deixa eu tentar fazer um exercício"},
    ]
    
    # Conversa 3: Aluno com risco médio
    conversa3 = [
        {"role": "assistant", "content": "E aí! 😊 Eu sou o Nino!"},
        {"role": "user", "content": "Oi"},
        {"role": "assistant", "content": "Como você está? Posso te ajudar com algo?"},
        {"role": "user", "content": "Tô com dúvida na tarefa de português"},
        {"role": "assistant", "content": "Qual é a dúvida?"},
        {"role": "user", "content": "Não entendi muito bem o que é pra fazer"},
    ]
    
    conversas = [
        ("558132991244", conversa1, "Seu número - Desmotivado"),
        ("5581987654322", conversa2, "Aluno engajado"),
        ("5581923456780", conversa3, "Risco médio"),
    ]
    
    print("🧪 Simulando conversas para gerar dados reais...\n")
    
    for phone, conversa, descricao in conversas:
        print(f"📱 {descricao} ({phone})")
        resultado = await analytics.analisar_conversa(phone, conversa)
        
        print(f"   Score: {resultado.score_desmotivacao:.2f}")
        print(f"   Escola: {resultado.escola}")
        
        if resultado.score_desmotivacao >= 0.7:
            print(f"   Status: 🔴 CRÍTICO")
        elif resultado.score_desmotivacao >= 0.5:
            print(f"   Status: 🟠 MÉDIO")
        else:
            print(f"   Status: 🟢 BAIXO")
        print()
    
    print("✅ Conversas simuladas e dados salvos em alertas.json")
    print("📊 Recarregue o dashboard para ver os novos dados!")

if __name__ == "__main__":
    asyncio.run(simulate_multiple_conversations())
