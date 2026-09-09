import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="MANTIS 4.0 - Inteligência em Manutenção",
    page_icon="🦾",
    layout="wide"
)

# Mapeamento de 10 Máquinas por Setor
MAQUINAS_POR_SETOR = {
    "Injetora Plástica": [f"INJ-{i:02d} (Injetora {i})" for i in range(1, 11)],
    "Linha de Montagem": [f"MONT-{i:02d} (Montagem {i})" for i in range(1, 11)],
    "Embalagem & Selagem": [f"EMB-{i:02d} (Embalagem {i})" for i in range(1, 11)]
}

# ==============================================================================
# BANCO DE DADOS LOCAL (SESSION STATE)
# ==============================================================================
if 'usuarios_db' not in st.session_state:
    st.session_state['usuarios_db'] = {
        "ADM01": {"nome": "Carlos Administrador", "perfil": "Administrador", "senha": "123"},
        "M001": {"nome": "Roberto Mecânico", "perfil": "Mecânico", "senha": "123"},
        "M002": {"nome": "Marcos Técnico", "perfil": "Mecânico", "senha": "123"},
        "OP101": {"nome": "João Operador", "perfil": "Operador", "senha": "123"}
    }

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = {}

if 'lista_os' not in st.session_state:
    st.session_state['lista_os'] = [
        {"id": "OS-1001", "setor": "Injetora Plástica", "maquina": "INJ-01 (Injetora 1)", "defeito": "Vazamento de óleo no cilindro", "prioridade": "Alta", "hora_abertura": "08:15", "autor_abertura": "João Operador"},
        {"id": "OS-1002", "setor": "Injetora Plástica", "maquina": "INJ-05 (Injetora 5)", "defeito": "Ruído no exaustor", "prioridade": "Média", "hora_abertura": "09:30", "autor_abertura": "João Operador"}
    ]

if 'em_andamento_os' not in st.session_state:
    st.session_state['em_andamento_os'] = [
        {"id": "OS-1003", "setor": "Linha de Montagem", "maquina": "MONT-02 (Montagem 2)", "defeito": "Ajuste na garra pneumática", "prioridade": "Baixa", "hora_abertura": "10:05", "hora_inicio": "10:20", "mecanico_responsavel": "Roberto Mecânico"}
    ]

if 'historico_os' not in st.session_state:
    st.session_state['historico_os'] = [
        {"id": "OS-0998", "setor": "Injetora Plástica", "maquina": "INJ-01 (Injetora 1)", "defeito": "Troca de resistência Z2", "prioridade": "Média", "hora_abertura": "06:20", "hora_inicio": "06:25", "hora_conclusao": "07:10", "status": "Concluída", "mecanico_responsavel": "Roberto Mecânico", "relatorio_fechamento": "Substituído o cartucho de resistência queimado e testado o circuito elétrico com sucesso."}
    ]

