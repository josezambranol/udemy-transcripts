@echo off
setlocal
cd /d "%~dp0"
title Udemy Transcripts Pro - Centro de Estudio

echo ======================================================================
echo       UDEMY TRANSCRIPTS PRO - CENTRO DE ESTUDIO INTERACTIVO
echo ======================================================================
echo.

set "PY_EXE=python"
if exist "%LOCALAPPDATA%\udemy-transcripts\venv\Scripts\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\udemy-transcripts\venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PY_EXE=venv\Scripts\python.exe"
)

"%PY_EXE%" udemy_transcripts.py --portal seti --chrome %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Finalizado o cancelado. Presiona cualquier tecla para cerrar...
    pause >nul
)
