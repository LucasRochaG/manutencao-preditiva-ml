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

# Mapeamento de 10 Máquinas por Setor
MAQUINAS_POR_SETOR = {
    "Injetora": [f"INJ-{i:02d} (Injetora Plástica {i})" for i in range(1, 11)],
    "Montagem": [f"MONT-{i:02d} (Linha Montagem {i})" for i in range(1, 11)],
    "Embalagem": [f"EMB-{i:02d} (Seladora & Blister {i})" for i in range(1, 11)]
}

# Inicialização do session_state com dados iniciais
if 'lista_os' not in st.session_state:
    st.session_state['lista_os'] = [
        {
            "id": "OS-1001",
            "setor": "Injetora",
            "maquina": "INJ-01 (Injetora Plástica 1)",
            "defeito": "Vazamento de óleo no cilindro de injeção",
            "prioridade": "Alta",
            "hora_abertura": "08:15:22"
        },
        {
            "id": "OS-1002",
            "setor": "Injetora",
            "maquina": "INJ-05 (Injetora Plástica 5)",
            "defeito": "Ruído anormal no exaustor",
            "prioridade": "Média",
            "hora_abertura": "09:30:10"
        },
        {
            "id": "OS-1004",
            "setor": "Embalagem",
            "maquina": "EMB-03 (Seladora & Blister 3)",
            "defeito": "Falha na resistência de selagem",
            "prioridade": "Alta",
            "hora_abertura": "10:11:05"
        }
    ]

if 'em_andamento_os' not in st.session_state:
    st.session_state['em_andamento_os'] = [
        {
            "id": "OS-1003",
            "setor": "Montagem",
            "maquina": "MONT-02 (Linha Montagem 2)",
            "defeito": "Ajuste na garra pneumática do êmbolo",
            "prioridade": "Baixa",
            "hora_abertura": "10:05:44",
            "hora_inicio": "10:20:15"
        }
    ]

if 'historico_os' not in st.session_state:
    st.session_state['historico_os'] = [
        {
            "id": "OS-0998",
            "setor": "Injetora",
            "maquina": "INJ-01 (Injetora Plástica 1)",
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
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL: SELEÇÃO E FORMULÁRIO DE OS
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/syringe.png", width=70)
st.sidebar.title("Injex Cirúrgica LTDA")
st.sidebar.caption("PCM & Inteligência Preditiva")

# NAVEGAÇÃO DE SETOR E MÁQUINA
setor_selecionado = st.sidebar.selectbox("🏢 Selecione o Setor Fabril:", ["Injetora", "Montagem", "Embalagem"])
maquinas_disponiveis = MAQUINAS_POR_SETOR[setor_selecionado]
maquina_selecionada = st.sidebar.selectbox("⚙️ Selecione a Máquina:", maquinas_disponiveis)

st.sidebar.markdown("---")

# FORMULÁRIO DE ABERTURA DE OS COM MÁQUINA SELECIONÁVEL
st.sidebar.subheader("📝 Abertura Rápida de OS")

with st.sidebar.form(key="form_os_simplificada", clear_on_submit=True):
    os_setor = st.selectbox("Setor Destino:", ["Injetora", "Montagem", "Embalagem"])
    
    # Máquina dinamicamente atualizada com base no setor selecionado no formulário
    maquinas_form = MAQUINAS_POR_SETOR[os_setor]
    os_maquina = st.selectbox("Máquina:", maquinas_form)
    
    os_defeito = st.text_area("Sintoma / Defeito:", placeholder="Descreva brevemente o problema...")
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
        st.sidebar.success(f"✅ {nova_os['id']} registrada para {os_maquina.split(' ')[0]}!")
        st.rerun()
    else:
        st.sidebar.error("Descreva o defeito antes de enviar.")

# Gerador Dinâmico de Componentes de Preventiva por Categoria
def get_preventiva_dados(maquina_nome):
    tag = maquina_nome.split(' ')[0]
    return {
        "tempo": "2h 00min",
        "pecas_por_tipo": {
            "🔩 Mecânica & Estrutural": [f"Conjunto de Bujões {tag}", f"Anel de Guia Protetor", "Eixo Principal"],
            "💨 Pneumática & Hidráulica": [f"Filtro de Pressão {tag}", "Reparo Solenóide", "Válvula Reguladora"],
            "⚡ Elétrica & Automação": ["Sensor de Posição M12", "Cabo Protetor de Sinal", "Cartucho Aquecedor"]
        }
    }

info_prev = get_preventiva_dados(maquina_selecionada)

# ==============================================================================
# ESTRUTURA DE ABAS PRINCIPAIS
# ==============================================================================
st.title(f"🏭 Injex Cirúrgica | {maquina_selecionada}")

tab_global, tab_principal, tab_preventiva, tab_abertas, tab_andamento, tab_historico = st.tabs([
    "🌐 Visão Geral Fábrica (Tabela OSs)",
    "📊 Visão Geral & Telemetria",
    "🛠️ Plano de Preventiva",
    "📌 OSs Abertas", 
    "⚙️ Em Andamento", 
    "✅ Histórico / Resolvidas"
])

# ------------------------------------------------------------------------------
# ABA 0: VISÃO GERAL FÁBRICA (TABELA GLOBAL DE OSs DE TODAS AS MÁQUINAS)
# ------------------------------------------------------------------------------
with tab_global:
    st.subheader("🌐 Painel Global do PCM — Visão Geral de Todas as Máquinas da Fábrica")
    st.caption("Acompanhamento unificado de todas as Ordens de Serviço abertas, em andamento e encerradas.")
    
    col_tab_aberta, col_tab_andamento, col_tab_resolvido = st.columns(3)
    
    # COLUNA 1: PARADAS / ABERTAS
    with col_tab_aberta:
        st.markdown("### 🔴 Parada / Abertas")
        st.caption(f"Total: {len(st.session_state['lista_os'])}")
        
        if st.session_state['lista_os']:
            for os_item in st.session_state['lista_os']:
                st.markdown(f"**{os_item['id']}** | `{os_item['setor']}` - **{os_item['maquina'].split(' ')[0]}**")
                st.write(f"⚠️ *{os_item['defeito']}*")
                st.caption(f"Prioridade: {os_item['prioridade']} | Abertura: {os_item.get('hora_abertura', 'N/A')}")
                
                if st.button(f"▶️ Iniciar {os_item['id']}", key=f"global_iniciar_{os_item['id']}", use_container_width=True):
                    os_and = os_item.copy()
                    os_and["hora_inicio"] = datetime.now().strftime('%H:%M:%S')
                    st.session_state['em_andamento_os'].insert(0, os_and)
                    st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != os_item['id']]
                    st.rerun()
                st.divider()
        else:
            st.success("Nenhuma OS aberta na fábrica no momento.")

    # COLUNA 2: EM ANDAMENTO
    with col_tab_andamento:
        st.markdown("### ⚙️ Em Andamento")
        st.caption(f"Total: {len(st.session_state['em_andamento_os'])}")
        
        if st.session_state['em_andamento_os']:
            for os_item in st.session_state['em_andamento_os']:
                st.markdown(f"**{os_item['id']}** | `{os_item['setor']}` - **{os_item['maquina'].split(' ')[0]}**")
                st.write(f"🛠️ *{os_item['defeito']}*")
                st.caption(f"Início: {os_item.get('hora_inicio', 'N/A')}")
                
                if st.button(f"✅ Finalizar {os_item['id']}", key=f"global_concluir_{os_item['id']}", use_container_width=True):
                    os_conc = os_item.copy()
                    os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M:%S')
                    os_conc["status"] = "Concluída"
                    st.session_state['historico_os'].insert(0, os_conc)
                    st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != os_item['id']]
                    st.rerun()
                st.divider()
        else:
            st.info("Nenhuma manutenção em execução na fábrica.")

    # COLUNA 3: RESOLVIDAS
    with col_tab_resolvido:
        st.markdown("### ✅ Resolvidas")
        st.caption(f"Total: {len(st.session_state['historico_os'])}")
        
        if st.session_state['historico_os']:
            for os_item in st.session_state['historico_os']:
                st.markdown(f"**{os_item['id']}** | `{os_item['setor']}` - **{os_item['maquina'].split(' ')[0]}**")
                st.write(f"✔️ *{os_item['defeito']}*")
                st.caption(f"Concluída às: {os_item.get('hora_conclusao', 'N/A')}")
                
                if st.button(f"🔄 Reabrir {os_item['id']}", key=f"global_reabrir_{os_item['id']}", use_container_width=True):
                    os_reab = {
                        "id": os_item["id"],
                        "setor": os_item["setor"],
                        "maquina": os_item["maquina"],
                        "defeito": os_item["defeito"],
                        "prioridade": os_item["prioridade"],
                        "hora_abertura": datetime.now().strftime('%H:%M:%S')
                    }
                    st.session_state['lista_os'].insert(0, os_reab)
                    st.session_state['historico_os'] = [o for o in st.session_state['historico_os'] if o['id'] != os_item['id']]
                    st.rerun()
                st.divider()
        else:
            st.info("Nenhuma OS finalizada no histórico.")

