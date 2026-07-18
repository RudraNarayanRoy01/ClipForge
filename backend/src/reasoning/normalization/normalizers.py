import re
import unicodedata
from .interfaces import INormalizer

class UnicodeNormalizer(INormalizer):
    """
    Normalizes characters to their canonical composed forms (NFKC).
    """
    def apply(self, text: str) -> str:
        return unicodedata.normalize("NFKC", text)


class LineEndingNormalizer(INormalizer):
    """
    Normalizes Windows \\r\\n and old Mac \\r line endings to standard \\n.
    """
    def apply(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")


class ControlCharacterNormalizer(INormalizer):
    """
    Removes invisible control characters while preserving newlines and tabs.
    """
    def apply(self, text: str) -> str:
        # Regex to strip out non-printable control characters
        # Keeps \t (0x09), \n (0x0a)
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)


class WhitespaceNormalizer(INormalizer):
    """
    Trims leading and trailing whitespace on a per-line basis.
    """
    def apply(self, text: str) -> str:
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        return "\n".join(lines)


class BulletNormalizer(INormalizer):
    """
    Normalizes various common bullet point characters to standard markdown '-'.
    """
    def apply(self, text: str) -> str:
        # Matches beginning of string or line, followed by bullet chars and space
        lines = text.split("\n")
        bullet_pattern = re.compile(r'^[\*\+•▪◦‣⁃]\s+')
        lines = [bullet_pattern.sub("- ", line) for line in lines]
        return "\n".join(lines)


class QuoteNormalizer(INormalizer):
    """
    Normalizes smart quotes and directional quotes to standard straight quotes.
    """
    def apply(self, text: str) -> str:
        # unicodedata NFKC typically handles some of this, but we explicitly target common ones.
        return text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")


class BlankLineNormalizer(INormalizer):
    """
    Collapses three or more consecutive newlines into two.
    Also trims whitespace from the very beginning and end of the document.
    """
    def apply(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
