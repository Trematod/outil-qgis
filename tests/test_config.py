from app.config import SUPPORTED_TYPES, load_server_roots


def test_ps_is_supported_and_configured() -> None:
    assert "PS" in SUPPORTED_TYPES

    roots = load_server_roots()
    assert "PS" in roots
    assert str(roots["PS"]).endswith("PS")
