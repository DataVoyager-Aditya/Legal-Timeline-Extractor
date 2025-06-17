
import streamlit as st
import sys
import os
from pathlib import Path
from streamlit_extras.switch_page_button import switch_page

# Add src directory to Python path for imports
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Configure the Streamlit page
st.set_page_config(
    page_title="AI Legal Timeline Builder Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }

    /* Feature cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #2a5298;
    }

    .feature-card h3 {
        color: #1e3c72;
        margin-top: 0;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.5rem 0;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(42, 82, 152, 0.3);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Remove Streamlit watermarks */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom success/info boxes */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Load custom CSS
    load_custom_css()

    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ AI Legal Timeline Builder Pro</h1>
        <p>Powered by Legal-BERT • Professional Document Analysis • Evidence Tracking</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📤 Upload Documents", key="upload_btn"):
            switch_page("document_upload")

    with col2:
        if st.button("📊 Build Timeline", key="timeline_btn"):
            switch_page("timeline_builder")

    with col3:
        if st.button("📄 Export Reports", key="export_btn"):
            switch_page("export_manager")

    with col4:
        if st.button("⚙️ Settings", key="settings_btn"):
            switch_page("settings")
    # Feature overview
    st.markdown("## 🚀 Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🧠 Legal-BERT AI Analysis</h3>
            <p>Advanced natural language processing using specialized Legal-BERT models for Indian and international legal documents. Extracts events, dates, people, and legal entities with high accuracy.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>🔗 Evidence Linking</h3>
            <p>Every timeline event is linked to its source document with page-level precision. Download original files directly from timeline entries to verify evidence.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📁 Multi-Format Support</h3>
            <p>Process PDFs, images, WhatsApp screenshots, emails (.eml/.msg), and text files. Advanced OCR for scanned documents and handwritten text.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-card">
            <h3>📈 Professional Reports</h3>
            <p>Generate court-ready reports in PDF, Excel, Word, and JSON formats. Include evidence citations, confidence scores, and comprehensive timelines.</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick start guide
    st.markdown("## 🎯 Quick Start Guide")

    st.markdown("""
    <div class="info-box">
        <strong>Step 1:</strong> Click "📤 Upload Documents" to add your legal files<br>
        <strong>Step 2:</strong> Go to "📊 Build Timeline" to process documents with Legal-BERT AI<br>
        <strong>Step 3:</strong> Review extracted events and evidence links<br>
        <strong>Step 4:</strong> Export professional reports using "📄 Export Reports"
    </div>
    """, unsafe_allow_html=True)

    # System status
    st.markdown("## 📊 System Status")

    status_col1, status_col2, status_col3, status_col4 = st.columns(4)

    with status_col1:
        st.metric("Legal-BERT Models", "3 Active", "✅ Ready")

    with status_col2:
        st.metric("Supported Formats", "6 Types", "PDF, IMG, EMAIL")

    with status_col3:
        st.metric("Export Options", "4 Formats", "PDF, XLSX, DOCX, JSON")

    with status_col4:
        st.metric("Processing Speed", "Fast", "GPU Accelerated")

if __name__ == "__main__":
    main()
