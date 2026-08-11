"""Détection déterministe des doublons sur le numéro normalisé."""

import pandas as pd


def mark_duplicates(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """Keep the first usable occurrence and report every later occurrence."""
    result = dataframe.copy()
    result["__statut"] = "Conservée"
    anomalies: list[dict[str, object]] = []
    seen: set[str] = set()

    for index, row in result.iterrows():
        number = row["NO"]
        if not row["__numero_utilisable"]:
            continue
        if number in seen:
            result.at[index, "__statut"] = "Doublon supprimé"
            anomalies.append(
                {
                    "niveau": "Anomalie",
                    "problème": "Doublon",
                    "NO": number,
                    "numéro original": row["Numéro original"],
                    "fichier source": row["__fichier_source"],
                    "ligne source": row["__ligne_source"],
                    "action": "Ligne écartée ; première occurrence conservée",
                }
            )
        else:
            seen.add(number)

    return result, anomalies