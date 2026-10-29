@echo off
chcp 65001 >nul
title Udemy Transcripts Pro - Centro de Estudio y Transcripción
cd /d "%~dp0"

echo ======================================================================
echo             UDEMY TRANSCRIPTS PRO - CENTRO DE ESTUDIO
echo ======================================================================
echo.

set "PY_EXE=python"
if exist "venv\Scripts\python.exe" (
    set "PY_EXE=venv\Scripts\python.exe"
) else if exist "%LOCALAPPDATA%\udemy-transcripts\venv\Scripts\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\udemy-transcripts\venv\Scripts\python.exe"
)

echo Iniciando programa con %PY_EXE%...
echo.
"%PY_EXE%" udemy_transcripts.py
echo.
pause
