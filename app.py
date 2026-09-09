import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Injeção Cirúrgica - Gestão Preditiva Fabril",
    page_icon="💉",
    layout="wide"
)

# ==============================================================================
# BARRA LATERAL: SELEÇÃO DE SETOR E MÁQUINA
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/syringe.png", width=70)
st.sidebar.title("Injeção Cirúrgica LTDA")
st.sidebar.subheader("Nível Fabril - Indústria 4.0")

# 1. Seleção do Setor
setor_selecionado = st.sidebar.selectbox(
    "🏢 Selecione o Setor Fabril:",
    ["1. Injeção Plástica", "2. Montagem Automática", "3. Embalagem & Blister"]
)

# 2. Mapeamento de Máquinas por Setor
if setor_selecionado == "1. Injeção Plástica":
    maquinas = ["INJ-01 (KraussMaffei 200T)", "INJ-02 (Romi Prática 130T)"]
elif setor_selecionado == "2. Montagem Automática":
    maquinas = ["MONT-01 (Linha Alta Velocidade - 5ml)", "MONT-02 (Montadora Êmbolo/Corpo 10ml)"]
else:
    maquinas = ["EMB-01 (Termoformadora Blister 01)", "EMB-02 (Seladora & Encartonadora 02)"]

maquina_selecionada = st.sidebar.selectbox("⚙️ Selecione a Máquina:", maquinas)

st.sidebar.markdown("---")
st.sidebar.caption("Status Conexão: 🟢 OPC UA Server Active")

# ==============================================================================
# DADOS DE TELEMETRIA POR SETOR (LÓGICA DOS SENSORES)
# ==============================================================================

if setor_selecionado == "1. Injeção Plástica":
    st.title(f"🏭 Setor: Injeção Plástica | {maquina_selecionada}")
    
    # Contexto Operacional
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    col_i1.info("**Produto:** Corpo Seringa 5ml")
    col_i2.info("**Molde:** 64 Cavidades (PP Medical)")
    col_i3.info("**OPC UA IP:** 192.168.1.101")
    col_i4.info("**Meta Hora:** 12.000 pçs/h")
    
    # Simulação de Sensores
    st.sidebar.subheader("Simulação CLP - Injeção")
    temp_canhao = st.sidebar.slider("Temp. Canhão Z1 (°C)", 180.0, 260.0, 220.0)
    temp_molde = st.sidebar.slider("Temp. Água Molde (°C)", 15.0, 70.0, 32.0)
    pressao_recalque = st.sidebar.slider("Pressão Injeção (bar)", 50.0, 160.0, 95.0)
    ciclos = st.sidebar.number_input("Ciclos Acumulados Molde", value=380000)
    
    # Cálculo de Risco
    risco = min(100.0, (pressao_recalque * temp_molde) / 80) if ciclos > 300000 else 12.0
    
    # Métricas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temp. Canhão", f"{temp_canhao:.1f} °C", f"{temp_canhao-210:.1f} °C")
    m2.metric("Temp. Molde", f"{temp_molde:.1f} °C", "Abaixo do Limite" if temp_molde < 45 else "Crítico")
    m3.metric("Pressão Recalque", f"{pressao_recalque:.0f} bar")
    m4.metric("Ciclos do Molde", f"{ciclos:,}")

