from abc import ABC
from dataclasses import dataclass
from typing import List, Optional

class DocumentElement(ABC):
    """
    Lightweight base class for structural document elements.
    Provides no semantic inference, only document syntax.
    """
    pass

@dataclass(frozen=True)
class ParagraphBlock(DocumentElement):
    """
    A contiguous block of text lines.
    """
    text: str
    original_lines: List[str]
    start_line: int
    end_line: int

@dataclass(frozen=True)
class BulletListBlock(DocumentElement):
    """
    A grouping of consecutive bullet point items.
    """
    items: List[str]
    original_lines: List[str]
    start_line: int
    end_line: int

@dataclass(frozen=True)
class NumberedListBlock(DocumentElement):
    """
    A grouping of consecutive numbered list items.
    """
    items: List[str]
    original_lines: List[str]
    start_line: int
    end_line: int

@dataclass(frozen=True)
class SeparatorBlock(DocumentElement):
    """
    A visual separator (e.g. ---, ***).
    """
    original_line: str
    start_line: int
    end_line: int

@dataclass(frozen=True)
class DocumentSection:
    """
    A distinct structural section of a document, optionally starting with a heading.
    """
    position: int
    title: Optional[str]
    elements: List[DocumentElement]

@dataclass(frozen=True)
class StructuredCampaignDocument:
    """
    The deterministic structural representation of a campaign text.
    """
    sections: List[DocumentSection]
