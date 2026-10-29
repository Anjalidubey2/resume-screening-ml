@echo off
cd /d "%~dp0"

echo [1/3] Creating Python 3.11 environment...
if not exist "backend\venv\Scripts\python.exe" (
    py -3.11 -m venv backend\venv || goto :error
)

echo [2/3] Installing Python libraries...
"backend\venv\Scripts\python.exe" -m pip install -r backend\requirements-dev.txt || goto :error

echo [3/3] Installing frontend libraries...
cd frontend
call npm install || goto :error
cd ..

echo.
echo Checking the ML models...
cd backend
"venv\Scripts\python.exe" check_models.py
cd ..

echo.
echo Setup complete. Run run_all.bat to start the app.
pause
exit /b 0

:error
echo.
echo Setup failed. Read the error above.
pause
exit /b 1
