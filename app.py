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

# Inicialização da Lista Global de Ordens de Serviço (Persistência em Sessão)
if 'lista_os' not in st.session_state:
    st.session_state['lista_os'] = [
        # Exemplos iniciais para teste
        {
            "id": "OS-1001",
            "setor": "1. Injeção Plástica",
            "maquina": "INJ-01",
            "defeito": "Vazamento de óleo no cilindro de injeção",
            "prioridade": "Alta",
            "hora": "08:15:22"
        },
        {
            "id": "OS-1002",
            "setor": "1. Injeção Plástica",
            "maquina": "INJ-02",
            "defeito": "Ruído anormal no exaustor",
            "prioridade": "Média",
            "hora": "09:30:10"
        },
        {
            "id": "OS-1003",
            "setor": "2. Montagem Automática",
            "maquina": "MONT-01",
            "defeito": "Ajuste na garra pneumática do êMBolo",
            "prioridade": "Baixa",
            "hora": "10:05:44"
        }
    ]

# Estilo CSS Personalizado para os Cards Compactos de OS
st.markdown("""
<style>
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 8px; }
    
    /* Cards Compactos de OS */
    .os-card-alta {
        background-color: #450a0a;
        border-left: 6px solid #dc2626;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        color: #fef2f2;
    }
    .os-card-media {
        background-color: #451a03;
        border-left: 6px solid #d97706;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        color: #fffbeb;
    }
    .os-card-baixa {
        background-color: #052e16;
        border-left: 6px solid #16a34a;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        color: #f0fdf4;
    }
    
    .preventiva-card { 
        background-color: #1e293b; 
        border-left: 4px solid #3b82f6; 
        padding: 10px; 
        margin-bottom: 10px; 
        border-radius: 4px; 
    }
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
# SEÇÃO PREVENTIVA (SIDEBAR)
# ==============================================================================
st.sidebar.subheader("🛠️ Plano de Preventiva")

dados_preventiva = {
    "INJ-01 (KraussMaffei 200T)": {
        "pecas": ["Anel de Bloqueio", "Jogo Buchas Extratoras"],
        "tempo": "2h 30min"
    },
    "INJ-02 (Romi Prática 130T)": {
        "pecas": ["Resistência Cerâmica Z1", "Filtro Refrigeração"],
        "tempo": "1h 45min"
    },
    "MONT-01 (Linha Alta Velocidade)": {
        "pecas": ["Atuadores Festo", "Garras do Êmbolo"],
        "tempo": "1h 15min"
    },
    "MONT-02 (Montadora Êmbolo/Corpo)": {
        "pecas": ["Atuador Rotativo Servo", "Ventosas Silicone"],
        "tempo": "2h 00min"
    },
    "EMB-01 (Termoformadora Blister)": {
        "pecas": ["Matriz Selagem Térmica", "Borracha Hálux"],
        "tempo": "3h 00min"
    },
    "EMB-02 (Seladora & Encartonadora)": {
        "pecas": ["Correia Dentada Tração", "Cartucho Aquecedor"],
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
    <b>Tempo Estimado:</b> ⏱️ {info_prev['tempo']}
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# ==============================================================================
# FORMULÁRIO DE ABERTURA RÁPIDA DE OS (SIDEBAR)
# ==============================================================================
st.sidebar.subheader("📝 Abertura Rápida de OS")

with st.sidebar.form(key="form_os_simplificada"):
    os_setor = st.selectbox("Setor Destino:", ["1. Injeção Plástica", "2. Montagem Automática", "3. Embalagem & Blister"])
    os_maquina = st.text_input("Máquina:", value=maquina_selecionada.split(' ')[0])
    os_defeito = st.text_area("Sintoma / Defeito:", placeholder="Descreva brevemente...")
    os_prioridade = st.selectbox("Prioridade:", ["Alta", "Média", "Baixa"])
    
    submit_os = st.form_submit_button("🚀 Registrar OS")

if submit_os:
    if os_defeito.strip() != "":
        nova_os = {
            "id": f"OS-{datetime.now().strftime('%M%S')}",
            "setor": os_setor,
            "maquina": os_maquina,
            "defeito": os_defeito,
            "prioridade": os_prioridade,
            "hora": datetime.now().strftime('%H:%M:%S')
        }
        # Adiciona no topo da lista (ordem de abertura)
        st.session_state['lista_os'].insert(0, nova_os)
        st.sidebar.success(f"✅ {nova_os['id']} registrada com sucesso!")
        st.rerun()
    else:
        st.sidebar.error("Descreva o defeito antes de enviar.")

# ==============================================================================
# PAINEL PRINCIPAL
# ==============================================================================
st.title(f"🏭 Injex Cirúrgica | {maquina_selecionada}")

# ------------------------------------------------------------------------------
# QUADRO DE ORDENS DE SERVIÇO ABERTAS DO SETOR
# ------------------------------------------------------------------------------
st.subheader(f"📋 Ordens de Serviço Abertas no Setor: {setor_selecionado}")

# Filtragem das OSs que pertencem apenas ao setor atualmente visualizado
os_do_setor = [os for os in st.session_state['lista_os'] if os['setor'] == setor_selecionado]

if os_do_setor:
    # Exibe as OS em colunas para criar um layout de quadro compacto
    cols_os = st.columns(min(len(os_do_setor), 4))
    
    for idx, item in enumerate(os_do_setor):
        col_target = cols_os[idx % 4]
        
        # Seleção da cor por prioridade
        if item['prioridade'] == "Alta":
            css_class = "os-card-alta"
            icone = "🔴 ALTA"
        elif item['prioridade'] == "Média":
            css_class = "os-card-media"
            icone = "🟡 MÉDIA"
        else:
            css_class = "os-card-baixa"
            icone = "🟢 BAIXA"
            
        with col_target:
            st.markdown(f"""
            <div class="{css_class}">
                <div style="display:flex; justify-between; align-items:center;">
                    <b>{item['id']} | {item['maquina']}</b>
                    <small style="float: right;">⏱️ {item['hora']}</small>
                </div>
                <div style="margin-top: 4px; font-size: 0.9em;">
                    <b>Prioridade:</b> {icone}<br>
                    <b>Defeito:</b> {item['defeito']}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("✨ Nenhuma Ordem de Serviço aberta para este setor no momento.")

st.markdown("---")

# ==============================================================================
# TELEMETRIA E OEE
# ==============================================================================
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

# ==============================================================================
# DIAGNÓSTICO PREDITIVO
# ==============================================================================
st.markdown("---")
col_p1, col_p2 = st.columns([1, 1])

with col_p1:
    st.subheader("🤖 Diagnóstico da IA")
    st.progress(int(risco))
    st.write(f"**Risco Calculado:** `{risco:.1f}%`")
    if risco < 35:
        st.success("🟢 **OPERAÇÃO NORMAL**")
    elif 35 <= risco < 65:
        st.warning("🟡 **MOMENTO DE ATENÇÃO**")
    else:
        st.error("🔴 **RISCO DE PARADA DE LINHA**")

with col_p2:
    st.subheader("🔧 Componentes para Preventiva")
    st.write(f"**Tempo Necessário Parada:** `{info_prev['tempo']}`")
    for p in info_prev['pecas']:
        st.write(f"• {p}")
