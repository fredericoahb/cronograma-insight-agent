from __future__ import annotations

from typing import Dict

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.services.parser_excel import (
    normalize_dataframe,
    parse_tabular_file,
    validate_required_columns,
)
from backend.services.parser_pdf import extract_pdf_text
from backend.services.qa_service import answer_question
from backend.services.validator import validate_documents

app = FastAPI(title="Cronograma Insight Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE: Dict[str, object] = {
    "documents": {},
    "validation_result": {"status": "empty", "highlights": [], "issues": [], "summary": ""},
    "pdf_notes": {},
}


@app.get("/")
def healthcheck() -> dict:
    return {"message": "Cronograma Insight Agent API online"}


@app.post("/upload")
async def upload_document(
    doc_type: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    allowed_types = {"cronograma", "ppu", "eap", "histograma"}
    if doc_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de documento inválido.")

    content = await file.read()
    filename = file.filename or "arquivo"

    if filename.lower().endswith(".pdf"):
        text = extract_pdf_text(content)
        STATE["pdf_notes"][doc_type] = {
            "filename": filename,
            "text_excerpt": text[:3000],
            "message": "PDF recebido. Nesta versão, o PDF é armazenado como texto de apoio."
        }
        return {"message": f"PDF {filename} recebido como apoio para o tipo {doc_type}."}

    try:
        df = parse_tabular_file(filename, content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    df = normalize_dataframe(df)
    missing = validate_required_columns(doc_type, df)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Colunas obrigatórias ausentes para {doc_type}: {', '.join(missing)}",
        )

    STATE["documents"][doc_type] = df
    return {
        "message": f"Arquivo {filename} carregado com sucesso para {doc_type}.",
        "rows": len(df),
        "columns": list(df.columns),
    }


@app.post("/validate")
def validate() -> dict:
    documents: Dict[str, pd.DataFrame] = STATE["documents"]  # type: ignore[assignment]
    if not documents:
        raise HTTPException(status_code=400, detail="Nenhum documento estruturado foi enviado ainda.")

    result = validate_documents(documents)
    STATE["validation_result"] = result
    return result


@app.post("/ask")
def ask(question: str = Form(...)) -> dict:
    validation_result = STATE.get("validation_result", {})
    answer = answer_question(question, validation_result)
    return {"answer": answer}


@app.get("/state")
def get_state() -> dict:
    documents = STATE.get("documents", {})
    pdf_notes = STATE.get("pdf_notes", {})
    return {
        "loaded_documents": list(documents.keys()),
        "pdf_documents": list(pdf_notes.keys()),
        "validation_result": STATE.get("validation_result", {}),
    }
