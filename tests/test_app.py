from fastapi.testclient import TestClient
from io import BytesIO

import pandas as pd

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Préparer les données" in response.text


def test_process_requires_a_file() -> None:
    response = client.post("/process", files={})

    assert response.status_code == 400
    assert "Sélectionnez un fichier Excel source" in response.text


def test_process_accepts_one_parent_workbook() -> None:
    workbook = BytesIO()
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

    response = client.post(
        "/process",
        files={"source_file": ("parent.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )

    assert response.status_code == 200
    assert "Lignes analysées" in response.text
    assert "Fichier(s) traité(s)" in response.text
    assert "parent.xlsx" in response.text


def test_process_accepts_multiple_parent_workbooks() -> None:
    workbook_a = BytesIO()
    pd.DataFrame(
        {
            "Numéro de dossier": ["123"],
            "Libellé": ["Projet A"],
            "Comm.": ["Centre"],
            "Référent SEE": ["A"],
            "Type": ["AUTRE"],
            "Délais SERMA": [1],
        }
    ).to_excel(workbook_a, index=False)

    workbook_b = BytesIO()
    pd.DataFrame(
        {
            "Numéro de dossier": ["456"],
            "Libellé": ["Projet B"],
            "Comm.": ["Nord"],
            "Référent SEE": ["B"],
            "Type": ["AUTRE"],
            "Délais SERMA": [2],
        }
    ).to_excel(workbook_b, index=False)

    response = client.post(
        "/process",
        files=[
            ("source_file", ("parent_a.xlsx", workbook_a.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
            ("source_file", ("parent_b.xlsx", workbook_b.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
        ],
    )

    assert response.status_code == 200
    assert "Lignes analysées" in response.text
    assert "Fichier(s) traité(s)" in response.text
    assert "parent_a.xlsx" in response.text
    assert "parent_b.xlsx" in response.text
