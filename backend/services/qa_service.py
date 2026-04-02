from __future__ import annotations

from typing import Any, Dict


def answer_question(question: str, validation_result: Dict[str, Any]) -> str:
    normalized = question.lower().strip()
    issues = validation_result.get("issues", [])
    highlights = validation_result.get("highlights", [])

    if not question.strip():
        return "Envie uma pergunta para que a análise possa ser respondida."

    if "cobertura orçament" in normalized or "ppu" in normalized:
        matched = [issue for issue in issues if "PPU" in issue or "custo" in issue]
        if matched:
            return "Foram encontrados indícios de inconsistência orçamentária: " + " | ".join(matched)
        return "Não foram encontradas inconsistências orçamentárias nas regras básicas avaliadas."

    if "eap" in normalized or "pacote" in normalized:
        matched = [issue for issue in issues if "EAP" in issue or "Pacotes" in issue]
        if matched:
            return "A análise da EAP apontou os seguintes pontos: " + " | ".join(matched)
        return "Não foram encontradas divergências relevantes entre cronograma e EAP nas regras básicas."

    if "equipe" in normalized or "recurso" in normalized or "histograma" in normalized:
        matched = [issue for issue in issues if "histograma" in issue or "recurso" in issue]
        if matched:
            return "A análise de recursos identificou: " + " | ".join(matched)
        return "Não foram encontradas inconsistências relevantes de recursos nas regras básicas."

    if "resumo" in normalized or "principais" in normalized or "inconsist" in normalized:
        summary = validation_result.get("summary", "")
        details = " | ".join(issues[:5]) if issues else "Nenhuma inconsistência crítica encontrada."
        return f"{summary} Detalhes: {details}"

    base = "; ".join(highlights[:4]) if highlights else "Nenhum documento estruturado foi processado ainda."
    return (
        "Pergunta recebida. Nesta versão inicial, a resposta é baseada em regras. "
        f"Contexto disponível: {base}"
    )
