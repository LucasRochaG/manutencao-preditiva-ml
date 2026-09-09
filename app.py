import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="MANTIS 4.0 - Inteligência em Manutenção",
    page_icon="💉",
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
# Perfis possíveis: "Administrador", "Mecânico", "Operador"
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
        {"id": "OS-0998", "setor": "Injetora Plástica", "maquina": "INJ-01 (Injetora 1)", "defeito": "Troca de resistência Z2", "prioridade": "Média", "hora_abertura": "06:20", "hora_inicio": "06:25", "hora_conclusao": "07:10", "status": "Concluída", "mecanico_responsavel": "Roberto Mecânico", "relatorio_fechamento": "Substituído o cartucho de resistência queimado e testado o circuito."}
    ]

# Estilo CSS Personalizado
st.markdown("""
<style>
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 8px; }
    .iot-card-mini {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 6px 12px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.75rem;
    }
    .badge-adm { background-color: #dc2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
    .badge-mec { background-color: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
    .badge-op  { background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL: LOGIN DISCRETO & NAVEGAÇÃO
# ==============================================================================
st.sidebar.caption("🤖 PROJETO INDUSTRIAL (MOBILE PWA)")
st.sidebar.markdown("### 🦾 MANTIS 4.0")
st.sidebar.caption("Maintenance & Machine Intelligence System")
st.sidebar.markdown("---")

# Módulo de Login Discreto
if not st.session_state['autenticado']:
    with st.sidebar.expander("🔐 Identificação / Login"):
        mat_input = st.text_input("Matrícula:", key="mat_discreto")
        senha_input = st.text_input("Senha:", type="password", key="senha_discreto")
        if st.button("Entrar", use_container_width=True):
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
    if usuario['perfil'] == "Administrador":
        badge_classe = "badge-adm"
    elif usuario['perfil'] == "Mecânico":
        badge_classe = "badge-mec"
    else:
        badge_classe = "badge-op"

    st.sidebar.markdown(f"👤 **{usuario['nome']}**")
    st.sidebar.markdown(f"Perfil: <span class='{badge_classe}'>{usuario['perfil']}</span>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state['autenticado'] = False
        st.session_state['usuario_logado'] = {}
        st.rerun()

st.sidebar.markdown("---")

# NAVEGAÇÃO ENTRE TELAS (Painel, Fábrica e Gestão de Usuários se for ADM)
paineis_disponiveis = ["🖥️ Painel", "🌐 Fábrica"]
if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] == "Administrador":
    paineis_disponiveis.append("👥 Cadastros (ADM)")

if 'aba_selecionada' not in st.session_state:
    st.session_state['aba_selecionada'] = "🖥️ Painel"

st.session_state['aba_selecionada'] = st.sidebar.radio("Navegação:", paineis_disponiveis, index=paineis_disponiveis.index(st.session_state['aba_selecionada']) if st.session_state['aba_selecionada'] in paineis_disponiveis else 0)

st.sidebar.markdown("---")

# SELEÇÃO DE MÁQUINA (NO PAINEL)
if st.session_state['aba_selecionada'] == "🖥️ Painel":
    setor_selecionado = st.sidebar.selectbox("Setor:", ["Injetora Plástica", "Linha de Montagem", "Embalagem & Selagem"])
    maquinas_disponiveis = MAQUINAS_POR_SETOR[setor_selecionado]
    maquina_selecionada = st.sidebar.selectbox("Máquina:", maquinas_disponiveis)
    st.sidebar.markdown("---")
else:
    setor_selecionado = "Injetora Plástica"
    maquina_selecionada = MAQUINAS_POR_SETOR["Injetora Plástica"][0]

# ABERTURA RÁPIDA DE OS (QUALQUER UM PODE ABRIR)
st.sidebar.markdown("##### 📝 Nova OS")
os_setor = st.sidebar.selectbox("Setor Destino:", ["Injetora Plástica", "Linha de Montagem", "Embalagem & Selagem"], key="os_setor_select")
maquinas_form_dinamicas = MAQUINAS_POR_SETOR[os_setor]

with st.sidebar.form(key="form_os_simplificada", clear_on_submit=True):
    os_maquina = st.selectbox("Máquina:", maquinas_form_dinamicas)
    os_defeito = st.text_area("Problema:", placeholder="Descreva o problema...", height=60)
    os_prioridade = st.selectbox("Prioridade:", ["Alta", "Média", "Baixa"])
    submit_os = st.form_submit_button("🚀 Abrir OS")

if submit_os:
    if os_defeito.strip() != "":
        autor_nome = st.session_state['usuario_logado']['nome'] if st.session_state['autenticado'] else "Usuário Anônimo"
        nova_os = {
            "id": f"OS-{datetime.now().strftime('%M%S')}",
            "setor": os_setor,
            "maquina": os_maquina,
            "defeito": os_defeito,
            "prioridade": os_prioridade,
            "hora_abertura": datetime.now().strftime('%H:%M'),
            "autor_abertura": autor_nome
        }
        st.session_state['lista_os'].insert(0, nova_os)
        st.sidebar.success(f"OS Criada: {nova_os['id']}")
        st.rerun()
    else:
        st.sidebar.error("Informe o problema.")

# Dados de Preventiva
def get_preventiva_dados(maquina_nome):
    tag = maquina_nome.split(' ')[0]
    return {
        "tempo": "2 horas",
        "pecas_por_tipo": {
            "🔩 Mecânica": [f"Bujões {tag}", "Anel Guia"],
            "💨 Pneumática": [f"Filtro {tag}", "Válvula Solenóide"],
            "⚡ Elétrica": ["Sensor M12", "Cartucho Aquecedor"]
        }
    }

info_prev = get_preventiva_dados(maquina_selecionada)

# ==============================================================================
# TELA 1: GESTÃO DE CADASTROS (EXCLUSIVO PARA ADMINISTRADOR)
# ==============================================================================
if st.session_state['aba_selecionada'] == "👥 Cadastros (ADM)":
    st.markdown("### 👥 Painel Administrativo — Gestão de Funcionários")
    st.caption("Cadastre, remova ou edite os acessos do sistema (Operadores, Mecânicos e Administradores).")
    
    col_cad1, col_cad2 = st.columns(2)
    
    with col_cad1:
        st.markdown("##### ➕ Novo Cadastro")
        with st.form("form_adm_novo_usuario"):
            mat_novo = st.text_input("Matrícula (Ex: M005, ADM02, OP105):")
            nome_novo = st.text_input("Nome Completo:")
            perfil_novo = st.selectbox("Perfil de Acesso:", ["Mecânico", "Administrador", "Operador"])
            senha_nova = st.text_input("Senha de Acesso:", type="password")
            btn_salvar_adm = st.form_submit_button("Cadastrar Funcionário", use_container_width=True)
            
            if btn_salvar_adm:
                if mat_novo.strip() and nome_novo.strip() and senha_nova.strip():
                    if mat_novo.strip() in st.session_state['usuarios_db']:
                        st.error("Esta matrícula já está cadastrada!")
                    else:
                        st.session_state['usuarios_db'][mat_novo.strip()] = {
                            "nome": nome_novo.strip(),
                            "perfil": perfil_novo,
                            "senha": senha_nova.strip()
                        }
                        st.success(f"Funcionário {nome_novo} cadastrado com sucesso!")
                        st.rerun()
                else:
                    st.warning("Preencha todos os campos obrigatórios.")
                    
    with col_cad2:
        st.markdown("##### 📋 Usuários Atualmente Cadastrados")
        df_usuarios = pd.DataFrame([
            {"Matrícula": k, "Nome": v["nome"], "Perfil": v["perfil"]} 
            for k, v in st.session_state['usuarios_db'].items()
        ])
        st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
        
        # Opção de exclusão
        mat_para_remover = st.selectbox("Selecionar Matrícula para Remover:", [""] + list(st.session_state['usuarios_db'].keys()))
        if st.button("🗑️ Remover Usuário Selecionado", use_container_width=True):
            if mat_para_remover:
                if mat_para_remover == st.session_state['usuario_logado'].get('matricula'):
                    st.error("Você não pode remover seu próprio usuário ativo!")
                else:
                    del st.session_state['usuarios_db'][mat_para_remover]
                    st.success("Usuário removido com sucesso!")
                    st.rerun()

# ==============================================================================
# TELA 2: FÁBRICA (VISÃO GERAL)
# ==============================================================================
elif st.session_state['aba_selecionada'] == "🌐 Fábrica":
    st.markdown("### 🌐 Visão Geral Fábrica — MANTIS 4.0")
    
    df_os_todas = pd.DataFrame(st.session_state['lista_os'] + st.session_state['em_andamento_os'] + st.session_state['historico_os'])
    if not df_os_todas.empty:
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            df_counts = df_os_todas.groupby("setor").size().reset_index(name="Total de OSs")
            st.markdown("##### 📊 Volume de Demandas por Setor Fabril")
            st.bar_chart(df_counts.set_index("setor"))
        with col_g2:
            st.metric("Total de OSs Registradas", len(df_os_todas))
            st.metric("Em Atendimento Agora", len(st.session_state['em_andamento_os']))
            st.metric("Taxa de Resolução", f"{int((len(st.session_state['historico_os'])/len(df_os_todas))*100)}%")

    st.markdown("---")

    tab_inj, tab_mont, tab_emb = st.tabs(["🏢 Injetora Plástica", "🏢 Linha de Montagem", "🏢 Embalagem & Selagem"])

    def render_tabela_setor(setor_nome):
        col_ab, col_and, col_res = st.columns(3)
        
        # OS ABERTAS
        with col_ab:
            os_ab = [o for o in st.session_state['lista_os'] if o['setor'] == setor_nome]
            st.markdown(f"##### 🔴 Paradas / Abertas ({len(os_ab)})")
            if os_ab:
                for item in os_ab:
                    st.markdown(f"**{item['id']}** | {item['maquina']}")
                    st.caption(f"⚠️ {item['defeito']} | Por: {item.get('autor_abertura','N/D')}")
                    
                    if st.button(f"▶️ Iniciar {item['id']}", key=f"f_in_{setor_nome}_{item['id']}", use_container_width=True):
                        if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                            os_and = item.copy()
                            os_and["hora_inicio"] = datetime.now().strftime('%H:%M')
                            os_and["mecanico_responsavel"] = st.session_state['usuario_logado']['nome']
                            st.session_state['em_andamento_os'].insert(0, os_and)
                            st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != item['id']]
                            st.rerun()
                        else:
                            st.warning("⚠️ Apenas **Mecânicos ou Administradores** podem iniciar OSs!")
                    st.divider()
            else:
                st.caption("Nenhuma ordem aberta.")

        # OS EM ANDAMENTO (COM RELATÓRIO DE FECHAMENTO)
        with col_and:
            os_and = [o for o in st.session_state['em_andamento_os'] if o['setor'] == setor_nome]
            st.markdown(f"##### ⚙️ Em Atendimento ({len(os_and)})")
            if os_and:
                for item in os_and:
                    st.markdown(f"**{item['id']}** | {item['maquina']}")
                    st.caption(f"🛠️ {item['defeito']} | Resp: {item.get('mecanico_responsavel','Técnico')}")
                    
                    # Campo de relatório obrigatório para fechamento
                    relatorio_text = st.text_area(f"Relatório Técnico ({item['id']}):", placeholder="O que foi feito para corrigir?", key=f"rel_{setor_nome}_{item['id']}", height=70)
                    
                    if st.button(f"✅ Finalizar {item['id']}", key=f"f_fin_{setor_nome}_{item['id']}", use_container_width=True):
                        if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                            if relatorio_text.strip() == "":
                                st.error("⚠️ Preencha o relatório técnico de fechamento antes de concluir a OS!")
                            else:
                                os_conc = item.copy()
                                os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M')
                                os_conc["status"] = "Concluída"
                                os_conc["relatorio_fechamento"] = relatorio_text
                                st.session_state['historico_os'].insert(0, os_conc)
                                st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != item['id']]
                                st.rerun()
                        else:
                            st.warning("⚠️ Apenas **Mecânicos ou Administradores** podem fechar OSs!")
                    st.divider()
            else:
                st.caption("Nenhum atendimento.")

        # OS RESOLVIDAS (MOSTRANDO QUEM FECHOU E O RELATÓRIO)
        with col_res:
            os_res = [o for o in st.session_state['historico_os'] if o['setor'] == setor_nome]
            st.markdown(f"##### ✅ Concluídas ({len(os_res)})")
            if os_res:
                for item in os_res:
                    st.markdown(f"**{item['id']}** | {item['maquina']}")
                    st.caption(f"✔️ {item['defeito']}\n\n🛠️ **Mecânico Responsável:** {item.get('mecanico_responsavel','')}\n📝 **Relatório:** {item.get('relatorio_fechamento','Sem relatório')}")
                    
                    if st.button(f"🔄 Reabrir {item['id']}", key=f"f_re_{setor_nome}_{item['id']}", use_container_width=True):
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
                            st.warning("⚠️ Apenas **Mecânicos ou Administradores** podem reabrir.")
                    st.divider()
            else:
                st.caption("Sem histórico recente.")

    with tab_inj:
        render_tabela_setor("Injetora Plástica")
    with tab_mont:
        render_tabela_setor("Linha de Montagem")
    with tab_emb:
        render_tabela_setor("Embalagem & Selagem")

# ==============================================================================
# TELA 3: PAINEL DA MÁQUINA INDIVIDUAL
# ==============================================================================
else:
    st.markdown(f"### 🏢 Setor: **{setor_selecionado}** | ⚙️ **{maquina_selecionada}**")

    tag_maquina_atual = maquina_selecionada.split(' ')[0]
    st.markdown(f"""
    <div class="iot-card-mini">
        <div style="color: #64748b; font-family: monospace;">
            📡 <b>MANTIS IoT:</b> Conexão com o <b>CLP</b> pendente (Alvo: <b>{tag_maquina_atual}</b>)
        </div>
        <div style="background-color: #0284c7; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold;">
            ⏳ Sem Sincronização <b>CLP</b> (Modo Simulação)
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_principal, tab_preventiva, tab_abertas, tab_andamento, tab_historico = st.tabs([
        "📊 Telemetria", "🛠️ Plano Preventivo", "📌 OSs Abertas", "⚙️ Em Atendimento", "✅ Histórico"
    ])

    with tab_principal:
        if setor_selecionado == "Injetora Plástica":
            col_c1, col_c2, col_c3 = st.columns(3)
            temp_canhao = col_c1.slider("Temperatura do Canhão (°C)", 180.0, 260.0, 220.0)
            temp_molde = col_c2.slider("Temperatura do Molde (°C)", 15.0, 70.0, 32.0)
            pressao_recalque = col_c3.slider("Pressão de Recalque (bar)", 50.0, 160.0, 95.0)
            risco = min(100.0, (pressao_recalque * temp_molde) / 80)
        else:
            col_c1, col_c2 = st.columns(2)
            param1 = col_c1.slider("Pressão da Linha (bar)", 4.0, 10.0, 6.5)
            param2 = col_c2.slider("Velocidade do Ciclo (peças/min)", 100, 300, 240)
            risco = 15.0 if param1 >= 5.5 else 75.0

        disp = max(60, int(98 - (risco * 0.3)))
        perf = max(70, int(95 - (risco * 0.2)))
        qual = max(80, int(99 - (risco * 0.4)))
        oee = int((disp/100) * (perf/100) * (qual/100) * 100)

        st.markdown("##### 📉 Indicadores de Desempenho Operacional")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Disponibilidade da Máquina", f"{disp}%")
        m2.metric("Performance de Produção", f"{perf}%")
        m3.metric("Qualidade do Produto", f"{qual}%")
        m4.metric("Eficiência Global (OEE)", f"{oee}%")

        st.progress(int(risco))
        if risco < 35:
            st.success("🟢 Operação Normal — Preditiva OK")
        elif 35 <= risco < 65:
            st.warning("🟡 Modo de Atenção — Desvio Detectado")
        else:
            st.error("🔴 Risco Crítico — Alta Probabilidade de Parada")

        st.markdown("---")
        st.markdown("##### 📈 Telemetria em Tempo Real (Últimas medições)")
        df_chart = pd.DataFrame({
            "Pressão do Sistema (bar)": np.random.normal(loc=100, scale=2, size=20),
            "Temperatura Interna (°C)": np.random.normal(loc=220, scale=5, size=20)
        })
        st.line_chart(df_chart)

    with tab_preventiva:
        st.caption(f"Tempo estimado de parada programada: {info_prev['tempo']}")
        cols_cat = st.columns(3)
        for idx, (cat, pecas) in enumerate(info_prev['pecas_por_tipo'].items()):
            with cols_cat[idx]:
                st.markdown(f"**{cat}**")
                for p in pecas:
                    st.write(f"• {p}")

    with tab_abertas:
        os_ab_maquina = [o for o in st.session_state['lista_os'] if o['maquina'] == maquina_selecionada]
        if os_ab_maquina:
            for item in os_ab_maquina:
                st.write(f"📌 **{item['id']}** - **Problema:** {item['defeito']} | **Por:** {item.get('autor_abertura','N/D')}")
                
                if st.button(f"▶️ Iniciar Atendimento {item['id']}", key=f"p_in_{item['id']}"):
                    if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                        os_and = item.copy()
                        os_and["hora_inicio"] = datetime.now().strftime('%H:%M')
                        os_and["mecanico_responsavel"] = st.session_state['usuario_logado']['nome']
                        st.session_state['em_andamento_os'].insert(0, os_and)
                        st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != item['id']]
                        st.rerun()
                    else:
                        st.warning("⚠️ Restrito: Apenas **Mecânicos ou Administradores** podem iniciar.")
                st.divider()
        else:
            st.success(f"Nenhuma ordem aberta para a **{maquina_selecionada}**.")

    with tab_andamento:
        os_and_maquina = [o for o in st.session_state['em_andamento_os'] if o['maquina'] == maquina_selecionada]
        if os_and_maquina:
            for item in os_and_maquina:
                st.write(f"🛠️ **{item['id']}** - **Problema:** {item['defeito']} | **Técnico:** {item.get('mecanico_responsavel','')}")
                
                relatorio_text_p = st.text_area(f"Relatório Técnico ({item['id']}):", placeholder="O que foi feito?", key=f"p_rel_{item['id']}", height=70)
                
                if st.button(f"✅ Finalizar OS {item['id']}", key=f"p_fin_{item['id']}"):
                    if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                        if relatorio_text_p.strip() == "":
                            st.error("⚠️ Preencha o relatório técnico de fechamento!")
                        else:
                            os_conc = item.copy()
                            os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M')
                            os_conc["status"] = "Concluída"
                            os_conc["relatorio_fechamento"] = relatorio_text_p
                            st.session_state['historico_os'].insert(0, os_conc)
                            st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != item['id']]
                            st.rerun()
                    else:
                        st.warning("⚠️ Restrito: Apenas **Mecânicos ou Administradores** podem concluir.")
                st.divider()
        else:
            st.info(f"Nenhuma manutenção em andamento na **{maquina_selecionada}**.")

    with tab_historico:
        os_res_maquina = [o for o in st.session_state['historico_os'] if o['maquina'] == maquina_selecionada]
        if os_res_maquina:
            for item in os_res_maquina:
                st.write(f"✅ **{item['id']}** - **Solucionado:** {item['defeito']}\n\n🛠️ **Mecânico:** {item.get('mecanico_responsavel','')}\n📝 **Relatório:** {item.get('relatorio_fechamento','Sem relatório')}")
                st.divider()
        else:
            st.caption(f"Nenhum histórico recente para a **{maquina_selecionada}**.")
