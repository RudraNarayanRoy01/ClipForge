import re
from src.domain.ports import ICampaignNormalizationService

class TextNormalizationService(ICampaignNormalizationService):
    """
    Cleans and normalizes raw text before passing it to the intelligence layer.
    Removes redundant formatting, normalizes known platform names, etc.
    """
    def __init__(self):
        # Known platform mappings
        self.platform_mappings = {
            r'(?i)\btik\s*tok\b': 'TikTok',
            r'(?i)\big\b': 'Instagram',
            r'(?i)\binsta\b': 'Instagram',
            r'(?i)\binstagram\b': 'Instagram',
            r'(?i)\byoutube\b': 'YouTube',
            r'(?i)\byt\b': 'YouTube',
            r'(?i)\bshorts\b': 'YouTube Shorts',
            r'(?i)\breels\b': 'Instagram Reels',
        }
        
    def normalize(self, raw_text: str) -> str:
        if not raw_text:
            return ""
            
        # 1. Remove HTML tags (simple fallback if any leaked through)
        text = re.sub(r'<[^>]+>', ' ', raw_text)
        
        # 2. Normalize whitespace (remove excessive newlines and spaces)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 3. Normalize platform names
        for pattern, replacement in self.platform_mappings.items():
            text = re.sub(pattern, replacement, text)
            
        # 4. Standardize payout formats if they use weird spacing, e.g. $ 500 -> $500
        text = re.sub(r'\$\s+(\d+)', r'$\1', text)
        
        return text.strip()
