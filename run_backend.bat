@echo off
cd /d "%~dp0backend"
if not exist "venv\Scripts\python.exe" (
    echo Python environment not found. Run setup.bat first.
    pause
    exit /b 1
)
"venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
