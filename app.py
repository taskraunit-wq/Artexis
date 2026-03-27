import streamlit as st
from openai import OpenAI
import json
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber

# CONFIG
st.set_page_config(page_title="ARTEXIS", layout="wide")

# 🎨 ESTILO PREMIUM
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    background-color: #0E1117;
}

.header {
    text-align: center;
    padding: 20px;
}

.title {
    font-size: 42px;
    font-weight: 700;
    color: white;
}

.subtitle {
    color: #9CA3AF;
    font-size: 16px;
}

.metric-card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.stButton>button {
    background: linear-gradient(90deg, #1F6FEB, #3B82F6);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
<div class="header">
    <div class="title">ARTEXIS</div>
    <div class="subtitle">Auditoría documental inteligente</div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.title("ARTEXIS")
    st.markdown("### Panel de control")
    st.markdown("- 📄 Análisis")
    st.markdown("- 📊 Dashboard")
    st.markdown("- 📥 Exportación")
    st.divider()
    st.info("Sistema de auditoría con IA")

# 🔑 API KEY (CAMBIA ESTO)
client = client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 📄 LECTURA PDF PRO
def leer_pdf(file):
    texto = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() or ""
    return texto

# 🧠 IA
def analizar(ref_file, target_file):

    ref_text = leer_pdf(ref_file)
    target_text = leer_pdf(target_file)

    prompt = f"""
Eres un auditor regulatorio senior.

Devuelve SOLO JSON válido:

{{
  "material": "documento",
  "total_incumplimientos": número,
  "incumplimientos": [
    {{
      "tipo": "",
      "texto_objetivo": "",
      "texto_referencia": "",
      "motivo": "",
      "severidad": "ALTA | MEDIA | BAJA"
    }}
  ]
}}

DOCUMENTO REFERENCIA:
{ref_text[:15000]}

DOCUMENTO OBJETIVO:
{target_text[:15000]}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

# UI
col1, col2 = st.columns(2)

with col1:
    ref_file = st.file_uploader("📘 Documento de referencia", type="pdf")

with col2:
    target_file = st.file_uploader("📄 Documento a revisar", type="pdf")

st.markdown("---")

if st.button("🚀 Analizar documentos"):

    if ref_file and target_file:

        with st.spinner("Analizando..."):
            data = analizar(ref_file, target_file)

        st.success("Análisis completado")

        # KPIs
        total = data["total_incumplimientos"]
        altas = sum(1 for i in data["incumplimientos"] if i["severidad"] == "ALTA")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Material</h4>
                <h2>{data["material"]}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Incumplimientos</h4>
                <h2>{total}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Críticos</h4>
                <h2>{altas}</h2>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # TABLA
        df = pd.DataFrame(data["incumplimientos"])
        st.subheader("📋 Observaciones")
        st.dataframe(df)

        # GRÁFICA
        st.subheader("📊 Distribución de severidad")

        conteo = df["severidad"].value_counts()

        fig, ax = plt.subplots()
        ax.pie(conteo, labels=conteo.index, autopct="%1.1f%%")
        st.pyplot(fig)

        # EXPORTAR
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar Excel",
            csv,
            "reporte_artexis.csv",
            "text/csv"
        )

    else:
        st.warning("Debes subir ambos documentos")