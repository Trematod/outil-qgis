from app.services.normalization import normalize_case_number


def test_normalizes_slash_and_preserves_original() -> None:
    result = normalize_case_number(" 335140/1 ")

    assert result.original == " 335140/1 "
    assert result.value == "335140"
    assert result.changed is True
    assert result.usable is True


def test_removes_ascii_and_unicode_dashes() -> None:
    assert normalize_case_number("13-232").value == "13232"
    assert normalize_case_number("18–232").value == "18232"
    assert normalize_case_number("415—242").value == "415242"


def test_rejects_empty_values() -> None:
    result = normalize_case_number(" - ")

    assert result.value == ""
    assert result.usable is False
    assert result.reason == "Numéro vide"


def test_rejects_missing_values() -> None:
    assert normalize_case_number(None).usable is False