elif setor_selecionado == "2. Montagem Automática":
    st.title(f"⚙️ Setor: Montagem Automática | {maquina_selecionada}")
    
    # Contexto Operacional
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.info("**Processo:** Acoplamento Corpo + Êmbolo + Agulha")
    col_m2.info("**Atuadores:** Pneumáticos / Servo-motores")
    col_m3.info("**OPC UA IP:** 192.168.1.110")
    col_m4.info("**Meta Hora:** 15.000 pçs/h")
    
    # Simulação de Sensores de Montagem
    st.sidebar.subheader("Simulação CLP - Montagem")
    pressao_ar = st.sidebar.slider("Pressão Ar Comprimido (bar)", 4.0, 8.0, 6.2)
    vel_ciclo = st.sidebar.slider("Velocidade (Peças/Min)", 100, 300, 250)
    rejeição_visao = st.sidebar.slider("Taxa Rejeição Câmeras (%)", 0.0, 10.0, 0.8)
    vibracao_garra = st.sidebar.slider("Vibração Atuador (mm/s)", 0.5, 8.0, 1.8)
    
    # Cálculo de Risco da Montadora
    risco = min(100.0, (vibracao_garra * 12) + (rejeição_visao * 8))
    
    # Métricas da Montagem
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pressão Linha Ar", f"{pressao_ar:.1f} bar", "Normal" if pressao_ar >= 5.5 else "Baixa Pressão")
    m2.metric("Cadência Montagem", f"{vel_ciclo} pçs/min")
    m3.metric("Rejeição Visão Comp.", f"{rejeição_visao:.2f} %", "OK" if rejeição_visao < 2.0 else "Alta Rejeição")
    m4.metric("Vibração Atuadores", f"{vibracao_garra:.1f} mm/s", "Alinhado" if vibracao_garra < 4.0 else "Desalinhamento")

else:  # Embalagem & Blister
    st.title(f"📦 Setor: Embalagem & Blister | {maquina_selecionada}")
    
    # Contexto Operacional
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    col_e1.info("**Embalagem:** Papel Grau Cirúrgico / Filme LAMINADO")
    col_e2.info("**Norma:** Esterilidade ANVISA (ISO 11607)")
    col_e3.info("**OPC UA IP:** 192.168.1.120")
    col_e4.info("**Meta Hora:** 10.000 caixas/h")
    
    # Simulação de Sensores da Embaladora
    st.sidebar.subheader("Simulação CLP - Embalagem")
    temp_selagem = st.sidebar.slider("Temp. Matriz Selagem (°C)", 110.0, 180.0, 145.0)
    pressao_selagem = st.sidebar.slider("Pressão de Selagem (bar)", 1.5, 6.0, 3.5)
    vacuo_bolha = st.sidebar.slider("Vácuo Formação Blister (mbar)", -900, -200, -750)
    tensao_filme = st.sidebar.slider("Tensão do Filme (N)", 10, 80, 45)
    
    # Cálculo de Risco na Embalagem
    risco = 85.0 if (temp_selagem < 130 or temp_selagem > 160 or vacuo_bolha > -500) else 5.0
    
    # Métricas da Embaladora
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temp. Selagem Hálux", f"{temp_selagem:.1f} °C", "Dentro do Setpoint" if 135 <= temp_selagem <= 155 else "Fora do Padrão")
    m2.metric("Pressão de Selagem", f"{pressao_selagem:.1f} bar")
    m3.metric("Vácuo de Formação", f"{vacuo_bolha} mbar", "Selagem Estéril OK" if vacuo_bolha < -600 else "Risco Vazamento")
    m4.metric("Tensão do Filme", f"{tensao_filme} N")

# ==============================================================================
# PAINEL GERAL DE RISCO PREDITIVO E GRÁFICO (COMUM A TODOS OS SETORES)
# ==============================================================================
st.markdown("---")
c_status, c_bar = st.columns([1, 2])

with c_status:
    st.subheader("Status de Manutenção Preditiva")
    if risco < 35:
        st.success("🟢 **PROCESSO ESTÁVEL**\nParâmetros operando dentro da janela de qualidade.")
    elif 35 <= risco < 65:
        st.warning("🟡 **ATENÇÃO TÉCNICA**\nDesvio identificado. Agendar inspeção preventiva.")
    else:
        st.error("🔴 **ALERTA CRÍTICO**\nRisco imediato de refugo do lote ou parada não programada!")

with c_bar:
    st.subheader("Probabilidade de Falha / Parada")
    st.progress(int(risco))
    st.write(f"**Índice de Risco Calculado pela IA:** `{risco:.1f}%`")

# Tendência
st.subheader("📈 Monitoramento Contínuo de Estabilidade")
chart_data = pd.DataFrame(
    np.random.normal(loc=100, scale=3, size=(20, 3)),
    columns=["Variável Térmica/Mecânica", "Pressão do Sistema", "Índice Qualidade"]
)
st.line_chart(chart_data)
