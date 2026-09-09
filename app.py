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

# Estilo CSS Personalizado para Visual Industrial
st.markdown("""
<style>
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 8px; }
    .os-card { background-color: #2b1d1d; border: 1px solid #ff4b4b; padding: 15px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL: SELEÇÃO DE SETOR E MÁQUINA
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/syringe.png", width=70)
st.sidebar.title("Injex Cirúrgica LTDA")
st.sidebar.caption("Sistema de Monitoramento Preditivo & OEE")

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
st.sidebar.subheader("🎛️ Simulação de Telemetria CLP")

# ==============================================================================
# LÓGICA POR SETOR
# ==============================================================================
if setor_selecionado == "1. Injeção Plástica":
    st.title(f"🏭 Injeção Plástica | {maquina_selecionada}")
    
    # Controles
    temp_canhao = st.sidebar.slider("Temp. Canhão Z1 (°C)", 180.0, 260.0, 220.0)
    temp_molde = st.sidebar.slider("Temp. Água Molde (°C)", 15.0, 70.0, 32.0)
    pressao_recalque = st.sidebar.slider("Pressão Injeção (bar)", 50.0, 160.0, 95.0)
    ciclos = st.sidebar.number_input("Ciclos Acumulados Molde", value=380000)
    
    risco = min(100.0, (pressao_recalque * temp_molde) / 80) if ciclos > 300000 else 12.0
    
    # KPIs Rápidos
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temp. Canhão", f"{temp_canhao:.1f} °C")
    m2.metric("Temp. Molde", f"{temp_molde:.1f} °C", "Normal" if temp_molde < 45 else "Superaquecendo", delta_color="inverse")
    m3.metric("Pressão Injeção", f"{pressao_recalque:.0f} bar")
    m4.metric("Ciclos Totais", f"{ciclos:,}")

elif setor_selecionado == "2. Montagem Automática":
    st.title(f"⚙️ Montagem Automática | {maquina_selecionada}")
    
    pressao_ar = st.sidebar.slider("Pressão Ar Comprimido (bar)", 4.0, 8.0, 6.2)
    vel_ciclo = st.sidebar.slider("Velocidade (Peças/Min)", 100, 300, 250)
    vibracao_garra = st.sidebar.slider("Vibração Atuador (mm/s)", 0.5, 8.0, 1.8)
    
    risco = min(100.0, (vibracao_garra * 15))
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pressão Ar", f"{pressao_ar:.1f} bar")
    m2.metric("Velocidade", f"{vel_ciclo} pçs/min")
    m3.metric("Vibração Atuadores", f"{vibracao_garra:.1f} mm/s")
    m4.metric("Status Câmeras", "100% OK")

else:
    st.title(f"📦 Embalagem & Blister | {maquina_selecionada}")
    
    temp_selagem = st.sidebar.slider("Temp. Selagem (°C)", 110.0, 180.0, 145.0)
    vacuo_bolha = st.sidebar.slider("Vácuo Blister (mbar)", -900, -200, -750)
    
    risco = 85.0 if (temp_selagem < 130 or temp_selagem > 160 or vacuo_bolha > -500) else 8.0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temp. Selagem", f"{temp_selagem:.1f} °C")
    m2.metric("Vácuo Blister", f"{vacuo_bolha} mbar")
    m3.metric("Esterilidade", "Garantida (ISO 11607)")
    m4.metric("Filme Utilizado", "98.2 %")

# ==============================================================================
# PAINEL DE EFICIÊNCIA GLOBAL (OEE)
# ==============================================================================
st.markdown("---")
st.subheader("📊 Indicadores Industriais (OEE em Tempo Real)")

# Lógica de cálculo do OEE baseado no risco
disp = max(60, int(98 - (risco * 0.3)))
perf = max(70, int(95 - (risco * 0.2)))
qual = max(80, int(99 - (risco * 0.4)))
oee = int((disp/100) * (perf/100) * (qual/100) * 100)

col_oee1, col_oee2, col_oee3, col_oee4 = st.columns(4)
col_oee1.metric("Disponibilidade", f"{disp} %")
col_oee2.metric("Performance", f"{perf} %")
col_oee3.metric("Qualidade", f"{qual} %")
col_oee4.metric("OEE GLOBAL", f"{oee} %", delta=f"{oee - 85}% vs Meta World Class")

# ==============================================================================
# MANUTENÇÃO PREDITIVA & EMISSÃO DE ORDEM DE SERVIÇO (OS)
# ==============================================================================
st.markdown("---")
col_p1, col_p2 = st.columns([1, 1])

with col_p1:
    st.subheader("🤖 Diagnóstico da Inteligência Artificial")
    st.progress(int(risco))
    st.write(f"**Risco de Defeito / Parada:** `{risco:.1f}%`")
    
    if risco < 35:
        st.success("🟢 **SISTEMA OPERANDO EM CONDIÇÕES IDEIAIS**")
    elif 35 <= risco < 65:
        st.warning("🟡 **ALERTA TÉCNICO:** Variação detectada. Recomenda-se acompanhamento no próximo turno.")
    else:
        st.error("🔴 **ALERTA CRÍTICO:** Padrão de falha identificado!")

with col_p2:
    st.subheader("🛠️ Gestão de Manutenção Preditiva")
    if risco >= 65:
        st.markdown(f"""
        <div class="os-card">
            <h4>🚨 ORDEM DE SERVIÇO AUTOMÁTICA GERADA (#OS-{datetime.now().strftime('%H%M%S')})</h4>
            <p><b>Equipamento:</b> {maquina_selecionada}</p>
            <p><b>Ação Requerida:</b> Verificar sistema de refrigeração e lubrificação do molde.</p>
            <p><b>Prioridade:</b> ALTA (Prevenção de Parada de Linha)</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✅ Confirmar Recebimento da OS pelo Mecânico"):
            st.success("Ordem de serviço atribuída ao técnico de plantão!")
    else:
        st.info("Nenhuma ordem de serviço pendente para esta máquina. Operação dentro do padrão.")

# ==============================================================================
# HISTÓRICO E EXPORTAÇÃO DE DADOS (COMPLIANCE)
# ==============================================================================
st.markdown("---")
st.subheader("📈 Histórico do Turno & Exportação para Auditoria")

# Gerando histórico simulado
df_historico = pd.DataFrame({
    "Horário": [f"{h}:00" for h in range(6, 15)],
    "Temperatura (°C)": np.random.normal(215, 2, 9),
    "Pressão (bar)": np.random.normal(95, 3, 9),
    "Risco Calculado (%)": np.random.normal(risco, 5, 9)
})

st.line_chart(df_historico.set_index("Horário")[["Temperatura (°C)", "Pressão (bar)"]])

# Botão para baixar relatório CSV
csv = df_historico.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar Relatório do Turno (CSV / ANVISA)",
    data=csv,
    file_name=f"relatorio_injex_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
