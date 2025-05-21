import streamlit as st
import pdfplumber
import pandas as pd
from openai import OpenAI  # Using OpenAI SDK v1+

# ✅ Directly paste your Groq API key here
groq_api_key = "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"

# Streamlit page config
st.set_page_config(page_title="Bank Statement with Chatbot", layout="centered")
st.title("📄 Bank Statement Converter + 🤖 Chatbot")

# Upload bank statement
uploaded_file = st.file_uploader("📤 Upload your bank statement (PDF)", type="pdf")

if uploaded_file is not None:
    import io
    import os
    import tempfile
    import openai

    imported_text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            imported_text += page.extract_text() + "\n"

    # Extract transactions
    data = []
    for line in imported_text.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[0].count("-") == 2:
            date = parts[0]
            amount = parts[-1]
            description = " ".join(parts[1:-1])
            data.append([date, description, amount])

    if data:
        df = pd.DataFrame(data, columns=["Date", "Description", "Amount"])
        st.success("✅ Transactions extracted:")
        st.dataframe(df)

        # Download CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "bank_statement.csv", "text/csv")

        # Chatbot
        st.subheader("💬 Ask your statement:")
        question = st.text_input("Ask a question about your transactions")

        if question:
            with st.spinner("Thinking..."):
                client = OpenAI(
                    api_key=groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )

                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You're a helpful assistant analyzing a user's bank statement."},
                        {"role": "user", "content": f"Here is the statement:\n{df.to_string(index=False)}"},
                        {"role": "user", "content": question}
                    ]
                )

                answer = response.choices[0].message.content
                st.markdown(f"**🤖 Chatbot Answer:**\n\n{answer}")
    else:
        st.warning("⚠️ No valid transactions found in the PDF.")
else:
    st.info("📎 Please upload a PDF file to begin.")
