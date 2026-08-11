@echo off
setlocal
cd /d "%~dp0"
taskkill /IM PreparationDonnees.exe /T /F >nul 2>&1
if errorlevel 1 (echo L'application n'etait pas demarree.) else (echo Application arretee.)
pause
