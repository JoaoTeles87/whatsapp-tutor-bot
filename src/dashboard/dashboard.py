import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Sabiá - Monitor de Engajamento Escolar",
    page_icon="🦜",
    layout="wide"
)

# Título principal
st.title("🦜 Sabiá - Monitor de Engajamento Escolar (Paraíba)")

# Função para carregar dados
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        with open('alertas.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
        df = pd.DataFrame(dados)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        st.error("Arquivo alertas.json não encontrado!")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carregar dados
df = carregar_dados()

if df.empty:
    st.warning("Nenhum dado disponível para exibir.")
    st.stop()

# Filtro de período
st.sidebar.header("⚙️ Filtros")
periodo = st.sidebar.selectbox(
    "Período",
    ["Últimos 7 dias", "Últimos 30 dias"]
)

# Calcular data de corte (com timezone UTC para compatibilidade)
data_atual = pd.Timestamp.now(tz='UTC')
if periodo == "Últimos 7 dias":
    data_corte = data_atual - pd.Timedelta(days=7)
else:
    data_corte = data_atual - pd.Timedelta(days=30)

# Filtrar dados pelo período  
df_filtrado = df[df['timestamp'] >= data_corte].copy()

# KPIs principais
st.header("📊 Indicadores Principais")
col1, col2, col3 = st.columns(3)

# Total de alertas (score > 0.6)
alertas_criticos = df_filtrado[df_filtrado['score_desmotivacao'] > 0.6]
total_alertas = len(alertas_criticos)

# Média do score
media_score = df_filtrado['score_desmotivacao'].mean() if len(df_filtrado) > 0 else 0

# Total de alunos monitorados
total_alunos = len(df_filtrado)

with col1:
    st.metric(
        label="🚨 Total de Alertas",
        value=total_alertas,
        help="Alunos com score de desmotivação > 0.6"
    )

with col2:
    st.metric(
        label="📈 Média do Score",
        value=f"{media_score:.2f}",
        help="Média do score de desmotivação no período"
    )

with col3:
    st.metric(
        label="👥 Alunos Monitorados",
        value=total_alunos
    )

st.divider()

# Heatmap da Paraíba
st.header("🗺️ Mapa de Atenção por Cidade")

if len(df_filtrado) > 0:
    # Agregar dados por cidade
    df_cidades = df_filtrado.groupby(['cidade', 'lat', 'lon']).agg({
        'score_desmotivacao': ['mean', 'count']
    }).reset_index()
    
    df_cidades.columns = ['cidade', 'lat', 'lon', 'score_medio', 'num_alertas']
    
    # Normalizar o tamanho dos pontos (entre 100 e 500)
    df_cidades['size'] = 100 + (df_cidades['score_medio'] * 400)
    
    # Criar coluna de cor baseada no score
    def get_color(score):
        if score >= 0.7:
            return [255, 0, 0, 160]  # Vermelho
        elif score >= 0.5:
            return [255, 165, 0, 160]  # Laranja
        else:
            return [0, 255, 0, 160]  # Verde
    
    df_cidades['color'] = df_cidades['score_medio'].apply(get_color)
    
    # Exibir informações das cidades
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Mapa centrado na Paraíba
        st.map(
            df_cidades,
            latitude='lat',
            longitude='lon',
            size='size',
            color='color',
            zoom=7
        )
    
    with col2:
        st.subheader("📍 Resumo por Cidade")
        for _, row in df_cidades.sort_values('score_medio', ascending=False).iterrows():
            cor_emoji = "🔴" if row['score_medio'] >= 0.7 else "🟠" if row['score_medio'] >= 0.5 else "🟢"
            st.write(f"{cor_emoji} **{row['cidade']}**")
            st.write(f"   Score médio: {row['score_medio']:.2f}")
            st.write(f"   Alertas: {int(row['num_alertas'])}")
            st.write("")
else:
    st.info("Nenhum dado disponível para o período selecionado.")

st.divider()

# Tabela de alertas prioritários
st.header("⚠️ Alunos Prioritários")

if len(df_filtrado) > 0:
    # Ordenar por score (maior para menor)
    df_prioridade = df_filtrado.sort_values('score_desmotivacao', ascending=False).copy()
    
    # Preparar dados para exibição
    df_exibicao = pd.DataFrame({
        'Aluno (ID Anônimo)': df_prioridade['aluno_id'],
        'Score': df_prioridade['score_desmotivacao'].apply(lambda x: f"{x:.2f}"),
        'Cidade': df_prioridade['cidade'],
        'Observação Chave': df_prioridade['observacoes_chave'].apply(
            lambda x: '; '.join(x) if isinstance(x, list) else str(x)
        ),
        'Data': df_prioridade['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
    })
    
    # Aplicar estilo condicional
    def highlight_score(row):
        score = float(row['Score'])
        if score >= 0.7:
            return ['background-color: #ffcccc'] * len(row)
        elif score >= 0.5:
            return ['background-color: #ffe6cc'] * len(row)
        else:
            return [''] * len(row)
    
    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True
    )
    
    # Estatísticas adicionais
    st.subheader("📊 Distribuição de Risco")
    col1, col2, col3 = st.columns(3)
    
    alto_risco = len(df_filtrado[df_filtrado['score_desmotivacao'] >= 0.7])
    medio_risco = len(df_filtrado[(df_filtrado['score_desmotivacao'] >= 0.5) & 
                                   (df_filtrado['score_desmotivacao'] < 0.7)])
    baixo_risco = len(df_filtrado[df_filtrado['score_desmotivacao'] < 0.5])
    
    with col1:
        st.metric("🔴 Alto Risco", alto_risco, help="Score >= 0.7")
    with col2:
        st.metric("🟠 Médio Risco", medio_risco, help="0.5 <= Score < 0.7")
    with col3:
        st.metric("🟢 Baixo Risco", baixo_risco, help="Score < 0.5")
else:
    st.info("Nenhum aluno para exibir no período selecionado.")

# Rodapé
st.divider()
st.caption("🦜 Sabiá - Sistema de Acompanhamento de Bem-estar e Inteligência Acadêmica | Paraíba 2025")
st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Botão de atualização manual
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()
