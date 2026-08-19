"""Pipeline principal de préparation des données."""

from pathlib import Path

import pandas as pd

from app.config import SUPPORTED_TYPES
from app.services.duplicates import mark_duplicates
from app.services.excel_reader import read_excel_file
from app.services.normalization import normalize_case_number
from app.services.server_index import ServerIndex, build_server_index


def process_parent_files(
    paths: list[Path],
    server_roots: dict[str, Path],
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """Read, normalize, deduplicate and match one or more parent workbooks."""
    combined = pd.concat([read_excel_file(path) for path in paths], ignore_index=True)
    return _process_combined_dataframe(combined, server_roots)


def process_parent_file(
    path: Path,
    server_roots: dict[str, Path],
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """Read, normalize, deduplicate and match one parent workbook."""
    return process_parent_files([path], server_roots)


def _process_combined_dataframe(
    combined: pd.DataFrame,
    server_roots: dict[str, Path],
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    anomalies: list[dict[str, object]] = []
    combined["Numéro original"] = combined["Numéro de dossier"]
    normalized = combined["Numéro original"].map(normalize_case_number)
    combined["NO"] = normalized.map(lambda item: item.value)
    combined["__numero_utilisable"] = normalized.map(lambda item: item.usable)

    for index, item in normalized.items():
        if not item.usable:
            row = combined.loc[index]
            anomalies.append(
                {
                    "niveau": "Erreur",
                    "problème": item.reason or "Numéro inexploitable",
                    "NO": "",
                    "numéro original": row["Numéro original"],
                    "fichier source": row["__fichier_source"],
                    "ligne source": row["__ligne_source"],
                    "action": "Ligne conservée sans matching",
                }
            )
        elif item.changed:
            row = combined.loc[index]
            anomalies.append(
                {
                    "niveau": "Anomalie",
                    "problème": "Numéro normalisé",
                    "NO": item.value,
                    "numéro original": row["Numéro original"],
                    "fichier source": row["__fichier_source"],
                    "ligne source": row["__ligne_source"],
                    "action": "NO utilisé pour les contrôles et le matching",
                }
            )

    _report_unknown_types(combined, anomalies)
    supported_mask = combined["Type"].notna() & combined["Type"].astype(str).isin(
        SUPPORTED_TYPES
    )
    combined = combined.loc[supported_mask].copy().reset_index(drop=True)

    combined, duplicate_anomalies = mark_duplicates(combined)
    anomalies.extend(duplicate_anomalies)
    server_index = build_server_index(server_roots)
    anomalies.extend(server_index.anomalies)
    _match_server_folders(combined, server_index, anomalies)

    return combined, anomalies


def _report_unknown_types(
    dataframe: pd.DataFrame,
    anomalies: list[dict[str, object]],
) -> None:
    for index, row in dataframe.iterrows():
        file_type = row["Type"]
        if pd.isna(file_type) or str(file_type) not in SUPPORTED_TYPES:
            anomalies.append(
                {
                    "niveau": "Anomalie",
                    "problème": "Type inconnu",
                    "NO": row["NO"],
                    "numéro original": row["Numéro original"],
                    "type": "" if pd.isna(file_type) else file_type,
                    "fichier source": row["__fichier_source"],
                    "ligne source": row["__ligne_source"],
                    "action": "Ligne exclue des données nettoyées",
                }
            )


def _match_server_folders(
    dataframe: pd.DataFrame,
    server_index: ServerIndex,
    anomalies: list[dict[str, object]],
) -> None:
    dataframe["Chemin"] = ""
    dataframe["__dossier_trouve"] = False
    for index, row in dataframe.iterrows():
        if not row["__numero_utilisable"] or row["__statut"] == "Doublon supprimé":
            continue
        if pd.isna(row["Type"]) or str(row["Type"]) not in SUPPORTED_TYPES:
            continue
        matches = server_index.find(str(row["Type"]), row["NO"])
        if len(matches) == 1:
            dataframe.at[index, "Chemin"] = str(matches[0].path)
            dataframe.at[index, "__dossier_trouve"] = True
        elif not matches:
            anomalies.append(
                {
                    "niveau": "Anomalie",
                    "problème": "Dossier introuvable",
                    "NO": row["NO"],
                    "numéro original": row["Numéro original"],
                    "fichier source": row["__fichier_source"],
                    "ligne source": row["__ligne_source"],
                    "action": "Ligne conservée avec Chemin vide",
                }
            )
        else:
            anomalies.append(
                {
                    "niveau": "Anomalie",
                    "problème": "Plusieurs dossiers trouvés",
                    "NO": row["NO"],
                    "numéro original": row["Numéro original"],
                    "fichier source": row["__fichier_source"],
                    "ligne source": row["__ligne_source"],
                    "chemins": " | ".join(str(match.path) for match in matches),
                    "action": "Ligne conservée avec Chemin vide",
                }
            )
