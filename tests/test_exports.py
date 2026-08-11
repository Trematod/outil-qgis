from pathlib import Path

import pandas as pd

from app.services.exports import OUTPUT_COLUMNS, export_results


def test_exports_only_the_stable_qgis_columns(tmp_path: Path) -> None:
    dataframe = pd.DataFrame(
        {
            "Numéro de dossier": ["335140/1"],
            "NO": ["335140"],
            "Libellé": ["Projet"],
            "Comm.": ["Centre"],
            "Référent SEE": ["A"],
            "Type": ["DD"],
            "Délais SERMA": [1],
            "Chemin": [r"S:\DD 335140 Projet"],
            "__fichier_source": ["parent.xlsx"],
            "__statut": ["Conservée"],
            "__dossier_trouve": [True],
            "__numero_utilisable": [True],
        }
    )

    paths = export_results(dataframe, [], tmp_path)

    exported = pd.read_excel(paths["excel"])
    csv_exported = pd.read_csv(paths["csv"], sep=";", encoding="utf-8-sig")
    assert list(exported.columns) == list(OUTPUT_COLUMNS)
    assert list(csv_exported.columns) == list(OUTPUT_COLUMNS)