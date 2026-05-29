#!/usr/bin/env python3
import os
import json
import datetime
from pathlib import Path

def consolidate(session_dir):
    session_path = Path(session_dir)
    master_file = session_path / "CONTEXT.md"
    shards_dir = session_path / "shards"
    registry_file = session_path / "machines.json"
    
    if not shards_dir.exists():
        return "Nenhum shard encontrado para consolidação."

    # Carrega registro para saber o que já foi processado
    registry = {"machines": {}, "last_consolidation": None}
    if registry_file.exists():
        with open(registry_file, "r") as f:
            registry = json.load(f)

    # Coleta todos os shards
    shards = list(shards_dir.glob("CONTEXT-*.md"))
    if not shards:
        return "Nenhum arquivo de shard encontrado."

    # Lê o Master atual
    master_content = ""
    if master_file.exists():
        master_content = master_file.read_text()
    else:
        master_content = "# Contexto de Sessão Consolidado\n\n"

    new_entries = []
    
    for shard in shards:
        mtime = shard.stat().st_mtime
        machine_id = shard.name.replace("CONTEXT-", "").replace(".md", "")
        
        # Verifica se o shard é mais novo que o registro ou se nunca foi processado
        last_processed = registry["machines"].get(machine_id, {}).get("last_consolidated_mtime", 0)
        
        if mtime > last_processed:
            content = shard.read_text()
            # Extrai apenas o conteúdo relevante (remove o header principal se houver)
            # Assume que cada shard é uma entrada de sessão completa
            new_entries.append(f"\n--- \n### 🔄 Integrado de {machine_id} ({datetime.datetime.fromtimestamp(mtime).isoformat()})\n\n{content}")
            
            # Atualiza registro
            if machine_id not in registry["machines"]:
                registry["machines"][machine_id] = {}
            registry["machines"][machine_id]["last_consolidated_mtime"] = mtime

    if new_entries:
        # Insere novas entradas após o título principal
        lines = master_content.split("\n")
        header = lines[0]
        rest = "\n".join(lines[1:])
        
        updated_content = header + "\n" + "\n".join(new_entries) + "\n" + rest
        master_file.write_text(updated_content)
        
        registry["last_consolidation"] = datetime.datetime.now().isoformat()
        with open(registry_file, "w") as f:
            json.dump(registry, f, indent=2)
        
        return f"Consolidação concluída: {len(new_entries)} novos contextos integrados."
    
    return "Tudo atualizado. Nenhuma mudança nova nos shards."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(consolidate(sys.argv[1]))
