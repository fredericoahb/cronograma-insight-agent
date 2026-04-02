from __future__ import annotations

import os
from typing import Iterable

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Cronograma Insight Agent", layout="wide")
st.title("📊 Cronograma Insight Agent")
st.caption("Validação de cronograma, EAP, PPU e histograma em uma interface web simples.")


def render_issue_list(items: Iterable[str], title: str, icon: str) -> None:
    st.subheader(f"{icon} {title}")
    items = list(items)
    if not items:
        st.success("Nenhum item encontrado.")
        return
    for item in items:
        st.write(f"- {item}")


with st.sidebar:
    st.header("Arquivos")
    cronograma = st.file_uploader("Cronograma (CSV, XLSX ou PDF)", type=["csv", "xlsx", "xls", "pdf"])
    ppu = st.file_uploader("PPU (CSV, XLSX ou PDF)", type=["csv", "xlsx", "xls", "pdf"])
    eap = st.file_uploader("EAP (CSV, XLSX ou PDF)", type=["csv", "xlsx", "xls", "pdf"])
    histograma = st.file_uploader("Histograma (CSV, XLSX ou PDF)", type=["csv", "xlsx", "xls", "pdf"])

    if st.button("Enviar arquivos"):
        uploads = {
            "cronograma": cronograma,
            "ppu": ppu,
            "eap": eap,
            "histograma": histograma,
        }
        sent_any = False
        for doc_type, uploaded in uploads.items():
            if uploaded is None:
                continue
            files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
            data = {"doc_type": doc_type}
            response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data, timeout=60)
            if response.ok:
                st.success(response.json()["message"])
                sent_any = True
            else:
                detail = response.json().get("detail", response.text)
                st.error(f"Erro ao enviar {doc_type}: {detail}")
        if not sent_any:
            st.warning("Selecione pelo menos um arquivo antes de enviar.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Executar validação")
    if st.button("🔍 Validar projeto"):
        response = requests.post(f"{BACKEND_URL}/validate", timeout=60)
        if response.ok:
            result = response.json()
            st.session_state["validation_result"] = result
        else:
            detail = response.json().get("detail", response.text)
            st.error(detail)

    result = st.session_state.get("validation_result")
    if result:
        st.info(result.get("summary", ""))
        render_issue_list(result.get("highlights", []), "Resumo dos documentos", "📌")
        render_issue_list(result.get("issues", []), "Inconsistências encontradas", "🚨")

with col2:
    st.subheader("Pergunte ao agente")
    question = st.text_input(
        "Exemplo: Existe atividade sem cobertura orçamentária?",
        placeholder="Digite uma pergunta sobre os documentos carregados",
    )
    if st.button("Enviar pergunta"):
        response = requests.post(f"{BACKEND_URL}/ask", data={"question": question}, timeout=60)
        if response.ok:
            st.success(response.json().get("answer", "Sem resposta."))
        else:
            detail = response.json().get("detail", response.text)
            st.error(detail)

st.divider()
st.subheader("Sugestões de uso")
st.markdown(
    """
1. Envie os arquivos do projeto.
2. Clique em **Validar projeto**.
3. Faça perguntas sobre orçamento, EAP, recursos e inconsistências.
    """
)
