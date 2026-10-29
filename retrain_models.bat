@echo off
cd /d "%~dp0backend"
if not exist "venv\Scripts\python.exe" (
    echo Python environment not found. Run setup.bat first.
    pause
    exit /b 1
)

echo [1/4] Downloading the English matching dataset...
"venv\Scripts\python.exe" -m services.download_datasets || goto :error

echo.
echo [2/4] Cleaning the datasets...
"venv\Scripts\python.exe" -m services.data_preparation || goto :error

echo.
echo [3/4] Training the models (this can take several minutes)...
"venv\Scripts\python.exe" -m services.train_all || goto :error

echo.
echo [4/4] Checking the new models...
"venv\Scripts\python.exe" check_models.py || goto :error

echo.
echo Retraining complete. Restart the backend (run_all.bat) to use the new models.
pause
exit /b 0

:error
echo.
echo Retraining failed. Read the error above.
pause
exit /b 1