# ==============================================================================
# ESTILO CSS PROFISSIONAL
# ==============================================================================
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: 700; color: #f8fafc; margin-bottom: 0px; }
    .sub-header { font-size: 0.9rem; color: #94a3b8; margin-bottom: 20px; }
    .card-metric { background-color: #1e293b; border: 1px solid #334155; padding: 15px; border-radius: 8px; text-align: center; }
    .badge-adm { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
    .badge-mec { background-color: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
    .badge-op  { background-color: #3b82f6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL: LOGIN DISCRETO & NAVEGAÇÃO
# ==============================================================================
st.sidebar.markdown("### 🦾 MANTIS 4.0")
st.sidebar.caption("Inteligência em Manutenção Industrial")
st.sidebar.markdown("---")

# Login Discreto no Canto (Sidebar)
if not st.session_state['autenticado']:
    with st.sidebar.expander("🔐 Identificação / Login", expanded=False):
        with st.form("form_login_discreto"):
            mat_input = st.text_input("Matrícula:")
            senha_input = st.text_input("Senha:", type="password")
            btn_entrar = st.form_submit_button("Entrar", use_container_width=True)
            
            if btn_entrar:
                mat_limpa = mat_input.strip()
                if mat_limpa in st.session_state['usuarios_db']:
                    user_info = st.session_state['usuarios_db'][mat_limpa]
                    if user_info["senha"] == senha_input:
                        st.session_state['autenticado'] = True
                        st.session_state['usuario_logado'] = {
                            "matricula": mat_limpa,
                            "nome": user_info["nome"],
                            "perfil": user_info["perfil"]
                        }
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
                else:
                    st.error("Matrícula não encontrada.")
else:
    usuario = st.session_state['usuario_logado']
    b_class = "badge-adm" if usuario['perfil'] == "Administrador" else ("badge-mec" if usuario['perfil'] == "Mecânico" else "badge-op")
    st.sidebar.markdown(f"👤 **{usuario['nome']}**")
    st.sidebar.markdown(f"Perfil: <span class='{b_class}'>{usuario['perfil']}</span>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state['autenticado'] = False
        st.session_state['usuario_logado'] = {}
        st.rerun()

st.sidebar.markdown("---")

# Menu de Navegação Global
opcoes_navegacao = ["🖥️ Painel da Máquina", "🌐 Visão Geral Fábrica"]
if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] == "Administrador":
    opcoes_navegacao.append("👥 Gestão de Usuários (ADM)")

pagina_selecionada = st.sidebar.radio("Navegação Principal:", opcoes_navegacao)

st.sidebar.markdown("---")

# Seletor de Máquina (Disponível apenas quando estiver no Painel)
if pagina_selecionada == "🖥️ Painel da Máquina":
    st.sidebar.markdown("#### ⚙️ Seletor de Ativo")
    setor_selecionado = st.sidebar.selectbox("Setor:", list(MAQUINAS_POR_SETOR.keys()))
    maquina_selecionada = st.sidebar.selectbox("Máquina:", MAQUINAS_POR_SETOR[setor_selecionado])
    st.sidebar.markdown("---")
else:
    setor_selecionado = "Injetora Plástica"
    maquina_selecionada = MAQUINAS_POR_SETOR["Injetora Plástica"][0]

# Abertura Rápida de Ordem de Serviço (Qualquer um pode abrir)
st.sidebar.markdown("#### 📝 Abrir Nova OS")
with st.sidebar.form(key="form_os_rapida", clear_on_submit=True):
    os_setor = st.selectbox("Setor Destino:", list(MAQUINAS_POR_SETOR.keys()))
    os_maquina = st.selectbox("Máquina Alvo:", MAQUINAS_POR_SETOR[os_setor])
    os_defeito = st.text_area("Descrição do Problema:", placeholder="Ex: Vazamento no pistão...", height=70)
    os_prioridade = st.selectbox("Prioridade:", ["Alta", "Média", "Baixa"])
    submit_os = st.form_submit_button("🚀 Enviar Chamado", use_container_width=True)

if submit_os:
    if os_defeito.strip():
        autor = st.session_state['usuario_logado']['nome'] if st.session_state['autenticado'] else "Operador Padrão"
        nova_os = {
            "id": f"OS-{datetime.now().strftime('%M%S')}",
            "setor": os_setor,
            "maquina": os_maquina,
            "defeito": os_defeito,
            "prioridade": os_prioridade,
            "hora_abertura": datetime.now().strftime('%H:%M'),
            "autor_abertura": autor
        }
        st.session_state['lista_os'].insert(0, nova_os)
        st.sidebar.success(f"Criado: {nova_os['id']}")
        st.rerun()
    else:
        st.sidebar.error("Descreva o problema.")

# ==============================================================================
# TELA 1: GESTÃO DE USUÁRIOS (EXCLUSIVO PARA ADMINISTRADOR)
# ==============================================================================
if pagina_selecionada == "👥 Gestão de Usuários (ADM)":
    st.markdown('<p class="main-header">👥 Painel Administrativo de Usuários</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Controle central de cadastros, perfis de acesso e senhas do sistema.</p>', unsafe_allow_html=True)
    
    col_cad1, col_cad2 = st.columns([1, 1], gap="large")
    
    with col_cad1:
        st.markdown("##### ➕ Cadastrar Novo Colaborador")
        with st.form("form_novo_usuario_adm"):
            mat_novo = st.text_input("Matrícula (Ex: M005, ADM02):")
            nome_novo = st.text_input("Nome Completo:")
            perfil_novo = st.selectbox("Perfil de Acesso:", ["Mecânico", "Administrador", "Operador"])
            senha_nova = st.text_input("Senha Inicial:", type="password")
            btn_salvar = st.form_submit_button("Salvar Cadastro", use_container_width=True)
            
            if btn_salvar:
                if mat_novo.strip() and nome_novo.strip() and senha_nova.strip():
                    if mat_novo.strip() in st.session_state['usuarios_db']:
                        st.error("Matrícula já cadastrada no sistema.")
                    else:
                        st.session_state['usuarios_db'][mat_novo.strip()] = {
                            "nome": nome_novo.strip(),
                            "perfil": perfil_novo,
                            "senha": senha_nova.strip()
                        }
                        st.success(f"Usuário {nome_novo} cadastrado com sucesso!")
                        st.rerun()
                else:
                    st.warning("Preencha todos os campos.")
                    
    with col_cad2:
        st.markdown("##### 📋 Usuários Cadastrados no Banco")
        df_users = pd.DataFrame([
            {"Matrícula": k, "Nome": v["nome"], "Perfil": v["perfil"]} 
            for k, v in st.session_state['usuarios_db'].items()
        ])
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        
        st.markdown("##### 🗑️ Remover Cadastro")
        mat_remover = st.selectbox("Selecione a matrícula para excluir:", [""] + list(st.session_state['usuarios_db'].keys()))
        if st.button("Excluir Usuário Selecionado", use_container_width=True):
            if mat_remover:
                if mat_remover == st.session_state['usuario_logado'].get('matricula'):
                    st.error("Você não pode excluir sua própria conta ativa.")
                else:
                    del st.session_state['usuarios_db'][mat_remover]
                    st.success("Usuário removido!")
                    st.rerun()

# ==============================================================================
# TELA 2: VISÃO GERAL DA FÁBRICA
# ==============================================================================
elif pagina_selecionada == "🌐 Visão Geral Fábrica":
    st.markdown('<p class="main-header">🌐 Central de Operações da Fábrica</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Acompanhe as ordens abertas, em atendimento técnico e o histórico com relatórios de fechamento.</p>', unsafe_allow_html=True)

    tab_inj, tab_mont, tab_emb = st.tabs(["🏢 Injetora Plástica", "🏢 Linha de Montagem", "🏢 Embalagem & Selagem"])

    def render_colunas_setor(setor_nome):
        col_ab, col_and, col_res = st.columns(3, gap="medium")
        
        # 1. Abertas
        with col_ab:
            st.markdown(f"##### 🔴 Abertas / Paradas")
            os_ab = [o for o in st.session_state['lista_os'] if o['setor'] == setor_nome]
            if os_ab:
                for item in os_ab:
                    with st.container(border=True):
                        st.markdown(f"**{item['id']}** — {item['maquina']}")
                        st.caption(f"⚠️ {item['defeito']}\n\n👤 Aberto por: {item.get('autor_abertura','N/D')}")
                        if st.button(f"▶️ Iniciar Atendimento", key=f"fab_in_{setor_nome}_{item['id']}", use_container_width=True):
                            if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                                os_and = item.copy()
                                os_and["hora_inicio"] = datetime.now().strftime('%H:%M')
                                os_and["mecanico_responsavel"] = st.session_state['usuario_logado']['nome']
                                st.session_state['em_andamento_os'].insert(0, os_and)
                                st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != item['id']]
                                st.rerun()
                            else:
                                st.warning("⚠️ Faça login como **Mecânico** ou **Administrador**.")
            else:
                st.info("Nenhuma OS aberta.")

        # 2. Em Andamento (Com campo obrigatório de relatório)
        with col_and:
            st.markdown(f"##### ⚙️ Em Atendimento")
            os_and = [o for o in st.session_state['em_andamento_os'] if o['setor'] == setor_nome]
            if os_and:
                for item in os_and:
                    with st.container(border=True):
                        st.markdown(f"**{item['id']}** — {item['maquina']}")
                        st.caption(f"🛠️ {item['defeito']}\n\n👤 Técnico: {item.get('mecanico_responsavel','Técnico')}")
                        
                        relatorio_input = st.text_area(
                            "Relatório Técnico de Fechamento:", 
                            placeholder="Descreva a solução aplicada...", 
                            key=f"rel_fab_{setor_nome}_{item['id']}", 
                            height=80
                        )
                        
                        if st.button(f"✅ Concluir OS", key=f"fab_fin_{setor_nome}_{item['id']}", use_container_width=True):
                            if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                                if not relatorio_input.strip():
                                    st.error("⚠️ O relatório técnico é obrigatório para fechar a OS.")
                                else:
                                    os_conc = item.copy()
                                    os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M')
                                    os_conc["status"] = "Concluída"
                                    os_conc["relatorio_fechamento"] = relatorio_input
                                    st.session_state['historico_os'].insert(0, os_conc)
                                    st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != item['id']]
                                    st.rerun()
                            else:
                                st.warning("⚠️ Restrito a Mecânicos/Administradores logados.")
            else:
                st.info("Nenhum atendimento em curso.")

        # 3. Concluídas (Mostrando quem fechou e o relatório)
        with col_res:
            st.markdown(f"##### ✅ Concluídas")
            os_res = [o for o in st.session_state['historico_os'] if o['setor'] == setor_nome]
            if os_res:
                for item in os_res:
                    with st.container(border=True):
                        st.markdown(f"**{item['id']}** — {item['maquina']}")
                        st.markdown(f"**Defeito:** {item['defeito']}")
                        st.markdown(f"🛠️ **Mecânico:** `{item.get('mecanico_responsavel','N/D')}`")
                        st.markdown(f"📝 **Relatório:** _{item.get('relatorio_fechamento','Sem relatório')}_")
                        
                        if st.button(f"🔄 Reabrir OS", key=f"fab_re_{setor_nome}_{item['id']}", use_container_width=True):
                            if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                                os_reab = {
                                    "id": item["id"], "setor": item["setor"], "maquina": item["maquina"],
                                    "defeito": item["defeito"], "prioridade": item["prioridade"],
                                    "hora_abertura": datetime.now().strftime('%H:%M'),
                                    "autor_abertura": f"Reaberto por {st.session_state['usuario_logado']['nome']}"
                                }
                                st.session_state['lista_os'].insert(0, os_reab)
                                st.session_state['historico_os'] = [o for o in st.session_state['historico_os'] if o['id'] != item['id']]
                                st.rerun()
                            else:
                                st.warning("⚠️ Apenas Mecânicos/Administradores podem reabrir.")
            else:
                st.info("Sem histórico.")

    with tab_inj:
        render_colunas_setor("Injetora Plástica")
    with tab_mont:
        render_colunas_setor("Linha de Montagem")
    with tab_emb:
        render_colunas_setor("Embalagem & Selagem")

# ==============================================================================
# TELA 3: PAINEL DA MÁQUINA INDIVIDUAL
# ==============================================================================
else:
    st.markdown(f'<p class="main-header">⚙️ Setor: {setor_selecionado} — {maquina_selecionada}</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Painel de telemetria preditiva, preventiva e gestão de ordens específicas da máquina selecionada.</p>', unsafe_allow_html=True)

    tab_tel, tab_prev, tab_ab, tab_and, tab_hist = st.tabs([
        "📊 Telemetria OEE", "🛠️ Plano Preventivo", "📌 OSs Abertas", "⚙️ Em Atendimento", "✅ Histórico"
    ])

    with tab_tel:
        col_c1, col_c2, col_c3 = st.columns(3)
        temp_canhao = col_c1.slider("Temperatura do Canhão (°C)", 180.0, 260.0, 220.0)
        temp_molde = col_c2.slider("Temperatura do Molde (°C)", 15.0, 70.0, 32.0)
        pressao_recalque = col_c3.slider("Pressão de Recalque (bar)", 50.0, 160.0, 95.0)
        
        risco = min(100.0, (pressao_recalque * temp_molde) / 80)
        disp, perf, qual = max(60, int(98 - (risco * 0.3))), max(70, int(95 - (risco * 0.2))), max(80, int(99 - (risco * 0.4)))
        oee = int((disp/100) * (perf/100) * (qual/100) * 100)

        st.markdown("##### 📈 Indicadores de Desempenho Global (OEE)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Disponibilidade", f"{disp}%")
        m2.metric("Performance", f"{perf}%")
        m3.metric("Qualidade", f"{qual}%")
        m4.metric("OEE Geral", f"{oee}%")

        st.progress(int(risco))
        if risco < 35:
            st.success("🟢 Condição Operacional Estável")
        elif 35 <= risco < 65:
            st.warning("🟡 Atenção: Desvio nos parâmetros monitorados")
        else:
            st.error("🔴 Alerta Crítico: Risco Elevado de Parada")

    with tab_prev:
        tag = maquina_selecionada.split(' ')[0]
        st.markdown(f"**Tempo Estimado de Parada Preventiva:** 2 horas")
        c_prev1, c_prev2, c_prev3 = st.columns(3)
        with c_prev1:
            st.markdown("**🔩 Mecânica**")
            st.write(f"• Bujões {tag}")
            st.write("• Anel Guia Principal")
        with c_prev2:
            st.markdown("**💨 Pneumática**")
            st.write(f"• Elemento Filtrante {tag}")
            st.write("• Válvula Solenóide 5/2")
        with c_prev3:
            st.markdown("**⚡ Elétrica**")
            st.write("• Sensor Indutivo M12")
            st.write("• Cartucho Aquecedor")

    with tab_ab:
        os_ab_maq = [o for o in st.session_state['lista_os'] if o['maquina'] == maquina_selecionada]
        if os_ab_maq:
            for item in os_ab_maq:
                with st.container(border=True):
                    st.markdown(f"**{item['id']}** — {item['defeito']}")
                    st.caption(f"👤 Aberto por: {item.get('autor_abertura','N/D')}")
                    if st.button("▶️ Iniciar Atendimento", key=f"p_in_{item['id']}"):
                        if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                            os_and = item.copy()
                            os_and["hora_inicio"] = datetime.now().strftime('%H:%M')
                            os_and["mecanico_responsavel"] = st.session_state['usuario_logado']['nome']
                            st.session_state['em_andamento_os'].insert(0, os_and)
                            st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != item['id']]
                            st.rerun()
                        else:
                            st.warning("⚠️ Restrito a Mecânicos/Administradores.")
        else:
            st.success("Nenhuma OS aberta para esta máquina.")

    with tab_and:
        os_and_maq = [o for o in st.session_state['em_andamento_os'] if o['maquina'] == maquina_selecionada]
        if os_and_maq:
            for item in os_and_maq:
                with st.container(border=True):
                    st.markdown(f"**{item['id']}** — {item['defeito']}")
                    st.caption(f"🛠️ Técnico Responsável: {item.get('mecanico_responsavel','')}")
                    
                    rel_p = st.text_area("Relatório Técnico de Fechamento:", placeholder="O que foi reparado?", key=f"p_rel_{item['id']}", height=80)
                    
                    if st.button("✅ Finalizar OS", key=f"p_fin_{item['id']}"):
                        if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                            if not rel_p.strip():
                                st.error("⚠️ Preencha o relatório técnico!")
                            else:
                                os_conc = item.copy()
                                os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M')
                                os_conc["status"] = "Concluída"
                                os_conc["relatorio_fechamento"] = rel_p
                                st.session_state['historico_os'].insert(0, os_conc)
                                st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != item['id']]
                                st.rerun()
                        else:
                            st.warning("⚠️ Restrito a Mecânicos/Administradores.")
        else:
            st.info("Nenhuma manutenção em andamento.")

    with tab_hist:
        os_res_maq = [o for o in st.session_state['historico_os'] if o['maquina'] == maquina_selecionada]
        if os_res_maq:
            for item in os_res_maq:
                with st.container(border=True):
                    st.markdown(f"**{item['id']}** — {item['defeito']}")
                    st.markdown(f"🛠️ **Mecânico:** `{item.get('mecanico_responsavel','')}`")
                    st.markdown(f"📝 **Relatório:** _{item.get('relatorio_fechamento','Sem relatório')}_")
        else:
            st.info("Sem histórico registrado para esta máquina.")
