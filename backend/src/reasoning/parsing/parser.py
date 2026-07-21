import re
from typing import List, Optional
from src.reasoning.normalization.models import NormalizedCampaignText
from .models import (
    StructuredCampaignDocument,
    DocumentSection,
    DocumentElement,
    ParagraphBlock,
    BulletListBlock,
    NumberedListBlock,
    SeparatorBlock
)
from .interfaces import ICampaignStructureParser


class DefaultCampaignStructureParser(ICampaignStructureParser):
    """
    Default implementation of ICampaignStructureParser.
    Uses basic line-level deterministic rules to identify structure.
    """
    def __init__(self) -> None:
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        self.bullet_pattern = re.compile(r'^-\s+(.*)$')
        self.numbered_pattern = re.compile(r'^(\d+)\.\s+(.*)$')
        self.separator_pattern = re.compile(r'^[-*_]{3,}$')

    def parse(self, text: NormalizedCampaignText) -> StructuredCampaignDocument:
        lines = text.normalized_text.split('\n')
        sections: List[DocumentSection] = []
        
        current_section_title: Optional[str] = None
        current_elements: List[DocumentElement] = []
        section_position = 0
        
        n = len(lines)
        i = 0
        
        def push_section() -> None:
            nonlocal section_position, current_section_title, current_elements
            if current_elements or current_section_title is not None:
                sections.append(DocumentSection(
                    position=section_position,
                    title=current_section_title,
                    elements=current_elements
                ))
                section_position += 1
            current_section_title = None
            current_elements = []

        while i < n:
            line = lines[i]
            stripped_line = line.strip()
            
            if not stripped_line:
                i += 1
                continue
                
            heading_match = self.heading_pattern.match(stripped_line)
            if heading_match:
                push_section()
                current_section_title = heading_match.group(2).strip()
                i += 1
                continue
                
            separator_match = self.separator_pattern.match(stripped_line)
            if separator_match:
                current_elements.append(SeparatorBlock(
                    original_line=line,
                    start_line=i,
                    end_line=i
                ))
                i += 1
                continue
                
            bullet_match = self.bullet_pattern.match(stripped_line)
            if bullet_match:
                start_i = i
                items = []
                orig_lines = []
                while i < n:
                    curr_line = lines[i]
                    curr_stripped = curr_line.strip()
                    if not curr_stripped:
                        break  # Stop list on empty line
                        
                    bm = self.bullet_pattern.match(curr_stripped)
                    if bm:
                        items.append(bm.group(1).strip())
                        orig_lines.append(curr_line)
                        i += 1
                    else:
                        break
                current_elements.append(BulletListBlock(
                    items=items,
                    original_lines=orig_lines,
                    start_line=start_i,
                    end_line=i - 1
                ))
                continue
                
            num_match = self.numbered_pattern.match(stripped_line)
            if num_match:
                start_i = i
                items = []
                orig_lines = []
                while i < n:
                    curr_line = lines[i]
                    curr_stripped = curr_line.strip()
                    if not curr_stripped:
                        break
                        
                    nm = self.numbered_pattern.match(curr_stripped)
                    if nm:
                        items.append(nm.group(2).strip())
                        orig_lines.append(curr_line)
                        i += 1
                    else:
                        break
                current_elements.append(NumberedListBlock(
                    items=items,
                    original_lines=orig_lines,
                    start_line=start_i,
                    end_line=i - 1
                ))
                continue
                
            # If it's none of the above, it's a paragraph
            start_i = i
            orig_lines = []
            while i < n:
                curr_line = lines[i]
                curr_stripped = curr_line.strip()
                if not curr_stripped:
                    break
                    
                # A paragraph ends if we hit another block type
                if (self.heading_pattern.match(curr_stripped) or
                    self.separator_pattern.match(curr_stripped) or
                    self.bullet_pattern.match(curr_stripped) or
                    self.numbered_pattern.match(curr_stripped)):
                    break
                    
                orig_lines.append(curr_line)
                i += 1
                
            current_elements.append(ParagraphBlock(
                text=" ".join([line.strip() for line in orig_lines]),
                original_lines=orig_lines,
                start_line=start_i,
                end_line=i - 1
            ))
            
        # Push the final section
        push_section()
        
        # Ensure at least one section for an empty document
        if not sections:
            sections.append(DocumentSection(
                position=0,
                title=None,
                elements=[]
            ))
        
        return StructuredCampaignDocument(sections=sections)
