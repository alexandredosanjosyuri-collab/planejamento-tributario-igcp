import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="IGCP - Planning Tributário", page_icon="📊", layout="wide")

st.markdown("""
    <style>
        .main { background-color: #f8fafc; }
        .metric-card {
            background-color: #ffffff; padding: 16px; border-radius: 8px;
            border-left: 5px solid #1f497d; border-top: 1px solid #e2e8f0;
            border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .winner-card {
            background-color: #f0fdf4; padding: 16px; border-radius: 8px;
            border-left: 5px solid #16a34a; border-top: 1px solid #bbf7d0;
            border-right: 1px solid #bbf7d0; border-bottom: 1px solid #bbf7d0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# 1. EXIBE A LOGO NA BARRA LATERAL (Logo 2.jpg com 'L' maiúsculo)
try:
    st.sidebar.image("Logo 2.jpg", use_container_width=True)
except Exception:
    st.sidebar.markdown("### **IGCP CONTÁBIL**")

st.sidebar.header("⚙️ Parâmetros da Simulação")
razao_social = st.sidebar.text_input("Razão Social / Cliente", "Empresa Exemplo Ltda")
segmento = st.sidebar.selectbox("Segmento Principal", ["Serviços", "Comércio"])
periodo = st.sidebar.selectbox("Período de Análise", ["Mensal", "Trimestral", "Semestral", "Anual"], index=2)

meses_map = {"Mensal": 1, "Trimestral": 3, "Semestral": 6, "Anual": 12}
n_meses = meses_map[periodo]

st.sidebar.subheader("💰 Valores do Período (R$)")
faturamento_periodo = st.sidebar.number_input("Faturamento Bruto no Período", value=600000.00, step=10000.00)
folha_periodo = st.sidebar.number_input("Folha de Pagamento + Encargos", value=120000.00, step=5000.00)
despesas_periodo = st.sidebar.number_input("Despesas Operacionais Dedutíveis", value=300000.00, step=5000.00)

st.sidebar.subheader("📈 Apoio & Alíquotas")
rbt12 = st.sidebar.number_input("RBT12 Acumulado (Últimos 12 meses)", value=2400000.00, step=50000.00)
aliq_iss_icms = st.sidebar.slider("Alíquota ISS/ICMS (%)", min_value=0.0, max_value=18.0, value=5.0, step=0.5) / 100
aliq_inss_patronal = 0.278

margem_presunção = 0.32 if segmento == "Serviços" else 0.08

# CABEÇALHO COM A LOGO (Logo 2.jpg com 'L' maiúsculo)
head_col1, head_col2 = st.columns([1, 5])
with head_col1:
    try:
        st.image("Logo 2.jpg", width=110)
    except Exception:
        pass
with head_col2:
    st.markdown("<h1 style='color: #1f497d; margin-bottom: 0;'>📊 Dashboard de Planejamento Tributário</h1>", unsafe_allow_html=True)
    st.markdown("### **IGCP ESCRITÓRIO CONTÁBIL S/S** — *Simulador Comparativo Interativo*")

st.markdown("---")

# CÁLCULOS TRIBUTÁRIOS
aliq_efetiva_sn = 0.165
imposto_sn = faturamento_periodo * aliq_efetiva_sn
custo_total_sn = imposto_sn

base_presumida = faturamento_periodo * margem_presunção
irpj_basico_lp = base_presumida * 0.15
limite_isencao_irpj = 20000.00 * n_meses
adicional_irpj_lp = (base_presumida - limite_isencao_irpj) * 0.10 if base_presumida > limite_isencao_irpj else 0
csll_lp = base_presumida * 0.09
pis_lp = faturamento_periodo * 0.0065
cofins_lp = faturamento_periodo * 0.0300
iss_icms_lp = faturamento_periodo * aliq_iss_icms
inss_lp = folha_periodo * aliq_inss_patronal

impostos_federais_lp = irpj_basico_lp + adicional_irpj_lp + csll_lp + pis_lp + cofins_lp
custo_total_lp = impostos_federais_lp + iss_icms_lp + inss_lp

lucro_real_apurado = max(0.0, faturamento_periodo - despesas_periodo - folha_periodo)
irpj_basico_lr = lucro_real_apurado * 0.15
adicional_irpj_lr = (lucro_real_apurado - limite_isencao_irpj) * 0.10 if lucro_real_apurado > limite_isencao_irpj else 0
csll_lr = lucro_real_apurado * 0.09
pis_lr = faturamento_periodo * 0.0165
cofins_lr = faturamento_periodo * 0.0760
iss_icms_lr = faturamento_periodo * aliq_iss_icms
inss_lr = folha_periodo * aliq_inss_patronal

impostos_federais_lr = irpj_basico_lr + adicional_irpj_lr + csll_lr + pis_lr + cofins_lr
custo_total_lr = impostos_federais_lr + iss_icms_lr + inss_lr

resultados = {"Simples Nacional": custo_total_sn, "Lucro Presumido": custo_total_lp, "Lucro Real": custo_total_lr}
melhor_regime = min(resultados, key=resultados.get)
economia_vs_sn = custo_total_sn - resultados[melhor_regime]

# CARDS
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='metric-card'><small>Faturamento ({periodo})</small><h3 style='color: #1f497d;'>R$ {faturamento_periodo:,.2f}</h3></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><small>Simples Nacional</small><h3 style='color: #1f497d;'>R$ {custo_total_sn:,.2f}</h3><small>Carga: {(custo_total_sn/faturamento_periodo)*100:.2f}%</small></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><small>Lucro Presumido</small><h3 style='color: #1f497d;'>R$ {custo_total_lp:,.2f}</h3><small>Carga: {(custo_total_lp/faturamento_periodo)*100:.2f}%</small></div>", unsafe_allow_html=True)
with col4:
    color_card = "winner-card" if melhor_regime != "Simples Nacional" else "metric-card"
    st.markdown(f"<div class='{color_card}'><small style='color: #166534;'>🏆 Recomendação Principal</small><h3 style='color: #166534;'>{melhor_regime}</h3><small style='color: #166534; font-weight: bold;'>Economia: R$ {economia_vs_sn:,.2f}</small></div>", unsafe_allow_html=True)

st.markdown("---")

# GRÁFICOS
g_col1, g_col2 = st.columns([6, 4])
with g_col1:
    st.subheader("📊 Comparativo de Custo Tributário Total (R$)")
    df_chart = pd.DataFrame({"Regime": ["Simples Nacional", "Lucro Presumido", "Lucro Real"], "Custo Total (R$)": [custo_total_sn, custo_total_lp, custo_total_lr]})
    fig_bar = px.bar(df_chart, x="Regime", y="Custo Total (R$)", text_auto=".2s", color="Regime",
                     color_discrete_map={"Simples Nacional": "#94a3b8", "Lucro Presumido": "#16a34a" if melhor_regime == "Lucro Presumido" else "#1f497d", "Lucro Real": "#16a34a" if melhor_regime == "Lucro Real" else "#1f497d"})
    fig_bar.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig_bar, use_container_width=True)

with g_col2:
    st.subheader("🍕 Composição do Custo no Presumido")
    df_pie = pd.DataFrame({"Imposto": ["Impostos Federais", "ISS/ICMS", "INSS Patronal"], "Valor": [impostos_federais_lp, iss_icms_lp, inss_lp]})
    fig_pie = px.pie(df_pie, names="Imposto", values="Valor", hole=0.4, color_discrete_sequence=["#1f497d", "#0284c7", "#f59e0b"])
    fig_pie.update_layout(height=380)
    st.plotly_chart(fig_pie, use_container_width=True)

# TABELA
st.subheader("📋 Tabela Comparativa Consolidada")
df_resumo = pd.DataFrame({
    "Indicador / Regime": ["Faturamento Bruto", "Impostos Federais", "ISS/ICMS", "INSS Patronal", "CUSTO TRIBUTÁRIO TOTAL", "Carga Tributária Efetiva (%)", "Economia vs. Simples"],
    "Simples Nacional": [f"R$ {faturamento_periodo:,.2f}", "Incluso no DAS", "Incluso no DAS", "R$ 0,00", f"R$ {custo_total_sn:,.2f}", f"{(custo_total_sn/faturamento_periodo)*100:.2f}%", "Base"],
    "Lucro Presumido": [f"R$ {faturamento_periodo:,.2f}", f"R$ {impostos_federais_lp:,.2f}", f"R$ {iss_icms_lp:,.2f}", f"R$ {inss_lp:,.2f}", f"R$ {custo_total_lp:,.2f}", f"{(custo_total_lp/faturamento_periodo)*100:.2f}%", f"- R$ {custo_total_sn - custo_total_lp:,.2f}"],
    "Lucro Real": [f"R$ {faturamento_periodo:,.2f}", f"R$ {impostos_federais_lr:,.2f}", f"R$ {iss_icms_lr:,.2f}", f"R$ {inss_lr:,.2f}", f"R$ {custo_total_lr:,.2f}", f"{(custo_total_lr/faturamento_periodo)*100:.2f}%", f"- R$ {custo_total_sn - custo_total_lr:,.2f}"]
})
st.dataframe(df_resumo, use_container_width=True, hide_index=True)
