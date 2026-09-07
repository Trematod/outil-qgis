from app.config import SUPPORTED_TYPES, load_server_roots


def test_supported_types_are_configured() -> None:
    assert SUPPORTED_TYPES == (
        "DD",
        "PLQ",
        "MZ",
        "RAE",
        "PDZI",
        "PS",
        "PE",
        "PDZDAM",
    )

    roots = load_server_roots()
    assert set(roots) == set(SUPPORTED_TYPES)
    for file_type in SUPPORTED_TYPES:
        assert str(roots[file_type]).endswith(file_type)
