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

# Inicialização segura da Lista de OSs Abertas
if 'lista_os' not in st.session_state:
    st.session_state['lista_os'] = [
        {
            "id": "OS-1001",
            "setor": "1. Injeção Plástica",
            "maquina": "INJ-01",
            "defeito": "Vazamento de óleo no cilindro de injeção",
            "prioridade": "Alta",
            "hora_abertura": "08:15:22"
        },
        {
            "id": "OS-1002",
            "setor": "1. Injeção Plástica",
            "maquina": "INJ-02",
            "defeito": "Ruído anormal no exaustor",
            "prioridade": "Média",
            "hora_abertura": "09:30:10"
        }
    ]

# Inicialização da Lista de OSs Em Andamento
if 'em_andamento_os' not in st.session_state:
    st.session_state['em_andamento_os'] = [
        {
            "id": "OS-1003",
            "setor": "2. Montagem Automática",
            "maquina": "MONT-01",
            "defeito": "Ajuste na garra pneumática do êmbolo",
            "prioridade": "Baixa",
            "hora_abertura": "10:05:44",
            "hora_inicio": "10:20:15"
        }
    ]

# Inicialização do Histórico de OSs Concluídas
if 'historico_os' not in st.session_state:
    st.session_state['historico_os'] = [
        {
            "id": "OS-0998",
            "setor": "1. Injeção Plástica",
            "maquina": "INJ-01",
            "defeito": "Troca de resistência cerâmica Z2",
            "prioridade": "Média",
            "hora_abertura": "06:20:00",
            "hora_inicio": "06:25:10",
            "hora_conclusao": "07:10:15",
            "status": "Concluída"
        }
    ]

