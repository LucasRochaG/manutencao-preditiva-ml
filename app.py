import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="MANTIS 4.0 - Inteligência em Manutenção Industrial",
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
        {"id": "OS-1001", "setor": "Injetora Plástica", "maquina": "INJ-01 (Injetora 1)", "defeito": "Vazamento severo de óleo no cilindro hidráulico principal", "prioridade": "Alta", "hora_abertura": "08:15", "autor_abertura": "João Operador"},
        {"id": "OS-1002", "setor": "Injetora Plástica", "maquina": "INJ-05 (Injetora 5)", "defeito": "Ruído excessivo e vibração anormal no exaustor térmico", "prioridade": "Média", "hora_abertura": "09:30", "autor_abertura": "João Operador"}
    ]

if 'em_andamento_os' not in st.session_state:
    st.session_state['em_andamento_os'] = [
        {"id": "OS-1003", "setor": "Linha de Montagem", "maquina": "MONT-02 (Montagem 2)", "defeito": "Ajuste milimétrico necessário na garra pneumática do robô", "prioridade": "Baixa", "hora_abertura": "10:05", "hora_inicio": "10:20", "mecanico_responsavel": "Roberto Mecânico"}
    ]

if 'historico_os' not in st.session_state:
    st.session_state['historico_os'] = [
        {"id": "OS-0998", "setor": "Injetora Plástica", "maquina": "INJ-01 (Injetora 1)", "defeito": "Troca preventiva de resistência da Zona 2", "prioridade": "Média", "hora_abertura": "06:20", "hora_inicio": "06:25", "hora_conclusao": "07:10", "status": "Concluída", "mecanico_responsavel": "Roberto Mecânico", "relatorio_fechamento": "Substituído o cartucho de resistência queimado, aferido o termopar e testado o circuito de potência com sucesso."}
    ]

if 'aba_ativa' not in st.session_state:
    st.session_state['aba_ativa'] = "🖥️ Painel"

