import streamlit as st
import pandas as pd
import numpy as np
import time

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Injeção Cirúrgica - Monitoramento Preditivo",
    page_icon="💉",
    layout="wide"
)

# ==============================================================================
# BARRA LATERAL: SELEÇÃO E IDENTIFICAÇÃO DA MÁQUINA
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/syringe.png", width=70)
st.sidebar.title("Injeção Cirúrgica LTDA")
st.sidebar.subheader("Painel de Controle de Chão de Fábrica")

# Identificação Dinâmica da Máquina
maquina_selecionada = st.sidebar.selectbox(
    "Selecione a Injetora:",
    ["INJ-01 (KraussMaffei 200T)", "INJ-02 (Romi Prática 130T)", "INJ-03 (Engel e-motion)"]
)

# Dados cadastrais da máquina selecionada
dados_maquinas = {
    "INJ-01 (KraussMaffei 200T)": {
        "tag": "INJ-01",
        "molde": "MOL-SER-05ML (64 Cavidades)",
        "materia_prima": "Polipropileno (PP) Homopolímero Medical Grade",
        "linha": "Linha 01 - Seringas 5ml",
        "clp_ip": "192.168.1.101"
    },
    "INJ-02 (Romi Prática 130T)": {
        "tag": "INJ-02",
        "molde": "MOL-EMB-05ML (32 Cavidades)",
        "materia_prima": "Polietileno (PEAD) - Êmbolo",
        "linha": "Linha 02 - Êmbolos 5ml",
        "clp_ip": "192.168.1.102"
    },
    "INJ-03 (Engel e-motion)": {
        "tag": "INJ-03",
        "molde": "MOL-SER-10ML (48 Cavidades)",
        "materia_prima": "Polipropileno (PP) Transparente",
        "linha": "Linha 01 - Seringas 10ml",
        "clp_ip": "192.168.1.103"
    }
}

info_maq = dados_maquinas[maquina_selecionada]

# Controle de Simulação na Barra Lateral
st.sidebar.markdown("---")
st.sidebar.subheader("Simulador de Leitura do CLP")
temp_canhao = st.sidebar.slider("Temp. Canhão Z1 (°C)", 180.0, 260.0, 220.0)
temp_molde = st.sidebar.slider("Temp. Água do Molde (°C)", 15.0, 70.0, 32.0)
pressao_recalque = st.sidebar.slider("Pressão Injeção (bar)", 50.0, 160.0, 95.0)
ciclos_acumulados = st.sidebar.number_input("Ciclos Acumulados do Molde", value=380000, step=10000)

# ==============================================================================
# CABEÇALHO PRINCIPAL DA PÁGINA (DADOS DA MÁQUINA)
# ==============================================================================
st.title(f"⚙️ Monitoramento em Tempo Real: {info_maq['tag']}")

# Card de Identificação
col_info1, col_info2, col_info3, col_info4 = st.columns(4)
with col_info1:
    st.info(f"**Linha de Produção:**\n{info_maq['linha']}")
with col_info2:
    st.info(f"**Molde Ativo:**\n{info_maq['molde']}")
with col_info3:
    st.info(f"**Polímero:**\n{info_maq['materia_prima']}")
with col_info4:
    st.info(f"**Conexão CLP:**\n{info_maq['clp_ip']} (OPC UA Active)")

st.markdown("---")

# ==============================================================================
# CÁLCULO DE RISCO DE FALHA (MODELO IA)
# ==============================================================================
# Lógica do modelo preditivo
indicador_estresse = (pressao_recalque * temp_molde) / 100
risco_percentual = min(100, max(0, (indicador_estresse / 80) * 100)) if ciclos_acumulados > 300000 else 10.0

# STATUS DA MÁQUINA
col_status, col_alerta = st.columns([1, 2])

with col_status:
    st.subheader("Status Operacional")
    if risco_percentual < 35:
        st.success("🟢 **OPERAÇÃO NORMAL**\nParâmetros térmicos e de pressão estáveis.")
    elif 35 <= risco_percentual < 65:
        st.warning("🟡 **ATENÇÃO REQUERIDA**\nElevação de estresse térmico/mecânico no molde.")
    else:
        st.error("🔴 **ALERTA CRÍTICO DE PARADA**\nElevado risco de refugo ou empenamento das gavetas.")

with col_alerta:
    st.subheader("Índice Preditivo de Refugo/Falha")
    st.progress(int(risco_percentual))
    st.write(f"**Probabilidade de Defeito na Seringa:** `{risco_percentual:.1f}%`")

# ==============================================================================
# CARTOES DE METRICAS SENSORIAIS (SENSORES DO CLP)
# ==============================================================================
st.subheader("📊 Telemetria do CLP em Tempo Real")

m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Temp. Canhão (Z1)", value=f"{temp_canhao:.1f} °C", delta=f"{temp_canhao - 210.0:.1f} °C vs Setpoint")
m2.metric(label="ΔT Refrigeração Molde", value=f"{temp_molde:.1f} °C", delta="Abaixo do Crítico" if temp_molde < 45 else "Superaquecendo", delta_color="inverse")
m3.metric(label="Pressão de Recalque", value=f"{pressao_recalque:.0f} bar", delta=f"{pressao_recalque - 90:.0f} bar")
m4.metric(label="Ciclos Totais Molde", value=f"{ciclos_acumulados:,}", delta="Manutenção Recomendada" if ciclos_acumulados > 350000 else "Ok", delta_color="inverse")

# ==============================================================================
# GRÁFICO HISTÓRICO SIMULADO
# ==============================================================================
st.subheader("📈 Histórico Recente de Parâmetros da Injetora")

# Criando dados para o gráfico de tendência
chart_data = pd.DataFrame({
    "Temp Canhão (°C)": np.random.normal(temp_canhao, 1.5, 20),
    "Temp Molde (°C)": np.random.normal(temp_molde, 0.8, 20),
    "Pressão (bar)": np.random.normal(pressao_recalque, 2.0, 20)
})

st.line_chart(chart_data)
