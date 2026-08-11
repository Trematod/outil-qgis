@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
    echo ERREUR : Python est necessaire uniquement sur l'ordinateur qui construit le package.
    pause
    exit /b 1
)

if not exist ".build-venv\Scripts\python.exe" (
    py -3 -m venv .build-venv
    if errorlevel 1 goto failed
)

call ".build-venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip
call ".build-venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt -r requirements-build.txt
if errorlevel 1 goto failed

call ".build-venv\Scripts\python.exe" -m PyInstaller --clean --noconfirm PreparationDonnees.spec
if errorlevel 1 goto failed

if exist "distribution_windows" rmdir /s /q "distribution_windows"
mkdir "distribution_windows"
robocopy "dist\PreparationDonnees" "distribution_windows" /E /NFL /NDL /NJH /NJS >nul
copy /y "configuration.json" "distribution_windows\configuration.json" >nul
copy /y "portable_start.bat" "distribution_windows\start.bat" >nul
copy /y "portable_stop.bat" "distribution_windows\stop.bat" >nul
copy /y "README_PORTABLE_WINDOWS.txt" "distribution_windows\README_UTILISATEUR.txt" >nul

echo.
echo Package portable cree dans : %~dp0distribution_windows
echo Vous pouvez compresser ce dossier en ZIP.
pause
exit /b 0

:failed
echo.
echo ERREUR : la construction du package a echoue.
pause
exit /b 1
