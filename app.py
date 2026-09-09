import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Injex Cirúrgica - Gestão Preditiva",
    page_icon="💉",
    layout="wide"
)

# Mapeamento de 10 Máquinas por Setor
MAQUINAS_POR_SETOR = {
    "Injetora": [f"INJ-{i:02d} (Injetora {i})" for i in range(1, 11)],
    "Montagem": [f"MONT-{i:02d} (Montagem {i})" for i in range(1, 11)],
    "Embalagem": [f"EMB-{i:02d} (Embalagem {i})" for i in range(1, 11)]
}

# Inicialização do session_state
if 'lista_os' not in st.session_state:
    st.session_state['lista_os'] = [
        {"id": "OS-1001", "setor": "Injetora", "maquina": "INJ-01 (Injetora 1)", "defeito": "Vazamento de óleo no cilindro", "prioridade": "Alta", "hora_abertura": "08:15"},
        {"id": "OS-1002", "setor": "Injetora", "maquina": "INJ-05 (Injetora 5)", "defeito": "Ruído no exaustor", "prioridade": "Média", "hora_abertura": "09:30"},
        {"id": "OS-1004", "setor": "Embalagem", "maquina": "EMB-03 (Embalagem 3)", "defeito": "Falha na resistência", "prioridade": "Alta", "hora_abertura": "10:11"}
    ]

if 'em_andamento_os' not in st.session_state:
    st.session_state['em_andamento_os'] = [
        {"id": "OS-1003", "setor": "Montagem", "maquina": "MONT-02 (Montagem 2)", "defeito": "Ajuste na garra pneumática", "prioridade": "Baixa", "hora_abertura": "10:05", "hora_inicio": "10:20"}
    ]

if 'historico_os' not in st.session_state:
    st.session_state['historico_os'] = [
        {"id": "OS-0998", "setor": "Injetora", "maquina": "INJ-01 (Injetora 1)", "defeito": "Troca de resistência Z2", "prioridade": "Média", "hora_abertura": "06:20", "hora_inicio": "06:25", "hora_conclusao": "07:10", "status": "Concluída"}
    ]

