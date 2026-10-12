@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -m aphelion_deep.play --open
pause
