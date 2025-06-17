#!/bin/bash
echo "======================================================"
echo "       AI Legal Timeline Builder Pro - Setup"
echo "======================================================"
echo ""

echo "[1/5] Checking Python installation..."
if command -v python3 >/dev/null 2>&1 ; then
    python3 --version
else
    echo "ERROR: Python 3.8 or higher is required but not found."
    echo "Please install Python using your package manager:"
    echo "  Ubuntu: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python"
    exit 1
fi
echo "Python installation verified."
echo ""

echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created successfully."
fi
echo ""

echo "[3/5] Activating virtual environment and installing dependencies..."
source venv/bin/activate

echo "Installing required packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install required packages."
    exit 1
fi
echo "Dependencies installed successfully."
echo ""

echo "[4/5] Downloading spaCy model..."
python -m spacy download en_core_web_sm
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to download spaCy model."
    exit 1
fi
echo "spaCy model downloaded successfully."
echo ""

echo "[5/5] Checking Tesseract OCR installation..."
if command -v tesseract >/dev/null 2>&1 ; then
    tesseract --version | head -n 1
else
    echo "WARNING: Tesseract OCR is not found in PATH."
    echo ""
    echo "To install Tesseract OCR:"
    echo "  Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-hin"
    echo "  macOS: brew install tesseract tesseract-lang"
    echo ""
    echo "After installing, run this setup script again."
    echo ""
fi
echo ""

echo "====================================================="
echo "            Setup completed successfully!            "
echo "====================================================="
echo ""
echo "To start the application:"
echo "1. Activate the virtual environment (if not already):"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the application:"
echo "   streamlit run app.py"
echo ""
echo "3. Configure Hugging Face API token in the Settings"
echo "   panel (required for Legal-BERT models)"
echo ""
echo "Enjoy using AI Legal Timeline Builder Pro!"
echo ""
