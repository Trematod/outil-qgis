"""Lecture et validation des fichiers Excel d'entrée."""

import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import REQUIRED_COLUMNS


ALIASES = {
    "referent see": "Référent SEE",
    "type": "Type",
    "numero de dossier": "Numéro de dossier",
    "n de dossier": "Numéro de dossier",
    "no de dossier": "Numéro de dossier",
    "comm": "Comm.",
    "comm.": "Comm.",
    "libelle": "Libellé",
    "delais serma": "Délais SERMA",
}


class InputFileError(ValueError):
    """Erreur lisible liée à un fichier d'entrée."""


def read_excel_file(path: Path) -> pd.DataFrame:
    """Read one parent workbook and keep only the useful columns."""
    if path.suffix.casefold() != ".xlsx":
        raise InputFileError("Le fichier doit être au format .xlsx")

    try:
        dataframe = pd.read_excel(path, engine="openpyxl")
    except Exception as error:
        raise InputFileError(f"Le fichier est illisible : {error}") from error

    dataframe = _rename_known_columns(dataframe)
    missing = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise InputFileError(f"Colonnes obligatoires absentes : {missing_text}")

    dataframe = dataframe.loc[:, list(REQUIRED_COLUMNS)].copy()
    dataframe["Type"] = dataframe["Type"].astype("string").str.strip().str.upper()
    dataframe["__fichier_source"] = path.name
    dataframe["__ligne_source"] = dataframe.index + 2
    return dataframe


def _rename_known_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    rename_map: dict[Any, str] = {}
    for column in dataframe.columns:
        normalized = _normalize_header(str(column))
        canonical = ALIASES.get(normalized)
        if canonical and canonical not in dataframe.columns:
            rename_map[column] = canonical
    return dataframe.rename(columns=rename_map)


def _normalize_header(value: str) -> str:
    without_accents = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    return re.sub(r"\s+", " ", without_accents.strip().casefold())