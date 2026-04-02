from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def _safe_set(series: pd.Series) -> set[str]:
    return {str(value).strip() for value in series.dropna().tolist() if str(value).strip()}


def validate_documents(documents: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    issues: List[str] = []
    highlights: List[str] = []

    cronograma = documents.get("cronograma")
    ppu = documents.get("ppu")
    eap = documents.get("eap")
    histograma = documents.get("histograma")

    if cronograma is not None and ppu is not None:
        atividades_cronograma = _safe_set(cronograma["atividade"])
        atividades_ppu = _safe_set(ppu["atividade"])

        sem_cobertura = sorted(atividades_cronograma - atividades_ppu)
        sem_cronograma = sorted(atividades_ppu - atividades_cronograma)

        if sem_cobertura:
            issues.append(
                "Atividades no cronograma sem cobertura na PPU: " + ", ".join(sem_cobertura[:10])
            )
        if sem_cronograma:
            issues.append(
                "Itens da PPU sem atividade correspondente no cronograma: "
                + ", ".join(sem_cronograma[:10])
            )

    if cronograma is not None and eap is not None:
        pacotes_cronograma = _safe_set(cronograma["pacote_eap"])
        pacotes_eap = _safe_set(eap["pacote_eap"])
        fora_eap = sorted(pacotes_cronograma - pacotes_eap)
        nao_planejados = sorted(pacotes_eap - pacotes_cronograma)

        if fora_eap:
            issues.append(
                "Pacotes do cronograma que não constam na EAP: " + ", ".join(fora_eap[:10])
            )
        if nao_planejados:
            issues.append(
                "Pacotes da EAP sem atividades no cronograma: " + ", ".join(nao_planejados[:10])
            )

    if cronograma is not None:
        custo_zero = cronograma[cronograma["custo"].fillna(0) <= 0]
        sem_recurso = cronograma[cronograma["recurso"].astype(str).str.strip() == ""]
        if not custo_zero.empty:
            issues.append(
                f"Foram encontradas {len(custo_zero)} atividades com custo zerado ou ausente no cronograma."
            )
        if not sem_recurso.empty:
            issues.append(
                f"Foram encontradas {len(sem_recurso)} atividades sem recurso informado no cronograma."
            )

    if cronograma is not None and histograma is not None:
        atividades_cronograma = _safe_set(cronograma["atividade"])
        atividades_histograma = _safe_set(histograma["atividade"])
        sem_alocacao = sorted(atividades_cronograma - atividades_histograma)
        sem_atividade = sorted(atividades_histograma - atividades_cronograma)

        if sem_alocacao:
            issues.append(
                "Atividades do cronograma sem alocação no histograma: " + ", ".join(sem_alocacao[:10])
            )
        if sem_atividade:
            issues.append(
                "Atividades do histograma sem correspondência no cronograma: "
                + ", ".join(sem_atividade[:10])
            )

    if cronograma is not None:
        highlights.append(f"Cronograma carregado com {len(cronograma)} registros.")
    if ppu is not None:
        highlights.append(f"PPU carregada com {len(ppu)} registros.")
    if eap is not None:
        highlights.append(f"EAP carregada com {len(eap)} registros.")
    if histograma is not None:
        highlights.append(f"Histograma carregado com {len(histograma)} registros.")

    status = "ok" if not issues else "attention"

    return {
        "status": status,
        "highlights": highlights,
        "issues": issues,
        "summary": build_summary(highlights, issues),
    }


def build_summary(highlights: list[str], issues: list[str]) -> str:
    if not issues:
        return (
            "Análise concluída sem inconsistências críticas nas regras básicas configuradas. "
            "Ainda assim, recomenda-se validação de campo e revisão técnica do planejamento."
        )

    return (
        "Foram encontradas inconsistências entre os documentos enviados. "
        "Os principais pontos exigem revisão de cobertura orçamentária, estrutura EAP e alocação de recursos."
    )
