
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO
import logging
from typing import List, Dict, Any

class PDFExporter:
    """
    Professional PDF exporter for legal timeline reports.
    Generates court-ready documents with proper formatting.
    """

    def __init__(self):
        """Initialize PDF exporter with styling"""
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for legal documents"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3c72')
        ))

        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2a5298')
        ))

        # Legal text style
        self.styles.add(ParagraphStyle(
            name='LegalText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))

        # Evidence citation style
        self.styles.add(ParagraphStyle(
            name='Evidence',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            leftIndent=20,
            spaceAfter=3
        ))

    def create_timeline_report(self, timeline_events: List[Dict[str, Any]], metadata: Dict[str, Any]) -> BytesIO:
        """
        Create a comprehensive PDF timeline report.

        Args:
            timeline_events: List of timeline events
            metadata: Report metadata

        Returns:
            BytesIO buffer containing PDF data
        """
        buffer = BytesIO()

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            # Build document content
            story = []

            # Cover page
            story.extend(self._create_cover_page(metadata))
            story.append(PageBreak())

            # Executive summary
            story.extend(self._create_executive_summary(timeline_events, metadata))
            story.append(PageBreak())

            # Timeline section
            story.extend(self._create_timeline_section(timeline_events))
            story.append(PageBreak())

            # Evidence appendix
            story.extend(self._create_evidence_appendix(timeline_events))

            # Build PDF
            doc.build(story)
            buffer.seek(0)

            self.logger.info("PDF report generated successfully")
            return buffer

        except Exception as e:
            self.logger.error(f"Error creating PDF report: {e}")
            raise

    def _create_cover_page(self, metadata: Dict[str, Any]) -> List:
        """Create PDF cover page"""
        content = []

        # Title
        content.append(Spacer(1, 2*inch))
        content.append(Paragraph("LEGAL TIMELINE ANALYSIS REPORT", self.styles['CustomTitle']))
        content.append(Spacer(1, 0.5*inch))

        # Subtitle
        content.append(Paragraph("AI-Powered Document Analysis", self.styles['Heading2']))
        content.append(Spacer(1, 1*inch))

        # Report details
        report_details = f"""
        <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Total Events:</b> {metadata.get('total_events', 0)}<br/>
        <b>Source Documents:</b> {len(metadata.get('source_files', []))}<br/>
        <b>Analysis Method:</b> {metadata.get('extraction_method', 'Legal-BERT AI')}<br/>
        <b>System Version:</b> {metadata.get('system_version', 'AI Legal Timeline Builder Pro')}
        """
        content.append(Paragraph(report_details, self.styles['LegalText']))
        content.append(Spacer(1, 1*inch))

        # Source files
        if metadata.get('source_files'):
            content.append(Paragraph("Source Documents:", self.styles['CustomHeading']))
            for i, filename in enumerate(metadata['source_files'], 1):
                content.append(Paragraph(f"{i}. {filename}", self.styles['LegalText']))

        # Disclaimer
        content.append(Spacer(1, 1*inch))
        disclaimer = """
        <b>DISCLAIMER:</b> This timeline analysis was generated using artificial intelligence 
        and should be reviewed by qualified legal professionals. All source documents should 
        be independently verified for accuracy and completeness.
        """
        content.append(Paragraph(disclaimer, self.styles['Evidence']))

        return content

    def _create_executive_summary(self, timeline_events: List[Dict[str, Any]], metadata: Dict[str, Any]) -> List:
        """Create executive summary section"""
        content = []

        content.append(Paragraph("EXECUTIVE SUMMARY", self.styles['CustomTitle']))
        content.append(Spacer(1, 0.3*inch))

        # Summary statistics
        total_events = len(timeline_events)
        high_confidence = len([e for e in timeline_events if e.get('confidence', 0) > 0.8])
        date_range = self._get_date_range(timeline_events)

        summary_text = f"""
        This report presents a chronological analysis of {total_events} events extracted from 
        {len(metadata.get('source_files', []))} legal documents using advanced AI technology. 
        The analysis identified {high_confidence} high-confidence events spanning from {date_range}.

        The timeline extraction process utilized Legal-BERT, a specialized natural language processing 
        model trained on legal text, combined with pattern recognition algorithms optimized for 
        legal document analysis. Each event has been assigned a confidence score based on the 
        clarity of the source text and the reliability of the extraction method.
        """
        content.append(Paragraph(summary_text, self.styles['LegalText']))
        content.append(Spacer(1, 0.2*inch))

        # Key findings
        content.append(Paragraph("Key Findings:", self.styles['CustomHeading']))

        # Event type distribution
        event_types = {}
        for event in timeline_events:
            event_type = event.get('event_type', 'Unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1

        findings = []
        findings.append(f"• Total timeline events identified: {total_events}")
        findings.append(f"• High confidence events (>80%): {high_confidence}")
        findings.append(f"• Date range coverage: {date_range}")
        findings.append(f"• Most common event type: {max(event_types.items(), key=lambda x: x[1])[0] if event_types else 'N/A'}")

        for finding in findings:
            content.append(Paragraph(finding, self.styles['LegalText']))

        return content

    def _create_timeline_section(self, timeline_events: List[Dict[str, Any]]) -> List:
        """Create detailed timeline section"""
        content = []

        content.append(Paragraph("CHRONOLOGICAL TIMELINE", self.styles['CustomTitle']))
        content.append(Spacer(1, 0.3*inch))

        for i, event in enumerate(timeline_events, 1):
            # Event header
            event_header = f"{i}. {event.get('date', 'Unknown Date')} - {event.get('event', 'Unknown Event')}"
            content.append(Paragraph(event_header, self.styles['CustomHeading']))

            # Event details
            if event.get('entities'):
                entities_text = f"<b>Parties/Entities:</b> {', '.join(event['entities'])}"
                content.append(Paragraph(entities_text, self.styles['LegalText']))

            # Event description
            if event.get('text'):
                description_text = f"<b>Description:</b> {event['text'][:500]}{'...' if len(event.get('text', '')) > 500 else ''}"
                content.append(Paragraph(description_text, self.styles['LegalText']))

            # Confidence and source
            confidence = event.get('confidence', 0)
            source_file = event.get('metadata', {}).get('filename', 'Unknown Source')
            evidence_text = f"<b>Confidence:</b> {confidence:.1%} | <b>Source:</b> {source_file}"
            content.append(Paragraph(evidence_text, self.styles['Evidence']))

            content.append(Spacer(1, 0.1*inch))

        return content

    def _create_evidence_appendix(self, timeline_events: List[Dict[str, Any]]) -> List:
        """Create evidence appendix"""
        content = []

        content.append(Paragraph("EVIDENCE APPENDIX", self.styles['CustomTitle']))
        content.append(Spacer(1, 0.3*inch))

        # Group events by source file
        sources = {}
        for event in timeline_events:
            source = event.get('metadata', {}).get('filename', 'Unknown Source')
            if source not in sources:
                sources[source] = []
            sources[source].append(event)

        for source_file, events in sources.items():
            content.append(Paragraph(f"Source Document: {source_file}", self.styles['CustomHeading']))
            content.append(Paragraph(f"Events extracted: {len(events)}", self.styles['LegalText']))

            # Create table of events for this source
            table_data = [['Date', 'Event', 'Confidence']]
            for event in events:
                table_data.append([
                    event.get('date', 'Unknown'),
                    event.get('event', 'Unknown')[:50] + ('...' if len(event.get('event', '')) > 50 else ''),
                    f"{event.get('confidence', 0):.1%}"
                ])

            table = Table(table_data, colWidths=[1.5*inch, 3*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a5298')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            content.append(table)
            content.append(Spacer(1, 0.2*inch))

        return content

    def _get_date_range(self, timeline_events: List[Dict[str, Any]]) -> str:
        """Get date range from timeline events"""
        dates = [e.get('date', '') for e in timeline_events if e.get('date') and e.get('date') != 'Unknown']
        if dates:
            return f"{min(dates)} to {max(dates)}"
        return "Date range unavailable"
