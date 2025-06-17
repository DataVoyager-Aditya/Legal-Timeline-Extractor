
import streamlit as st
import sys
from pathlib import Path
import json

# Add src directory to Python path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from src.utils.config import Config

st.set_page_config(
    page_title="Settings - AI Legal Timeline Builder",
    page_icon="⚙️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.settings-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.setting-section {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 1rem 0;
    border-left: 4px solid #667eea;
}

.api-key-info {
    background: #e7f3ff;
    border: 1px solid #b8daff;
    color: #004085;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.success-save {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'config' not in st.session_state:
        st.session_state.config = Config()

def main():
    initialize_session_state()

    # Header
    st.markdown("""
    <div class="settings-header">
        <h1>⚙️ System Settings</h1>
        <p>Configure AI models, processing parameters, and system preferences</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏠 Home"):
            st.switch_page("app.py")
    with col2:
        if st.button("📤 Upload Documents"):
            st.switch_page("pages/document_upload.py")
    with col3:
        if st.button("📊 Build Timeline"):
            st.switch_page("pages/timeline_builder.py")
    with col4:
        if st.button("📄 Export Reports"):
            st.switch_page("pages/export_manager.py")

    st.markdown("---")

    # API Configuration
    st.markdown("## 🔑 API Configuration")

    st.markdown("""
    <div class="api-key-info">
        <strong>🔐 Hugging Face API Setup</strong><br>
        1. Visit <a href="https://huggingface.co/settings/tokens" target="_blank">Hugging Face Settings</a><br>
        2. Create a new token with "Read" access<br>
        3. Copy the token (starts with "hf_")<br>
        4. Paste it below to enable Legal-BERT models
    </div>
    """, unsafe_allow_html=True)

    # API Key input
    current_token = st.session_state.config.get_huggingface_token()
    token_display = current_token[:10] + "..." if current_token and len(current_token) > 10 else ""

    api_key = st.text_input(
        "Hugging Face API Token",
        value=token_display,
        type="password",
        help="Required for Legal-BERT models. Get your free token from Hugging Face."
    )

    if st.button("💾 Save API Token"):
        if api_key and api_key.startswith("hf_"):
            st.session_state.config.set_huggingface_token(api_key)
            st.markdown("""
            <div class="success-save">
                ✅ API token saved successfully! Legal-BERT models are now available.
            </div>
            """, unsafe_allow_html=True)
        elif api_key:
            st.error("❌ Invalid token format. Token should start with 'hf_'")
        else:
            st.warning("⚠️ Please enter a valid Hugging Face token")

    # Model Configuration
    st.markdown("## 🧠 AI Model Settings")

    with st.container():
        st.markdown("""
        <div class="setting-section">
            <h3>Legal-BERT Model Selection</h3>
            <p>Choose the most appropriate model for your legal documents</p>
        </div>
        """, unsafe_allow_html=True)

        model_options = [
            ("nlpaueb/legal-bert-base-uncased", "General Legal Documents", "Best for international legal text"),
            ("law-ai/InLegalBERT", "Indian Legal Documents", "Optimized for Indian legal system"),
            ("pile-of-law/legalbert-large-1.7M-2", "Large Legal Corpus", "High accuracy, slower processing")
        ]

        current_model = st.session_state.config.get_default_model()

        model_choice = st.radio(
            "Select Legal-BERT Model:",
            options=[opt[0] for opt in model_options],
            format_func=lambda x: next(opt[1] for opt in model_options if opt[0] == x),
            index=[opt[0] for opt in model_options].index(current_model) if current_model in [opt[0] for opt in model_options] else 0
        )

        # Display model description
        model_desc = next(opt[2] for opt in model_options if opt[0] == model_choice)
        st.info(f"ℹ️ {model_desc}")

        if st.button("🔄 Update Model"):
            st.session_state.config.set_default_model(model_choice)
            st.success(f"✅ Model updated to: {model_choice}")

    # Processing Parameters
    st.markdown("## 🔧 Processing Parameters")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="setting-section">
            <h3>Timeline Extraction</h3>
        </div>
        """, unsafe_allow_html=True)

        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.config.get_confidence_threshold(),
            step=0.1,
            help="Minimum confidence score for including events in timeline"
        )

        max_events = st.number_input(
            "Maximum Events per Document",
            min_value=10,
            max_value=1000,
            value=st.session_state.config.get_max_events(),
            step=10,
            help="Limit number of events extracted from each document"
        )

        enable_fuzzy_matching = st.checkbox(
            "Enable Fuzzy Date Matching",
            value=st.session_state.config.get_fuzzy_matching(),
            help="Allow approximate date matching for better extraction"
        )

    with col2:
        st.markdown("""
        <div class="setting-section">
            <h3>OCR Settings</h3>
        </div>
        """, unsafe_allow_html=True)

        ocr_languages = st.multiselect(
            "OCR Languages",
            options=["eng", "hin", "ben", "tam", "tel", "mar", "guj"],
            default=st.session_state.config.get_ocr_languages(),
            help="Languages for text recognition in images"
        )

        image_preprocessing = st.checkbox(
            "Enable Image Preprocessing",
            value=st.session_state.config.get_image_preprocessing(),
            help="Apply filters and enhancements before OCR"
        )

        ocr_confidence = st.slider(
            "OCR Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.config.get_ocr_confidence(),
            step=0.1,
            help="Minimum confidence for OCR text recognition"
        )

    # Export Settings
    st.markdown("## 📄 Export Settings")

    with st.container():
        st.markdown("""
        <div class="setting-section">
            <h3>Default Export Options</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            include_confidence = st.checkbox(
                "Include Confidence Scores",
                value=st.session_state.config.get_include_confidence(),
                help="Show confidence scores in exports"
            )

            include_metadata = st.checkbox(
                "Include File Metadata",
                value=st.session_state.config.get_include_metadata(),
                help="Add file information to exports"
            )

        with col2:
            include_evidence = st.checkbox(
                "Include Evidence Links",
                value=st.session_state.config.get_include_evidence(),
                help="Add evidence citations to exports"
            )

            watermark_reports = st.checkbox(
                "Watermark Reports",
                value=st.session_state.config.get_watermark_reports(),
                help="Add system watermark to generated reports"
            )

        with col3:
            report_logo = st.file_uploader(
                "Organization Logo",
                type=['png', 'jpg', 'jpeg'],
                help="Upload logo for report headers"
            )

            custom_footer = st.text_input(
                "Custom Footer Text",
                value=st.session_state.config.get_custom_footer(),
                help="Add custom text to report footers"
            )

    # Save Settings
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💾 Save All Settings", type="primary"):
            # Update configuration
            st.session_state.config.update_settings({
                'confidence_threshold': confidence_threshold,
                'max_events': max_events,
                'fuzzy_matching': enable_fuzzy_matching,
                'ocr_languages': ocr_languages,
                'image_preprocessing': image_preprocessing,
                'ocr_confidence': ocr_confidence,
                'include_confidence': include_confidence,
                'include_metadata': include_metadata,
                'include_evidence': include_evidence,
                'watermark_reports': watermark_reports,
                'custom_footer': custom_footer
            })

            st.success("✅ Settings saved successfully!")

    with col2:
        if st.button("🔄 Reset to Defaults"):
            st.session_state.config.reset_to_defaults()
            st.success("✅ Settings reset to defaults!")
            st.rerun()

    with col3:
        if st.button("📤 Export Settings"):
            settings_json = st.session_state.config.export_settings()
            st.download_button(
                label="⬇️ Download Settings",
                data=settings_json,
                file_name="timeline_builder_settings.json",
                mime="application/json"
            )

    # System Information
    st.markdown("## 📊 System Information")

    with st.expander("🖥️ View System Status", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Legal-BERT Models:**")
            models_available = st.session_state.config.get_available_models()
            for model in models_available:
                status = "✅" if model == model_choice else "⚪"
                st.markdown(f"{status} {model}")

        with col2:
            st.markdown("**System Capabilities:**")
            st.markdown("✅ PDF Processing")
            st.markdown("✅ Image OCR")
            st.markdown("✅ Email Processing")
            st.markdown("✅ Evidence Linking")
            st.markdown("✅ Multi-format Export")

if __name__ == "__main__":
    main()
