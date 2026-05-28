@echo off
REM ===============================================================================
REM Job Hunt Agent Automation Batch Script
REM 
REM This script runs the Job Hunt Agent inside the project's virtual environment.
REM It can be executed directly or scheduled via Windows Task Scheduler.
REM ===============================================================================

SETLOCAL

REM Get the directory where the script is located
SET "PROJECT_DIR=%~dp0"

REM Navigate to the project directory
CD /D "%PROJECT_DIR%"

REM Check if the virtual environment exists
IF NOT EXIST ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found at .venv\
    echo Please create it and run 'pip install -r requirements.txt' first.
    pause
    exit /b 1
)

REM Run the main program with default parameters, passing any command line arguments along
echo [AUTOMATION] Starting Job Scraper Execution...
.venv\Scripts\python.exe main.py --job-title "Frontend Developer" --location "Bangalore" %*

echo [AUTOMATION] Execution finished!
ENDLOCAL
