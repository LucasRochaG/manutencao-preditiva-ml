import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Injex Cirúrgica - Gestão Preditiva Fabril",
    page_icon="💉",
    layout="wide"
)

# Estilo CSS Personalizado
st.markdown("""
<style>
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 8px; }
    .os-card { background-color: #2b1d1d; border: 1px solid #ff4b4b; padding: 15px; border-radius: 8px; }
    .preventiva-card { background-color: #1e293b; border-left: 4px solid #3b82f6; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL: NAVEGAÇÃO, PREVENTIVA E ABERTURA DE OS
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/syringe.png", width=70)
st.sidebar.title("Injex Cirúrgica LTDA")
st.sidebar.caption("PCM & Inteligência Preditiva")

# 1. Seleção de Setor e Máquina
setor_selecionado = st.sidebar.selectbox(
    "🏢 Selecione o Setor Fabril:",
    ["1. Injeção Plástica", "2. Montagem Automática", "3. Embalagem & Blister"]
)

if setor_selecionado == "1. Injeção Plástica":
    maquinas = ["INJ-01 (KraussMaffei 200T)", "INJ-02 (Romi Prática 130T)"]
elif setor_selecionado == "2. Montagem Automática":
    maquinas = ["MONT-01 (Linha Alta Velocidade)", "MONT-02 (Montadora Êmbolo/Corpo)"]
else:
    maquinas = ["EMB-01 (Termoformadora Blister)", "EMB-02 (Seladora & Encartonadora)"]

maquina_selecionada = st.sidebar.selectbox("⚙️ Selecione a Máquina:", maquinas)

st.sidebar.markdown("---")

# ==============================================================================
# SEÇÃO 1: PAINEL DE PREVENTIVA (SIDEBAR)
# ==============================================================================
st.sidebar.subheader("🛠️ Plano de Preventiva")

# Banco de dados de peças e tempos por máquina
dados_preventiva = {
    "INJ-01 (KraussMaffei 200T)": {
        "pecas": ["Anel de Bloqueio (Válvula)", "Jogo de Buchas Extratoras", "Reparo do Cilindro Hidráulico"],
        "tempo": "2h 30min"
    },
    "INJ-02 (Romi Prática 130T)": {
        "pecas": ["Resistência Cerâmica Z1/Z2", "Filtro do Sistema de Refrigeração", "Gaxetas da Unidade Injetora"],
        "tempo": "1h 45min"
    },
    "MONT-01 (Linha Alta Velocidade)": {
        "pecas": ["Vectores Pneumáticos Festo", "Garras de Pegada do Êmbolo", "Sensor Óptico de Presença"],
        "tempo": "1h 15min"
    },
    "MONT-02 (Montadora Êmbolo/Corpo)": {
        "pecas": ["Atuador Rotativo Servo", "Ventosas de Vácuo Silicone", "Guias Lineares"],
        "tempo": "2h 00min"
    },
    "EMB-01 (Termoformadora Blister)": {
        "pecas": ["Matriz de Selagem Térmica", "Borracha de Silicone Hálux", "Faca de Corte Transversal"],
        "tempo": "3h 00min"
    },
    "EMB-02 (Seladora & Encartonadora)": {
        "pecas": ["Correia Dentada de Tração", "Cartucho Aquecedor 500W", "Filtro de Vácuo"],
        "tempo": "1h 30min"
    }
}

info_prev = dados_preventiva[maquina_selecionada]

st.sidebar.markdown(f"""
<div class="preventiva-card">
    <b>Equipamento:</b> {maquina_selecionada.split(' ')[0]}<br>
    <b>Peças Cadastradas:</b>
    <ul>
        {''.join([f'<li>{peca}</li>' for peca in info_prev['pecas']])}
    </ul>
    <b>Tempo Estimado Parada:</b> ⏱️ {info_prev['tempo']}
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# ==============================================================================
# SEÇÃO 2: ABERTURA DE OS SIMPLIFICADA (SIDEBAR)
# ==============================================================================
st.sidebar.subheader("📝 Abertura Rápida de OS")

with st.sidebar.form(key="form_os_simplificada"):
    os_setor = st.selectbox("Setor:", ["Injeção Plástica", "Montagem Automática", "Embalagem & Blister"])
    os_maquina = st.text_input("Máquina:", value=maquina_selecionada.split(' ')[0])
    os_defeito = st.text_area("Descrição do Defeito:", placeholder="Ex: Ruído na plastificação ou vazamento de água...")
    os_prioridade = st.select_slider("Prioridade:", options=["Baixa", "Média", "Alta", "Crítica"])
    
    submit_os = st.form_submit_button("🚀 Abrir Ordem de Serviço")

if submit_os:
    if os_defeito.strip() != "":
        st.sidebar.success(f"✅ OS para {os_maquina} criada com sucesso!")
        # Salva o alerta na sessão para exibir no painel principal
        st.session_state['ultima_os'] = {
            "id": f"OS-{datetime.now().strftime('%d%H%M')}",
            "setor": os_setor,
            "maquina": os_maquina,
            "defeito": os_defeito,
            "prioridade": os_prioridade,
            "hora": datetime.now().strftime('%H:%M:%S')
        }
    else:
        st.sidebar.error("Descreva o defeito antes de enviar.")

# ==============================================================================
# CORPO PRINCIPAL - TELEMETRIA E PAINEL
# ==============================================================================
st.title(f"🏭 Injex Cirúrgica | {maquina_selecionada}")

# Exibe OS aberta recentemente via Sidebar
if 'ultima_os' in st.session_state:
    os_info = st.session_state['ultima_os']
    st.info(f"📌 **ÚLTIMA OS REGISTRADA PELO OPERADOR [{os_info['id']}]** as {os_info['hora']} | **Setor:** {os_info['setor']} | **Máquina:** {os_info['maquina']} | **Prioridade:** {os_info['prioridade']} | **Defeito:** {os_info['defeito']}")

# CONTROLES E SIMULAÇÃO CLP
st.subheader("🎛️ Painel de Telemetria CLP")
if setor_selecionado == "1. Injeção Plástica":
    col_c1, col_c2, col_c3 = st.columns(3)
    temp_canhao = col_c1.slider("Temp. Canhão (°C)", 180.0, 260.0, 220.0)
    temp_molde = col_c2.slider("Temp. Água Molde (°C)", 15.0, 70.0, 32.0)
    pressao_recalque = col_c3.slider("Pressão Injeção (bar)", 50.0, 160.0, 95.0)
    risco = min(100.0, (pressao_recalque * temp_molde) / 80)
else:
    col_c1, col_c2 = st.columns(2)
    param1 = col_c1.slider("Pressão de Linha (bar)", 4.0, 10.0, 6.5)
    param2 = col_c2.slider("Velocidade Ciclo (pçs/min)", 100, 300, 240)
    risco = 15.0 if param1 >= 5.5 else 75.0

# METRICAS DE OEE
st.markdown("---")
st.subheader("📊 Indicadores Industriais (OEE)")
disp = max(60, int(98 - (risco * 0.3)))
perf = max(70, int(95 - (risco * 0.2)))
qual = max(80, int(99 - (risco * 0.4)))
oee = int((disp/100) * (perf/100) * (qual/100) * 100)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Disponibilidade", f"{disp} %")
m2.metric("Performance", f"{perf} %")
m3.metric("Qualidade", f"{qual} %")
m4.metric("OEE GLOBAL", f"{oee} %", delta=f"{oee - 85}% Meta")

# DIAGNÓSTICO PREDITIVO
st.markdown("---")
col_p1, col_p2 = st.columns([1, 1])

with col_p1:
    st.subheader("🤖 Diagnóstico da Inteligência Artificial")
    st.progress(int(risco))
    st.write(f"**Probabilidade de Defeito na Seringa:** `{risco:.1f}%`")
    if risco < 35:
        st.success("🟢 **OPERAÇÃO DENTRO DOS PARÂMETROS**")
    elif 35 <= risco < 65:
        st.warning("🟡 **ACOMPANHAMENTO RECOMENDADO**")
    else:
        st.error("🔴 **ALERTA DE SEGURANÇA E REFUGO**")

with col_p2:
    st.subheader("🔧 Ação de Manutenção Preditiva")
    st.write(f"**Tempo Estimado para Manutenção:** `{info_prev['tempo']}`")
    st.write("**Peças para Substituição Planejada:**")
    for p in info_prev['pecas']:
        st.write(f"• {p}")

# HISTÓRICO
st.markdown("---")
st.subheader("📈 Estabilidade Operacional")
chart_data = pd.DataFrame(
    np.random.normal(loc=100, scale=3, size=(20, 2)),
    columns=["Pressão Sistema", "Temperatura Zona Crítica"]
)
st.line_chart(chart_data)
