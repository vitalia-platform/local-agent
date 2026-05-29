"""
config_manager.py — Carregamento e Validação do criteria_config.yaml

Responsabilidades:
- Carregar o YAML usando yaml.safe_load (nunca parser manual)
- Validar a presença de todos os blocos obrigatórios
- Oferecer menu interativo quando blocos estão ausentes
- Carregar sources_config.yaml com resolução projeto > kit fallback
"""

import sys
import os
import yaml


# Blocos obrigatórios no criteria_config.yaml
REQUIRED_BLOCKS = [
    "study",
    "paths",
    "ollama",
    "processing",
    "criteria",
    "prompt_configuration",
]


def load_config(config_path: str = "./criteria_config.yaml") -> dict:
    """Carrega e valida o criteria_config.yaml. Encerra com orientação se inválido."""
    if not os.path.exists(config_path):
        print(f"\n\033[91m[ERRO] Arquivo de configuração não encontrado: {config_path}\033[0m")
        print("Execute o workflow /integrative-review para gerar o arquivo de configuração.")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"\n\033[91m[ERRO] Falha ao parsear {config_path}: {e}\033[0m")
        sys.exit(1)

    if config is None:
        config = {}

    ok, missing = validate_schema(config)
    if not ok:
        _handle_missing_blocks(missing, config_path)

    return config


def validate_schema(config: dict) -> tuple:
    """Retorna (True, []) se válido ou (False, [blocos ausentes])."""
    missing = [b for b in REQUIRED_BLOCKS if b not in config]
    return len(missing) == 0, missing


def _handle_missing_blocks(missing: list, config_path: str) -> None:
    """Menu interativo quando blocos obrigatórios estão ausentes."""
    print("\n\033[91m╔══════════════════════════════════════════════════════════╗")
    print("║  ERRO: Blocos obrigatórios ausentes no criteria_config    ║")
    print("╚══════════════════════════════════════════════════════════╝\033[0m")
    print(f"\nArquivo: {config_path}")
    print("\nBlocos ausentes:")
    for b in missing:
        print(f"  → \033[93m{b}\033[0m")

    print("\n\033[93mOpções:\033[0m")
    print("  [1] Parar e rodar /integrative-review para gerar os dados ausentes")
    print("  [2] Continuar mesmo assim \033[91m(não recomendado — pode gerar erros)\033[0m")
    print("  [3] Abortar")

    while True:
        choice = input("\nOpção [1/2/3]: ").strip()
        if choice == "1":
            print("\n\033[92m✔ Encerrado. Para criar a configuração completa, use o comando:\033[0m")
            print("   /integrative-review")
            print("\nApós concluir o setup, rode novamente este script.")
            sys.exit(0)
        elif choice == "2":
            print("\n\033[93m⚠ Continuando com configuração incompleta. Erros podem ocorrer.\033[0m")
            return
        elif choice == "3":
            print("\nAbortando.")
            sys.exit(1)
        else:
            print("Opção inválida. Digite 1, 2 ou 3.")


def load_sources_config(project_root: str = ".") -> dict:
    """
    Carrega sources_config.yaml com resolução:
      1. <project_root>/scripts/review_pipeline/sources_config.yaml (projeto)
      2. Fallback: mesmo diretório deste script (kit)
    """
    project_sources = os.path.join(
        project_root, "scripts", "review_pipeline", "sources_config.yaml"
    )
    kit_sources = os.path.join(os.path.dirname(__file__), "..", "sources_config.yaml")

    for path in [project_sources, kit_sources]:
        path = os.path.normpath(path)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return data.get("sources", {})

    print("\033[93m[AVISO] sources_config.yaml não encontrado. Detecção de fonte desativada.\033[0m")
    return {}
