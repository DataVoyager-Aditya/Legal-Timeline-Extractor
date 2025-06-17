
import logging
import email
from email.header import decode_header
from pathlib import Path
import extract_msg
from typing import Dict, Any

class EmailProcessor:
    """Process email files (.eml and .msg formats)"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_text(self, email_path: str) -> str:
        """Extract text from email file"""
        try:
            file_path = Path(email_path)

            if file_path.suffix.lower() == '.eml':
                return self._extract_from_eml(email_path)
            elif file_path.suffix.lower() == '.msg':
                return self._extract_from_msg(email_path)
            else:
                raise ValueError(f"Unsupported email format: {file_path.suffix}")

        except Exception as e:
            self.logger.error(f"Error extracting email text: {e}")
            return ""

    def _extract_from_eml(self, eml_path: str) -> str:
        """Extract text from EML file"""
        with open(eml_path, 'rb') as f:
            msg = email.message_from_bytes(f.read())

        # Extract headers
        subject = self._decode_header(msg.get('Subject', ''))
        from_addr = self._decode_header(msg.get('From', ''))
        to_addr = self._decode_header(msg.get('To', ''))
        date = msg.get('Date', '')

        # Extract body
        body = self._extract_body(msg)

        return f"""Subject: {subject}
From: {from_addr}
To: {to_addr}
Date: {date}

{body}"""

    def _extract_from_msg(self, msg_path: str) -> str:
        """Extract text from MSG file"""
        try:
            msg = extract_msg.Message(msg_path)

            return f"""Subject: {msg.subject or ''}
From: {msg.sender or ''}
To: {msg.to or ''}
Date: {msg.date or ''}

{msg.body or ''}"""
        except Exception as e:
            self.logger.error(f"Error extracting MSG file: {e}")
            return ""

    def _decode_header(self, header_value):
        """Decode email header"""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_string += part.decode(encoding)
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += part

        return decoded_string

    def _extract_body(self, msg):
        """Extract email body"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
            # Fallback to HTML
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        return ""
