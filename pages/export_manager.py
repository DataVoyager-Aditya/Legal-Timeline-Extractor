
import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
from io import BytesIO

# Add src directory to Python path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from src.exporters.pdf_exporter import PDFExporter
from src.exporters.excel_exporter import ExcelExporter
from src.exporters.word_exporter import WordExporter

st.set_page_config(
    page_title="Export Manager - AI Legal Timeline Builder",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.export-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.export-option {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 1rem 0;
    border-left: 4px solid #667eea;
}

.export-option:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}

.format-description {
    color: #6c757d;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

.export-summary {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.success-export {
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
    if 'timeline_events' not in st.session_state:
        st.session_state.timeline_events = []
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = {}

def export_to_pdf(timeline_events, metadata):
    """Export timeline to PDF format"""
    try:
        exporter = PDFExporter()
        pdf_buffer = exporter.create_timeline_report(timeline_events, metadata)

        return pdf_buffer.getvalue(), "timeline_report.pdf"

    except Exception as e:
        st.error(f"Error creating PDF: {e}")
        return None, None

def export_to_excel(timeline_events, metadata):
    """Export timeline to Excel format"""
    try:
        exporter = ExcelExporter()
        excel_buffer = exporter.create_timeline_workbook(timeline_events, metadata)

        return excel_buffer.getvalue(), "timeline_analysis.xlsx"

    except Exception as e:
        st.error(f"Error creating Excel file: {e}")
        return None, None

def export_to_word(timeline_events, metadata):
    """Export timeline to Word format"""
    try:
        exporter = WordExporter()
        word_buffer = exporter.create_timeline_document(timeline_events, metadata)

        return word_buffer.getvalue(), "timeline_report.docx"

    except Exception as e:
        st.error(f"Error creating Word document: {e}")
        return None, None

def export_to_json(timeline_events, metadata):
    """Export timeline to JSON format"""
    try:
        export_data = {
            "metadata": metadata,
            "timeline_events": timeline_events,
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "total_events": len(timeline_events),
                "format_version": "1.0"
            }
        }

        json_str = json.dumps(export_data, indent=2, default=str, ensure_ascii=False)
        return json_str.encode('utf-8'), "timeline_data.json"

    except Exception as e:
        st.error(f"Error creating JSON: {e}")
        return None, None

def main():
    initialize_session_state()

    # Header
    st.markdown("""
    <div class="export-header">
        <h1>📄 Export Manager</h1>
        <p>Generate professional reports and export timeline data</p>
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
        if st.button("⚙️ Settings"):
            st.switch_page("pages/settings.py")

    st.markdown("---")

    # Check if timeline data is available
    if not st.session_state.timeline_events:
        st.warning("⚠️ No timeline data available. Please build a timeline first.")
        if st.button("📊 Go to Timeline Builder"):
            st.switch_page("pages/timeline_builder.py")
        return

    # Export summary
    st.markdown("## 📊 Export Summary")

    event_count = len(st.session_state.timeline_events)
    file_count = len(st.session_state.processed_files)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Timeline Events", event_count)
    with col2:
        st.metric("Source Documents", file_count)
    with col3:
        avg_confidence = sum(e.get('confidence', 0) for e in st.session_state.timeline_events) / event_count if event_count > 0 else 0
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")
    with col4:
        date_range = "N/A"
        if st.session_state.timeline_events:
            dates = [e.get('date', '') for e in st.session_state.timeline_events if e.get('date') != 'Unknown']
            if dates:
                date_range = f"{min(dates)} to {max(dates)}"
        st.metric("Date Range", date_range)

    # Export options
    st.markdown("## 📁 Export Formats")

    # Prepare metadata for export
    export_metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_events": event_count,
        "source_files": [f["metadata"]["filename"] for f in st.session_state.processed_files.values()],
        "extraction_method": "Legal-BERT AI Analysis",
        "system_version": "AI Legal Timeline Builder Pro v2.0"
    }

    # Export format options
    col1, col2 = st.columns(2)

    with col1:
        # PDF Export
        st.markdown("""
        <div class="export-option">
            <h3>📑 PDF Report</h3>
            <div class="format-description">
                Professional court-ready PDF report with evidence citations and legal formatting.
                Includes cover page, executive summary, detailed timeline, and evidence appendix.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📑 Export PDF", type="primary", key="pdf_export"):
            with st.spinner("Generating PDF report..."):
                pdf_data, filename = export_to_pdf(st.session_state.timeline_events, export_metadata)

                if pdf_data:
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        key="download_pdf"
                    )
                    st.markdown("""
                    <div class="success-export">
                        ✅ PDF report generated successfully! Click the download button above.
                    </div>
                    """, unsafe_allow_html=True)

        # Excel Export
        st.markdown("""
        <div class="export-option">
            <h3>📊 Excel Workbook</h3>
            <div class="format-description">
                Comprehensive Excel analysis with multiple worksheets: Timeline data, Statistics,
                Evidence summary, and Pivot tables for advanced analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📊 Export Excel", type="primary", key="excel_export"):
            with st.spinner("Creating Excel workbook..."):
                excel_data, filename = export_to_excel(st.session_state.timeline_events, export_metadata)

                if excel_data:
                    st.download_button(
                        label="⬇️ Download Excel Workbook",
                        data=excel_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel"
                    )
                    st.markdown("""
                    <div class="success-export">
                        ✅ Excel workbook created successfully! Click the download button above.
                    </div>
                    """, unsafe_allow_html=True)

    with col2:
        # Word Export
        st.markdown("""
        <div class="export-option">
            <h3>📄 Word Document</h3>
            <div class="format-description">
                Formatted Word document with professional styling, tables, and evidence sections.
                Perfect for editing and collaboration with legal teams.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📄 Export Word", type="primary", key="word_export"):
            with st.spinner("Creating Word document..."):
                word_data, filename = export_to_word(st.session_state.timeline_events, export_metadata)

                if word_data:
                    st.download_button(
                        label="⬇️ Download Word Document",
                        data=word_data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_word"
                    )
                    st.markdown("""
                    <div class="success-export">
                        ✅ Word document created successfully! Click the download button above.
                    </div>
                    """, unsafe_allow_html=True)

        # JSON Export
        st.markdown("""
        <div class="export-option">
            <h3>🔗 JSON Data</h3>
            <div class="format-description">
                Structured JSON data for integration with case management systems,
                APIs, and custom applications. Includes all metadata and confidence scores.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔗 Export JSON", type="primary", key="json_export"):
            with st.spinner("Preparing JSON data..."):
                json_data, filename = export_to_json(st.session_state.timeline_events, export_metadata)

                if json_data:
                    st.download_button(
                        label="⬇️ Download JSON Data",
                        data=json_data,
                        file_name=filename,
                        mime="application/json",
                        key="download_json"
                    )
                    st.markdown("""
                    <div class="success-export">
                        ✅ JSON data prepared successfully! Click the download button above.
                    </div>
                    """, unsafe_allow_html=True)

    # Export options
    st.markdown("## ⚙️ Export Options")

    with st.expander("🔧 Advanced Export Settings", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            include_confidence = st.checkbox("Include Confidence Scores", value=True)
            include_metadata = st.checkbox("Include File Metadata", value=True)

        with col2:
            min_confidence = st.slider("Minimum Confidence Filter", 0.0, 1.0, 0.0, 0.1)
            include_evidence_links = st.checkbox("Include Evidence Links", value=True)

        with col3:
            custom_header = st.text_input("Custom Report Header", "Legal Timeline Analysis")
            include_summary = st.checkbox("Include Executive Summary", value=True)

    # Batch export
    st.markdown("## 📦 Batch Export")

    if st.button("📦 Export All Formats", type="secondary"):
        with st.spinner("Generating all export formats..."):
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            exports = []
            formats = [
                ("PDF", export_to_pdf, "application/pdf"),
                ("Excel", export_to_excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                ("Word", export_to_word, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                ("JSON", export_to_json, "application/json")
            ]

            for i, (format_name, export_func, mime_type) in enumerate(formats):
                status_text.text(f"Generating {format_name} export...")
                progress_bar.progress((i + 1) / len(formats))

                data, filename = export_func(st.session_state.timeline_events, export_metadata)
                if data:
                    exports.append((format_name, data, filename, mime_type))

            status_text.text("All exports completed!")

            # Display download buttons for all formats
            if exports:
                st.success("✅ All formats generated successfully!")

                for format_name, data, filename, mime_type in exports:
                    st.download_button(
                        label=f"⬇️ Download {format_name}",
                        data=data,
                        file_name=filename,
                        mime=mime_type,
                        key=f"batch_download_{format_name.lower()}"
                    )

    # Preview section
    st.markdown("## 👁️ Timeline Preview")

    with st.expander("📋 View Timeline Data", expanded=False):
        if st.session_state.timeline_events:
            # Create a DataFrame for display
            display_data = []
            for event in st.session_state.timeline_events:
                display_data.append({
                    "Date": event.get("date", "Unknown"),
                    "Event": event.get("event", ""),
                    "Entities": ", ".join(event.get("entities", [])),
                    "Confidence": f"{event.get('confidence', 0):.1%}",
                    "Source": event.get("metadata", {}).get("filename", "Unknown")
                })

            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, height=300)

            # Timeline statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High Confidence Events", len([e for e in st.session_state.timeline_events if e.get('confidence', 0) > 0.8]))
            with col2:
                st.metric("Medium Confidence Events", len([e for e in st.session_state.timeline_events if 0.5 < e.get('confidence', 0) <= 0.8]))
            with col3:
                st.metric("Low Confidence Events", len([e for e in st.session_state.timeline_events if e.get('confidence', 0) <= 0.5]))

if __name__ == "__main__":
    main()
