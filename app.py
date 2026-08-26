import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IGCP - Planning Tributário",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada (Visual Clean / Power BI Style)
st.markdown("""
    <style>
        .main {
            background-color: #f8fafc;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .metric-card {
            background-color: #ffffff;
            padding: 16px;
            border-radius: 8px;
            border-left: 5px solid #1f497d;
            border-top: 1px solid #e2e8f0;
            border-right: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        .winner-card {
            background-color: #f0fdf4;
            padding: 16px;
            border-radius: 8px;
            border-left: 5px solid #16a34a;
            border-top: 1px solid #bbf7d0;
            border-right: 1px solid #bbf7d0;
            border-bottom: 1px solid #bbf7d0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        .custom-title {
            color: #1f497d;
            font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CABEÇALHO
# -----------------------------------------------------------------------------
st.markdown("<h1 class='custom-title'>📊 Dashboard de Planejamento Tributário</h1>", unsafe_allow_html=True)
st.markdown("### **IGCP ESCRITÓRIO CONTÁBIL S/S** — *Simulador Comparativo de Regimes Tributários*")
st.markdown("---")

# -----------------------------------------------------------------------------
# BARRA LATERAL (CONTROLES E ENTRADA DE DADOS)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Parâmetros da Simulação")

razao_social = st.sidebar.text_input("Razão Social / Cliente", "Empresa Exemplo Ltda")
segmento = st.sidebar.selectbox("Segmento Principal", ["Serviços", "Comércio"])
periodo = st.sidebar.selectbox("Período de Análise", ["Mensal", "Trimestral", "Semestral", "Anual"], index=2)

# Fator de meses do período
meses_map = {"Mensal": 1, "Trimestral": 3, "Semestral": 6, "Anual": 12}
n_meses = meses_map[periodo]

st.sidebar.subheader("💰 Valores do Período (R$)")
faturamento_periodo = st.sidebar.number_input("Faturamento Bruto no Período", value=600000.00, step=10000.00, format="%.2f")
folha_periodo = st.sidebar.number_input("Folha de Pagamento + Encargos", value=120000.00, step=5000.00, format="%.2f")
despesas_periodo = st.sidebar.number_input("Despesas Operacionais Dedutíveis", value=300000.00, step=5000.00, format="%.2f")

st.sidebar.subheader("📈 Apoio & Alíquotas")
rbt12 = st.sidebar.number_input("RBT12 Acumulado (Últimos 12 meses)", value=2400000.00, step=50000.00, format="%.2f")
aliq_iss_icms = st.sidebar.slider("Alíquota ISS/ICMS (%)", min_value=0.0, max_value=18.0, value=5.0, step=0.5) / 100
aliq_inss_patronal = 0.278 # 27.8% fixa para Lucro Presumido e Real (INSS + Terceiros + RAT)

# Margem de Presunção
margem_presunção = 0.32 if segmento == "Serviços" else 0.08

# -----------------------------------------------------------------------------
# MOTOR DE CÁLCULO
# -----------------------------------------------------------------------------

# 1. SIMPLES NACIONAL
# Fator R
fator_r = folha_periodo / faturamento_periodo if faturamento_periodo > 0 else 0
aliq_efetiva_sn = 0.165 # Alíquota média de exemplo baseada no RBT12
imposto_sn = faturamento_periodo * aliq_efetiva_sn
inss_sn = 0.0 # CPP já incluso no DAS
custo_total_sn = imposto_sn + inss_sn

# 2. LUCRO PRESUMIDO
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

# 3. LUCRO REAL
lucro_real_apurado = faturamento_periodo - despesas_periodo - folha_periodo
lucro_tributavel = max(0.0, lucro_real_apurado)

irpj_basico_lr = lucro_tributavel * 0.15
adicional_irpj_lr = (lucro_tributavel - limite_isencao_irpj) * 0.10 if lucro_tributavel > limite_isencao_irpj else 0
csll_lr = lucro_tributavel * 0.09
pis_lr = faturamento_periodo * 0.0165 # Não cumulativo simplificado
cofins_lr = faturamento_periodo * 0.0760
iss_icms_lr = faturamento_periodo * aliq_iss_icms
inss_lr = folha_periodo * aliq_inss_patronal

impostos_federais_lr = irpj_basico_lr + adicional_irpj_lr + csll_lr + pis_lr + cofins_lr
custo_total_lr = impostos_federais_lr + iss_icms_lr + inss_lr

# Identificação do Vencedor
resultados = {
    "Simples Nacional": custo_total_sn,
    "Lucro Presumido": custo_total_lp,
    "Lucro Real": custo_total_lr
}
melhor_regime = min(resultados, key=resultados.get)
menor_custo = resultados[melhor_regime]
economia_vs_sn = custo_total_sn - menor_custo

# -----------------------------------------------------------------------------
# EXIBIÇÃO DE KPIS (CARDS SUPERIORES)
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class='metric-card'>
            <small style='color: #64748b;'>Faturamento do Período ({periodo})</small>
            <h3 style='margin: 0; color: #1f497d;'>R$ {faturamento_periodo:,.2f}</h3>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-card'>
            <small style='color: #64748b;'>Simples Nacional (Custo)</small>
            <h3 style='margin: 0; color: #1f497d;'>R$ {custo_total_sn:,.2f}</h3>
            <small>Carga: {(custo_total_sn/faturamento_periodo)*100:.2f}%</small>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <small style='color: #64748b;'>Lucro Presumido (Custo)</small>
            <h3 style='margin: 0; color: #1f497d;'>R$ {custo_total_lp:,.2f}</h3>
            <small>Carga: {(custo_total_lp/faturamento_periodo)*100:.2f}%</small>
        </div>
    """, unsafe_allow_html=True)

