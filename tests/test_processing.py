from pathlib import Path

import pandas as pd

from app.services.processing import process_parent_file


def test_processing_keeps_original_and_matches_by_type_and_number(tmp_path: Path) -> None:
    workbook = tmp_path / "DD.xlsx"
    pd.DataFrame(
        {
            "Référent SEE": ["A", "B"],
            "Libellé": ["A", "B"],
            "Délais SERMA": [1, 2],
            "Type": ["DD", "DD"],
            "Numéro de dossier": ["335140/1", "999"],
            "Comm.": ["Centre", "Nord"],
        }
    ).to_excel(workbook, index=False)
    root = tmp_path / "DD_root"
    root.mkdir()
    matching = root / "DD 335140 Bois Brûlé"
    matching.mkdir()

    dataframe, anomalies = process_parent_file(workbook, {"DD": root})

    assert dataframe.loc[0, "Numéro original"] == "335140/1"
    assert dataframe.loc[0, "NO"] == "335140"
    assert dataframe.loc[0, "Chemin"] == str(matching)
    assert dataframe.loc[1, "Chemin"] == ""
    assert bool(dataframe.loc[0, "__dossier_trouve"]) is True
    assert any(item["problème"] == "Dossier introuvable" for item in anomalies)


def test_unknown_type_is_kept_and_reported(tmp_path: Path) -> None:
    workbook = tmp_path / "parent.xlsx"
    pd.DataFrame(
        {
            "Numéro de dossier": ["123"],
            "Libellé": ["Projet"],
            "Comm.": ["Centre"],
            "Référent SEE": ["A"],
            "Type": ["AUTRE"],
            "Délais SERMA": [1],
        }
    ).to_excel(workbook, index=False)

    dataframe, anomalies = process_parent_file(workbook, {})

    assert len(dataframe) == 1
    assert dataframe.loc[0, "Chemin"] == ""
    assert any(item["problème"] == "Type inconnu" for item in anomalies)