import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="INJEX PREDITIX 4.0",
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
    .iot-card {
        background-color: #0f172a;
        border: 1px dashed #38bdf8;
        border-radius: 8px;
        padding: 12px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL: BOTÕES DE NAVEGAÇÃO & FORMULÁRIO
# ==============================================================================
st.sidebar.image("https://img.icons8.com/color/96/syringe.png", width=45)
st.sidebar.markdown("### INJEX PREDITIX 4.0")
st.sidebar.caption("Sistema Integrado Preditivo & PCM")

# NAVEGAÇÃO EM FORMA DE BOTÃO (PAINEL / FÁBRICA)
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

# SELEÇÃO DE MÁQUINA (NO PAINEL)
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
    os_defeito = st.text_area("Problema:", placeholder="Descreva o problema...", height=60)
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

# Preventive Data
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
    st.markdown("### 🌐 Visão Geral Fábrica — INJEX PREDITIX 4.0")
    
    # GRAFICO RESUMO DA FÁBRICA
    df_os_todas = pd.DataFrame(st.session_state['lista_os'] + st.session_state['em_andamento_os'] + st.session_state['historico_os'])
    if not df_os_todas.empty:
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            fig_bar = px.histogram(df_os_todas, x="setor", color="prioridade", barmode="group",
                                  title="Volume de Demandas por Setor Fabril",
                                  color_discrete_map={"Alta": "#ef4444", "Média": "#f59e0b", "Baixa": "#10b981"},
                                  height=230)
            fig_bar.update_layout(margin=dict(l=20, r=20, t=35, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_g2:
            st.metric("Total de OSs Registradas", len(df_os_todas))
            st.metric("Em Atendimento Agordo", len(st.session_state['em_andamento_os']))
            st.metric("Taxa de Resolução", f"{int((len(st.session_state['historico_os'])/len(df_os_todas))*100)}%")

    st.markdown("---")

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

        # METRICAS
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Disp.", f"{disp}%")
        m2.metric("Perf.", f"{perf}%")
        m3.metric("Qual.", f"{qual}%")
        m4.metric("OEE Global", f"{oee}%")

        st.progress(int(risco))
        if risco < 35:
            st.success("🟢 Operação Normal")
        elif 35 <= risco < 65:
            st.warning("🟡 Atenção Preditiva")
        else:
            st.error("🔴 Risco Crítico de Parada")

        st.markdown("---")

        # GRÁFICOS DINÂMICOS DA MÁQUINA
        col_g_left, col_g_right = st.columns([2, 1])

        with col_g_left:
            # Gráfico de Linhas / Área (Telemetria temporal)
            df_chart = pd.DataFrame({
                "Tempo (min)": list(range(1, 21)),
                "Pressão": np.random.normal(loc=100, scale=2, size=20),
                "Temperatura": np.random.normal(loc=220, scale=5, size=20)
            })
            fig_telemetry = px.line(df_chart, x="Tempo (min)", y=["Pressão", "Temperatura"],
                                    title="📈 Telemetria Contínua de Processo (Últimos 20 min)",
                                    height=250)
            fig_telemetry.update_layout(margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_telemetry, use_container_width=True)

        with col_g_right:
            # Gráfico Donut OEE
            df_oee = pd.DataFrame({
                "Categoria": ["Eficiência Operacional", "Perdas de Processo"],
                "Valor": [oee, 100 - oee]
            })
            fig_donut = px.pie(df_oee, values="Valor", names="Categoria", hole=0.6,
                               title="🍩 OEE Balance", color_discrete_sequence=["#10b981", "#ef4444"], height=250)
            fig_donut.update_layout(margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig_donut, use_container_width=True)

    with tab_preventiva:
        st.caption(f"Tempo estimado de intervenção: {info_prev['tempo']}")
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

# ==============================================================================
# RODAPÉ: MÓDULO DE CONEXÃO IOT / CLP (AGUARDANDO DADOS DA MÁQUINA)
# ==============================================================================
st.markdown("---")
tag_maquina_atual = maquina_selecionada.split(' ')[0] if st.session_state['pagina_ativa'] == "Painel" else "FÁBRICA-GENERAL"

st.markdown(f"""
<div class="iot-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <b style="color: #38bdf8;">📡 Gateway IoT & CLP Direct Link (OPC-UA / MQTT)</b><br>
            <small style="color: #94a3b8;">Endereço IP: 192.168.10.{np.random.randint(10,99)} | Máquina Alvo: <b>{tag_maquina_atual}</b></small>
        </div>
        <div>
            <span style="background-color: #0284c7; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem;">⏳ Aguardando Conexão Direta...</span>
        </div>
    </div>
    <div style="margin-top: 8px; font-family: monospace; font-size: 0.8rem; color: #64748b;">
        [SYSTEM LOG]: Handshake enviado via Modbus TCP. Aguardando pacotes de telemetria bruta da CLP... (0 bytes recebidos)
    </div>
</div>
""", unsafe_allow_html=True)
