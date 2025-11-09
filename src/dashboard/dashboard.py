import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Farol - Monitor de Engajamento Escolar",
    page_icon="🔦",
    layout="wide"
)

# Título principal
st.title("🔦 Farol - Monitor de Engajamento Escolar (Paraíba)")

# Função para carregar dados
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        # Read from root directory (two levels up from src/dashboard/)
        import os
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        alertas_path = os.path.join(root_dir, 'alertas.json')
        
        with open(alertas_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        df = pd.DataFrame(dados)
        # Parse timestamp with ISO8601 format to handle microseconds
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
        
        # Remover timezone do timestamp se existir para comparação
        if df['timestamp'].dt.tz is not None:
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
        
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
    ["Últimos 7 dias", "Últimos 30 dias", "Todos"]
)

# Calcular data de corte
if periodo != "Todos":
    data_atual = pd.Timestamp.now()
    if periodo == "Últimos 7 dias":
        data_corte = data_atual - pd.Timedelta(days=7)
    else:
        data_corte = data_atual - pd.Timedelta(days=30)
    
    # Filtrar dados pelo período  
    df_filtrado = df[df['timestamp'] >= data_corte].copy()
else:
    df_filtrado = df.copy()

# Filtro por nível de risco
nivel_risco = st.sidebar.multiselect(
    "Nível de Risco",
    ["🔴 Alto (≥0.7)", "🟠 Médio (0.5-0.7)", "🟢 Baixo (<0.5)"],
    default=["🔴 Alto (≥0.7)", "🟠 Médio (0.5-0.7)", "🟢 Baixo (<0.5)"]
)

# Aplicar filtro de risco
if nivel_risco:
    mask = pd.Series([False] * len(df_filtrado))
    if "🔴 Alto (≥0.7)" in nivel_risco:
        mask |= df_filtrado['score_desmotivacao'] >= 0.7
    if "🟠 Médio (0.5-0.7)" in nivel_risco:
        mask |= (df_filtrado['score_desmotivacao'] >= 0.5) & (df_filtrado['score_desmotivacao'] < 0.7)
    if "🟢 Baixo (<0.5)" in nivel_risco:
        mask |= df_filtrado['score_desmotivacao'] < 0.5
    df_filtrado = df_filtrado[mask]

# KPIs principais em cards
st.header("📊 Visão Geral")

col1, col2, col3, col4 = st.columns(4)

# Total de alertas críticos
alertas_criticos = len(df_filtrado[df_filtrado['score_desmotivacao'] >= 0.7])
alertas_medios = len(df_filtrado[(df_filtrado['score_desmotivacao'] >= 0.5) & (df_filtrado['score_desmotivacao'] < 0.7)])
alertas_baixos = len(df_filtrado[df_filtrado['score_desmotivacao'] < 0.5])

with col1:
    st.metric(
        label="🔴 Alertas Críticos",
        value=alertas_criticos,
        delta=f"{(alertas_criticos/len(df_filtrado)*100):.0f}%" if len(df_filtrado) > 0 else "0%",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="🟠 Alertas Médios",
        value=alertas_medios,
        delta=f"{(alertas_medios/len(df_filtrado)*100):.0f}%" if len(df_filtrado) > 0 else "0%",
        delta_color="off"
    )

with col3:
    st.metric(
        label="🟢 Alunos Engajados",
        value=alertas_baixos,
        delta=f"{(alertas_baixos/len(df_filtrado)*100):.0f}%" if len(df_filtrado) > 0 else "0%",
        delta_color="normal"
    )

with col4:
    media_score = df_filtrado['score_desmotivacao'].mean() if len(df_filtrado) > 0 else 0
    st.metric(
        label="📈 Score Médio",
        value=f"{media_score:.2f}",
        delta="Risco Geral",
        delta_color="off"
    )

st.divider()