with col4:
    color_card = "winner-card" if melhor_regime != "Simples Nacional" else "metric-card"
    st.markdown(f"""
        <div class='{color_card}'>
            <small style='color: #166534;'>🏆 Recomendação Principal</small>
            <h3 style='margin: 0; color: #166534;'>{melhor_regime}</h3>
            <small style='color: #166534; font-weight: bold;'>Economia: R$ {economia_vs_sn:,.2f}</small>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# GRÁFICOS INTERATIVOS POWER BI STYLE
# -----------------------------------------------------------------------------
g_col1, g_col2 = st.columns([6, 4])

with g_col1:
    st.subheader("📊 Comparativo de Custo Tributário Total (R$)")
    
    df_chart = pd.DataFrame({
        "Regime": ["Simples Nacional", "Lucro Presumido", "Lucro Real"],
        "Custo Total (R$)": [custo_total_sn, custo_total_lp, custo_total_lr],
        "Cor": ["#94a3b8", "#16a34a" if melhor_regime == "Lucro Presumido" else "#1f497d", "#16a34a" if melhor_regime == "Lucro Real" else "#1f497d"]
    })
    
    fig_bar = px.bar(
        df_chart, 
        x="Regime", 
        y="Custo Total (R$)", 
        text_auto=".2s",
        color="Regime",
        color_discrete_map={
            "Simples Nacional": "#94a3b8",
            "Lucro Presumido": "#16a34a" if melhor_regime == "Lucro Presumido" else "#1f497d",
            "Lucro Real": "#16a34a" if melhor_regime == "Lucro Real" else "#1f497d"
        }
    )
    fig_bar.update_layout(showlegend=False, height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with g_col2:
    st.subheader("🍕 Composição do Custo no Presumido")
    
    df_pie = pd.DataFrame({
        "Imposto": ["Impostos Federais", "ISS/ICMS", "INSS Patronal"],
        "Valor": [impostos_federais_lp, iss_icms_lp, inss_lp]
    })
    
    fig_pie = px.pie(
        df_pie, 
        names="Imposto", 
        values="Valor", 
        hole=0.4,
        color_discrete_sequence=["#1f497d", "#0284c7", "#f59e0b"]
    )
    fig_pie.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# TABELA DETALHADA E MATRIZ DE DECISÃO
# -----------------------------------------------------------------------------
st.subheader("📋 Tabela Comparativa Consolidada")

df_resumo = pd.DataFrame({
    "Indicador / Regime": [
        "Faturamento Bruto no Período",
        "Impostos Federais (IRPJ/CSLL/PIS/COFINS)",
        "Impostos Municipais/Estaduais (ISS/ICMS)",
        "Encargos Trabalhistas (INSS Patronal)",
        "CUSTO TRIBUTÁRIO TOTAL",
        "Carga Tributária Efetiva (%)",
        "Economia vs. Simples Nacional"
    ],
    "Simples Nacional": [
        f"R$ {faturamento_periodo:,.2f}",
        "Incluso no DAS",
        "Incluso no DAS",
        f"R$ {inss_sn:,.2f}",
        f"R$ {custo_total_sn:,.2f}",
        f"{(custo_total_sn/faturamento_periodo)*100:.2f}%",
        "Base"
    ],
    "Lucro Presumido": [
        f"R$ {faturamento_periodo:,.2f}",
        f"R$ {impostos_federais_lp:,.2f}",
        f"R$ {iss_icms_lp:,.2f}",
        f"R$ {inss_lp:,.2f}",
        f"R$ {custo_total_lp:,.2f}",
        f"{(custo_total_lp/faturamento_periodo)*100:.2f}%",
        f"- R$ {custo_total_sn - custo_total_lp:,.2f}"
    ],
    "Lucro Real": [
        f"R$ {faturamento_periodo:,.2f}",
        f"R$ {impostos_federais_lr:,.2f}",
        f"R$ {iss_icms_lr:,.2f}",
        f"R$ {inss_lr:,.2f}",
        f"R$ {custo_total_lr:,.2f}",
        f"{(custo_total_lr/faturamento_periodo)*100:.2f}%",
        f"- R$ {custo_total_sn - custo_total_lr:,.2f}"
    ]
})

st.dataframe(df_resumo, use_container_width=True, hide_index=True)
