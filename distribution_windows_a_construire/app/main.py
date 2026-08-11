"""Serveur web local de l'application."""

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import SERVER_ROOTS, server_root_status
from app.services.excel_reader import InputFileError
from app.services.exports import export_results
from app.services.processing import process_parent_file


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
app = FastAPI(
    title="Préparation des données QGIS",
    description="Préparation locale de données Excel avant une future intégration QGIS.",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/downloads", StaticFiles(directory=OUTPUT_DIR), name="downloads")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={"server_status": server_root_status()},
    )


@app.post("/process", response_class=HTMLResponse)
async def process_upload(request: Request) -> HTMLResponse:
    form = await request.form()
    upload = form.get("source_file")

    if upload is None or not getattr(upload, "filename", ""):
        return templates.TemplateResponse(
            request=request,
            name="upload.html",
                context={
                    "error": "Sélectionnez un fichier Excel source.",
                    "server_status": server_root_status(),
                },
            status_code=400,
        )

    with TemporaryDirectory() as temporary_directory:
        filename = Path(upload.filename).name
        path = Path(temporary_directory) / filename
        path.write_bytes(await upload.read())
        try:
            dataframe, anomalies = process_parent_file(path, SERVER_ROOTS)
        except InputFileError as error:
            return templates.TemplateResponse(
                request=request,
                name="upload.html",
                context={
                    "error": str(error),
                    "filename": upload.filename,
                    "server_status": server_root_status(),
                },
                status_code=400,
            )

    paths = export_results(dataframe, anomalies, OUTPUT_DIR)
    analyzed = len(dataframe)
    kept_mask = dataframe["__statut"] != "Doublon supprimé"
    kept = int(kept_mask.sum())
    found = int((kept_mask & dataframe["__dossier_trouve"]).sum())
    summary = {
        "lignes_analysees": analyzed,
        "lignes_conservees": kept,
        "doublons": analyzed - kept,
        "dossiers_trouves": found,
        "dossiers_introuvables": kept - found,
        "anomalies": len(anomalies),
    }
    downloads = {key: f"/downloads/{path.name}" for key, path in paths.items()}
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"summary": summary, "downloads": downloads, "filename": upload.filename},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
