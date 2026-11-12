"""Exporte le schéma OpenAPI de l'API dans docs/openapi.json.

Usage :
    python export_openapi.py

Ne nécessite ni Ollama ni base vectorielle : le schéma est lu dans le code.
À relancer après toute modification des routes ou des modèles de api.py.
"""

import json
from pathlib import Path

import api

OUTPUT = Path(__file__).resolve().parent / "docs" / "openapi.json"


def main() -> None:
    OUTPUT.write_text(json.dumps(api.app.openapi(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Schéma OpenAPI écrit dans {OUTPUT}")


if __name__ == "__main__":
    main()
