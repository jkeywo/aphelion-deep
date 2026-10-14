@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -m aphelion_deep.multiplayer --open
if errorlevel 1 pause
