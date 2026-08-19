from pathlib import Path

import pandas as pd

from app.services.processing import process_parent_file, process_parent_files


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


def test_processing_accepts_multiple_workbooks(tmp_path: Path) -> None:
    workbook_a = tmp_path / "A.xlsx"
    pd.DataFrame(
        {
            "Référent SEE": ["A"],
            "Libellé": ["Projet A"],
            "Délais SERMA": [1],
            "Type": ["DD"],
            "Numéro de dossier": ["335140"],
            "Comm.": ["Centre"],
        }
    ).to_excel(workbook_a, index=False)

    workbook_b = tmp_path / "B.xlsx"
    pd.DataFrame(
        {
            "Référent SEE": ["B"],
            "Libellé": ["Projet B"],
            "Délais SERMA": [2],
            "Type": ["DD"],
            "Numéro de dossier": ["999"],
            "Comm.": ["Nord"],
        }
    ).to_excel(workbook_b, index=False)

    root = tmp_path / "DD_root"
    root.mkdir()
    (root / "DD 335140 Bois Brûlé").mkdir()

    dataframe, anomalies = process_parent_files([workbook_a, workbook_b], {"DD": root})

    assert list(dataframe["__fichier_source"]) == ["A.xlsx", "B.xlsx"]
    assert dataframe.loc[0, "Chemin"] == str(root / "DD 335140 Bois Brûlé")
    assert dataframe.loc[1, "Chemin"] == ""
    assert any(item["problème"] == "Dossier introuvable" for item in anomalies)


def test_unknown_type_is_excluded_and_reported(tmp_path: Path) -> None:
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

    assert dataframe.empty
    assert any(
        item["problème"] == "Type inconnu"
        and item["type"] == "AUTRE"
        and item["action"] == "Ligne exclue des données nettoyées"
        for item in anomalies
    )


def test_unknown_type_is_excluded_before_duplicate_detection(tmp_path: Path) -> None:
    workbook = tmp_path / "parent.xlsx"
    pd.DataFrame(
        {
            "Numéro de dossier": ["123456", "123456"],
            "Libellé": ["Projet PAP", "Projet DD"],
            "Comm.": ["Centre", "Centre"],
            "Référent SEE": ["A", "B"],
            "Type": ["PAP", "DD"],
            "Délais SERMA": [1, 2],
        }
    ).to_excel(workbook, index=False)
    root = tmp_path / "DD_root"
    root.mkdir()

    dataframe, anomalies = process_parent_file(workbook, {"DD": root})

    assert len(dataframe) == 1
    assert dataframe.loc[0, "Type"] == "DD"
    assert dataframe.loc[0, "NO"] == "123456"
    assert dataframe.loc[0, "__statut"] != "Doublon supprimé"
    assert any(
        item["problème"] == "Type inconnu" and item["type"] == "PAP"
        for item in anomalies
    )
    assert not any(item["problème"] == "Doublon" for item in anomalies)
