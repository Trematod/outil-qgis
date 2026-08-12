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

    def find(
        self,
        file_type: str,
        number: str,
        original_number: str | None = None,
    ) -> tuple[ServerFolder, ...]:
        normalized_type = _normalize_file_type(file_type)
        normalized_number = normalize_case_number(number)
        if not normalized_number.usable:
            return ()

        matches: list[ServerFolder] = []
        seen: set[Path] = set()
        lookup_keys = [(normalized_type, normalized_number.value)]

        if original_number is not None:
            raw_original = str(original_number).strip()
            if raw_original and raw_original != normalized_number.value:
                lookup_keys.append((normalized_type, raw_original))

        for key in lookup_keys:
            for folder in self.folders.get(key, ()):  # type: ignore[arg-type]
                if folder.path not in seen:
                    seen.add(folder.path)
                    matches.append(folder)

        return tuple(matches)


def build_server_index(roots: dict[str, Path]) -> ServerIndex:
    """Index only immediate subdirectories and use their second name part."""
    indexed: defaultdict[tuple[str, str], list[ServerFolder]] = defaultdict(list)
    anomalies: list[dict[str, str]] = []

    for file_type, root in roots.items():
        normalized_type = _normalize_file_type(file_type)
        if not root.exists():
            anomalies.append(
                {
                    "type": normalized_type,
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
                    "type": normalized_type,
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
                        "type": normalized_type,
                        "problème": "Nom de sous-dossier sans deuxième partie",
                        "chemin": str(child),
                    }
                )
                continue

            number = normalize_case_number(parts[1])
            if not number.usable:
                anomalies.append(
                    {
                        "type": normalized_type,
                        "problème": "Numéro de sous-dossier inexploitable",
                        "chemin": str(child),
                    }
                )
                continue

            folder = ServerFolder(normalized_type, number.value, child.name, child)
            indexed[(normalized_type, number.value)].append(folder)
            raw_number = parts[1].strip()
            if raw_number != number.value:
                indexed[(normalized_type, raw_number)].append(folder)

    return ServerIndex(
        folders={key: tuple(value) for key, value in indexed.items()},
        anomalies=tuple(anomalies),
    )


def _normalize_file_type(value: str) -> str:
    return str(value).strip().upper()