# Gráficos de análise
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribuição de Risco")
    
    # Gráfico de pizza
    risk_data = pd.DataFrame({
        'Nível': ['🔴 Alto', '🟠 Médio', '🟢 Baixo'],
        'Quantidade': [alertas_criticos, alertas_medios, alertas_baixos],
        'Cor': ['#ff4444', '#ff9944', '#44ff44']
    })
    
    fig_pie = px.pie(
        risk_data, 
        values='Quantidade', 
        names='Nível',
        color='Nível',
        color_discrete_map={'🔴 Alto': '#ff4444', '🟠 Médio': '#ff9944', '🟢 Baixo': '#44ff44'},
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🏫 Top 5 Escolas com Maior Risco")
    
    if 'escola' in df_filtrado.columns:
        escola_risk = df_filtrado.groupby('escola').agg({
            'score_desmotivacao': 'mean',
            'aluno_id': 'count'
        }).reset_index()
        escola_risk.columns = ['Escola', 'Score Médio', 'Alunos']
        escola_risk = escola_risk.sort_values('Score Médio', ascending=False).head(5)
        
        fig_bar = px.bar(
            escola_risk,
            x='Score Médio',
            y='Escola',
            orientation='h',
            text='Alunos',
            color='Score Médio',
            color_continuous_scale=['green', 'yellow', 'red'],
            range_color=[0, 1]
        )
        fig_bar.update_traces(texttemplate='%{text} alunos', textposition='outside')
        fig_bar.update_layout(showlegend=False, height=300, xaxis_range=[0, 1])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Campo 'escola' não disponível nos dados")

st.divider()

# Mapa e insights lado a lado
st.header("🗺️ Mapa de Calor - Paraíba")

col1, col2 = st.columns([3, 2])

with col1:
    if len(df_filtrado) > 0:
        # Preparar dados para o mapa
        df_map = df_filtrado.copy()
        df_map['size'] = 100 + (df_map['score_desmotivacao'] * 400)
        
        # Criar mapa com plotly para melhor visualização
        fig_map = px.scatter_mapbox(
            df_map,
            lat='lat',
            lon='lon',
            size='size',
            color='score_desmotivacao',
            hover_name='escola' if 'escola' in df_map.columns else 'cidade',
            hover_data={
                'score_desmotivacao': ':.2f',
                'cidade': True,
                'lat': False,
                'lon': False,
                'size': False
            },
            color_continuous_scale=['green', 'yellow', 'red'],
            range_color=[0, 1],
            zoom=8,  # Zoom focado em João Pessoa e Campina Grande
            height=500
        )
        
        fig_map.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": -7.17, "lon": -35.4},  # Entre João Pessoa e Campina Grande
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para o mapa")

with col2:
    st.subheader("💡 Insights para Gestão")
    
    if len(df_filtrado) > 0:
        # Insight 1: Escola com maior risco
        if 'escola' in df_filtrado.columns:
            escola_maior_risco = df_filtrado.groupby('escola')['score_desmotivacao'].mean().idxmax()
            score_maior_risco = df_filtrado.groupby('escola')['score_desmotivacao'].mean().max()
            
            st.markdown(f"""
            **🎯 Prioridade Máxima:**
            - **{escola_maior_risco}**
            - Score médio: {score_maior_risco:.2f}
            - Requer intervenção imediata
            """)
            
            st.divider()
        
        # Insight 2: Tendência de engajamento
        if 'engajamento_emocional' in df_filtrado.columns:
            eng_emocional_medio = df_filtrado['engajamento_emocional'].mean()
            eng_comportamental_medio = df_filtrado['engajamento_comportamental'].mean()
            eng_cognitivo_medio = df_filtrado['engajamento_cognitivo'].mean()
            
            st.markdown("**📈 Engajamento Médio:**")
            st.progress(eng_emocional_medio, text=f"Emocional: {eng_emocional_medio:.0%}")
            st.progress(eng_comportamental_medio, text=f"Comportamental: {eng_comportamental_medio:.0%}")
            st.progress(eng_cognitivo_medio, text=f"Cognitivo: {eng_cognitivo_medio:.0%}")
            
            st.divider()
        
        # Insight 3: Alunos que precisam de atenção
        alunos_criticos = df_filtrado[df_filtrado['score_desmotivacao'] >= 0.7]
        if len(alunos_criticos) > 0:
            st.markdown(f"""
            **⚠️ Ação Necessária:**
            - {len(alunos_criticos)} alunos em risco crítico
            - Contato com famílias recomendado
            - Acompanhamento psicopedagógico
            """)
        else:
            st.success("✅ Nenhum aluno em risco crítico no momento!")

st.divider()

# Tabela de alunos prioritários - mais compacta e informativa
st.header("⚠️ Alunos Prioritários - Ação Requerida")

if len(df_filtrado) > 0:
    # Filtrar apenas alunos com risco médio ou alto
    df_prioridade = df_filtrado[df_filtrado['score_desmotivacao'] >= 0.5].sort_values('score_desmotivacao', ascending=False).copy()
    
    if len(df_prioridade) > 0:
        # Preparar dados para exibição
        colunas = {
            'ID': df_prioridade['aluno_id'].apply(lambda x: f"***{str(x)[-4:]}"),  # Últimos 4 dígitos
            'Score': df_prioridade['score_desmotivacao'].apply(lambda x: f"{x:.2f}"),
            'Risco': df_prioridade['score_desmotivacao'].apply(
                lambda x: "🔴 Crítico" if x >= 0.7 else "🟠 Médio"
            ),
            'Principal Observação': df_prioridade['observacoes_chave'].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else str(x)
            ),
            'Data': df_prioridade['timestamp'].dt.strftime('%d/%m %H:%M')
        }
        
        # Adicionar escola se disponível
        if 'escola' in df_prioridade.columns:
            colunas['Escola'] = df_prioridade['escola']
        
        df_exibicao = pd.DataFrame(colunas)
        
        # Exibir tabela com estilo
        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Estatísticas de ação
        criticos_count = len(df_prioridade[df_prioridade['score_desmotivacao'] >= 0.7])
        st.info(f"💼 **Recomendação**: Priorizar contato com os {criticos_count} alunos em risco crítico nas próximas 24-48h")
    else:
        st.success("✅ Nenhum aluno requer atenção prioritária no momento!")
else:
    st.info("Nenhum aluno para exibir no período selecionado.")

# Rodapé com informações
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🔦 **Farol** - Sistema de Monitoramento e Apoio ao Engajamento Escolar")

with col2:
    st.caption(f"📅 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

with col3:
    st.caption(f"📊 Total de registros: {len(df_filtrado)}")

# Botão de atualização manual
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()
