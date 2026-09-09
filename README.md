# ⚙️ Manutenção Preditiva & Inteligência Industrial

Este repositório contém uma solução completa de **Manutenção Preditiva**, combinando Machine Learning (Random Forest) com parâmetros físicos de engenharia mecânica para prevenir paradas não programadas em linhas de produção.

---

## 🛠️ Engenharia de Features Mecânicas
O modelo foi treinado utilizando três indicadores calculados a partir dos sensores IoT:
* **Potência Mecânica Requerida ($kW$):** $(\text{Torque} \times \text{RPM}) / 9550$
* **Elevação Térmica ($\Delta T$):** $T_{\text{processo}} - T_{\text{ambiente}}$
* **Estresse de Ferramenta:** $\text{Torque} \times \text{Desgaste Acumulado}$

---

## 📊 Impacto Financeiro Estimado
* **Custo da Falha Não Programada (Quebra):** R$ 15.000,00
* **Custo do Reparo Preventivo:** R$ 1.500,00
* **Economia Estimada:** R$ 1.100.000,00+ em um parque de 1.000 equipamentos.

---

## 🚀 Como Executar Localmente

```bash
# Clone o repositório
git clone [https://github.com/seu-usuario/manutencao-preditiva.git](https://github.com/seu-usuario/manutencao-preditiva.git)

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo Streamlit
streamlit run app.py
