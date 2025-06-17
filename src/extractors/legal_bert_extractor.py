
import re
import spacy
import warnings
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification,
    pipeline,
    logging as transformers_logging
)
import torch

# Suppress transformer warnings
warnings.filterwarnings("ignore")
transformers_logging.set_verbosity_error()

class LegalBERTExtractor:
    """
    Professional Legal-BERT powered timeline extractor for legal documents.
    Supports multiple Legal-BERT models for optimal accuracy.
    """

    def __init__(self, model_name: str = "nlpaueb/legal-bert-base-uncased"):
        """
        Initialize Legal-BERT extractor with specified model.

        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)

        # Initialize models
        self._load_models()
        self._load_legal_patterns()

    def _load_models(self):
        """Load Legal-BERT and spaCy models"""
        try:
            # Load spaCy model for basic NLP tasks
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except IOError:
                self.logger.warning("spaCy en_core_web_sm not found. Installing...")
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")

            # Load Legal-BERT tokenizer and model
            self.logger.info(f"Loading Legal-BERT model: {self.model_name}")

            # Use CPU for compatibility (can be changed to GPU if available)
            device = 0 if torch.cuda.is_available() else -1

            # Initialize NER pipeline for entity extraction
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model_name,
                tokenizer=self.model_name,
                aggregation_strategy="simple",
                device=device
            )

            self.logger.info("Legal-BERT model loaded successfully")

        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            # Fallback to spaCy only
            self.ner_pipeline = None

    def _load_legal_patterns(self):
        """Load legal event patterns for Indian and international law"""
        self.legal_patterns = [
            # Criminal Law Patterns
            {
                "pattern": r"(?:FIR|First Information Report).*?(?:filed|registered|lodged)",
                "event_type": "FIR_FILED",
                "description": "FIR Filed"
            },
            {
                "pattern": r"(?:arrest|arrested|apprehended).*?(?:accused|suspect|defendant)",
                "event_type": "ARREST",
                "description": "Arrest Made"
            },
            {
                "pattern": r"(?:charge|charged|chargesheet).*?(?:filed|submitted)",
                "event_type": "CHARGES_FILED",
                "description": "Charges Filed"
            },
            {
                "pattern": r"(?:bail|anticipatory bail).*?(?:granted|rejected|applied)",
                "event_type": "BAIL_APPLICATION",
                "description": "Bail Application"
            },

            # Court Proceedings
            {
                "pattern": r"(?:hearing|proceeding|case).*?(?:scheduled|adjourned|postponed)",
                "event_type": "HEARING_SCHEDULED",
                "description": "Court Hearing"
            },
            {
                "pattern": r"(?:judgment|order|verdict).*?(?:pronounced|delivered|passed)",
                "event_type": "JUDGMENT",
                "description": "Judgment Delivered"
            },
            {
                "pattern": r"(?:appeal|revision|writ).*?(?:filed|submitted|dismissed)",
                "event_type": "APPEAL_FILED",
                "description": "Appeal Filed"
            },

            # Civil Law Patterns
            {
                "pattern": r"(?:suit|petition|complaint).*?(?:filed|instituted|lodged)",
                "event_type": "SUIT_FILED",
                "description": "Legal Suit Filed"
            },
            {
                "pattern": r"(?:agreement|contract|deed).*?(?:executed|signed|entered)",
                "event_type": "AGREEMENT_SIGNED",
                "description": "Agreement Executed"
            },
            {
                "pattern": r"(?:notice|summons).*?(?:served|issued|delivered)",
                "event_type": "NOTICE_SERVED",
                "description": "Legal Notice Served"
            },

            # Administrative Actions
            {
                "pattern": r"(?:license|permit|approval).*?(?:granted|issued|revoked)",
                "event_type": "LICENSE_ACTION",
                "description": "License/Permit Action"
            },
            {
                "pattern": r"(?:investigation|inquiry|probe).*?(?:initiated|commenced|started)",
                "event_type": "INVESTIGATION_STARTED",
                "description": "Investigation Initiated"
            },

            # Indian Legal Specific
            {
                "pattern": r"(?:Section|Sec\.?)\s*(\d+).*?(?:IPC|Indian Penal Code)",
                "event_type": "IPC_SECTION",
                "description": "IPC Section Applied"
            },
            {
                "pattern": r"(?:Article|Art\.?)\s*(\d+).*?(?:Constitution|constitutional)",
                "event_type": "CONSTITUTIONAL_ARTICLE",
                "description": "Constitutional Article"
            }
        ]

        self.logger.info(f"Loaded {len(self.legal_patterns)} legal event patterns")

    def _extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates from text using multiple methods"""
        dates = []

        # Date patterns (multiple formats)
        date_patterns = [
            r"(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})",  # DD/MM/YYYY or DD-MM-YYYY
            r"(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})",  # YYYY/MM/DD or YYYY-MM-DD
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",  # DD Month YYYY
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})",  # Month DD, YYYY
            r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})"  # DDth Month YYYY
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append({
                    "text": match.group(1),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.9
                })

        return dates

    def _extract_entities_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using spaCy"""
        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "LAW", "MONEY", "DATE"]:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.8
                })

        return entities

    def _extract_entities_legal_bert(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using Legal-BERT"""
        if not self.ner_pipeline:
            return []

        try:
            # Truncate text to model's max length (512 tokens for BERT)
            max_length = 500  # Leave some buffer
            words = text.split()
            if len(words) > max_length:
                text = " ".join(words[:max_length])

            results = self.ner_pipeline(text)
            entities = []

            for result in results:
                entities.append({
                    "text": result["word"],
                    "label": result["entity_group"],
                    "start": result["start"],
                    "end": result["end"],
                    "confidence": result["score"]
                })

            return entities

        except Exception as e:
            self.logger.error(f"Error in Legal-BERT extraction: {e}")
            return []

    def _extract_legal_events(self, text: str) -> List[Dict[str, Any]]:
        """Extract legal events using pattern matching"""
        events = []

        for pattern_info in self.legal_patterns:
            pattern = pattern_info["pattern"]
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)

            for match in matches:
                # Extract surrounding context
                start_context = max(0, match.start() - 100)
                end_context = min(len(text), match.end() + 100)
                context = text[start_context:end_context]

                events.append({
                    "text": match.group(),
                    "context": context,
                    "event_type": pattern_info["event_type"],
                    "description": pattern_info["description"],
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.7
                })

        return events

    def _normalize_date(self, date_text: str) -> str:
        """Normalize date to YYYY-MM-DD format"""
        try:
            # Common date formats
            formats = [
                "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
                "%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d",
                "%d %B %Y", "%d %b %Y",
                "%B %d, %Y", "%b %d, %Y",
                "%d %B, %Y", "%d %b, %Y"
            ]

            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_text.strip(), fmt)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            # If no format matches, return original
            return date_text

        except Exception:
            return date_text

    def extract_events(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract timeline events from text using Legal-BERT and pattern matching.

        Args:
            text: Input text to analyze
            metadata: File metadata

        Returns:
            List of extracted events with dates, entities, and confidence scores
        """
        self.logger.info(f"Extracting events from {metadata.get('filename', 'unknown file')}")

        # Split text into manageable chunks
        max_chunk_size = 1000
        chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]

        all_events = []

        for i, chunk in enumerate(chunks):
            try:
                # Extract components
                dates = self._extract_dates(chunk)
                legal_events = self._extract_legal_events(chunk)

                # Extract entities using both methods
                spacy_entities = self._extract_entities_spacy(chunk)
                bert_entities = self._extract_entities_legal_bert(chunk)

                # Combine entities (prefer Legal-BERT results)
                all_entities = bert_entities + spacy_entities

                # Create timeline events by combining dates with legal events
                for event in legal_events:
                    # Find closest date to the event
                    closest_date = None
                    min_distance = float('inf')

                    for date in dates:
                        distance = abs(event["start"] - date["start"])
                        if distance < min_distance:
                            min_distance = distance
                            closest_date = date

                    # Find relevant entities near the event
                    relevant_entities = []
                    for entity in all_entities:
                        if (abs(entity["start"] - event["start"]) < 200 and 
                            entity["label"] in ["PERSON", "ORG", "GPE"]):
                            relevant_entities.append(entity["text"])

                    # Create event entry
                    timeline_event = {
                        "date": self._normalize_date(closest_date["text"]) if closest_date else "Unknown",
                        "event": event["description"],
                        "text": event["text"],
                        "context": event["context"],
                        "entities": list(set(relevant_entities)),  # Remove duplicates
                        "event_type": event["event_type"],
                        "confidence": min(event["confidence"], closest_date["confidence"] if closest_date else 0.5),
                        "chunk_index": i,
                        "metadata": metadata
                    }

                    all_events.append(timeline_event)

            except Exception as e:
                self.logger.error(f"Error processing chunk {i}: {e}")
                continue

        # Remove duplicate events and sort by confidence
        unique_events = []
        seen_events = set()

        for event in sorted(all_events, key=lambda x: x["confidence"], reverse=True):
            event_key = (event["date"], event["event"], tuple(event["entities"]))
            if event_key not in seen_events:
                seen_events.add(event_key)
                unique_events.append(event)

        # Sort by date
        try:
            unique_events.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d") if x["date"] != "Unknown" else datetime.min)
        except ValueError:
            # If date parsing fails, sort by original date string
            unique_events.sort(key=lambda x: x["date"])

        self.logger.info(f"Extracted {len(unique_events)} unique timeline events")
        return unique_events

    def set_model(self, model_name: str):
        """Change the Legal-BERT model"""
        self.model_name = model_name
        self._load_models()
        self.logger.info(f"Switched to model: {model_name}")

    def get_supported_models(self) -> List[str]:
        """Get list of supported Legal-BERT models"""
        return [
            "nlpaueb/legal-bert-base-uncased",
            "law-ai/InLegalBERT", 
            "pile-of-law/legalbert-large-1.7M-2"
        ]
