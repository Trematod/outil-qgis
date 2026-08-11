@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PID_FILE=%~dp0.server.pid"
set "URL=http://127.0.0.1:8000"

if not exist "%~dp0PreparationDonnees.exe" (
    echo ERREUR : PreparationDonnees.exe est absent.
    pause
    exit /b 1
)
if not exist "%~dp0configuration.json" (
    echo ERREUR : configuration.json est absent.
    pause
    exit /b 1
)

if exist "%PID_FILE%" (
    set /p OLD_PID=<"%PID_FILE%"
    tasklist /FI "PID eq %OLD_PID%" | find "%OLD_PID%" >nul 2>&1
    if not errorlevel 1 (
        echo L'application est deja demarree.
        start "" %URL%
        exit /b 0
    )
    del "%PID_FILE%" >nul 2>&1
)

for /f "usebackq delims=" %%p in (`powershell -NoProfile -Command "$p=Start-Process -FilePath '%~dp0PreparationDonnees.exe' -WorkingDirectory '%~dp0' -PassThru; $p.Id"`) do set "SERVER_PID=%%p"
if not defined SERVER_PID (
    echo ERREUR : impossible de demarrer l'application.
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
echo Consultez la fenetre noire de l'application pour le detail.
pause
exit /b 1

:ready
echo Application demarree : %URL%
start "" %URL%
echo Pour arreter l'application, double-cliquez sur stop.bat.
exit /b 0
