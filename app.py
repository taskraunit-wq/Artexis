import streamlit as st
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import sys

# 🔥 FIX AUTOMÁTICO OPENAI
try:
    from openai import OpenAI
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI

# 🔐 CONFIG API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🎨 CONFIGURACIÓN UI
st.set_page_config(page_title="ARTEXIS", layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .big-title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        color: gray;
    }
    </style>
""", unsafe_allow_html=True)

# 🧾 HEADER
st.markdown('<div class="big-title">ARTEXIS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sistema inteligente de auditoría documental</div>', unsafe_allow_html=True)

st.divider()

# 📂 FUNCION PARA LEER PDF
def leer_pdf(file):
    texto = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() or ""
    return texto

# 📤 UPLOADS
col1, col2 = st.columns(2)

with col1:
    ref_file = st.file_uploader("📘 Documento de referencia", type="pdf")

with col2:
    eval_file = st.file_uploader("📄 Documento a revisar", type="pdf")

# 🚀 BOTÓN
if st.button("Analizar documentos"):

    if ref_file and eval_file:

        with st.spinner("Analizando documentos..."):

            texto_ref = leer_pdf(ref_file)
            texto_eval = leer_pdf(eval_file)

            prompt = f"""
            Eres un auditor experto.

            Compara estos dos documentos:

            DOCUMENTO DE REFERENCIA:
            {texto_ref}

            DOCUMENTO A REVISAR:
            {texto_eval}

            INSTRUCCIONES:

            1. Identifica TODAS las diferencias
            2. Indica TEXTUALMENTE qué contenido no cumple
            3. Señala qué falta, qué sobra y qué está incorrecto
            4. Da recomendaciones específicas
            5. Organiza por secciones
            6. Sé claro, estructurado y profesional

            FORMATO:

            - Sección:
            - Diferencia encontrada:
            - Texto problemático:
            - Recomendación:
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            resultado = response.choices[0].message.content

        st.success("Análisis completado")

        st.subheader("📋 Resultado del análisis")
        st.write(resultado)

        # 📊 DASHBOARD
        st.subheader("📊 Dashboard de observaciones")

        total_obs = resultado.count("Diferencia")
        cumplimiento = max(0, 100 - total_obs * 5)

        df = pd.DataFrame({
            "Métrica": ["Observaciones", "Nivel de cumplimiento"],
            "Valor": [total_obs, cumplimiento]
        })

        st.dataframe(df)

        fig, ax = plt.subplots()
        ax.bar(df["Métrica"], df["Valor"])
        ax.set_title("Resumen de Auditoría")
        st.pyplot(fig)

    else:
        st.warning("Sube ambos documentos")

    else:
        st.warning("Debes subir ambos documentos")
