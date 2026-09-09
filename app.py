import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Configuração da página
st.set_page_config(page_title="Painel de Manutenção Preditiva", page_icon="⚙️", layout="wide")

st.title("⚙️ Painel Preditivo de Sensores Industriais")
st.markdown("Ajuste os valores dos sensores na barra lateral para simular o equipamento em tempo real.")

# Barra lateral com os controles
st.sidebar.header("🕹️ Simulação dos Sensores")
tipo_maquina = st.sidebar.selectbox("Tipo de Equipamento", ["L", "M", "H"], index=0)
air_temp = st.sidebar.slider("Temperatura Ambiente (K)", 295.0, 305.0, 300.0, 0.1)
process_temp = st.sidebar.slider("Temperatura do Processo (K)", 305.0, 315.0, 310.0, 0.1)
rpm = st.sidebar.slider("Rotação (RPM)", 1100, 2900, 1500, 10)
torque = st.sidebar.slider("Torque (Nm)", 3.0, 75.0, 40.0, 0.5)
tool_wear = st.sidebar.slider("Desgaste da Ferramenta (min)", 0, 250, 100, 1)

# Carregar e treinar o modelo
@st.cache_resource
def treinar_modelo():
    url = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
    df = pd.read_csv(url)
    
    mapeamento = {
        df.columns[0]: 'UDI', df.columns[1]: 'Product_ID', df.columns[2]: 'Type',
        df.columns[3]: 'Air_Temp', df.columns[4]: 'Process_Temp',
        df.columns[5]: 'Rotational_Speed', df.columns[6]: 'Torque',
        df.columns[7]: 'Tool_Wear', df.columns[8]: 'Target', df.columns[9]: 'Failure_Type'
    }
    df = df.rename(columns=mapeamento)
    
    # Métricas Mecânicas
    df['Delta_Temp'] = df['Process_Temp'] - df['Air_Temp']
    df['Power_kW'] = (df['Torque'] * df['Rotational_Speed']) / 9550
    df['Torque_Wear_Ratio'] = df['Torque'] * df['Tool_Wear']
    
    df_encoded = pd.get_dummies(df, columns=['Type'], drop_first=True)
    
    feats = [
        'Air_Temp', 'Process_Temp', 'Delta_Temp', 
        'Rotational_Speed', 'Torque', 'Power_kW', 
        'Tool_Wear', 'Torque_Wear_Ratio',
        'Type_M', 'Type_L'
    ]
    
    X = df_encoded[feats]
    y = df_encoded['Target']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', max_depth=12)
    model.fit(X, y)
    return model, feats

model, feats = treinar_modelo()

# Cálculos instantâneos
delta_temp = process_temp - air_temp
power_kw = (torque * rpm) / 9550
torque_wear = torque * tool_wear
type_m = 1 if tipo_maquina == 'M' else 0
type_l = 1 if tipo_maquina == 'L' else 0

input_df = pd.DataFrame([[
    air_temp, process_temp, delta_temp, rpm, torque,
    power_kw, tool_wear, torque_wear, type_m, type_l
]], columns=feats)

prob_falha = model.predict_proba(input_df)[0][1]

# Exibição na Tela
col1, col2, col3 = st.columns(3)
col1.metric("Potência Exigida", f"{power_kw:.2f} kW")
col2.metric("Delta Térmico (ΔT)", f"{delta_temp:.2f} K")
col3.metric("Risco de Quebra", f"{prob_falha * 100:.1f}%")

st.divider()

if prob_falha >= 0.40:
    st.error("🔴 ALERTA CRÍTICO: RISCO ELEVADO DE FALHA MECÂNICA!")
    st.write("Recomendação: Parar equipamento para manutenção preventiva imediata.")
elif prob_falha >= 0.20:
    st.warning("🟡 ATENÇÃO: OPERAÇÃO EM LIMITE DE TENSÃO")
    st.write("Recomendação: Planejar troca da ferramenta no próximo intervalo.")
else:
    st.success("🟢 OPERAÇÃO NORMAL")
    st.write("Equipamento operando dentro dos parâmetros de segurança.")