# ------------------------------------------------------------------------------
# ABA 1: VISÃO GERAL DA MÁQUINA SELECIONADA
# ------------------------------------------------------------------------------
with tab_principal:
    st.subheader(f"🎛️ Telemetria & Monitoramento CLP - {maquina_selecionada}")
    
    if setor_selecionado == "Injetora":
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
        st.subheader("📈 Estabilidade de Processo")
        chart_data = pd.DataFrame(
            np.random.normal(loc=100, scale=3, size=(20, 2)),
            columns=["Pressão Sistema", "Temperatura Zona Crítica"]
        )
        st.line_chart(chart_data)

# ------------------------------------------------------------------------------
# ABA 2: PLANO DE PREVENTIVA DA MÁQUINA SELECIONADA
# ------------------------------------------------------------------------------
with tab_preventiva:
    st.subheader(f"🛠️ Plano de Preventiva — {maquina_selecionada}")
    st.info(f"⏱️ **Tempo Estimado de Parada Programada:** {info_prev['tempo']}")
    
    st.markdown("### 📦 Componentes & Peças Separadas por Categoria")
    
    categorias = info_prev['pecas_por_tipo']
    cols_cat = st.columns(len(categorias))
    
    for idx, (categoria_nome, lista_pecas) in enumerate(categorias.items()):
        with cols_cat[idx]:
            st.markdown(f"#### {categoria_nome}")
            for peca in lista_pecas:
                st.write(f"✅ {peca}")
                
    st.markdown("---")
    st.caption("💡 *Nota do PCM:* Verifique a disponibilidade em almoxarifado antes da parada.")

# ------------------------------------------------------------------------------
# ABA 3: OSs ABERTAS DO SETOR
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
                
            hora_exibicao = item.get('hora_abertura', item.get('hora', 'N/A'))
            
            with col_target:
                st.markdown(f"""
                <div class="{css_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>{item['id']} | {item['maquina'].split(' ')[0]}</b>
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
# ABA 4: OSs EM ANDAMENTO DO SETOR
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
# ABA 5: HISTÓRICO DE OSs CONCLUÍDAS DO SETOR
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
            file_name=f"historico_injex_{setor_selecionado}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info(f"Nenhuma Ordem de Serviço foi concluída para o setor **{setor_selecionado}** neste turno.")
