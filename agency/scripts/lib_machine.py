#!/usr/bin/env python3
import os
import json
import uuid
import datetime
from pathlib import Path

def get_machine_id():
    # Tenta ler ID global do usuário ou local do projeto
    global_config = Path.home() / ".vitalia" / "machine_id"
    if global_config.exists():
        return global_config.read_text().strip()
    
    # Se não existe, gera um novo
    new_id = str(uuid.uuid4())[:8] # ID curto para facilidade
    global_config.parent.mkdir(parents=True, exist_ok=True)
    global_config.write_text(new_id)
    return new_id

def update_machine_registry(session_dir, machine_id, name=None, status=None, activity=None):
    registry_path = Path(session_dir) / "machines.json"
    data = {"machines": {}}
    
    if registry_path.exists():
        try:
            with open(registry_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass

    now = datetime.datetime.now().isoformat()
    
    if machine_id not in data["machines"]:
        data["machines"][machine_id] = {
            "name": name or f"Machine-{machine_id}",
            "first_seen": now
        }
    
    data["machines"][machine_id]["last_seen"] = now
    if name: data["machines"][machine_id]["name"] = name
    if status: data["machines"][machine_id]["status"] = status
    if activity is not None: data["machines"][machine_id]["activity"] = activity

    with open(registry_path, "w") as f:
        json.dump(data, f, indent=2)
    
    return data["machines"][machine_id]

def get_status_report(session_dir):
    registry_path = Path(session_dir) / "machines.json"
    if not registry_path.exists():
        return "Nenhum registro de máquina encontrado."
    
    try:
        with open(registry_path, "r") as f:
            data = json.load(f)
    except:
        return "Erro ao ler registro."

    report = ["### 🚥 Status Global das Máquinas\n"]
    report.append("| Máquina | Status | Atividade | Último Sinal |")
    report.append("| :--- | :--- | :--- | :--- |")
    
    for mid, info in data["machines"].items():
        status_emoji = "🟢 IDLE" if info.get("status") == "IDLE" else "🔴 BUSY"
        activity = info.get("activity", "-")
        last_seen = info.get("last_seen", "N/A").split("T")[0]
        report.append(f"| {info['name']} ({mid}) | {status_emoji} | {activity} | {last_seen} |")
    
    return "\n".join(report)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--get-id":
        print(get_machine_id())
    elif len(sys.argv) > 1 and sys.argv[1] == "--status-report":
        print(get_status_report(sys.argv[2]))
    elif len(sys.argv) > 3 and sys.argv[1] == "--register":
        # Argumentos: session_dir, machine_id, name, status, activity
        update_machine_registry(
            sys.argv[2], 
            sys.argv[3], 
            sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "None" else None,
            sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != "None" else None,
            sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != "None" else None
        )
