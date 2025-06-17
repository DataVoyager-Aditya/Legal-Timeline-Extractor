
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

class ImageProcessor:
    """
    Professional image processing with OCR for legal documents.
    Handles screenshots, scanned documents, and WhatsApp images.
    """

    def __init__(self):
        """Initialize image processor with OCR configuration"""
        self.logger = logging.getLogger(__name__)

        # Configure Tesseract OCR
        self.ocr_config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?()[]{}\"'-/@#$%^&*+=<>|\\~`"


    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using OCR with preprocessing.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text content
        """
        try:
            # Load and preprocess image
            processed_image = self._preprocess_image(image_path)

            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                processed_image, 
                config=self.ocr_config,
                lang='eng+hin'  # English and Hindi support
            )

            # Clean extracted text
            cleaned_text = self._clean_text(text)

            self.logger.info(f"Extracted {len(cleaned_text)} characters from {Path(image_path).name}")
            return cleaned_text

        except Exception as e:
            self.logger.error(f"Error extracting text from image: {e}")
            return ""

    def _preprocess_image(self, image_path: str) -> Image.Image:
        """
        Preprocess image for better OCR results.

        Args:
            image_path: Path to image file

        Returns:
            Preprocessed PIL Image
        """
        # Load image
        image = Image.open(image_path)

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Apply preprocessing steps
        image = self._enhance_contrast(image)
        image = self._denoise_image(image)
        image = self._adjust_brightness(image)
        image = self._sharpen_image(image)

        return image

    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Enhance image contrast for better text recognition"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.5)  # Increase contrast by 50%

    def _denoise_image(self, image: Image.Image) -> Image.Image:
        """Remove noise from image"""
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Apply bilateral filter for noise reduction
        denoised = cv2.bilateralFilter(cv_image, 9, 75, 75)

        # Convert back to PIL
        return Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))

    def _adjust_brightness(self, image: Image.Image) -> Image.Image:
        """Adjust image brightness if too dark"""
        # Calculate average brightness
        grayscale = image.convert('L')
        stat = np.array(grayscale)
        avg_brightness = np.mean(stat)

        # Adjust if too dark
        if avg_brightness < 100:
            enhancer = ImageEnhance.Brightness(image)
            brightness_factor = 100 / avg_brightness
            image = enhancer.enhance(min(brightness_factor, 2.0))

        return image

    def _sharpen_image(self, image: Image.Image) -> Image.Image:
        """Sharpen image for better text clarity"""
        return image.filter(ImageFilter.SHARPEN)

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text to remove OCR artifacts.

        Args:
            text: Raw OCR text

        Returns:
            Cleaned text
        """
        import re

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove isolated single characters (common OCR errors)
        text = re.sub(r'\b[a-zA-Z]\b', '', text)

        # Fix common OCR errors
        replacements = {
            '0': 'O',  # Zero to O in words
            '1': 'I',  # One to I in words
            '5': 'S',  # Five to S in words
            '@': 'a',  # At symbol to 'a'
            '|': 'I',  # Pipe to I
            '!': 'l',  # Exclamation to l
        }

        # Apply replacements only in word contexts
        for old, new in replacements.items():
            text = re.sub(f'\b{old}\b', new, text)

        # Remove lines with only special characters
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if re.search(r'[a-zA-Z]', line):  # Keep lines with letters
                cleaned_lines.append(line.strip())

        return '\n'.join(cleaned_lines)

    def extract_whatsapp_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract structured data from WhatsApp screenshots.

        Args:
            image_path: Path to WhatsApp screenshot

        Returns:
            Structured WhatsApp data
        """
        try:
            text = self.extract_text(image_path)

            # Pattern to match WhatsApp message format
            import re

            # WhatsApp timestamp patterns
            timestamp_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?:\s*[APap][Mm])?)'

            messages = []
            lines = text.split('\n')

            current_message = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for timestamp
                timestamp_match = re.search(timestamp_pattern, line)
                if timestamp_match:
                    # Save previous message
                    if current_message:
                        messages.append(current_message)

                    # Start new message
                    date = timestamp_match.group(1)
                    time = timestamp_match.group(2)

                    # Extract sender and message
                    remaining_text = line[timestamp_match.end():].strip()
                    if ':' in remaining_text:
                        sender, message = remaining_text.split(':', 1)
                        sender = sender.strip()
                        message = message.strip()
                    else:
                        sender = "Unknown"
                        message = remaining_text

                    current_message = {
                        "date": date,
                        "time": time,
                        "sender": sender,
                        "message": message,
                        "full_text": line
                    }
                else:
                    # Continuation of previous message
                    if current_message:
                        current_message["message"] += " " + line
                        current_message["full_text"] += "\n" + line

            # Add last message
            if current_message:
                messages.append(current_message)

            return {
                "type": "whatsapp_chat",
                "messages": messages,
                "message_count": len(messages),
                "raw_text": text
            }

        except Exception as e:
            self.logger.error(f"Error extracting WhatsApp data: {e}")
            return {"error": str(e), "raw_text": ""}

    def detect_document_type(self, image_path: str) -> str:
        """
        Detect the type of document in the image.

        Args:
            image_path: Path to image file

        Returns:
            Document type classification
        """
        try:
            text = self.extract_text(image_path)
            text_lower = text.lower()

            # Keywords for different document types
            if any(word in text_lower for word in ['whatsapp', 'last seen', 'online', 'typing']):
                return "whatsapp_chat"
            elif any(word in text_lower for word in ['fir', 'police', 'station', 'complaint']):
                return "police_report"
            elif any(word in text_lower for word in ['court', 'judge', 'hearing', 'order']):
                return "court_document"
            elif any(word in text_lower for word in ['agreement', 'contract', 'party', 'whereas']):
                return "legal_agreement"
            elif any(word in text_lower for word in ['email', 'from:', 'to:', 'subject:']):
                return "email_screenshot"
            else:
                return "general_document"

        except Exception as e:
            self.logger.error(f"Error detecting document type: {e}")
            return "unknown"

    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extract image metadata including EXIF data.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary containing image metadata
        """
        try:
            from PIL.ExifTags import TAGS

            image = Image.open(image_path)

            metadata = {
                "filename": Path(image_path).name,
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "file_size": Path(image_path).stat().st_size
            }

            # Extract EXIF data if available
            exifdata = image.getexif()
            if exifdata:
                exif_dict = {}
                for tag_id in exifdata:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exifdata.get(tag_id)
                    if isinstance(data, bytes):
                        data = data.decode('utf-8', errors='ignore')
                    exif_dict[tag] = data

                metadata["exif"] = exif_dict

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting image metadata: {e}")
            return {"error": str(e)}

    def enhance_for_ocr(self, image_path: str, output_path: Optional[str] = None) -> str:
        """
        Enhance image specifically for OCR processing.

        Args:
            image_path: Path to input image
            output_path: Path to save enhanced image

        Returns:
            Path to enhanced image
        """
        try:
            if not output_path:
                output_path = str(Path(image_path).with_suffix('.enhanced.png'))

            # Load and preprocess image
            image = Image.open(image_path)

            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')

            # Apply morphological operations using OpenCV
            cv_image = np.array(image)

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(cv_image, (3, 3), 0)

            # Apply threshold to get binary image
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Apply morphological operations to clean up
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

            # Convert back to PIL and save
            enhanced_image = Image.fromarray(cleaned)
            enhanced_image.save(output_path)

            self.logger.info(f"Enhanced image saved to {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error enhancing image: {e}")
            return image_path  # Return original path if enhancement fails

    def get_text_confidence(self, image_path: str) -> float:
        """
        Get OCR confidence score for extracted text.

        Args:
            image_path: Path to image file

        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            processed_image = self._preprocess_image(image_path)

            # Get detailed OCR data with confidence scores
            data = pytesseract.image_to_data(
                processed_image, 
                config=self.ocr_config,
                output_type=pytesseract.Output.DICT
            )

            # Calculate average confidence for words with reasonable confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]

            if confidences:
                return sum(confidences) / len(confidences) / 100.0  # Convert to 0-1 scale
            else:
                return 0.0

        except Exception as e:
            self.logger.error(f"Error calculating OCR confidence: {e}")
            return 0.0
