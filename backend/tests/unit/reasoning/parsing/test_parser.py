import pytest
from src.reasoning.normalization.models import NormalizedCampaignText
from src.reasoning.parsing.parser import DefaultCampaignStructureParser
from src.reasoning.parsing.models import (
    ParagraphBlock,
    BulletListBlock,
    NumberedListBlock,
    SeparatorBlock
)

@pytest.fixture
def parser():
    return DefaultCampaignStructureParser()

def test_parse_empty_document(parser):
    text = NormalizedCampaignText(original_text="", normalized_text="")
    doc = parser.parse(text)
    
    assert len(doc.sections) == 1
    assert doc.sections[0].position == 0
    assert doc.sections[0].title is None
    assert len(doc.sections[0].elements) == 0

def test_parse_simple_paragraphs_without_heading(parser):
    normalized = "First paragraph.\n\nSecond paragraph."
    text = NormalizedCampaignText(original_text=normalized, normalized_text=normalized)
    doc = parser.parse(text)
    
    assert len(doc.sections) == 1
    section = doc.sections[0]
    assert section.title is None
    assert len(section.elements) == 2
    
    p1 = section.elements[0]
    assert isinstance(p1, ParagraphBlock)
    assert p1.text == "First paragraph."
    assert p1.start_line == 0
    assert p1.end_line == 0
    
    p2 = section.elements[1]
    assert isinstance(p2, ParagraphBlock)
    assert p2.text == "Second paragraph."
    assert p2.start_line == 2
    assert p2.end_line == 2

def test_parse_headings_and_paragraphs(parser):
    normalized = "# Introduction\nIntro text.\n\n## Details\nDetail text."
    text = NormalizedCampaignText(original_text=normalized, normalized_text=normalized)
    doc = parser.parse(text)
    
    assert len(doc.sections) == 2
    
    s1 = doc.sections[0]
    assert s1.position == 0
    assert s1.title == "Introduction"
    assert len(s1.elements) == 1
    assert isinstance(s1.elements[0], ParagraphBlock)
    assert s1.elements[0].text == "Intro text."
    
    s2 = doc.sections[1]
    assert s2.position == 1
    assert s2.title == "Details"
    assert len(s2.elements) == 1
    assert isinstance(s2.elements[0], ParagraphBlock)
    assert s2.elements[0].text == "Detail text."

def test_parse_bullet_lists(parser):
    normalized = "Here is a list:\n- item 1\n- item 2\n\nEnd list."
    text = NormalizedCampaignText(original_text=normalized, normalized_text=normalized)
    doc = parser.parse(text)
    
    section = doc.sections[0]
    assert len(section.elements) == 3
    
    assert isinstance(section.elements[0], ParagraphBlock)
    
    bullet_list = section.elements[1]
    assert isinstance(bullet_list, BulletListBlock)
    assert bullet_list.items == ["item 1", "item 2"]
    assert bullet_list.start_line == 1
    assert bullet_list.end_line == 2
    
    assert isinstance(section.elements[2], ParagraphBlock)
    assert section.elements[2].text == "End list."

def test_parse_numbered_lists(parser):
    normalized = "Steps:\n1. one\n2. two"
    text = NormalizedCampaignText(original_text=normalized, normalized_text=normalized)
    doc = parser.parse(text)
    
    section = doc.sections[0]
    assert len(section.elements) == 2
    
    assert isinstance(section.elements[0], ParagraphBlock)
    
    num_list = section.elements[1]
    assert isinstance(num_list, NumberedListBlock)
    assert num_list.items == ["one", "two"]
    assert num_list.start_line == 1
    assert num_list.end_line == 2

def test_parse_separator(parser):
    normalized = "Before\n---\nAfter"
    text = NormalizedCampaignText(original_text=normalized, normalized_text=normalized)
    doc = parser.parse(text)
    
    section = doc.sections[0]
    assert len(section.elements) == 3
    
    assert isinstance(section.elements[0], ParagraphBlock)
    assert section.elements[0].text == "Before"
    
    separator = section.elements[1]
    assert isinstance(separator, SeparatorBlock)
    assert separator.original_line == "---"
    
    assert isinstance(section.elements[2], ParagraphBlock)
    assert section.elements[2].text == "After"

def test_multi_line_paragraph(parser):
    normalized = "Line 1\nLine 2\nLine 3"
    text = NormalizedCampaignText(original_text=normalized, normalized_text=normalized)
    doc = parser.parse(text)
    
    section = doc.sections[0]
    assert len(section.elements) == 1
    
    p = section.elements[0]
    assert isinstance(p, ParagraphBlock)
    assert p.text == "Line 1 Line 2 Line 3"
    assert p.original_lines == ["Line 1", "Line 2", "Line 3"]
    assert p.start_line == 0
    assert p.end_line == 2
