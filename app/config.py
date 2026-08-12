"""Configuration centrale de l'application."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SUPPORTED_TYPES = ("DD", "PLQ", "MZ", "RAE", "PDZI", "PS")
REQUIRED_COLUMNS = (
    "Numéro de dossier",
    "Libellé",
    "Comm.",
    "Référent SEE",
    "Type",
    "Délais SERMA",
)

DEFAULT_SERVER_ROOTS = {
    "DD": Path(r"S:\UO5196\50\_SERMA\04\_SECTEUR\_EE\02\_EVAL\_ENVIRO\DD"),
    "PLQ": Path(r"S:\UO5196\50\_SERMA\04\_SECTEUR\_EE\02\_EVAL\_ENVIRO\PLQ"),
    "MZ": Path(r"S:\UO5196\50\_SERMA\04\_EE\02\_EVAL\_ENVIRO\MZ"),
    "RAE": Path(r"S:\UO5196\50\_SERMA\04\_SECTEUR\_EE\02\_EVAL\_ENVIRO\RAE"),
    "PDZI": Path(r"S:\UO5196\50\_SERMA\04\_SECTEUR\_EE\02\_EVAL\_ENVIRO\PDZI"),
    "PS": Path(r"S:\UO5196\50\_SERMA\04\_SECTEUR\_EE\02\_EVAL\_ENVIRO\PS"),
}


def _configuration_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "configuration.json"
    return PROJECT_ROOT / "configuration.json"


def load_server_roots() -> dict[str, Path]:
    configuration_path = _configuration_path()
    if not configuration_path.exists():
        return DEFAULT_SERVER_ROOTS.copy()
    try:
        configuration = json.loads(configuration_path.read_text(encoding="utf-8"))
        configured_roots = configuration.get("server_roots", {})
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SERVER_ROOTS.copy()

    roots = DEFAULT_SERVER_ROOTS.copy()
    roots.update(
        {
            file_type: Path(value)
            for file_type, value in configured_roots.items()
            if file_type in SUPPORTED_TYPES and isinstance(value, str) and value.strip()
        }
    )
    return roots


SERVER_ROOTS = load_server_roots()


def server_root_status() -> dict[str, bool]:
    return {file_type: path.exists() for file_type, path in SERVER_ROOTS.items()}