# ==============================================================================
# ESTILO CSS PROFISSIONAL (DESIGN SYSTEM INDUSTRIAL)
# ==============================================================================
st.markdown("""
<style>
    .industrial-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-left: 4px solid #3b82f6;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .card-critical { border-left-color: #ef4444 !important; }
    .card-warning { border-left-color: #f59e0b !important; }
    .card-success { border-left-color: #10b981 !important; }

    .badge-adm { background-color: #dc2626; color: white; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.5px; }
    .badge-mec { background-color: #10b981; color: white; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.5px; }
    .badge-op  { background-color: #3b82f6; color: white; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.5px; }

    .iot-banner-waiting {
        background: #1e293b;
        border: 1px dashed #64748b;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #94a3b8;
    }
    .iot-banner-online {
        background: linear-gradient(90deg, #0f172a 0%, #064e3b 100%);
        border: 1px solid #059669;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL: AUTENTICAÇÃO E NAVEGAÇÃO
# ==============================================================================
st.sidebar.caption("🤖 ARQUITETURA INDUSTRIAL 4.0 (PWA)")
st.sidebar.markdown("### 🦾 MANTIS SYSTEM")
st.sidebar.caption("Maintenance & Machine Intelligence")
st.sidebar.markdown("---")

# Seção de Login na Sidebar
if not st.session_state['autenticado']:
    with st.sidebar.expander("🔐 Credenciais de Acesso", expanded=True):
        mat_input = st.text_input("Matrícula ID:", key="mat_discreto", placeholder="Ex: ADM01, M001")
        senha_input = st.text_input("Senha de Acesso:", type="password", key="senha_discreto")
        
        if st.button("Autenticar Sistema", use_container_width=True):
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
                st.error("Matrícula não cadastrada.")
                # Dica automática para facilitar os testes
                matriculas_disponiveis = ", ".join(st.session_state['usuarios_db'].keys())
                st.info(f"💡 **Dica de Acesso:** Utilize uma das matrículas válidas: `{matriculas_disponiveis}` (Senha padrão: `123`)")
else:
    usuario = st.session_state['usuario_logado']
    if usuario['perfil'] == "Administrador":
        badge_classe = "badge-adm"
    elif usuario['perfil'] == "Mecânico":
        badge_classe = "badge-mec"
    else:
        badge_classe = "badge-op"

    st.sidebar.markdown(f"👤 **{usuario['nome']}**")
    st.sidebar.markdown(f"Nível: <span class='{badge_classe}'>{usuario['perfil']}</span>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Encerrar Sessão", use_container_width=True):
        st.session_state['autenticado'] = False
        st.session_state['usuario_logado'] = {}
        st.rerun()

st.sidebar.markdown("---")

# ------------------------------------------------------------------------------
# BOTÕES DE NAVEGAÇÃO LADO A LADO COM DESTAQUE NO ATIVO
# ------------------------------------------------------------------------------
col_nav1, col_nav2 = st.sidebar.columns(2)

with col_nav1:
    tipo_btn_1 = "primary" if st.session_state['aba_ativa'] == "🖥️ Painel" else "secondary"
    if st.button("🖥️ Painel", use_container_width=True, type=tipo_btn_1):
        st.session_state['aba_ativa'] = "🖥️ Painel"
        st.rerun()

with col_nav2:
    tipo_btn_2 = "primary" if st.session_state['aba_ativa'] == "🌐 Fábrica" else "secondary"
    if st.button("🌐 Fábrica", use_container_width=True, type=tipo_btn_2):
        st.session_state['aba_ativa'] = "🌐 Fábrica"
        st.rerun()

# Aba exclusiva para Administradores
if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] == "Administrador":
    tipo_btn_adm = "primary" if st.session_state['aba_ativa'] == "👥 Cadastros (ADM)" else "secondary"
    if st.sidebar.button("👥 Gestão de Cadastros (ADM)", use_container_width=True, type=tipo_btn_adm):
        st.session_state['aba_ativa'] = "👥 Cadastros (ADM)"
        st.rerun()
else:
    if st.session_state['aba_ativa'] == "👥 Cadastros (ADM)":
        st.session_state['aba_ativa'] = "🖥️ Painel"

st.sidebar.markdown("---")

# SELEÇÃO DE MÁQUINA (ATIVA NO PAINEL)
if st.session_state['aba_ativa'] == "🖥️ Painel":
    setor_selecionado = st.sidebar.selectbox("Setor Industrial:", ["Injetora Plástica", "Linha de Montagem", "Embalagem & Selagem"])
    maquinas_disponiveis = MAQUINAS_POR_SETOR[setor_selecionado]
    maquina_selecionada = st.sidebar.selectbox("Ativo / Máquina:", maquinas_disponiveis)
    st.sidebar.markdown("---")
else:
    setor_selecionado = "Injetora Plástica"
    maquina_selecionada = MAQUINAS_POR_SETOR["Injetora Plástica"][0]

# MÓDULO DE ABERTURA RÁPIDA DE ORDEM DE SERVIÇO
st.sidebar.markdown("##### 📝 Abertura Rápida de Chamado (OS)")
os_setor = st.sidebar.selectbox("Setor de Destino:", ["Injetora Plástica", "Linha de Montagem", "Embalagem & Selagem"], key="os_setor_select")
maquinas_form_dinamicas = MAQUINAS_POR_SETOR[os_setor]

with st.sidebar.form(key="form_os_simplificada", clear_on_submit=True):
    os_maquina = st.selectbox("Selecione o Equipamento:", maquinas_form_dinamicas)
    os_defeito = st.text_area("Descrição Detalhada do Problema:", placeholder="Relate o defeito observado...", height=70)
    os_prioridade = st.selectbox("Grau de Prioridade:", ["Baixa", "Média", "Alta", "Crítica"])
    submit_os = st.form_submit_button("🚀 Emitir Ordem de Serviço")

if submit_os:
    if os_defeito.strip() != "":
        autor_nome = st.session_state['usuario_logado']['nome'] if st.session_state['autenticado'] else "Operador Anônimo"
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
        st.sidebar.success(f"OS emitida com sucesso: {nova_os['id']}")
        st.rerun()
    else:
        st.sidebar.error("A descrição do problema é obrigatória.")

# Dados dinâmicos de preventiva
def get_preventiva_dados(maquina_nome):
    tag = maquina_nome.split(' ')[0]
    return {
        "tempo": "2h 30min",
        "pecas_por_tipo": {
            "🔩 Mecânica Industrial": [f"Bujões e vedações {tag}", "Anel Guia do Cilindro", "Graxa de Alta Temperatura"],
            "💨 Sistema Pneumático": [f"Elemento Filtrante {tag}", "Válvula Solenóide 5/2 vias", "Mangueira PU 8mm"],
            "⚡ Automação & Elétrica": ["Sensor Indutivo M12", "Cartucho Aquecedor Cerâmico", "Bornes de Conexão Wago"]
        }
    }

info_prev = get_preventiva_dados(maquina_selecionada)

# ==============================================================================
# TELA 1: CADASTROS (EXCLUSIVO ADMINISTRADOR)
# ==============================================================================
if st.session_state['aba_ativa'] == "👥 Cadastros (ADM)":
    st.markdown("### 👥 Painel de Controle de Usuários e Acessos (ADM)")
    st.markdown("Gerenciamento centralizado de colaboradores autorizados a interagir com o sistema MANTIS 4.0.")
    st.markdown("---")
    
    col_cad1, col_cad2 = st.columns([1, 1], gap="large")
    
    with col_cad1:
        st.markdown("#### ➕ Cadastrar Novo Colaborador")
        with st.form("form_novo_user"):
            mat_c = st.text_input("Matrícula Funcional (Ex: M005, ADM02):")
            nome_c = st.text_input("Nome Completo do Funcionário:")
            perfil_c = st.selectbox("Perfil de Permissão:", ["Mecânico", "Administrador", "Operador"])
            senha_c = st.text_input("Senha de Acesso Inicial:", type="password")
            btn_cad = st.form_submit_button("💾 Salvar Novo Cadastro", use_container_width=True)
            
            if btn_cad:
                if mat_c.strip() and nome_c.strip() and senha_c.strip():
                    if mat_c.strip() in st.session_state['usuarios_db']:
                        st.error("Erro: Esta matrícula já está cadastrada no sistema.")
                    else:
                        st.session_state['usuarios_db'][mat_c.strip()] = {
                            "nome": nome_c.strip(),
                            "perfil": perfil_c,
                            "senha": senha_c.strip()
                        }
                        st.success(f"Colaborador {nome_c} cadastrado com sucesso!")
                        st.rerun()
                else:
                    st.warning("Preencha todos os campos obrigatórios.")
                    
    with col_cad2:
        st.markdown("#### 📋 Quadro de Colaboradores Ativos")
        df_u = pd.DataFrame([{"Matrícula": k, "Nome Completo": v["nome"], "Perfil de Acesso": v["perfil"]} for k, v in st.session_state['usuarios_db'].items()])
        st.dataframe(df_u, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### 🗑️ Desativar / Remover Colaborador")
        mat_del = st.selectbox("Selecione a Matrícula para Remover:", [""] + list(st.session_state['usuarios_db'].keys()))
        if st.button("⚠️ Excluir Colaborador Selecionado", use_container_width=True):
            if mat_del:
                if mat_del == st.session_state['usuario_logado'].get('matricula'):
                    st.error("Ação negada: Você não pode excluir sua própria conta enquanto estiver logado.")
                else:
                    del st.session_state['usuarios_db'][mat_del]
                    st.success("Colaborador removido do banco de dados!")
                    st.rerun()

# ==============================================================================
# TELA 2: VISÃO GERAL DA FÁBRICA
# ==============================================================================
elif st.session_state['aba_ativa'] == "🌐 Fábrica":
    st.markdown("### 🌐 Centro de Controle e Gestão da Fábrica")
    st.markdown("Acompanhamento multi-setorial de Ordens de Serviço, filas de atendimento e relatórios técnicos.")
    st.markdown("---")
    
    df_os_todas = pd.DataFrame(st.session_state['lista_os'] + st.session_state['em_andamento_os'] + st.session_state['historico_os'])
    if not df_os_todas.empty:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total de Ordens Registradas", len(df_os_todas))
        col_m2.metric("Chamados em Aberto", len(st.session_state['lista_os']))
        col_m3.metric("Em Manutenção Ativa", len(st.session_state['em_andamento_os']))
        col_m4.metric("Concluídas com Sucesso", len(st.session_state['historico_os']))
        st.markdown("---")

    tab_inj, tab_mont, tab_emb = st.tabs(["🏢 Setor: Injetora Plástica", "🏢 Setor: Linha de Montagem", "🏢 Setor: Embalagem & Selagem"])

    def render_tabela_setor(setor_nome):
        col_ab, col_and, col_res = st.columns(3, gap="medium")
        
        with col_ab:
            os_ab = [o for o in st.session_state['lista_os'] if o['setor'] == setor_nome]
            st.markdown(f"#### 🔴 Abertas ({len(os_ab)})")
            if os_ab:
                for item in os_ab:
                    st.markdown(f"""
                    <div class="industrial-card card-critical">
                        <b>{item['id']}</b> | {item['maquina']}<br>
                        <small>⚠️ <b>Problema:</b> {item['defeito']}</small><br>
                        <small>👤 <b>Solicitante:</b> {item.get('autor_abertura','N/D')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"▶️ Iniciar Atendimento {item['id']}", key=f"f_in_{setor_nome}_{item['id']}", use_container_width=True):
                        if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                            os_and = item.copy()
                            os_and["hora_inicio"] = datetime.now().strftime('%H:%M')
                            os_and["mecanico_responsavel"] = st.session_state['usuario_logado']['nome']
                            st.session_state['em_andamento_os'].insert(0, os_and)
                            st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != item['id']]
                            st.rerun()
                        else:
                            st.warning("⚠️ Restrito: Faça login como **Mecânico** ou **Administrador**.")
            else:
                st.info("Nenhuma ordem aberta neste setor.")

        with col_and:
            os_and = [o for o in st.session_state['em_andamento_os'] if o['setor'] == setor_nome]
            st.markdown(f"#### ⚙️ Em Atendimento ({len(os_and)})")
            if os_and:
                for item in os_and:
                    st.markdown(f"""
                    <div class="industrial-card card-warning">
                        <b>{item['id']}</b> | {item['maquina']}<br>
                        <small>🛠️ <b>Serviço:</b> {item['defeito']}</small><br>
                        <small>👨‍🔧 <b>Técnico:</b> {item.get('mecanico_responsavel','Técnico')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    rel_fechamento = st.text_area(f"Relatório Técnico Obrigatório ({item['id']}):", placeholder="Descreva detalhadamente o que foi feito na máquina...", key=f"f_rel_{setor_nome}_{item['id']}", height=80)
                    
                    if st.button(f"✅ Finalizar e Fechar {item['id']}", key=f"f_fin_{setor_nome}_{item['id']}", use_container_width=True):
                        if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                            if rel_fechamento.strip() == "":
                                st.error("⚠️ O preenchimento do relatório técnico é OBRIGATÓRIO para encerrar a OS!")
                            else:
                                os_conc = item.copy()
                                os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M')
                                os_conc["status"] = "Concluída"
                                os_conc["relatorio_fechamento"] = rel_fechamento
                                st.session_state['historico_os'].insert(0, os_conc)
                                st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != item['id']]
                                st.rerun()
                        else:
                            st.warning("⚠️ Apenas Mecânicos e Administradores podem concluir ordens!")
            else:
                st.info("Nenhuma manutenção em andamento.")

        with col_res:
            os_res = [o for o in st.session_state['historico_os'] if o['setor'] == setor_nome]
            st.markdown(f"#### ✅ Concluídas ({len(os_res)})")
            if os_res:
                for item in os_res:
                    st.markdown(f"""
                    <div class="industrial-card card-success">
                        <b>{item['id']}</b> | {item['maquina']}<br>
                        <small>✔️ <b>Problema:</b> {item['defeito']}</small><br>
                        <small>🛠️ <b>Responsável:</b> {item.get('mecanico_responsavel','N/D')}</small><br>
                        <small>📝 <b>Relatório:</b> {item.get('relatorio_fechamento','Sem relatório')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
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
                            st.warning("⚠️ Restrito a Mecânicos/Administradores.")
            else:
                st.info("Sem histórico recente.")

    with tab_inj:
        render_tabela_setor("Injetora Plástica")
    with tab_mont:
        render_tabela_setor("Linha de Montagem")
    with tab_emb:
        render_tabela_setor("Embalagem & Selagem")

# ==============================================================================
# TELA 3: PAINEL DA MÁQUINA INDIVIDUAL & TELEMETRIA
# ==============================================================================
else:
    st.markdown(f"### 🖥️ Painel Operacional — Setor: **{setor_selecionado}** | Ativo: **{maquina_selecionada}**")
    
    tag_maquina_atual = maquina_selecionada.split(' ')[0]
    
    if 'clp_conectado' not in st.session_state:
        st.session_state['clp_conectado'] = False

    col_clp1, col_clp2 = st.columns([4, 1])
    with col_clp2:
        if st.button("🔌 Conectar CLP", use_container_width=True):
            st.session_state['clp_conectado'] = not st.session_state['clp_conectado']
            st.rerun()

    with col_clp1:
        if st.session_state['clp_conectado']:
            st.markdown(f"""
            <div class="iot-banner-online">
                <div>
                    📡 <b>MANTIS IoT Engine:</b> Conexão estabilizada com o CLP do ativo <b>{tag_maquina_atual}</b>
                </div>
                <div><b>🟢 CONECTADO (ONLINE)</b></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="iot-banner-waiting">
                <div>
                    📡 <b>MANTIS IoT Engine:</b> Aguardando conexão com o CLP de <b>{tag_maquina_atual}</b>...
                </div>
                <div><b>⏳ AGUARDANDO CONEXÃO</b></div>
            </div>
            """, unsafe_allow_html=True)

    tab_principal, tab_preventiva, tab_abertas, tab_andamento, tab_historico = st.tabs([
        "📊 Telemetria & OEE", "🛠️ Plano Preventivo", "📌 OSs Abertas", "⚙️ Em Atendimento", "✅ Histórico de OS"
    ])

    with tab_principal:
        if not st.session_state['clp_conectado']:
            st.warning("⚠️ O CLP está desconectado. Clique no botão **'Conectar CLP'** acima para iniciar a leitura dos dados em tempo real.")
        
        if setor_selecionado == "Injetora Plástica":
            col_c1, col_c2, col_c3 = st.columns(3)
            temp_canhao = col_c1.slider("Temperatura do Canhão (°C)", 180.0, 260.0, 220.0)
            temp_molde = col_c2.slider("Temperatura do Molde (°C)", 15.0, 70.0, 32.0)
            pressao_recalque = col_c3.slider("Pressão de Recalque (bar)", 50.0, 160.0, 95.0)
            risco = min(100.0, (pressao_recalque * temp_molde) / 80)
        else:
            col_c1, col_c2 = st.columns(2)
            param1 = col_c1.slider("Pressão da Linha Pneumática (bar)", 4.0, 10.0, 6.5)
            param2 = col_c2.slider("Velocidade de Operação (peças/min)", 100, 300, 240)
            risco = 15.0 if param1 >= 5.5 else 75.0

        disp = max(60, int(98 - (risco * 0.3))) if st.session_state['clp_conectado'] else 0
        perf = max(70, int(95 - (risco * 0.2))) if st.session_state['clp_conectado'] else 0
        qual = max(80, int(99 - (risco * 0.4))) if st.session_state['clp_conectado'] else 0
        oee = int((disp/100) * (perf/100) * (qual/100) * 100) if st.session_state['clp_conectado'] else 0

        st.markdown("##### 📈 Indicadores Chave de Desempenho (OEE Global)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Disponibilidade", f"{disp}%")
        m2.metric("Performance", f"{perf}%")
        m3.metric("Qualidade", f"{qual}%")
        m4.metric("OEE Total", f"{oee}%")

        st.progress(int(risco) if st.session_state['clp_conectado'] else 0, text=f"Índice Preditivo de Risco / Carga Térmica: {int(risco) if st.session_state['clp_conectado'] else 0}%")
        
        if st.session_state['clp_conectado']:
            if risco < 35:
                st.success("🟢 Condição Operacional Ideal — Parâmetros Estáveis")
            elif 35 <= risco < 65:
                st.warning("🟡 Atenção Operacional — Oscilações Detectadas no Sistema")
            else:
                st.error("🔴 Alerta Crítico — Risco Imediato de Parada por Falha Mecânica")
        else:
            st.info("ℹ️ Dados em modo offline aguardando conexão com a máquina.")

        st.markdown("---")
        st.markdown("##### 📉 Histograma de Telemetria (Tempo Real)")
        df_chart = pd.DataFrame({
            "Pressão do Sistema (bar)": np.random.normal(loc=100, scale=2, size=20) if st.session_state['clp_conectado'] else np.zeros(20),
            "Temperatura Interna (°C)": np.random.normal(loc=220, scale=5, size=20) if st.session_state['clp_conectado'] else np.zeros(20)
        })
        st.line_chart(df_chart)

    with tab_preventiva:
        st.markdown(f"#### 🛠️ Plano de Manutenção Preventiva — {maquina_selecionada}")
        st.caption(f"Tempo estimado de parada programada: {info_prev['tempo']}")
        
        cols_cat = st.columns(3, gap="medium")
        for idx, (cat, pecas) in enumerate(info_prev['pecas_por_tipo'].items()):
            with cols_cat[idx]:
                st.markdown(f"**{cat}**")
                for p in pecas:
                    st.markdown(f"- ✅ {p}")

    with tab_abertas:
        os_ab_maquina = [o for o in st.session_state['lista_os'] if o['maquina'] == maquina_selecionada]
        if os_ab_maquina:
            for item in os_ab_maquina:
                st.markdown(f"""
                <div class="industrial-card card-critical">
                    <b>{item['id']}</b> | <b>Problema:</b> {item['defeito']}<br>
                    <small>👤 <b>Solicitante:</b> {item.get('autor_abertura','N/D')} | ⏰ {item['hora_abertura']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"▶️ Iniciar Atendimento desta OS ({item['id']})", key=f"p_in_{item['id']}", use_container_width=True):
                    if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                        os_and = item.copy()
                        os_and["hora_inicio"] = datetime.now().strftime('%H:%M')
                        os_and["mecanico_responsavel"] = st.session_state['usuario_logado']['nome']
                        st.session_state['em_andamento_os'].insert(0, os_and)
                        st.session_state['lista_os'] = [o for o in st.session_state['lista_os'] if o['id'] != item['id']]
                        st.rerun()
                    else:
                        st.warning("⚠️ Restrito: Apenas Mecânicos ou Administradores podem iniciar.")
        else:
            st.success(f"Nenhuma ordem aberta pendente para o ativo **{maquina_selecionada}**.")

    with tab_andamento:
        os_and_maquina = [o for o in st.session_state['em_andamento_os'] if o['maquina'] == maquina_selecionada]
        if os_and_maquina:
            for item in os_and_maquina:
                st.markdown(f"""
                <div class="industrial-card card-warning">
                    <b>{item['id']}</b> | <b>Serviço:</b> {item['defeito']}<br>
                    <small>👨‍🔧 <b>Técnico Responsável:</b> {item.get('mecanico_responsavel','Técnico')}</small>
                </div>
                """, unsafe_allow_html=True)
                
                rel_p_maq = st.text_area(f"Relatório Técnico Obrigatório ({item['id']}):", placeholder="Descreva o procedimento realizado...", key=f"p_rel_{item['id']}", height=80)
                
                if st.button(f"✅ Concluir OS {item['id']}", key=f"p_fin_{item['id']}", use_container_width=True):
                    if st.session_state['autenticado'] and st.session_state['usuario_logado']['perfil'] in ["Mecânico", "Administrador"]:
                        if rel_p_maq.strip() == "":
                            st.error("⚠️ O relatório técnico é OBRIGATÓRIO para finalizar a OS!")
                        else:
                            os_conc = item.copy()
                            os_conc["hora_conclusao"] = datetime.now().strftime('%H:%M')
                            os_conc["status"] = "Concluída"
                            os_conc["relatorio_fechamento"] = rel_p_maq
                            st.session_state['historico_os'].insert(0, os_conc)
                            st.session_state['em_andamento_os'] = [o for o in st.session_state['em_andamento_os'] if o['id'] != item['id']]
                            st.rerun()
                    else:
                        st.warning("⚠️ Restrito a Mecânicos ou Administradores.")
        else:
            st.info(f"Nenhuma manutenção ativa no momento para a **{maquina_selecionada}**.")

    with tab_historico:
        os_res_maquina = [o for o in st.session_state['historico_os'] if o['maquina'] == maquina_selecionada]
        if os_res_maquina:
            for item in os_res_maquina:
                st.markdown(f"""
                <div class="industrial-card card-success">
                    <b>{item['id']}</b> | <b>Solucionado:</b> {item['defeito']}<br>
                    <small>🛠️ <b>Técnico:</b> {item.get('mecanico_responsavel','N/D')}</small><br>
                    <small>📝 <b>Relatório:</b> {item.get('relatorio_fechamento','Sem relatório')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"Nenhum registro histórico recente para a **{maquina_selecionada}**.")
