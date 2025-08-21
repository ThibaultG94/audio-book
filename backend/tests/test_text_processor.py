"""Tests for text processing services."""

from app.services.text_processor import TextProcessor

def test_clean_text():
    """Test text cleaning functionality."""
    dirty_text = "Text   with    multiple   spaces\n\n\nand\n\nnewlines"
    clean = TextProcessor.clean_text(dirty_text)
    assert "   " not in clean
    assert "\n\n\n" not in clean

def test_chunk_paragraphs():
    """Test text chunking."""
    text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
    chunks = list(TextProcessor.chunk_paragraphs(text, max_chars=20))
    assert len(chunks) > 1
    assert all(len(chunk) <= 20 for chunk in chunks)