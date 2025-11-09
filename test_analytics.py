"""
Teste do sistema de analytics - Simula conversa com desmotivação
"""
import asyncio
import os
from dotenv import load_dotenv
from src.analytics_agent import AgenteAnalista

load_dotenv()

async def test_analytics():
    """Testa análise de engajamento com conversa desmotivada"""
    
    # Inicializar agente
    analytics = AgenteAnalista(
        api_key=os.getenv("LLM_API_KEY"),
        model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    )
    
    # Simular conversa com sinais de desmotivação
    conversa_desmotivada = [
        {"role": "assistant", "content": "E aí! 😊 Eu sou o Nino, tô aqui pra te ajudar! Qual é o seu nome?"},
        {"role": "user", "content": "João"},
        {"role": "assistant", "content": "Legal, João! Como posso te ajudar hoje?"},
        {"role": "user", "content": "Não sei... tô meio desanimado com a escola"},
        {"role": "assistant", "content": "Entendo que você está se sentindo assim. Quer me contar o que está acontecendo?"},
        {"role": "user", "content": "Acho que não tô entendendo nada de matemática, tá muito difícil"},
        {"role": "assistant", "content": "Matemática pode ser desafiadora mesmo. Qual parte está mais difícil pra você?"},
        {"role": "user", "content": "Tudo... não consigo fazer nada direito. Acho que vou desistir"},
    ]
    
    print("🧪 Testando análise de engajamento...")
    print("📝 Conversa simulada com sinais de desmotivação\n")
    
    # Analisar conversa
    resultado = await analytics.analisar_conversa("558132991244", conversa_desmotivada)
    
    print("📊 RESULTADO DA ANÁLISE:")
    print(f"   Engajamento Comportamental: {resultado.engajamento_comportamental:.2f}")
    print(f"   Engajamento Emocional: {resultado.engajamento_emocional:.2f}")
    print(f"   Engajamento Cognitivo: {resultado.engajamento_cognitivo:.2f}")
    print(f"   🚨 Score de Desmotivação: {resultado.score_desmotivacao:.2f}")
    print(f"   📍 Cidade: {resultado.cidade}")
    print(f"   💬 Observações: {resultado.observacoes_chave}")
    print()
    
    if resultado.score_desmotivacao >= 0.7:
        print("🔴 ALERTA ALTO: Aluno em risco de evasão!")
    elif resultado.score_desmotivacao >= 0.5:
        print("🟠 ALERTA MÉDIO: Aluno precisa de atenção")
    else:
        print("🟢 OK: Aluno engajado")
    
    print("\n✅ Dados salvos em alertas.json")
    print("📊 Verifique o dashboard em: src/dashboard/dashboard.py")

if __name__ == "__main__":
    asyncio.run(test_analytics())
