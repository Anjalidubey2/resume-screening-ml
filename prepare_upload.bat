@echo off
rem Copies only the files that belong on GitHub into a clean folder next to this project.
set "DEST=%~dp0..\resume-screening-ml-github"

robocopy "%~dp0." "%DEST%" /MIR /NFL /NDL /NJH /NP ^
    /XD venv node_modules dist __pycache__ .pytest_cache .claude .ipynb_checkpoints .vite versions ^
        dataset_1_resumes dataset_2_resume_job_matching dataset_2_resume_job_fit dataset_3_ai_screening ^
        processed feedback ^
    /XF *.pyc *.log model_registry.json resume_rankings_*.csv
if %ERRORLEVEL% GEQ 8 (
    echo Copy failed.
    pause
    exit /b 1
)

echo.
for /f %%N in ('dir /s /b /a-d "%DEST%" ^| find /c /v ""') do echo %%N files ready in: %DEST%
echo Drag the CONTENTS of that folder onto your GitHub repository's "Add file > Upload files" page.
pause
exit /b 0