# Estilo CSS Personalizado
st.markdown("""
<style>
    .stMetric { background-color: #1f2937; padding: 6px; border-radius: 6px; }
    .os-card-alta { background-color: #450a0a; border-left: 4px solid #dc2626; padding: 6px; border-radius: 4px; color: #fef2f2; font-size: 0.85rem; }
    .os-card-media { background-color: #451a03; border-left: 4px solid #d97706; padding: 6px; border-radius: 4px; color: #fffbeb; font-size: 0.85rem; }
    .os-card-baixa { background-color: #052e16; border-left: 4px solid #16a34a; padding: 6px; border-radius: 4px; color: #f0fdf4; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL: BOTÕES DE NAVEGAÇÃO & FORMULÁRIO
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/syringe.png", width=50)
st.sidebar.markdown("##### Injex Cirúrgica")

# NAVEGAÇÃO EM FORMA DE BOTÃO (PAINEL / FÁBRICA)
st.sidebar.caption("Menu")
if 'pagina_ativa' not in st.session_state:
    st.session_state['pagina_ativa'] = "Painel"

col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("🖥️ Painel", use_container_width=True, type="primary" if st.session_state['pagina_ativa'] == "Painel" else "secondary"):
    st.session_state['pagina_ativa'] = "Painel"
    st.rerun()

if col_btn2.button("🌐 Fábrica", use_container_width=True, type="primary" if st.session_state['pagina_ativa'] == "Fábrica" else "secondary"):
    st.session_state['pagina_ativa'] = "Fábrica"
    st.rerun()

st.sidebar.markdown("---")

# SELEÇÃO DE MAQUINA (EXIBIDA APENAS SE ESTIVER NO PAINEL)
if st.session_state['pagina_ativa'] == "Painel":
    setor_selecionado = st.sidebar.selectbox("Setor:", ["Injetora", "Montagem", "Embalagem"])
    maquinas_disponiveis = MAQUINAS_POR_SETOR[setor_selecionado]
    maquina_selecionada = st.sidebar.selectbox("Máquina:", maquinas_disponiveis)
    st.sidebar.markdown("---")
else:
    setor_selecionado = "Injetora"
    maquina_selecionada = MAQUINAS_POR_SETOR["Injetora"][0]

# ABERTURA RÁPIDA DE OS
st.sidebar.markdown("##### 📝 Nova OS")
os_setor = st.sidebar.selectbox("Setor Destino:", ["Injetora", "Montagem", "Embalagem"], key="os_setor_select")
maquinas_form_dinamicas = MAQUINAS_POR_SETOR[os_setor]

with st.sidebar.form(key="form_os_simplificada", clear_on_submit=True):
    os_maquina = st.selectbox("Máquina:", maquinas_form_dinamicas)
    os_defeito = st.text_area("Problema:", placeholder="Descreva o problema...", height=70)
    os_prioridade = st.selectbox("Prioridade:", ["Alta", "Média", "Baixa"])
    submit_os = st.form_submit_button("🚀 Abrir OS")

if submit_os:
    if os_defeito.strip() != "":
        nova_os = {
            "id": f"OS-{datetime.now().strftime('%M%S')}",
            "setor": os_setor,
            "maquina": os_maquina,
            "defeito": os_defeito,
            "prioridade": os_prioridade,
            "hora_abertura": datetime.now().strftime('%H:%M')
        }
        st.session_state['lista_os'].insert(0, nova_os)
        st.sidebar.success(f"OS Criada: {nova_os['id']}")
        st.rerun()
    else:
        st.sidebar.error("Informe o problema.")

# Preventiva
def get_preventiva_dados(maquina_nome):
    tag = maquina_nome.split(' ')[0]
    return {
        "tempo": "2h",
        "pecas_por_tipo": {
            "🔩 Mecânica": [f"Bujões {tag}", "Anel Guia"],
            "💨 Pneumática": [f"Filtro {tag}", "Válvula Solenóide"],
            "⚡ Elétrica": ["Sensor M12", "Cartucho Aquecedor"]
        }
    }

info_prev = get_preventiva_dados(maquina_selecionada)

# ==============================================================================
# PÁGINA: FÁBRICA (VISÃO GERAL DIVIDIDA EM 3 SUB-MENUS POR SETOR)
# ==============================================================================
if st.session_state['pagina_ativa'] == "Fábrica":
    st.markdown("### 🌐 Visão Geral Fábrica")
    
    # 3 MENUS/ABAS PARA CADA SETOR
    tab_inj, tab_mont, tab_emb = st.tabs(["🏢 Injetora", "🏢 Montagem", "🏢 Embalagem"])

    def render_tabela_setor(setor_nome):
        col_ab, col_and, col_res = st.columns(3)
        
        # OS ABERTAS
        with col_ab:
            os_ab = [o for o in st.session_state['lista_os'] if o['setor'] == setor_nome]
            st.markdown(f"##### 🔴 Paradas/Abertas ({len(os_ab)})")
            if os_ab:
                for item in os_ab:
                    st.markdown(f"**{item['id']}** | {item['maquina'].split(' ')[0]}")
                    st.caption(f"⚠️ {item['defeito']} | {item['prioridade']} | {item.get('hora_abertura','')}")
                    if st.button(f"▶️ Iniciar {item['id']}", key=f"f_in_{setor_nome}_{item['id']}", use_container_width=True):
                        os_and = item.copy()
                        os_and["hora_inicio"] = datetime.now().strftime('%H:%M')
                        st.session_state['em_andamento_os'].insert(0, os_and)
                        st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != item['id']]
                        st.rerun()
                    st.divider()
            else:
                st.caption("Sem OSs abertas.")

        # OS EM ANDAMENTO
        with col_and:
            os_and = [o for o in st.session_state['em_andamento_os'] if o['setor'] == setor_nome]
            st.markdown(f"##### ⚙️ Em Andamento ({len(os_and)})")
            if os_and:
                for item in os_and:
                    st.markdown(f"**{item['id']}** | {item['maquina'].split(' ')[0]}")
                    st.caption(f"🛠️ {item['defeito']} | Início: {item.get('hora_inicio','')}")
                    if st.button(f"✅ Finalizar {item['id']}", key=f"f_fin_{setor_nome}_{item['id']}", use_container_width=True):
                        os_conc = item.copy()
                        os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M')
                        os_conc["status"] = "Concluída"
                        st.session_state['historico_os'].insert(0, os_conc)
                        st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != item['id']]
                        st.rerun()
                    st.divider()
            else:
                st.caption("Nenhum atendimento.")

        # OS RESOLVIDAS
        with col_res:
            os_res = [o for o in st.session_state['historico_os'] if o['setor'] == setor_nome]
            st.markdown(f"##### ✅ Resolvidas ({len(os_res)})")
            if os_res:
                for item in os_res:
                    st.markdown(f"**{item['id']}** | {item['maquina'].split(' ')[0]}")
                    st.caption(f"✔️ {item['defeito']} | Fim: {item.get('hora_conclusao','')}")
                    if st.button(f"🔄 Reabrir {item['id']}", key=f"f_re_{setor_nome}_{item['id']}", use_container_width=True):
                        os_reab = {
                            "id": item["id"], "setor": item["setor"], "maquina": item["maquina"],
                            "defeito": item["defeito"], "prioridade": item["prioridade"],
                            "hora_abertura": datetime.now().strftime('%H:%M')
                        }
                        st.session_state['lista_os'].insert(0, os_reab)
                        st.session_state['historico_os'] = [o for o in st.session_state['historico_os'] if o['id'] != item['id']]
                        st.rerun()
                    st.divider()
            else:
                st.caption("Nenhum histórico.")

    with tab_inj:
        render_tabela_setor("Injetora")
        
    with tab_mont:
        render_tabela_setor("Montagem")
        
    with tab_emb:
        render_tabela_setor("Embalagem")

# ==============================================================================
# PÁGINA: PAINEL DA MÁQUINA INDIVIDUAL
# ==============================================================================
else:
    st.markdown(f"### ⚙️ {maquina_selecionada}")

    tab_principal, tab_preventiva, tab_abertas, tab_andamento, tab_historico = st.tabs([
        "📊 Telemetria", "🛠️ Preventiva", "📌 Abertas", "⚙️ Andamento", "✅ Resolvidas"
    ])

    with tab_principal:
        if setor_selecionado == "Injetora":
            col_c1, col_c2, col_c3 = st.columns(3)
            temp_canhao = col_c1.slider("Temp. Canhão (°C)", 180.0, 260.0, 220.0)
            temp_molde = col_c2.slider("Temp. Molde (°C)", 15.0, 70.0, 32.0)
            pressao_recalque = col_c3.slider("Pressão (bar)", 50.0, 160.0, 95.0)
            risco = min(100.0, (pressao_recalque * temp_molde) / 80)
        else:
            col_c1, col_c2 = st.columns(2)
            param1 = col_c1.slider("Pressão (bar)", 4.0, 10.0, 6.5)
            param2 = col_c2.slider("Velocidade (pç/min)", 100, 300, 240)
            risco = 15.0 if param1 >= 5.5 else 75.0

        disp = max(60, int(98 - (risco * 0.3)))
        perf = max(70, int(95 - (risco * 0.2)))
        qual = max(80, int(99 - (risco * 0.4)))
        oee = int((disp/100) * (perf/100) * (qual/100) * 100)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Disp.", f"{disp}%")
        m2.metric("Perf.", f"{perf}%")
        m3.metric("Qual.", f"{qual}%")
        m4.metric("OEE", f"{oee}%")

        st.progress(int(risco))
        if risco < 35:
            st.success("🟢 Operação Normal")
        elif 35 <= risco < 65:
            st.warning("🟡 Atenção")
        else:
            st.error("🔴 Risco de Parada")

    with tab_preventiva:
        st.caption(f"Tempo estimado: {info_prev['tempo']}")
        cols_cat = st.columns(3)
        for idx, (cat, pecas) in enumerate(info_prev['pecas_por_tipo'].items()):
            with cols_cat[idx]:
                st.markdown(f"**{cat}**")
                for p in pecas:
                    st.write(f"• {p}")

    with tab_abertas:
        os_ab = [o for o in st.session_state['lista_os'] if o['setor'] == setor_selecionado]
        if os_ab:
            for item in os_ab:
                st.write(f"**{item['id']}** ({item['maquina'].split(' ')[0]}) - {item['defeito']}")
                if st.button(f"▶️ Atender {item['id']}", key=f"p_in_{item['id']}"):
                    os_and = item.copy()
                    os_and["hora_inicio"] = datetime.now().strftime('%H:%M')
                    st.session_state['em_andamento_os'].insert(0, os_and)
                    st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != item['id']]
                    st.rerun()
        else:
            st.caption("Sem OSs abertas para este setor.")

    with tab_andamento:
        os_and = [o for o in st.session_state['em_andamento_os'] if o['setor'] == setor_selecionado]
        if os_and:
            for item in os_and:
                st.write(f"🛠️ **{item['id']}** ({item['maquina'].split(' ')[0]}) - {item['defeito']}")
                if st.button(f"✅ Finalizar {item['id']}", key=f"p_fin_{item['id']}"):
                    os_conc = item.copy()
                    os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M')
                    os_conc["status"] = "Concluída"
                    st.session_state['historico_os'].insert(0, os_conc)
                    st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != item['id']]
                    st.rerun()
        else:
            st.caption("Sem manutenções em andamento neste setor.")

    with tab_historico:
        os_res = [o for o in st.session_state['historico_os'] if o['setor'] == setor_selecionado]
        if os_res:
            for item in os_res:
                st.write(f"✅ **{item['id']}** ({item['maquina'].split(' ')[0]}) - {item['defeito']}")
        else:
            st.caption("Sem histórico para este setor.")
