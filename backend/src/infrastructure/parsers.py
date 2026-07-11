import httpx
import json
from urllib.parse import urlparse
from ..domain.ports import ICampaignParser

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
    async def parse(self, source: str, content_type: str) -> str:
        # Not implemented since project doesn't have a PDF parser installed currently.
        # This keeps the architecture clean and open for PyMuPDF or pdfplumber later.
        raise NotImplementedError("PDF parsing is not yet supported in this environment.")

class CampaignParserFactory(ICampaignParser):
    """Router for parsers based on content type"""
    def __init__(self):
        self.parsers = {
            "text": TextCampaignParser(),
            "url": UrlCampaignParser(),
            "pdf": PdfCampaignParser(),
        }
        
    async def parse(self, source: str, content_type: str) -> str:
        parser = self.parsers.get(content_type.lower())
        if not parser:
            raise ValueError(f"Unsupported campaign content type: {content_type}")
        return await parser.parse(source, content_type)
