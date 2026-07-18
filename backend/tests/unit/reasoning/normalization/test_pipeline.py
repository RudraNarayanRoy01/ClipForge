import pytest
from src.reasoning.normalization import DefaultCampaignNormalizationPipeline, CampaignSource

@pytest.fixture
def pipeline():
    return DefaultCampaignNormalizationPipeline()

def test_pipeline_preserves_plain_text(pipeline):
    text = "Just a regular campaign description.\nNo weird stuff."
    result = pipeline.normalize(text)
    assert result.original_text == text
    assert result.normalized_text == text
    assert result.source == CampaignSource.UNKNOWN

def test_pipeline_removes_carriage_returns(pipeline):
    text = "Line 1\r\nLine 2\rLine 3"
    result = pipeline.normalize(text)
    assert result.normalized_text == "Line 1\nLine 2\nLine 3"

def test_pipeline_normalizes_bullets(pipeline):
    text = "• Point 1\n* Point 2\n+ Point 3\n▪ Point 4"
    result = pipeline.normalize(text)
    assert result.normalized_text == "- Point 1\n- Point 2\n- Point 3\n- Point 4"

def test_pipeline_normalizes_quotes(pipeline):
    text = "“Smart quotes” and ‘single quotes’"
    result = pipeline.normalize(text)
    assert result.normalized_text == '"Smart quotes" and \'single quotes\''

def test_pipeline_removes_invisible_characters(pipeline):
    # Includes some null bytes and vertical tabs
    text = "Text\x00 with\x0b control\x1f chars."
    result = pipeline.normalize(text)
    assert result.normalized_text == "Text with control chars."

def test_pipeline_trims_lines_and_document(pipeline):
    text = "   \n  Line 1  \n\tLine 2\t\n   "
    result = pipeline.normalize(text)
    assert result.normalized_text == "Line 1\nLine 2"

def test_pipeline_collapses_blank_lines(pipeline):
    text = "Line 1\n\n\n\nLine 2\n\n\nLine 3"
    result = pipeline.normalize(text)
    assert result.normalized_text == "Line 1\n\nLine 2\n\nLine 3"

def test_pipeline_idempotency(pipeline):
    raw_text = "  • Messy\r\n\n\n\nText \x0b  “here”  "
    
    first_run = pipeline.normalize(raw_text)
    assert first_run.normalized_text == "- Messy\n\nText   \"here\""
    
    # Running it again on the already normalized text should yield the same output
    second_run = pipeline.normalize(first_run.normalized_text)
    assert second_run.normalized_text == first_run.normalized_text

def test_pipeline_with_source(pipeline):
    text = "Discord copy paste"
    result = pipeline.normalize(text, source=CampaignSource.DISCORD)
    assert result.source == CampaignSource.DISCORD
    assert result.normalized_text == "Discord copy paste"
