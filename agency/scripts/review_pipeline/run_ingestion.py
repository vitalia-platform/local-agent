"""
run_ingestion.py — Entrypoint de Ingestão: Exports → PRISMA_LOG.csv

Uso:
    python run_ingestion.py [--config ./criteria_config.yaml] [--project-root .]

Fluxo:
    1. Carrega criteria_config.yaml e sources_config.yaml
    2. Localiza todos os CSVs na pasta raw_export (suporte a múltiplos arquivos)
    3. Para cada CSV: detecta a fonte, lê os registros, normaliza
    4. Consolida tudo, deduplica e gera saida/PRISMA_LOG.csv
"""

import argparse
import csv
import glob
import os
import sys

# Garante que o pacote core seja encontrado quando rodado diretamente
sys.path.insert(0, os.path.dirname(__file__))

from core.config_manager import load_config, load_sources_config
from core.ingestion.source_detector import (
    detect_source,
    build_canonical_row,
    warn_abstract_unavailable,
)
from core.ingestion.normalizer import to_prisma_log


def _read_csv(file_path: str, delimiter: str, encoding: str) -> tuple[list[str], list[dict]]:
    """Lê um CSV com o delimitador e encoding especificados. Retorna (fieldnames, rows)."""
    try:
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            fieldnames = list(reader.fieldnames or [])
            rows = [dict(r) for r in reader]
        return fieldnames, rows
    except Exception as e:
        print(f"  \033[91m[ERRO] Falha ao ler {file_path}: {e}\033[0m")
        return [], []


def _try_detect(file_path: str, sources: dict) -> tuple[str, dict, list[dict]]:
    """
    Tenta detectar a fonte e ler os registros. Experimenta os delimitadores
    mais comuns se o primeiro detectado resultar em 0 colunas.
    """
    candidate_delimiters = [",", "\t", ";"]

    for delim in candidate_delimiters:
        fieldnames, rows = _read_csv(file_path, delim, "utf-8-sig")
        if not fieldnames and delim == ",":
            fieldnames, rows = _read_csv(file_path, delim, "utf-8")
        if len(fieldnames) > 2:
            source_id, column_map = detect_source(fieldnames, sources)
            if source_id != "unknown":
                return source_id, column_map, rows
            # Fonte desconhecida mas arquivo legível — guarda para fallback
            last_fieldnames, last_rows, last_delim = fieldnames, rows, delim

    # Fallback: tenta com o delimitador que deu mais colunas
    try:
        source_id, column_map = detect_source(last_fieldnames, sources)
        return source_id, column_map, last_rows
    except Exception:
        return "unknown", {}, []


def process_file(file_path: str, sources: dict) -> tuple[list[dict], str]:
    """
    Processa um único arquivo CSV de exportação.

    Returns:
        (lista de registros canônicos, source_id detectado)
    """
    print(f"\n  Arquivo: \033[96m{os.path.basename(file_path)}\033[0m")

    source_id, column_map, rows = _try_detect(file_path, sources)

    if source_id == "unknown" or not column_map:
        print(f"  \033[93m[AVISO] Fonte não reconhecida. Tentando mapeamento genérico.\033[0m")
        # Fallback genérico: tenta detectar colunas por aliases conhecidos
        column_map = _generic_fallback_map(list(rows[0].keys()) if rows else [])

    source_profile = sources.get(source_id, {})
    print(f"  Fonte detectada: \033[92m{source_profile.get('name', source_id)}\033[0m")
    print(f"  Registros lidos: {len(rows)}")

    warn_abstract_unavailable(source_id, sources)

    canonical_rows = []
    for row in rows:
        cr = build_canonical_row(row, column_map)
        if cr.get("title"):
            cr["source"] = source_id
            canonical_rows.append(cr)

    print(f"  Registros válidos (com título): {len(canonical_rows)}")
    return canonical_rows, source_id


