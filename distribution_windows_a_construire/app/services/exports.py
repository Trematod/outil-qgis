"""Génération des fichiers de sortie."""

from pathlib import Path

import pandas as pd


OUTPUT_COLUMNS = (
    "Numéro de dossier",
    "NO",
    "Libellé",
    "Comm.",
    "Référent SEE",
    "Type",
    "Délais SERMA",
    "Chemin",
)


def export_results(
    dataframe: pd.DataFrame,
    anomalies: list[dict[str, object]],
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned = dataframe[dataframe["__statut"] != "Doublon supprimé"].copy()
    cleaned = cleaned.loc[:, list(OUTPUT_COLUMNS)]
    report = pd.DataFrame(anomalies)

    excel_path = output_dir / "donnees_nettoyees.xlsx"
    report_path = output_dir / "rapport_anomalies.xlsx"
    csv_path = output_dir / "donnees_qgis.csv"
    cleaned.to_excel(excel_path, index=False)
    report.to_excel(report_path, index=False)
    cleaned.to_csv(csv_path, index=False, sep=";", encoding="utf-8-sig")
    return {"excel": excel_path, "rapport": report_path, "csv": csv_path}