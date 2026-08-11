from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


project_root = Path(SPEC).parent

template_files = [
    (str(project_root / "app" / "templates" / "upload.html"), "app/templates"),
    (str(project_root / "app" / "templates" / "result.html"), "app/templates"),
]
static_files = [
    (str(project_root / "app" / "static" / "styles.css"), "app/static"),
    (str(project_root / "app" / "static" / "app.js"), "app/static"),
]

a = Analysis(
    [str(project_root / "Partie1.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=template_files + static_files,
    hiddenimports=collect_submodules("uvicorn"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "httpx"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="PreparationDonnees",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    exclude_binaries=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="PreparationDonnees",
)
