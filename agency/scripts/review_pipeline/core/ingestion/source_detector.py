"""
source_detector.py — Detecção Automática de Fonte Acadêmica

Detecta o formato do CSV comparando os cabeçalhos encontrados com os perfis
definidos no sources_config.yaml. Não depende de conhecimento internalizado.

Retorna o ID da fonte (ex: "wos_excel", "scopus") e o mapeamento de colunas
canônico (title, abstract, doi, year, journal, authors).
"""

from __future__ import annotations


CANONICAL_FIELDS = ["title", "abstract", "doi", "year", "journal", "authors"]


def detect_source(fieldnames: list[str], sources: dict) -> tuple[str, dict]:
    """
    Detecta a fonte acadêmica comparando fieldnames com os perfis em sources_config.

    Args:
        fieldnames: Lista de cabeçalhos do CSV lido.
        sources:    Dicionário de perfis do sources_config.yaml.

    Returns:
        (source_id, column_map) onde column_map mapeia campo canônico → nome real no CSV.
        Retorna ("unknown", {}) se nenhuma fonte for detectada.
    """
    headers_set = {h.strip() for h in fieldnames}
    best_id = "unknown"
    best_score = 0
    best_map: dict[str, str] = {}

    for source_id, profile in sources.items():
        columns = profile.get("columns", {})
        score = 0
        candidate_map: dict[str, str] = {}

        for canonical, aliases in columns.items():
            for alias in aliases:
                if alias in headers_set:
                    score += 1
                    candidate_map[canonical] = alias
                    break

        if score > best_score:
            best_score = score
            best_id = source_id
            best_map = candidate_map

    if best_score == 0:
        return "unknown", {}

    return best_id, best_map


def get_source_profile(source_id: str, sources: dict) -> dict:
    """Retorna o perfil completo de uma fonte pelo ID."""
    return sources.get(source_id, {})


def resolve_field(row: dict, canonical: str, column_map: dict) -> str:
    """
    Resolve o valor de um campo canônico a partir de um registro CSV.

    Args:
        row:        Dicionário do registro (cabeçalho → valor).
        canonical:  Nome do campo canônico (ex: "title", "abstract").
        column_map: Mapeamento canônico → coluna real do CSV.

    Returns:
        Valor da coluna ou string vazia se não encontrado.
    """
    col = column_map.get(canonical, "")
    return row.get(col, "").strip() if col else ""


def build_canonical_row(row: dict, column_map: dict) -> dict:
    """
    Transforma um registro CSV bruto em um registro com campos canônicos.

    Campos canônicos: title, abstract, doi, year, journal, authors.
    Campos ausentes ficam como string vazia.
    """
    return {field: resolve_field(row, field, column_map) for field in CANONICAL_FIELDS}


def warn_abstract_unavailable(source_id: str, sources: dict) -> bool:
    """
    Verifica se a fonte tem abstract_available: false e exibe aviso.
    Retorna True se abstract NÃO está disponível nesta fonte.
    """
    profile = sources.get(source_id, {})
    if profile.get("abstract_available") is False:
        print(
            f"\n\033[93m[AVISO] A fonte '{profile.get('name', source_id)}' "
            f"NÃO inclui Abstract no export CSV nativo.\033[0m"
        )
        print(
            "  Para triagem de título+resumo, use um exportador alternativo "
            "que inclua abstract (ex: E-utilities, Zotero)."
        )
        print(f"  Docs: {profile.get('official_docs', 'N/A')}\n")
        return True
    return False
