from pathlib import Path

import pandas as pd
import pytest

from app.services.excel_reader import InputFileError, read_excel_file


def test_reads_columns_in_any_order_and_adds_source_metadata(tmp_path: Path) -> None:
    path = tmp_path / "DD.xlsx"
    pd.DataFrame(
        {
            "Comm.": ["Centre"],
            "Numéro de dossier": ["335140/1"],
            "Libellé": ["Projet"],
            "Référent SEE": ["ABC"],
            "Délais SERMA": [12],
            "Type": ["DD"],
            "Colonne supplémentaire": ["valeur"],
        }
    ).to_excel(path, index=False)

    dataframe = read_excel_file(path)

    assert dataframe.loc[0, "Numéro de dossier"] == "335140/1"
    assert dataframe.loc[0, "__fichier_source"] == "DD.xlsx"
    assert dataframe.loc[0, "__ligne_source"] == 2
    assert list(dataframe.columns[:6]) == [
        "Numéro de dossier",
        "Libellé",
        "Comm.",
        "Référent SEE",
        "Type",
        "Délais SERMA",
    ]
    assert "Colonne supplémentaire" not in dataframe.columns


def test_reports_missing_required_columns(tmp_path: Path) -> None:
    path = tmp_path / "DD.xlsx"
    pd.DataFrame({"Type": ["DD"]}).to_excel(path, index=False)

    with pytest.raises(InputFileError, match="Colonnes obligatoires absentes"):
        read_excel_file(path)


def test_normalizes_type_without_replacing_unknown_values(tmp_path: Path) -> None:
    path = tmp_path / "parent.xlsx"
    pd.DataFrame(
        {
            "Numéro de dossier": ["1", "2"],
            "Libellé": ["A", "B"],
            "Comm.": ["Centre", "Nord"],
            "Référent SEE": ["A", "B"],
            "Type": [" dd ", "Autre"],
            "Délais SERMA": [1, 2],
        }
    ).to_excel(path, index=False)

    dataframe = read_excel_file(path)

    assert dataframe["Type"].tolist() == ["DD", "AUTRE"]