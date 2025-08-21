"""Tests for text extraction services."""

import pytest
from pathlib import Path
from app.services.text_extractor import TextExtractor
from app.core.exceptions import TextExtractionError

def test_extract_from_pdf():
    """Test PDF text extraction."""
    # Create a simple test PDF or use fixture
    # This would require a test PDF file
    pass

def test_extract_from_epub():
    """Test EPUB text extraction.""" 
    # Create a simple test EPUB or use fixture
    pass

def test_unsupported_format():
    """Test handling of unsupported file formats."""
    with pytest.raises(TextExtractionError):
        TextExtractor.extract_from_file(Path("test.txt"))