from pathlib import Path

from app.services.server_index import build_server_index


def test_indexes_second_folder_name_part(tmp_path: Path) -> None:
    root = tmp_path / "DD"
    root.mkdir()
    matching = root / "DD 335140 Bois Brûlé"
    matching.mkdir()
    (root / "DD autre dossier 335140").mkdir()

    index = build_server_index({"DD": root})

    matches = index.find("DD", "335140")
    assert len(matches) == 1
    assert matches[0].path == matching


def test_reports_missing_root_and_duplicate_matches(tmp_path: Path) -> None:
    root = tmp_path / "DD"
    root.mkdir()
    (root / "DD 13-232 A").mkdir()
    (root / "DD 13232 B").mkdir()

    index = build_server_index({"DD": root, "PLQ": tmp_path / "missing"})

    assert len(index.find("DD", "13232")) == 2
    assert any(item["type"] == "PLQ" for item in index.anomalies)


def test_matching_normalizes_type_and_number_at_lookup(tmp_path: Path) -> None:
    root = tmp_path / "DD"
    (root / "DD 342701 BHNS St-Genis").mkdir(parents=True)

    index = build_server_index({" dd ": root})

    matches = index.find(" dd ", "342-701")
    assert len(matches) == 1
    assert matches[0].name == "DD 342701 BHNS St-Genis"