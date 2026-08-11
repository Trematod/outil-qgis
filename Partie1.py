"""Point d'entrée de l'application locale de préparation des données."""

import uvicorn

from app.config import SERVER_ROOTS, _configuration_path
from app.main import app
from app.services.server_index import build_server_index


def print_startup_diagnostic() -> None:
	"""Display the external configuration used by the packaged application."""
	print("CONFIGURATION CHARGEE :")
	print(_configuration_path())
	print()
	for file_type in ("DD", "PLQ", "MZ", "RAE", "PDZI"):
		print(f"{file_type} = {SERVER_ROOTS[file_type]}")

	dd_root = SERVER_ROOTS["DD"]
	try:
		dd_exists = dd_root.exists()
		subfolder_count = sum(1 for child in dd_root.iterdir() if child.is_dir()) if dd_exists else 0
	except OSError as error:
		dd_exists = False
		subfolder_count = 0
		print(f"Erreur de lecture de la racine DD : {error}")

	print()
	print(f"DD existe : {dd_exists}")
	print(f"Nombre de sous-dossiers DD : {subfolder_count}")

	target_folder = dd_root / "DD 342701 BHNS St-Genis"
	print(f"Dossier DD 342701 BHNS St-Genis existe : {target_folder.exists()}")

	server_index = build_server_index({"DD": dd_root})
	indexed_key = ("DD", "342701")
	print(f"Cle {indexed_key!r} presente dans l'index : {indexed_key in server_index.folders}")
	if indexed_key in server_index.folders:
		for folder in server_index.folders[indexed_key]:
			print(f"Dossier indexe : {folder.path}")
	print()


if __name__ == "__main__":
	print_startup_diagnostic()
	uvicorn.run(
		app,
		host="127.0.0.1",
		port=8000,
		reload=False,
	)
