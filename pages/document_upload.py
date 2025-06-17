
import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
import hashlib
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page
# Add src directory to Python path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from src.storage.evidence_linker import EvidenceLinker
from src.processors.pdf_processor import PDFProcessor
from src.processors.image_processor import ImageProcessor
from src.processors.email_processor import EmailProcessor
from src.processors.text_processor import TextProcessor

st.set_page_config(
    page_title="Document Upload - AI Legal Timeline Builder",
    page_icon="📤",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.upload-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.upload-section h1 {
    margin: 0;
    font-size: 2.5rem;
}

.file-info {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin: 0.5rem 0;
}

.success-upload {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.processing-status {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'evidence_linker' not in st.session_state:
        st.session_state.evidence_linker = EvidenceLinker()
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = {}

def get_file_hash(file_content):
    """Generate hash for file content"""
    return hashlib.md5(file_content).hexdigest()

def process_uploaded_file(uploaded_file, evidence_linker):
    """Process uploaded file based on its type"""
    try:
        file_content = uploaded_file.read()
        file_hash = get_file_hash(file_content)

        # Reset file pointer
        uploaded_file.seek(0)

        # Save file temporarily for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(file_content)
            temp_path = tmp_file.name

        # Store file in evidence storage
        stored_path = evidence_linker.store_file(uploaded_file, temp_path)

        # Process based on file type
        file_ext = Path(uploaded_file.name).suffix.lower()
        processed_text = ""
        metadata = {
            "filename": uploaded_file.name,
            "size": len(file_content),
            "hash": file_hash,
            "upload_time": datetime.now().isoformat(),
            "stored_path": stored_path
        }

        if file_ext == '.pdf':
            processor = PDFProcessor()
            processed_text = processor.extract_text(temp_path)
            metadata["type"] = "PDF Document"

        elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            processor = ImageProcessor()
            processed_text = processor.extract_text(temp_path)
            metadata["type"] = "Image/Screenshot"

        elif file_ext in ['.eml', '.msg']:
            processor = EmailProcessor()
            processed_text = processor.extract_text(temp_path)
            metadata["type"] = "Email"

        elif file_ext in ['.txt', '.docx', '.rtf']:
            processor = TextProcessor()
            processed_text = processor.extract_text(temp_path)
            metadata["type"] = "Text Document"
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        # Clean up temporary file
        os.unlink(temp_path)

        metadata["text_length"] = len(processed_text)
        metadata["word_count"] = len(processed_text.split())

        return {
            "success": True,
            "text": processed_text,
            "metadata": metadata,
            "stored_path": stored_path
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "metadata": {"filename": uploaded_file.name}
        }

def main():
    initialize_session_state()

    # Header
    st.markdown("""
    <div class="upload-section">
        <h1>📤 Document Upload</h1>
        <p>Upload legal documents for AI-powered timeline extraction</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏠 Home"):
            st.switch_page("app.py")
    with col2:
        if st.button("📊 Build Timeline"):
            switch_page("timeline_builder")

    with col3:
        if st.button("📄 Export Reports"):
            st.switch_page("pages/export_manager.py")
    with col4:
        if st.button("⚙️ Settings"):
            st.switch_page("pages/settings.py")

    st.markdown("---")

    # File upload section
    st.markdown("## 📁 Upload Legal Documents")

    # Supported formats info
    with st.expander("📋 Supported File Formats", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Document Formats:**
            - 📄 PDF files (.pdf)
            - 📝 Text files (.txt)
            - 📄 Word documents (.docx)
            - 📄 RTF files (.rtf)
            """)
        with col2:
            st.markdown("""
            **Image Formats:**
            - 🖼️ PNG images (.png)
            - 📸 JPEG images (.jpg, .jpeg)
            - 🖼️ TIFF images (.tiff)
            - 📱 WhatsApp screenshots

            **Email Formats:**
            - 📧 EML files (.eml)
            - 📧 MSG files (.msg)
            """)

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose legal documents to upload",
        accept_multiple_files=True,
        type=['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'txt', 'docx', 'rtf', 'eml', 'msg'],
        help="Upload multiple files at once. Supported formats: PDF, Images, Text, Email files"
    )

    if uploaded_files:
        st.markdown("## 🔄 Processing Files")

        # Process each uploaded file
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in [f["metadata"]["filename"] for f in st.session_state.processed_files.values()]:

                with st.spinner(f"Processing {uploaded_file.name}..."):
                    result = process_uploaded_file(uploaded_file, st.session_state.evidence_linker)

                    if result["success"]:
                        # Store in session state
                        file_id = f"file_{len(st.session_state.processed_files)}"
                        st.session_state.processed_files[file_id] = result

                        st.markdown(f"""
                        <div class="success-upload">
                            <strong>✅ {uploaded_file.name}</strong> processed successfully!<br>
                            📊 Extracted {result['metadata']['word_count']} words from {result['metadata']['text_length']} characters<br>
                            💾 File stored securely with evidence tracking
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Failed to process {uploaded_file.name}: {result['error']}")

    # Display processed files
    if st.session_state.processed_files:
        st.markdown("## 📋 Processed Documents")

        for file_id, file_data in st.session_state.processed_files.items():
            metadata = file_data["metadata"]

            with st.expander(f"📄 {metadata['filename']} ({metadata['type']})", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    **File Information:**
                    - **Type:** {metadata['type']}
                    - **Size:** {metadata['size']:,} bytes
                    - **Words:** {metadata['word_count']:,}
                    - **Upload Time:** {metadata['upload_time'][:19]}
                    """)

                with col2:
                    st.markdown(f"""
                    **Processing Status:**
                    - **Status:** ✅ Ready for Timeline
                    - **Hash:** {metadata['hash'][:16]}...
                    - **Evidence ID:** {file_id}
                    """)

                # Text preview
                if len(file_data["text"]) > 0:
                    st.markdown("**Text Preview:**")
                    preview_text = file_data["text"][:500] + "..." if len(file_data["text"]) > 500 else file_data["text"]
                    st.text_area("Extracted Text", preview_text, height=100, disabled=True, key=f"preview_{file_id}")

                # Download original file
                if st.button(f"⬬ Download Original", key=f"download_{file_id}"):
                    try:
                        with open(metadata['stored_path'], 'rb') as f:
                            st.download_button(
                                label="Download File",
                                data=f.read(),
                                file_name=metadata['filename'],
                                key=f"dl_btn_{file_id}"
                            )
                    except Exception as e:
                        st.error(f"Error downloading file: {e}")

        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑️ Clear All Files", type="secondary"):
                st.session_state.processed_files = {}
                st.rerun()

        with col2:
            file_count = len(st.session_state.processed_files)
            st.metric("Documents Ready", file_count, "Files processed")

        with col3:
            if st.button("➡️ Build Timeline", type="primary", disabled=len(st.session_state.processed_files) == 0):
                st.switch_page("pages/timeline_builder.py")

    else:
        st.info("👆 Upload legal documents above to begin timeline extraction")

if __name__ == "__main__":
    main()
