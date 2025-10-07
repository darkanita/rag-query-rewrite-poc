@echo off
REM Startup script for RAG Query Rewrite POC (Windows)

echo ==========================================
echo RAG Query Rewrite POC - Setup Script
echo ==========================================
echo.

REM Check Python installation
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo.
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Created .env file
    echo.
    echo IMPORTANT: Please edit .env and add your OPENAI_API_KEY
    echo Press any key to continue after updating .env...
    pause >nul
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist data\vector_store mkdir data\vector_store
if not exist logs mkdir logs
echo Directories created

REM Check if OpenAI API key is set
echo.
echo Checking configuration...
findstr "your_openai_api_key_here" .env >nul
if %errorlevel% equ 0 (
    echo WARNING: OpenAI API key not set in .env file!
    echo Please update OPENAI_API_KEY in .env before running the application
) else (
    echo Configuration looks good
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Ensure your OpenAI API key is set in .env
echo 2. Run examples: python example.py
echo 3. Start API server: python api.py
echo 4. Or use Docker: docker-compose up -d
echo.
echo For more information, see README.md
echo.
pause
