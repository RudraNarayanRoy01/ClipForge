import os
import pymupdf
import email
from email import policy
import httpx
from urllib.parse import urlparse
from src.domain.ports import ICampaignParser

class TextCampaignParser(ICampaignParser):
    async def parse(self, source: str, content_type: str) -> str:
        # Source is just raw text
        return source

class UrlCampaignParser(ICampaignParser):
    def __init__(self, max_bytes: int = 5 * 1024 * 1024):
        self.max_bytes = max_bytes

    async def parse(self, source: str, content_type: str) -> str:
        # Validate URL
        parsed = urlparse(source)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
            
        # Basic SSRF prevention: ensure it's not a local address (simplified for this scope)
        if parsed.hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            raise ValueError("Local IP addresses are not permitted")
            
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # We enforce a timeout and a limit on the response size implicitly by reading stream
            try:
                response = await client.get(source, timeout=10.0)
                response.raise_for_status()
                
                # Check content type if needed, typically text/html
                content_type_header = response.headers.get("Content-Type", "")
                if "text" not in content_type_header and "json" not in content_type_header:
                    raise ValueError(f"Unsupported URL content type: {content_type_header}")
                
                content = response.text
                if len(content.encode('utf-8')) > self.max_bytes:
                    raise ValueError("Campaign URL content exceeds size limits")
                    
                return content
            except httpx.RequestError as e:
                raise ValueError(f"Failed to fetch campaign URL: {str(e)}")

class PdfCampaignParser(ICampaignParser):
    def __init__(self, max_bytes: int = 5 * 1024 * 1024):
        self.max_bytes = max_bytes

    async def parse(self, source: str, content_type: str) -> str:
        if not os.path.exists(source):
            raise ValueError(f"PDF file not found: {source}")
            
        file_size = os.path.getsize(source)
        if file_size > self.max_bytes:
            raise ValueError("PDF file exceeds size limits")
            
        try:
            text_content = []
            with pymupdf.open(source) as doc:
                for page in doc:
                    text_content.append(page.get_text())
            return "\n".join(text_content)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

class EmailCampaignParser(ICampaignParser):
    def __init__(self, max_bytes: int = 5 * 1024 * 1024):
        self.max_bytes = max_bytes

    async def parse(self, source: str, content_type: str) -> str:
        if not os.path.exists(source):
            raise ValueError(f"Email file not found: {source}")
            
        if os.path.getsize(source) > self.max_bytes:
            raise ValueError("Email file exceeds size limits")
            
        try:
            with open(source, 'rb') as f:
                msg = email.message_from_binary_file(f, policy=policy.default)
            
            text_content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    cdisp = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in cdisp:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            text_content += payload.decode(part.get_content_charset() or 'utf-8', errors='replace')
            else:
                payload = msg.get_payload(decode=True)
                if isinstance(payload, bytes):
                    text_content = payload.decode(msg.get_content_charset() or 'utf-8', errors='replace')
                
            return text_content
        except Exception as e:
            raise ValueError(f"Failed to parse email: {str(e)}")

class ExportedTextCampaignParser(ICampaignParser):
    def __init__(self, max_bytes: int = 5 * 1024 * 1024):
        self.max_bytes = max_bytes

    async def parse(self, source: str, content_type: str) -> str:
        if os.path.exists(source) and os.path.isfile(source):
            if os.path.getsize(source) > self.max_bytes:
                raise ValueError(f"{content_type} file exceeds size limits")
            try:
                with open(source, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Failed to read exported text file: {str(e)}")
        
        if len(source.encode('utf-8')) > self.max_bytes:
            raise ValueError(f"{content_type} text exceeds size limits")
            
        return source

class CampaignParserFactory(ICampaignParser):
    """Router for parsers based on content type"""
    def __init__(self):
        self.parsers = {
            "text": TextCampaignParser(),
            "url": UrlCampaignParser(),
            "pdf": PdfCampaignParser(),
            "email": EmailCampaignParser(),
            "discord": ExportedTextCampaignParser(),
            "telegram": ExportedTextCampaignParser(),
        }
        
    async def parse(self, source: str, content_type: str) -> str:
        parser = self.parsers.get(content_type.lower())
        if not parser:
            raise ValueError(f"Unsupported campaign content type: {content_type}")
        return await parser.parse(source, content_type)