# Estilo CSS Personalizado
st.markdown("""
<style>
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 8px; }
    
    .os-card-alta {
        background-color: #450a0a;
        border-left: 6px solid #dc2626;
        padding: 8px 12px;
        margin-bottom: 4px;
        border-radius: 6px 6px 0px 0px;
        color: #fef2f2;
    }
    .os-card-media {
        background-color: #451a03;
        border-left: 6px solid #d97706;
        padding: 8px 12px;
        margin-bottom: 4px;
        border-radius: 6px 6px 0px 0px;
        color: #fffbeb;
    }
    .os-card-baixa {
        background-color: #052e16;
        border-left: 6px solid #16a34a;
        padding: 8px 12px;
        margin-bottom: 4px;
        border-radius: 6px 6px 0px 0px;
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

# SEÇÃO PREVENTIVA (SIDEBAR)
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

# FORMULÁRIO DE ABERTURA RÁPIDA DE OS
st.sidebar.subheader("📝 Abertura Rápida de OS")

with st.sidebar.form(key="form_os_simplificada", clear_on_submit=True):
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
            "hora_abertura": datetime.now().strftime('%H:%M:%S')
        }
        st.session_state['lista_os'].insert(0, nova_os)
        st.sidebar.success(f"✅ {nova_os['id']} registrada com sucesso!")
        st.rerun()
    else:
        st.sidebar.error("Descreva o defeito antes de enviar.")

# ==============================================================================
# ESTRUTURA DE ABAS NA TELA PRINCIPAL (PRINCIPAL EMPRIMEIRO LUGAR)
# ==============================================================================
st.title(f"🏭 Injex Cirúrgica | {maquina_selecionada}")

tab_principal, tab_abertas, tab_andamento, tab_historico = st.tabs([
    "📊 Visão Geral & Telemetria", 
    "📌 OSs Abertas", 
    "⚙️ Em Andamento", 
    "✅ Histórico / Resolvidas"
])

# ------------------------------------------------------------------------------
# ABA 1: VISÃO GERAL DA MÁQUINA, TELEMETRIA E OEE (MENU PRINCIPAL)
# ------------------------------------------------------------------------------
with tab_principal:
    st.subheader("🎛️ Painel de Telemetria CLP em Tempo Real")
    
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

    st.markdown("---")
    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        st.subheader("🤖 Diagnóstico da Inteligência Artificial")
        st.progress(int(risco))
        st.write(f"**Risco Calculado:** `{risco:.1f}%`")
        if risco < 35:
            st.success("🟢 **OPERAÇÃO NORMAL**")
        elif 35 <= risco < 65:
            st.warning("🟡 **MOMENTO DE ATENÇÃO**")
        else:
            st.error("🔴 **RISCO DE PARADA DE LINHA**")

    with col_p2:
        st.subheader("🔧 Componentes da Preventiva")
        st.write(f"**Tempo Estimado Parada:** `{info_prev['tempo']}`")
        for p in info_prev['pecas']:
            st.write(f"• {p}")

    st.markdown("---")
    st.subheader("📈 Estabilidade de Processo")
    chart_data = pd.DataFrame(
        np.random.normal(loc=100, scale=3, size=(20, 2)),
        columns=["Pressão Sistema", "Temperatura Zona Crítica"]
    )
    st.line_chart(chart_data)

# ------------------------------------------------------------------------------
# ABA 2: OSs ABERTAS (PENDENTES)
# ------------------------------------------------------------------------------
with tab_abertas:
    st.subheader(f"📌 Chamados Aguardando Atendimento no Setor: {setor_selecionado}")

    os_abertas_setor = [os for os in st.session_state['lista_os'] if os['setor'] == setor_selecionado]

    if os_abertas_setor:
        cols_os = st.columns(min(len(os_abertas_setor), 4))
        
        for idx, item in enumerate(os_abertas_setor):
            col_target = cols_os[idx % 4]
            
            if item['prioridade'] == "Alta":
                css_class = "os-card-alta"
                icone = "🔴 ALTA"
            elif item['prioridade'] == "Média":
                css_class = "os-card-media"
                icone = "🟡 MÉDIA"
            else:
                css_class = "os-card-baixa"
                icone = "🟢 BAIXA"
                
            # Tratamento de chave seguro contra KeyError
            hora_exibicao = item.get('hora_abertura', item.get('hora', 'N/A'))
            
            with col_target:
                st.markdown(f"""
                <div class="{css_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>{item['id']} | {item['maquina']}</b>
                        <small style="float: right;">⏱️ {hora_exibicao}</small>
                    </div>
                    <div style="margin-top: 4px; font-size: 0.9em;">
                        <b>Prioridade:</b> {icone}<br>
                        <b>Defeito:</b> {item['defeito']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"▶️ Iniciar Atendimento {item['id']}", key=f"btn_iniciar_{item['id']}", use_container_width=True):
                    os_andamento = item.copy()
                    os_andamento["hora_inicio"] = datetime.now().strftime('%H:%M:%S')
                    
                    st.session_state['em_andamento_os'].insert(0, os_andamento)
                    st.session_state['lista_os'] = [os for os in st.session_state['lista_os'] if os['id'] != item['id']]
                    st.toast(f"OS {item['id']} movida para Em Andamento!", icon="⚙️")
                    st.rerun()
    else:
        st.info("✨ Nenhuma Ordem de Serviço aberta aguardando atendimento para este setor.")

# ------------------------------------------------------------------------------
# ABA 3: OSs EM ANDAMENTO
# ------------------------------------------------------------------------------
with tab_andamento:
    st.subheader(f"⚙️ Manutenções em Execução no Setor: {setor_selecionado}")

    os_andamento_setor = [os for os in st.session_state['em_andamento_os'] if os['setor'] == setor_selecionado]

    if os_andamento_setor:
        for idx, item_and in enumerate(os_andamento_setor):
            col_info, col_acao = st.columns([3, 1])
            
            hora_ab = item_and.get('hora_abertura', item_and.get('hora', 'N/A'))
            
            with col_info:
                st.write(f"🛠️ **{item_and['id']}** | **Máquina:** {item_and['maquina']} | **Abertura:** {hora_ab} | **Início Atendimento:** {item_and.get('hora_inicio', 'N/A')}")
                st.caption(f"Sintoma: {item_and['defeito']} (Prioridade: {item_and['prioridade']})")
                
            with col_acao:
                if st.button(f"✅ Concluir {item_and['id']}", key=f"btn_concluir_{item_and['id']}", use_container_width=True):
                    os_concluida = item_and.copy()
                    os_concluida["hora_conclusao"] = datetime.now().strftime('%H:%M:%S')
                    os_concluida["status"] = "Concluída"
                    
                    st.session_state['historico_os'].insert(0, os_concluida)
                    st.session_state['em_andamento_os'] = [os for os in st.session_state['em_andamento_os'] if os['id'] != item_and['id']]
                    st.toast(f"OS {item_and['id']} concluída com sucesso!", icon="🎉")
                    st.rerun()
            st.divider()
    else:
        st.info("✨ Nenhuma manutenção em execução no momento para este setor.")

# ------------------------------------------------------------------------------
# ABA 4: HISTÓRICO DE OSs CONCLUÍDAS
# ------------------------------------------------------------------------------
with tab_historico:
    st.subheader(f"✅ Histórico de OSs Resolvidas no Setor: {setor_selecionado}")
    
    historico_setor = [os for os in st.session_state['historico_os'] if os['setor'] == setor_selecionado]
    
    if historico_setor:
        col_h1, col_h2, col_h3 = st.columns(3)
        col_h1.metric("OSs Encerradas (Este Setor)", len(historico_setor))
        col_h2.metric("Status PCM", "100% Auditado")
        col_h3.metric("Última Resolução", historico_setor[0].get('hora_conclusao', 'N/A'))
        
        st.markdown("---")
        
        for idx, item_hist in enumerate(historico_setor):
            c_info, c_acao = st.columns([4, 1])
            
            hora_ab = item_hist.get('hora_abertura', item_hist.get('hora', 'N/A'))
            
            with c_info:
                st.write(f"✅ **{item_hist['id']}** | **Máquina:** {item_hist['maquina']} | **Abertura:** {hora_ab} | **Conclusão:** {item_hist.get('hora_conclusao', 'N/A')}")
                st.caption(f"Defeito Resolvido: {item_hist['defeito']} (Prioridade: {item_hist['prioridade']})")
            
            with c_acao:
                if st.button(f"🔄 Reabrir {item_hist['id']}", key=f"btn_reabrir_{item_hist['id']}", use_container_width=True):
                    os_reaberta = {
                        "id": item_hist["id"],
                        "setor": item_hist["setor"],
                        "maquina": item_hist["maquina"],
                        "defeito": item_hist["defeito"],
                        "prioridade": item_hist["prioridade"],
                        "hora_abertura": datetime.now().strftime('%H:%M:%S')
                    }
                    st.session_state['lista_os'].insert(0, os_reaberta)
                    st.session_state['historico_os'] = [os for os in st.session_state['historico_os'] if os['id'] != item_hist['id']]
                    st.toast(f"OS {item_hist['id']} reaberta com sucesso!", icon="🔄")
                    st.rerun()
            st.divider()
            
        df_historico_setor = pd.DataFrame(historico_setor)
        csv_historico = df_historico_setor.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Histórico do Setor em CSV",
            data=csv_historico,
            file_name=f"historico_injex_{setor_selecionado.split('.')[1].strip()}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info(f"Nenhuma Ordem de Serviço foi concluída para o setor **{setor_selecionado}** neste turno.")
