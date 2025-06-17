import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import fitz  # pymupdf
import pdfplumber
from pdfminer.high_level import extract_text as pdfminer_extract
import io

class PDFProcessor:
    """
    Professional PDF processing with multiple extraction methods and fallbacks.
    Handles various PDF formats including scanned documents.
    """

    def __init__(self):
        """Initialize PDF processor with logging"""
        self.logger = logging.getLogger(__name__)

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using multiple methods with fallbacks.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        methods = [
            ("PyMuPDF", self._extract_with_pymupdf),
            ("pdfplumber", self._extract_with_pdfplumber),
            ("pdfminer", self._extract_with_pdfminer)
        ]

        for method_name, method_func in methods:
            try:
                self.logger.info(f"Attempting PDF extraction with {method_name}")
                text = method_func(pdf_path)
                if text and len(text.strip()) > 50:  # Minimum viable text length
                    self.logger.info(f"Successfully extracted text using {method_name}")
                    return text
                else:
                    self.logger.warning(f"{method_name} extracted insufficient text")
            except Exception as e:
                self.logger.warning(f"{method_name} extraction failed: {e}")
                continue

        # If all methods fail
        self.logger.error("All PDF extraction methods failed")
        return ""

    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (fastest method)"""
        doc = fitz.open(pdf_path)
        text_content = []

        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_content.append(f"\n--- Page {page_num + 1} ---\n{text}")

        doc.close()
        return "\n".join(text_content)

    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (good for tables and complex layouts)"""
        text_content = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_content.append(f"\n--- Page {page_num + 1} ---\n{text}")

                # Also extract table data if present
                tables = page.extract_tables()
                for table in tables:
                    table_text = "\n".join([" | ".join(row) for row in table if row])
                    if table_text:
                        text_content.append(f"\n[TABLE]\n{table_text}\n[/TABLE]\n")

        return "\n".join(text_content)

    def _extract_with_pdfminer(self, pdf_path: str) -> str:
        """Extract text using pdfminer (robust for complex PDFs)"""
        return pdfminer_extract(pdf_path)

    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata including page count, creation date, etc.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing metadata
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata

            result = {
                "page_count": doc.page_count,
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "encrypted": doc.needs_pass,
                "file_size": Path(pdf_path).stat().st_size
            }

            doc.close()
            return result

        except Exception as e:
            self.logger.error(f"Error extracting PDF metadata: {e}")
            return {"error": str(e)}

    def extract_text_by_page(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text page by page with page numbers for evidence linking.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of dictionaries with page text and metadata
        """
        pages = []

        try:
            doc = fitz.open(pdf_path)

            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text()

                page_info = {
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                    "word_count": len(text.split()) if text else 0,
                    "has_images": len(page.get_images()) > 0,
                    "has_text": bool(text.strip())
                }

                pages.append(page_info)

            doc.close()
            return pages

        except Exception as e:
            self.logger.error(f"Error extracting PDF by pages: {e}")
            return []

    def is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Determine if PDF is scanned (image-based) or text-based.

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if PDF appears to be scanned
        """
        try:
            doc = fitz.open(pdf_path)

            # Check first 3 pages for text content
            pages_to_check = min(3, doc.page_count)
            total_text_length = 0
            total_images = 0

            for page_num in range(pages_to_check):
                page = doc[page_num]
                text = page.get_text()
                total_text_length += len(text.strip())
                total_images += len(page.get_images())

            doc.close()

            # Heuristic: if very little text but many images, likely scanned
            avg_text_per_page = total_text_length / pages_to_check
            avg_images_per_page = total_images / pages_to_check

            return avg_text_per_page < 100 and avg_images_per_page > 0

        except Exception as e:
            self.logger.error(f"Error checking if PDF is scanned: {e}")
            return False

    def extract_images(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Extract images from PDF for OCR processing.

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted images

        Returns:
            List of paths to extracted image files
        """
        if not output_dir:
            output_dir = Path(pdf_path).parent / "extracted_images"

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        extracted_images = []

        try:
            doc = fitz.open(pdf_path)

            for page_num in range(doc.page_count):
                page = doc[page_num]
                image_list = page.get_images()

                for img_index, img in enumerate(image_list):
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)

                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                        img_path = output_path / img_filename
                        pix.save(str(img_path))
                        extracted_images.append(str(img_path))

                    pix = None

            doc.close()
            return extracted_images

        except Exception as e:
            self.logger.error(f"Error extracting images from PDF: {e}")
            return []

    def search_text(self, pdf_path: str, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for specific text in PDF and return locations.

        Args:
            pdf_path: Path to PDF file
            search_term: Text to search for

        Returns:
            List of search results with page numbers and context
        """
        results = []

        try:
            doc = fitz.open(pdf_path)

            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_instances = page.search_for(search_term)

                if text_instances:
                    page_text = page.get_text()
                    # Find context around the search term
                    for instance in text_instances:
                        # Get surrounding text for context
                        words = page_text.split()
                        search_words = search_term.split()

                        for i, word in enumerate(words):
                            if search_term.lower() in " ".join(words[i:i+len(search_words)]).lower():
                                start_idx = max(0, i - 10)
                                end_idx = min(len(words), i + len(search_words) + 10)
                                context = " ".join(words[start_idx:end_idx])

                                results.append({
                                    "page_number": page_num + 1,
                                    "context": context,
                                    "coordinates": instance
                                })
                                break

            doc.close()
            return results

        except Exception as e:
            self.logger.error(f"Error searching PDF: {e}")
            return []
