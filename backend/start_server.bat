@echo off
cd /d "%~dp0"
echo Iniciando servidor FastAPI en http://127.0.0.1:8000...
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
