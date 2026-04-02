import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.validator import validate_documents
import pandas as pd


def test_validate_documents_detects_inconsistencies() -> None:
    cronograma = pd.DataFrame(
        [
            {"atividade": "A", "pacote_eap": "1.1", "data_inicio": "2026-01-01", "data_fim": "2026-01-02", "custo": 100, "recurso": "Equipe 1"},
            {"atividade": "B", "pacote_eap": "1.2", "data_inicio": "2026-01-03", "data_fim": "2026-01-04", "custo": 0, "recurso": ""},
        ]
    )
    ppu = pd.DataFrame(
        [
            {"atividade": "A", "item_ppu": "PPU-1", "valor": 100},
            {"atividade": "C", "item_ppu": "PPU-2", "valor": 200},
        ]
    )
    eap = pd.DataFrame(
        [
            {"pacote_eap": "1.1", "descricao": "Pacote 1"},
            {"pacote_eap": "1.3", "descricao": "Pacote 3"},
        ]
    )
    histograma = pd.DataFrame(
        [
            {"atividade": "A", "recurso": "Equipe 1", "quantidade": 2},
            {"atividade": "C", "recurso": "Equipe 3", "quantidade": 1},
        ]
    )

    result = validate_documents(
        {
            "cronograma": cronograma,
            "ppu": ppu,
            "eap": eap,
            "histograma": histograma,
        }
    )

    assert result["status"] == "attention"
    assert len(result["issues"]) >= 1
