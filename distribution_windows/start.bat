@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "APP_DIR=%~dp0"
set "VENV_DIR=%~dp0.venv"
set "PID_FILE=%~dp0.server.pid"
set "URL=http://127.0.0.1:8000"

where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON=py -3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERREUR : Python 3 est introuvable.
        echo Installez Python 3 puis relancez start.bat.
        pause
        exit /b 1
    )
    set "PYTHON=python"
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Premiere utilisation : creation de l'environnement local...
    %PYTHON% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERREUR : impossible de creer l'environnement Python.
        echo Verifiez que Python inclut le module venv.
        pause
        exit /b 1
    )
)

echo Verification des dependances...
"%VENV_DIR%\Scripts\python.exe" -m pip install --disable-pip-version-check --quiet -r requirements.txt
if errorlevel 1 (
    echo ERREUR : installation des dependances impossible.
    echo Verifiez la connexion Internet ou contactez votre support informatique.
    pause
    exit /b 1
)

if not exist "%APP_DIR%configuration.json" (
    echo ERREUR : configuration.json est absent.
    pause
    exit /b 1
)

echo Verification des chemins serveur...
"%VENV_DIR%\Scripts\python.exe" -c "import json; from pathlib import Path; c=json.load(open('configuration.json', encoding='utf-8')); missing=[f'{k}: {v}' for k,v in c.get('server_roots', {}).items() if not Path(v).exists()]; print('ATTENTION : certains chemins serveur sont inaccessibles :'); [print('  - '+p) for p in missing]; print('Le traitement reste possible, mais les dossiers correspondants seront signales comme introuvables.') if missing else print('Tous les chemins serveur sont accessibles.')"

if exist "%PID_FILE%" (
    set /p OLD_PID=<"%PID_FILE%"
    tasklist /FI "PID eq %OLD_PID%" | find "%OLD_PID%" >nul 2>&1
    if not errorlevel 1 (
        echo L'application est deja demarree sur %URL%.
        start "" %URL%
        exit /b 0
    )
    del "%PID_FILE%" >nul 2>&1
)

echo Demarrage de l'application...
for /f "usebackq delims=" %%p in (`powershell -NoProfile -Command "$p=Start-Process -FilePath '%VENV_DIR%\Scripts\python.exe' -ArgumentList 'Partie1.py' -WorkingDirectory '%APP_DIR%' -PassThru; $p.Id"`) do set "SERVER_PID=%%p"
if not defined SERVER_PID (
    echo ERREUR : impossible de demarrer le serveur.
    pause
    exit /b 1
)
echo %SERVER_PID%>"%PID_FILE%"

for /L %%i in (1,1,30) do (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r=Invoke-WebRequest -UseBasicParsing %URL%/health -TimeoutSec 1; if ($r.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>&1
    if not errorlevel 1 goto ready
    ping 127.0.0.1 -n 2 >nul
)

echo ERREUR : le serveur n'a pas demarre.
echo Consultez application.log si le fichier existe.
pause
exit /b 1

:ready
echo Application demarree : %URL%
start "" %URL%
echo Pour arreter l'application, double-cliquez sur stop.bat.
exit /b 0
