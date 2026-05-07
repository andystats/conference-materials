@echo off
cd /d "%~dp0"
py -3.13 -m shiny run --port 8000 app.py
if errorlevel 1 python -m shiny run --port 8000 app.py
