from __future__ import annotations

from io import BytesIO
from typing import Dict

import pandas as pd


ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


def parse_tabular_file(filename: str, content: bytes) -> pd.DataFrame:
    extension = filename.lower().rsplit(".", 1)[-1]
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Formato não suportado: {extension}")

    if extension == "csv":
        return pd.read_csv(BytesIO(content))

    return pd.read_excel(BytesIO(content))


REQUIRED_COLUMNS: Dict[str, list[str]] = {
    "cronograma": ["atividade", "pacote_eap", "data_inicio", "data_fim", "custo", "recurso"],
    "ppu": ["atividade", "item_ppu", "valor"],
    "eap": ["pacote_eap", "descricao"],
    "histograma": ["atividade", "recurso", "quantidade"],
}


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(col).strip().lower() for col in normalized.columns]
    return normalized


def validate_required_columns(doc_type: str, df: pd.DataFrame) -> list[str]:
    required = REQUIRED_COLUMNS.get(doc_type, [])
    missing = [col for col in required if col not in df.columns]
    return missing
