
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Add src directory to Python path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from extractors.legal_bert_extractor import LegalBERTExtractor
from utils.config import Config

st.set_page_config(
    page_title="Timeline Builder - AI Legal Timeline Builder",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.timeline-header {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.event-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 1rem 0;
    border-left: 4px solid #11998e;
}

.event-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

.event-meta {
    background: #f8f9fa;
    padding: 0.5rem;
    border-radius: 5px;
    font-size: 0.9rem;
    color: #6c757d;
    margin-top: 0.5rem;
}

.confidence-high { border-left-color: #28a745; }
.confidence-medium { border-left-color: #ffc107; }
.confidence-low { border-left-color: #dc3545; }

.timeline-stats {
    display: flex;
    justify-content: space-around;
    margin: 2rem 0;
}

.stat-card {
    text-align: center;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    margin: 0 0.5rem;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'timeline_events' not in st.session_state:
        st.session_state.timeline_events = []
    if 'extraction_complete' not in st.session_state:
        st.session_state.extraction_complete = False
    if 'legal_bert_extractor' not in st.session_state:
        st.session_state.legal_bert_extractor = LegalBERTExtractor()

def extract_timeline_from_files():
    """Extract timeline events from processed files"""
    if 'processed_files' not in st.session_state or not st.session_state.processed_files:
        st.error("No processed files found. Please upload documents first.")
        return

    extractor = st.session_state.legal_bert_extractor
    all_events = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, (file_id, file_data) in enumerate(st.session_state.processed_files.items()):
        progress = (i + 1) / len(st.session_state.processed_files)
        progress_bar.progress(progress)
        status_text.text(f"Processing {file_data['metadata']['filename']}...")

        # Extract events from text
        text = file_data["text"]
        metadata = file_data["metadata"]

        events = extractor.extract_events(text, metadata)

        # Add source information to each event
        for event in events:
            event["source_file"] = metadata["filename"]
            event["source_path"] = metadata["stored_path"]
            event["file_id"] = file_id

        all_events.extend(events)

    # Sort events by date
    all_events.sort(key=lambda x: x.get("date", "1900-01-01"))

    st.session_state.timeline_events = all_events
    st.session_state.extraction_complete = True

    progress_bar.progress(1.0)
    status_text.text("✅ Timeline extraction complete!")

def render_timeline_table():
    """Render timeline events in a professional table"""
    if not st.session_state.timeline_events:
        st.info("No timeline events extracted yet.")
        return

    events_df = pd.DataFrame(st.session_state.timeline_events)

    # Configure the dataframe display
    st.dataframe(
        events_df[['date', 'event', 'entities', 'confidence', 'source_file']],
        use_container_width=True,
        height=400,
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "event": st.column_config.TextColumn("Event Description", width="large"),
            "entities": st.column_config.ListColumn("People/Entities"),
            "confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1),
            "source_file": st.column_config.TextColumn("Source File")
        }
    )

def render_timeline_cards():
    """Render timeline events as cards"""
    if not st.session_state.timeline_events:
        return

    for i, event in enumerate(st.session_state.timeline_events):
        confidence_class = "confidence-high" if event["confidence"] > 0.8 else "confidence-medium" if event["confidence"] > 0.5 else "confidence-low"

        st.markdown(f"""
        <div class="event-card {confidence_class}">
            <h4>📅 {event['date']} - {event['event']}</h4>
            <p><strong>People/Entities:</strong> {', '.join(event.get('entities', []))}</p>
            <div class="event-meta">
                📁 Source: {event['source_file']} | 
                🎯 Confidence: {event['confidence']:.1%} |
                📄 Evidence: <a href="#" onclick="downloadEvidence('{event['file_id']}')">View Original</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Evidence download button
        col1, col2, col3 = st.columns([1, 1, 8])
        with col1:
            if st.button("📥 Evidence", key=f"evidence_{i}"):
                try:
                    with open(event['source_path'], 'rb') as f:
                        st.download_button(
                            label="Download Evidence",
                            data=f.read(),
                            file_name=event['source_file'],
                            key=f"download_evidence_{i}"
                        )
                except Exception as e:
                    st.error(f"Error accessing evidence: {e}")

def render_timeline_chart():
    """Render timeline events as an interactive chart"""
    if not st.session_state.timeline_events:
        return

    events_df = pd.DataFrame(st.session_state.timeline_events)

    # Convert date column to datetime
    events_df['datetime'] = pd.to_datetime(events_df['date'], errors='coerce')
    events_df = events_df.dropna(subset=['datetime'])

    if events_df.empty:
        st.warning("No valid dates found for timeline visualization.")
        return

    # Create timeline chart
    fig = px.scatter(
        events_df, 
        x='datetime', 
        y='event',
        color='confidence',
        size='confidence',
        hover_data=['entities', 'source_file'],
        title="Legal Timeline Visualization",
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        height=600,
        xaxis_title="Date",
        yaxis_title="Events",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

def main():
    initialize_session_state()

    # Header
    st.markdown("""
    <div class="timeline-header">
        <h1>📊 AI Timeline Builder</h1>
        <p>Legal-BERT powered timeline extraction and analysis</p>
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
        if st.button("📄 Export Reports"):
            st.switch_page("pages/export_manager.py")
    with col4:
        if st.button("⚙️ Settings"):
            st.switch_page("pages/settings.py")

    st.markdown("---")

    # Check if files are available
    if 'processed_files' not in st.session_state or not st.session_state.processed_files:
        st.warning("⚠️ No documents uploaded yet. Please upload documents first.")
        if st.button("📤 Go to Upload"):
            st.switch_page("pages/document_upload.py")
        return

    # Document summary
    st.markdown("## 📋 Document Summary")
    file_count = len(st.session_state.processed_files)
    total_words = sum(f["metadata"]["word_count"] for f in st.session_state.processed_files.values())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Documents", file_count)
    with col2:
        st.metric("Total Words", f"{total_words:,}")
    with col3:
        events_count = len(st.session_state.timeline_events) if st.session_state.timeline_events else 0
        st.metric("Events Extracted", events_count)
    with col4:
        status = "✅ Complete" if st.session_state.extraction_complete else "⏳ Pending"
        st.metric("Status", status)

    # Timeline extraction section
    st.markdown("## 🤖 Legal-BERT Timeline Extraction")

    if not st.session_state.extraction_complete:
        st.info("🚀 Ready to extract timeline using Legal-BERT AI models")

        # Model selection
        model_option = st.selectbox(
            "Select Legal-BERT Model:",
            ["nlpaueb/legal-bert-base-uncased", "law-ai/InLegalBERT", "pile-of-law/legalbert-large-1.7M-2"],
            help="Choose the most appropriate model for your legal documents"
        )

        col1, col2 = st.columns(2)
        with col1:
            confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.1)
        with col2:
            max_events = st.number_input("Max Events to Extract", 1, 1000, 100)

        if st.button("🚀 Extract Timeline", type="primary"):
            with st.spinner("🧠 Analyzing documents with Legal-BERT..."):
                extract_timeline_from_files()
                st.success("✅ Timeline extraction completed!")
                st.rerun()

    # Display timeline if available
    if st.session_state.timeline_events:
        st.markdown("## 📊 Generated Timeline")

        # Display options
        view_mode = st.radio(
            "Choose View Mode:",
            ["📋 Table View", "🎯 Card View", "📈 Chart View"],
            horizontal=True
        )

        # Filter options
        with st.expander("🔍 Filter Options", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                min_confidence = st.slider("Minimum Confidence", 0.0, 1.0, 0.0, 0.1)
            with col2:
                date_range = st.date_input("Date Range", [])
            with col3:
                source_filter = st.multiselect(
                    "Source Files",
                    options=list(set([e['source_file'] for e in st.session_state.timeline_events])),
                    default=list(set([e['source_file'] for e in st.session_state.timeline_events]))
                )

        # Apply filters
        filtered_events = [
            e for e in st.session_state.timeline_events
            if e['confidence'] >= min_confidence and e['source_file'] in source_filter
        ]

        # Update session state with filtered events for display
        original_events = st.session_state.timeline_events
        st.session_state.timeline_events = filtered_events

        # Render based on view mode
        if view_mode == "📋 Table View":
            render_timeline_table()
        elif view_mode == "🎯 Card View":
            render_timeline_cards()
        elif view_mode == "📈 Chart View":
            render_timeline_chart()

        # Restore original events
        st.session_state.timeline_events = original_events

        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Re-extract Timeline"):
                st.session_state.extraction_complete = False
                st.session_state.timeline_events = []
                st.rerun()

        with col2:
            if st.button("📄 Export Timeline"):
                st.switch_page("pages/export_manager.py")

        with col3:
            # Download timeline as JSON
            timeline_json = json.dumps(st.session_state.timeline_events, indent=2, default=str)
            st.download_button(
                "⬬ Download JSON",
                timeline_json,
                file_name=f"timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
