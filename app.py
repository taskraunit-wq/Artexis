import streamlit as st
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import sys

# 🔥 FIX OPENAI
try:
    from openai import OpenAI
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI

# 🔐 API KEY
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🎨 UI
st.set_page_config(page_title="ARTEXIS", layout="wide")

st.title("ARTEXIS")
st.caption("Sistema inteligente de auditoría documental")

st.divider()

# 📄 FUNCIÓN PDF
def leer_pdf(file):
    texto = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() or ""
    return texto

# 📂 CARGA
col1, col2 = st.columns(2)

with col1:
    ref_file = st.file_uploader("Documento de referencia", type="pdf")

with col2:
    eval_file = st.file_uploader("Documento a revisar", type="pdf")

# 🚀 BOTÓN
if st.button("Analizar documentos"):

    if ref_file is not None and eval_file is not None:

        with st.spinner("Analizando..."):

            texto_ref = leer_pdf(ref_file)
            texto_eval = leer_pdf(eval_file)

            prompt = f"""
            Compara estos documentos.

            REFERENCIA:
            {texto_ref}

            DOCUMENTO:
            {texto_eval}

            Indica:
            - Diferencias
            - Qué no cumple (cita texto exacto)
            - Recomendaciones
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            resultado = response.choices[0].message.content

        st.success("Análisis completado")
        st.write(resultado)

        # 📊 Dashboard simple
        st.subheader("Resumen")

        total = resultado.count("Diferencia")
        cumplimiento = max(0, 100 - total * 5)

        df = pd.DataFrame({
            "Métrica": ["Observaciones", "Cumplimiento"],
            "Valor": [total, cumplimiento]
        })

        st.dataframe(df)

        fig, ax = plt.subplots()
        ax.bar(df["Métrica"], df["Valor"])
        st.pyplot(fig)

    else:
        st.warning("Sube ambos documentos")
