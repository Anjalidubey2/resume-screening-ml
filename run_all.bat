@echo off
start "Resume Screening Backend" cmd /k ""%~dp0run_backend.bat""
start "Resume Screening Frontend" cmd /k ""%~dp0run_frontend.bat""
echo Waiting for the servers to start...
timeout /t 8 /nobreak >nul
start "" http://127.0.0.1:5173
