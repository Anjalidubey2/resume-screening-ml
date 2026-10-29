@echo off
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo Frontend libraries not found. Run setup.bat first.
    pause
    exit /b 1
)
npm run dev
