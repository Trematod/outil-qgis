"""Indexation des dossiers serveur par type et numéro normalisé."""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from app.services.normalization import normalize_case_number


@dataclass(frozen=True)
class ServerFolder:
    file_type: str
    number: str
    name: str
    path: Path


@dataclass(frozen=True)
class ServerIndex:
    folders: dict[tuple[str, str], tuple[ServerFolder, ...]]
    anomalies: tuple[dict[str, str], ...]

    def find(self, file_type: str, number: str) -> tuple[ServerFolder, ...]:
        return self.folders.get((file_type, number), ())


def build_server_index(roots: dict[str, Path]) -> ServerIndex:
    """Index only immediate subdirectories and use their second name part."""
    indexed: defaultdict[tuple[str, str], list[ServerFolder]] = defaultdict(list)
    anomalies: list[dict[str, str]] = []

    for file_type, root in roots.items():
        if not root.exists():
            anomalies.append(
                {
                    "type": file_type,
                    "problème": "Racine serveur inaccessible",
                    "chemin": str(root),
                }
            )
            continue

        try:
            children = sorted(root.iterdir(), key=lambda item: item.name.casefold())
        except OSError as error:
            anomalies.append(
                {
                    "type": file_type,
                    "problème": "Lecture de la racine serveur impossible",
                    "chemin": str(root),
                    "détail": str(error),
                }
            )
            continue

        for child in children:
            if not child.is_dir():
                continue
            parts = child.name.split()
            if len(parts) < 2:
                anomalies.append(
                    {
                        "type": file_type,
                        "problème": "Nom de sous-dossier sans deuxième partie",
                        "chemin": str(child),
                    }
                )
                continue

            number = normalize_case_number(parts[1])
            if not number.usable:
                anomalies.append(
                    {
                        "type": file_type,
                        "problème": "Numéro de sous-dossier inexploitable",
                        "chemin": str(child),
                    }
                )
                continue

            folder = ServerFolder(file_type, number.value, child.name, child)
            indexed[(file_type, number.value)].append(folder)

    return ServerIndex(
        folders={key: tuple(value) for key, value in indexed.items()},
        anomalies=tuple(anomalies),
    )