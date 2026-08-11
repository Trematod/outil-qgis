@echo off
setlocal
cd /d "%~dp0"
set "PID_FILE=%~dp0.server.pid"

if not exist "%PID_FILE%" (
    echo L'application n'est pas demarree.
    pause
    exit /b 0
)

set /p SERVER_PID=<"%PID_FILE%"
taskkill /PID %SERVER_PID% /T /F >nul 2>&1
if errorlevel 1 (
    echo Le serveur n'etait plus actif.
) else (
    echo Application arretee.
)
del "%PID_FILE%" >nul 2>&1
pause