def _generic_fallback_map(fieldnames: list[str]) -> dict:
    """Mapeamento genérico de último recurso baseado em aliases comuns."""
    title_aliases = ["title", "article title", "document title", "record title"]
    abstract_aliases = ["abstract", "summary"]
    doi_aliases = ["doi"]
    year_aliases = ["year", "publication year", "pubdate(year)"]
    journal_aliases = ["source title", "source", "journal", "publication title"]
    author_aliases = ["authors", "author"]

    result = {}
    lower_fields = {f.lower(): f for f in fieldnames}

    for canon, aliases in [
        ("title", title_aliases),
        ("abstract", abstract_aliases),
        ("doi", doi_aliases),
        ("year", year_aliases),
        ("journal", journal_aliases),
        ("authors", author_aliases),
    ]:
        for alias in aliases:
            if alias in lower_fields:
                result[canon] = lower_fields[alias]
                break

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Ingestion Pipeline: converte exports de bases acadêmicas → PRISMA_LOG.csv"
    )
    parser.add_argument(
        "--config",
        default="./criteria_config.yaml",
        help="Caminho para o criteria_config.yaml (default: ./criteria_config.yaml)",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Raiz do projeto para resolver sources_config.yaml (default: .)",
    )
    args = parser.parse_args()

    # 1. Carregar configurações
    config = load_config(args.config)
    sources = load_sources_config(args.project_root)

    if not sources:
        print("\033[93m[AVISO] Nenhum perfil de fonte carregado. Detecção automática desativada.\033[0m")

    # 2. Localizar CSVs de exportação
    raw_export_dir = config.get("paths", {}).get("raw_export", "exportacao")
    csv_pattern = os.path.join(raw_export_dir, "*.csv")
    csv_files = sorted(glob.glob(csv_pattern))

    if not csv_files:
        print(f"\n\033[91m[ERRO] Nenhum arquivo CSV encontrado em: {raw_export_dir}\033[0m")
        print("Deposite os exports das bases de dados nesta pasta e rode novamente.")
        sys.exit(1)

    print(f"\n\033[94m{'═'*60}\033[0m")
    print(f"\033[94m  INGESTÃO DE DADOS — {len(csv_files)} arquivo(s) encontrado(s)\033[0m")
    print(f"\033[94m{'═'*60}\033[0m")

    # 3. Processar cada arquivo
    all_articles: list[dict] = []
    sources_used: list[str] = []

    for file_path in csv_files:
        articles, source_id = process_file(file_path, sources)
        all_articles.extend(articles)
        if source_id not in sources_used:
            sources_used.append(source_id)

    # 4. Consolidar e gerar PRISMA_LOG.csv
    output_dir = config.get("paths", {}).get("output_prisma", "saida")
    output_path = os.path.join(output_dir, "PRISMA_LOG.csv")

    # Merge com PRISMA_LOG existente se houver
    existing_path = output_path if os.path.exists(output_path) else None
    if existing_path:
        print(f"\n  \033[93m[INFO] PRISMA_LOG.csv existente detectado. Fazendo merge...\033[0m")

    total, removed = to_prisma_log(
        all_articles,
        output_path,
        source_label=",".join(sources_used),
        existing_path=existing_path,
    )

    # 5. Relatório final
    print(f"\n\033[94m{'═'*60}\033[0m")
    print(f"\033[92m  INGESTÃO CONCLUÍDA\033[0m")
    print(f"\033[94m{'═'*60}\033[0m")
    print(f"  Total de registros lidos:       {len(all_articles)}")
    print(f"  Duplicatas removidas:           {removed}")
    print(f"  Artigos únicos no PRISMA_LOG:   \033[92m{total}\033[0m")
    print(f"  Arquivo gerado:                 {output_path}")
    print(f"  Fontes processadas:             {', '.join(sources_used)}")
    print(f"\033[94m{'═'*60}\033[0m\n")


if __name__ == "__main__":
    main()
