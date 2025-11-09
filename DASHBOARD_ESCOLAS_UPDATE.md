# 📊 Dashboard - Atualização com Nomes de Escolas

## ✅ Mudanças Implementadas

### 1. Campo "Escola" Adicionado ao Sistema

**Modelo de Dados Atualizado:**
```python
class AnaliseEngajamento:
    escola: str  # NOVO: Nome da instituição
    cidade: str
    lat: float
    lon: float
```

### 2. Escola Padrão Configurada

**Para novos alertas do agente:**
- Escola: `"Vista Alegre Park, Haras e Hípica"`
- Cidade: `"João Pessoa"`
- Coordenadas: lat=-7.1195, lon=-34.845

### 3. Dados Mockados Atualizados

**Exemplos no alertas.json:**

1. **Escola Municipal Santos Dumont** (João Pessoa)
   - Score: 0.3 (🟢 Baixo risco)
   - Aluno engajado

2. **Colégio Estadual Padre Roma** (Campina Grande)
   - Score: 0.7 (🔴 Alto risco)
   - Aluno com frustração

3. **Vista Alegre Park, Haras e Hípica** (João Pessoa)
   - Score: 0.47 (🟢 Baixo risco)
   - Aluno participativo

### 4. Dashboard Atualizado

**Seção "Resumo por Localização":**

Antes:
```
🔴 João Pessoa
   Score médio: 0.65
   Alertas: 5
```

Agora:
```
🔴 Vista Alegre Park, Haras e Hípica
   📍 João Pessoa
   Score médio: 0.65
   Alertas: 3

🟠 Escola Municipal Santos Dumont
   📍 João Pessoa
   Score médio: 0.55
   Alertas: 2
```

**Tabela de Alunos Prioritários:**

Nova coluna "Escola" adicionada:
```
| Aluno ID | Score | Escola | Cidade | Observação | Data |
```

### 5. Compatibilidade com Dados Antigos

O dashboard detecta automaticamente se o campo "escola" existe:
- ✅ **Com campo escola**: Mostra nome da escola + cidade
- ✅ **Sem campo escola**: Mostra apenas cidade (fallback)

## 🎯 Como Funciona

### Fluxo Automático

1. **Aluno conversa com Nino** via WhatsApp
2. **Após 2+ trocas de mensagens** → Analytics analisa
3. **Dados salvos** incluem:
   - Scores de engajamento
   - Score de desmotivação
   - **Nome da escola** ← NOVO
   - Cidade e coordenadas
4. **Dashboard atualiza** a cada 5 segundos
5. **Visualização** mostra escola + cidade

### Configuração de Escolas

Para adicionar mais escolas, edite `src/analytics_agent.py`:

```python
# Linha ~115
if "escola" not in analise_dict:
    analise_dict["escola"] = "Vista Alegre Park, Haras e Hípica"
```

Ou crie um mapeamento por região/telefone:

```python
ESCOLAS_POR_REGIAO = {
    "joao_pessoa": "Vista Alegre Park, Haras e Hípica",
    "campina_grande": "Colégio Estadual Padre Roma",
    # ...
}
```

## 📱 Testando

### 1. Ver Dashboard
```bash
venv\Scripts\activate
streamlit run src/dashboard/dashboard.py
```

### 2. Simular Conversa com Desmotivação
```bash
venv\Scripts\activate
python test_analytics.py
```

### 3. Enviar Mensagem Real
Envie pelo WhatsApp para o número conectado ao "Pro Letras"

## 📊 Visualização no Dashboard

### Mapa
- Pontos coloridos por score (vermelho/laranja/verde)
- Tamanho proporcional ao risco
- Agrupado por coordenadas (cidade)

### Lista Lateral
- **Nome da Escola** em destaque
- Cidade abaixo
- Score médio
- Número de alertas

### Tabela de Alunos
- Coluna "Escola" mostra instituição
- Coluna "Cidade" mostra localização
- Ordenado por score (maior risco primeiro)

## 🎨 Exemplo Visual

```
📍 Resumo por Localização

🔴 Vista Alegre Park, Haras e Hípica
   📍 João Pessoa
   Score médio: 0.80
   Alertas: 2

🟠 Colégio Estadual Padre Roma
   📍 Campina Grande
   Score médio: 0.70
   Alertas: 1

🟢 Escola Municipal Santos Dumont
   📍 João Pessoa
   Score médio: 0.30
   Alertas: 1
```

## ✅ Checklist de Implementação

- ✅ Campo "escola" adicionado ao modelo `AnaliseEngajamento`
- ✅ Escola padrão configurada: "Vista Alegre Park, Haras e Hípica"
- ✅ Função `_save_alert` atualizada para salvar escola
- ✅ Dados mockados atualizados com nomes de escolas
- ✅ Dashboard atualizado para mostrar escolas
- ✅ Compatibilidade com dados antigos mantida
- ✅ Testes realizados e funcionando

## 🚀 Próximos Passos (Opcional)

1. **Mapeamento Automático**: Detectar escola pelo número do aluno
2. **Múltiplas Escolas**: Suporte para várias instituições
3. **Filtro por Escola**: Adicionar filtro no dashboard
4. **Relatórios por Escola**: Gerar relatórios individuais

---

**Status**: ✅ Implementado e Testado
**Data**: 2025-11-09
**Versão**: 1.1.0
