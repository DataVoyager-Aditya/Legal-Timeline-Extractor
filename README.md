# AI Legal Timeline Builder Pro

<div align="center">

![Legal Timeline Builder](https://img.shields.io/badge/Legal-Timeline%20Builder-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen?style=for-the-badge)
![Legal-BERT](https://img.shields.io/badge/Legal--BERT-AI%20Powered-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Professional AI-powered legal document analysis and timeline extraction system**

🚀 **Legal-BERT Integration** • 📄 **Multi-format Support** • 🔗 **Evidence Linking** • 📊 **Professional Reports**

</div>

---

## 🎯 Overview

AI Legal Timeline Builder Pro is a cutting-edge system that automatically extracts chronological timelines from legal documents using advanced AI technology. Built specifically for legal professionals, it processes PDFs, images, WhatsApp screenshots, emails, and text files to create comprehensive case timelines with evidence linking.

### 🌟 Key Features

- **🧠 Legal-BERT AI Integration**: Uses specialized Legal-BERT models optimized for legal text analysis
- **📁 Multi-Format Document Processing**: PDFs, images, emails, Word docs, text files
- **🔗 Evidence Linking**: Every timeline event links to its source document with page-level precision
- **📊 Professional Export**: Generate court-ready reports in PDF, Excel, Word, and JSON formats
- **🎯 Confidence Scoring**: AI-powered reliability indicators for each extracted event
- **🇮🇳 Indian Legal Support**: Specialized patterns for Indian legal documents and IPC sections
- **📱 WhatsApp Chat Analysis**: Extract timelines from messaging screenshots
- **🔍 Advanced OCR**: High-accuracy text extraction from scanned documents

---

## 🚀 Quick Start Guide

### Step 1: System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 8GB minimum (16GB recommended for large documents)
- **Storage**: 5GB free space for models and processing

### Step 2: Install Tesseract OCR

#### Windows
1. Download Tesseract installer from [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to default location (`C:\Program Files\Tesseract-OCR`)
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

#### macOS
```bash
brew install tesseract
brew install tesseract-lang  # For additional languages
```

#### Ubuntu/Linux
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-hin tesseract-ocr-ben  # Indian languages
```

### Step 3: Setup Application

#### Automated Setup (Recommended)

**Windows:**
```cmd
# Extract the ZIP file
# Double-click setup.bat
# Or run in Command Prompt:
setup.bat
```

**Linux/macOS:**
```bash
# Extract the ZIP file
chmod +x setup.sh
./setup.sh
```

#### Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Create environment file
echo "HF_TOKEN=your_huggingface_token_here" > .env
```

### Step 4: Get Hugging Face API Token (FREE)

1. Visit [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create account (free) if you don't have one
3. Click "New token" → Select "Read" access
4. Copy the token (starts with `hf_...`)
5. Add to `.env` file: `HF_TOKEN=hf_your_actual_token_here`

### Step 5: Launch Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📖 Complete Setup Instructions

### Environment Setup

1. **Extract ZIP File**
   ```bash
   unzip ai_legal_timeline_builder_final.zip
   cd ai_legal_timeline_builder_final
   ```

2. **Python Virtual Environment**
   ```bash
   # Create isolated environment
   python -m venv venv

   # Activate (Windows)
   venv\Scripts\activate

   # Activate (Linux/macOS)
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Install all required packages
   pip install -r requirements.txt

   # Download spaCy English model
   python -m spacy download en_core_web_sm
   ```

### Configuration

1. **API Token Setup**
   - Create `.env` file in project root
   - Add your Hugging Face token:
     ```
     HF_TOKEN=hf_your_token_here
     ```

2. **Tesseract Configuration**
   - Ensure Tesseract is installed and in PATH
   - Test with: `tesseract --version`

3. **Model Download**
   - Legal-BERT models download automatically on first use
   - Requires ~1-3GB storage depending on model

### Verification

Test your installation:
```bash
# Check Python version
python --version  # Should be 3.8+

# Check Tesseract
tesseract --version

# Check Streamlit
streamlit --version

# Launch application
streamlit run app.py
```

---

## 🎯 How to Use

### 1. Upload Documents
- Click "📤 Upload Documents"
- Drag and drop or select files
- Supported formats: PDF, PNG, JPG, DOCX, TXT, EML, MSG
- Multiple files can be processed simultaneously

### 2. Build Timeline
- Navigate to "📊 Build Timeline"
- Select Legal-BERT model (recommended: InLegalBERT for Indian law)
- Set confidence threshold (0.5 recommended)
- Click "🚀 Extract Timeline"

### 3. Review Results
- View timeline in table, card, or chart format
- Filter by confidence level, date range, or source files
- Click evidence links to download source documents
- Verify and validate extracted events

### 4. Export Reports
- Go to "📄 Export Reports"
- Choose format: PDF (court-ready), Excel (analysis), Word (editable), JSON (data)
- Customize export settings
- Download professional reports

---

## 📁 Project Structure

```
ai_legal_timeline_builder_final/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── setup.bat / setup.sh           # Automated setup scripts
├── README.md                       # This file
├── .env                           # Environment variables (create this)
│
├── pages/                         # Streamlit pages
│   ├── document_upload.py         # File upload interface
│   ├── timeline_builder.py        # AI timeline extraction
│   ├── export_manager.py          # Report generation
│   └── settings.py                # System configuration
│
├── src/                           # Core application modules
│   ├── processors/                # Document processors
│   │   ├── pdf_processor.py       # PDF text extraction
│   │   ├── image_processor.py     # OCR and image processing
│   │   ├── email_processor.py     # Email parsing
│   │   └── text_processor.py      # Text file processing
│   │
│   ├── extractors/                # AI extraction engines
│   │   └── legal_bert_extractor.py # Legal-BERT timeline extraction
│   │
│   ├── exporters/                 # Report generators
│   │   ├── pdf_exporter.py        # PDF report generation
│   │   ├── excel_exporter.py      # Excel workbook creation
│   │   └── word_exporter.py       # Word document generation
│   │
│   ├── storage/                   # Data management
│   │   └── evidence_linker.py     # Evidence tracking system
│   │
│   └── utils/                     # Utilities
│       └── config.py              # Configuration management
│
├── data/                          # Sample data and test files
├── assets/                        # Static resources
└── tests/                         # Test suites
```

---

## 🔧 Advanced Configuration

### Legal-BERT Models

Choose the appropriate model for your documents:

| Model | Best For | Size | Speed |
|-------|----------|------|-------|
| `nlpaueb/legal-bert-base-uncased` | International legal documents | 440MB | Fast |
| `law-ai/InLegalBERT` | Indian legal system (IPC, CrPC) | 440MB | Fast |
| `pile-of-law/legalbert-large-1.7M-2` | High accuracy analysis | 1.3GB | Slower |

### Processing Parameters

Optimize for your use case:
- **Confidence Threshold**: 0.3-0.8 (lower = more events, higher = more accurate)
- **Max Events**: 50-500 (limit per document)
- **OCR Languages**: Add Hindi, Bengali, Tamil, etc. for multilingual documents

### Export Customization

Configure default export settings:
- Include/exclude confidence scores
- Add organization logo to reports
- Custom footer text
- Watermark settings

---

## 📊 Supported Document Types

### Legal Documents
- **FIR Reports**: Automatic extraction of complaint details
- **Court Orders**: Hearing dates, judgments, directives
- **Legal Agreements**: Contract execution, amendments
- **Police Records**: Investigation timelines, arrest details
- **Notice Documents**: Service dates, legal notices

### Communication Records
- **WhatsApp Chats**: Message timestamps and parties
- **Email Threads**: Communication chronology
- **Call Records**: When available in document form

### Evidence Files
- **Scanned Documents**: OCR with high accuracy
- **Photographs**: Text extraction from images
- **Screenshots**: Social media, messaging apps

---

## 🛠️ Troubleshooting

### Common Issues

**1. Tesseract Not Found**
```bash
# Windows: Add to PATH
set PATH=%PATH%;C:\Program Files\Tesseract-OCR

# Linux: Install package
sudo apt install tesseract-ocr

# macOS: Use Homebrew
brew install tesseract
```

**2. Legal-BERT Model Loading Error**
- Check your Hugging Face token is valid
- Ensure internet connection for model download
- Verify available disk space (1-3GB per model)

**3. Poor OCR Results**
- Increase image resolution before upload
- Ensure good contrast and lighting in scanned documents
- Enable image preprocessing in settings

**4. Timeline Not Generating**
- Lower confidence threshold in settings
- Check if documents contain recognizable dates and events
- Try different Legal-BERT models

**5. Export Files Corrupted**
- Check available disk space
- Ensure write permissions in project directory
- Try exporting fewer events or smaller files

### Getting Help

1. **Check Logs**: Enable debug mode in settings
2. **Verify Installation**: Run `python -c "import streamlit; print('OK')"`
3. **Test Components**: Use sample documents provided
4. **Update Dependencies**: `pip install -r requirements.txt --upgrade`

---

## 🎯 Best Practices

### Document Preparation
- **Scan Quality**: 300 DPI minimum for scanned documents
- **File Names**: Use descriptive names (e.g., "FIR_Case123_2024.pdf")
- **Organization**: Group related documents by case
- **Format**: Convert images to PDF when possible for better text extraction

### Timeline Review
- **Verify Dates**: Check extracted dates for accuracy
- **Validate Events**: Confirm event descriptions match source documents
- **Evidence Links**: Test download links to ensure proper file storage
- **Confidence Scores**: Focus on events with >70% confidence

### Report Generation
- **Professional Format**: Use PDF for court submissions
- **Analysis Format**: Use Excel for detailed case analysis
- **Collaboration**: Use Word format for team review and editing
- **Data Integration**: Use JSON for case management systems

---

## 🔒 Security and Privacy

### Data Protection
- **Local Processing**: All analysis happens on your machine
- **No Cloud Storage**: Documents never leave your system
- **Secure Storage**: Evidence files stored with hash verification
- **Access Control**: File system permissions protect sensitive data

### Legal Compliance
- **Chain of Custody**: Complete evidence tracking and metadata preservation
- **Audit Trail**: All processing activities logged
- **Source Attribution**: Every timeline event linked to original documents
- **Integrity Verification**: SHA-256 hashing ensures file integrity

---

## 📈 System Requirements

### Minimum Requirements
- **CPU**: Dual-core 2.5GHz processor
- **RAM**: 8GB (4GB available for processing)
- **Storage**: 10GB free space
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04

### Recommended Requirements
- **CPU**: Quad-core 3.0GHz processor (Intel i7 or AMD Ryzen 7)
- **RAM**: 16GB (8GB available for processing)
- **Storage**: 25GB free space (SSD recommended)
- **GPU**: CUDA-compatible GPU for faster AI processing (optional)

### Performance Optimization
- **GPU Acceleration**: Install CUDA for faster Legal-BERT processing
- **SSD Storage**: Improves model loading and file processing speed
- **Memory**: More RAM allows processing larger document sets
- **Internet**: Required for initial model downloads only

---

## 🤝 Support and Updates

### Getting Support
- **Documentation**: Comprehensive guides in `/docs` folder
- **Sample Files**: Test documents in `/data` folder
- **Configuration**: Settings panel with tooltips and help text
- **Troubleshooting**: Built-in diagnostic tools

### Version Information
- **Current Version**: 2.0.0
- **Python Compatibility**: 3.8, 3.9, 3.10, 3.11
- **Last Updated**: 2024
- **License**: MIT License

---

## 📄 License

MIT License - See LICENSE file for details.

---

<div align="center">

**🎉 Ready to revolutionize your legal document analysis!**

*Built with ❤️ for legal professionals worldwide*

</div>
