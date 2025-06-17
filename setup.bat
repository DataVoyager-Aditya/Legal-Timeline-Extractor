@echo off
echo ======================================================
echo        AI Legal Timeline Builder Pro - Setup
echo ======================================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.8 or higher is required but not found.
    echo Please install Python from https://www.python.org/downloads/
    echo and make sure it's added to PATH.
    pause
    exit /b 1
)
echo Python installation verified.
echo.

echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)
echo.

echo [3/5] Activating virtual environment and installing dependencies...
call venv\Scripts\activate

echo Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

echo [4/5] Downloading spaCy model...
python -m spacy download en_core_web_sm
if %errorlevel% neq 0 (
    echo ERROR: Failed to download spaCy model.
    pause
    exit /b 1
)
echo spaCy model downloaded successfully.
echo.

echo [5/5] Checking Tesseract OCR installation...
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Tesseract OCR is not found in PATH.
    echo.
    echo To install Tesseract OCR:
    echo 1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Install to default location (C:\Program Files\Tesseract-OCR)
    echo 3. Add to PATH: C:\Program Files\Tesseract-OCR
    echo.
    echo After installing, run this setup script again.
    echo.
) else (
    echo Tesseract OCR installation verified.
)
echo.

echo =====================================================
echo             Setup completed successfully!            
echo =====================================================
echo.
echo To start the application:
echo 1. Activate the virtual environment (if not already):
echo    venv\Scripts\activate
echo.
echo 2. Run the application:
echo    streamlit run app.py
echo.
echo 3. Configure Hugging Face API token in the Settings
echo    panel (required for Legal-BERT models)
echo.
echo Enjoy using AI Legal Timeline Builder Pro!
echo.
pause
