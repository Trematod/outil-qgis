# Préparation des données pour QGIS

Application web locale destinée à préparer et contrôler un fichier Excel parent avant une future intégration dans QGIS.

La partie QGIS est volontairement hors périmètre de cette première version.

## Démarrage

Depuis ce dossier, créer un environnement virtuel puis installer les dépendances :

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Lancer ensuite l'application :

```bash
.venv/bin/python Partie1.py
```

Ouvrir [http://127.0.0.1:8000](http://127.0.0.1:8000) dans un navigateur.

## Distribution Windows portable

Sur l'ordinateur de développement Windows, double-cliquer sur
`build_portable_windows.bat`. Le script utilise Python uniquement pour construire
le package, installe PyInstaller dans `.build-venv`, puis crée `distribution_windows`.

Le dossier final contient l'exécutable, les bibliothèques Python, les ressources
web, `configuration.json`, `start.bat` et `stop.bat`. Il peut être compressé en ZIP
et transmis sans Python, VS Code ou droits administrateur sur le poste utilisateur.

Le collègue doit décompresser le dossier dans un emplacement où il peut écrire,
connecter le lecteur `S:`, puis double-cliquer sur `start.bat`. Les chemins restent
modifiables dans `configuration.json` sans reconstruire l'application.

## Structure

- `Partie1.py` : point d'entrée local.
- `app/main.py` : serveur web FastAPI.
- `app/config.py` : types, colonnes obligatoires et racines serveur.
- `configuration.json` : chemins des racines serveur, modifiables sans reconstruire l'application.
- `app/services/` : modules de lecture, validation, normalisation, matching et export à venir.
- `tests/` : tests automatisés.

## Données existantes

`Jointure.csv` utilise un séparateur `;` et contient des chemins de dossiers Windows. Les caractères accentués doivent être relus avec l'encodage réel du fichier lors de l'implémentation du lecteur. Les fichiers d'entrée principaux de l'application resteront les `.xlsx` prévus dans la spécification.
