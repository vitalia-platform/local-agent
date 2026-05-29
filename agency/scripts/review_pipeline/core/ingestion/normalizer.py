"""
normalizer.py — Normalização, Deduplicação e Geração do PRISMA_LOG.csv

Responsabilidades:
- Normalizar DOIs (remover prefixos https://doi.org/)
- Deduplicar registros (DOI como chave primária, título como fallback)
- Gerar PRISMA_LOG.csv no formato padrão canônico
"""

from __future__ import annotations

import csv
import os
import re


# Campos canônicos do PRISMA_LOG.csv
PRISMA_FIELDNAMES = [
    "Title",
    "Authors",
    "Year",
    "Journal",
    "DOI",
    "Abstract",
    "Status",
    "Exclusion_Reason",
    "Source",
]


def normalize_doi(doi_str: str) -> str:
    """Remove prefixos de URL e normaliza o DOI."""
    if not doi_str:
        return ""
    doi_str = doi_str.strip()
    doi_str = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi_str, flags=re.IGNORECASE)
    return doi_str.strip()


def normalize_title(title: str) -> str:
    """Normaliza título para uso como chave de deduplicação."""
    return re.sub(r"\s+", " ", title.lower().strip())


def deduplicate(articles: list[dict]) -> tuple[list[dict], int]:
    """
    Deduplica lista de registros.

    Estratégia:
    1. DOI normalizado como chave primária (se disponível)
    2. Título normalizado como chave de fallback

    Returns:
        (lista_única, total_duplicatas_removidas)
    """
    seen_dois: dict[str, bool] = {}
    seen_titles: dict[str, bool] = {}
    unique: list[dict] = []
    duplicates = 0

    for article in articles:
        doi = normalize_doi(article.get("doi", "") or article.get("DOI", ""))
        title = normalize_title(article.get("title", "") or article.get("Title", ""))

        if doi:
            if doi in seen_dois:
                duplicates += 1
                continue
            seen_dois[doi] = True
        elif title:
            if title in seen_titles:
                duplicates += 1
                continue
            seen_titles[title] = True
        else:
            # Sem DOI e sem título — incluir (não conseguimos deduplica)
            pass

        # Registrar título também para evitar dups de registros sem DOI
        if title:
            seen_titles[title] = True

        unique.append(article)

    return unique, duplicates


def to_prisma_log(
    articles: list[dict],
    output_path: str,
    source_label: str = "",
    existing_path: str | None = None,
) -> tuple[int, int]:
    """
    Gera ou atualiza o PRISMA_LOG.csv no formato canônico.

    Se existing_path for fornecido, faz merge e deduplicação com o arquivo existente.

    Args:
        articles:      Lista de dicionários com campos canônicos (lowercase).
        output_path:   Caminho de saída do PRISMA_LOG.csv.
        source_label:  Label da fonte (ex: "wos_excel") para rastreabilidade.
        existing_path: Path de PRISMA_LOG.csv existente para merge.

    Returns:
        (total_gravados, duplicatas_removidas)
    """
    existing_rows: list[dict] = []

    if existing_path and os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normaliza para formato interno (lowercase)
                existing_rows.append({
                    "title": row.get("Title", ""),
                    "authors": row.get("Authors", ""),
                    "year": row.get("Year", ""),
                    "journal": row.get("Journal", ""),
                    "doi": row.get("DOI", ""),
                    "abstract": row.get("Abstract", ""),
                    "status": row.get("Status", "Aguardando Fase 1"),
                    "exclusion_reason": row.get("Exclusion_Reason", ""),
                    "source": row.get("Source", ""),
                })

    all_articles = existing_rows + articles
    unique, removed = deduplicate(all_articles)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PRISMA_FIELDNAMES)
        writer.writeheader()

        for article in unique:
            doi_raw = article.get("doi", "") or article.get("DOI", "")
            writer.writerow({
                "Title":            article.get("title", "") or article.get("Title", ""),
                "Authors":          article.get("authors", "") or article.get("Authors", ""),
                "Year":             article.get("year", "") or article.get("Year", ""),
                "Journal":          article.get("journal", "") or article.get("Journal", ""),
                "DOI":              normalize_doi(doi_raw),
                "Abstract":         article.get("abstract", "") or article.get("Abstract", ""),
                "Status":           article.get("status", "") or article.get("Status", "Aguardando Fase 1"),
                "Exclusion_Reason": article.get("exclusion_reason", "") or article.get("Exclusion_Reason", ""),
                "Source":           article.get("source", source_label),
            })

    return len(unique), removed
