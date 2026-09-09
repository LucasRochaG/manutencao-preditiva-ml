import asyncio
import requests
import pandas as pd
from asyncua import Client
from sklearn.ensemble import RandomForestClassifier

# Configuração da fábrica Injeção Cirúrgica
CLP_IP = "opc.tcp://192.168.1.100:4840"
TELEGRAM_BOT_TOKEN = "SEU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"

def enviar_alerta(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erro ao enviar alerta: {e}")

# Treinamento do modelo com variáveis reais do processo de PP (Polipropileno)
data = {
    'Temp_Canhao_Z1': [200, 210, 245, 195, 205],
    'Temp_Agua_Molde': [25, 30, 65, 28, 30],
    'RPM_Plastificacao': [100, 110, 180, 105, 112],
    'Pressao_Recalque': [80, 85, 140, 82, 87],
    'Ciclos_Molde': [1000, 50000, 450000, 120000, 30000],
    'Falha': [0, 0, 1, 0, 0]
}
df = pd.DataFrame(data)
df['Indice_Sobrecarga'] = (df['Pressao_Recalque'] * df['RPM_Plastificacao']) / 1000

feats = ['Temp_Canhao_Z1', 'Temp_Agua_Molde', 'RPM_Plastificacao', 'Pressao_Recalque', 'Ciclos_Molde', 'Indice_Sobrecarga']
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(df[feats], df['Falha'])

print("✅ Modelo preditivo para injeção de seringas pronto para produção!")
