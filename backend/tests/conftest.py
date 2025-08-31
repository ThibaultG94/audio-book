"""
Pytest configuration and shared fixtures
"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_epub_file(temp_directory):
    """Create a mock EPUB file"""
    epub_file = temp_directory / "test.epub"
    epub_file.write_bytes(b"fake epub content")
    return epub_file


@pytest.fixture
def mock_pdf_file(temp_directory):
    """Create a mock PDF file"""
    pdf_file = temp_directory / "test.pdf"
    pdf_file.write_bytes(b"fake pdf content")
    return pdf_file


@pytest.fixture
def sample_manifest():
    """Create a sample manifest for testing"""
    return {
        "book_id": "test_book_123",
        "book_title": "Test Book",
        "author": "Test Author",
        "total_chapters": 3,
        "chapters": [
            {
                "index": 0,
                "title": "Chapter 1",
                "filename": "001_TestBook_Chapter1",
                "text_file": "/tmp/ch1.txt",
                "status": "pending",
                "estimated_duration_seconds": 300
            },
            {
                "index": 1,
                "title": "Chapter 2",
                "filename": "002_TestBook_Chapter2",
                "text_file": "/tmp/ch2.txt",
                "status": "pending",
                "estimated_duration_seconds": 450
            },
            {
                "index": 2,
                "title": "Chapter 3",
                "filename": "003_TestBook_Chapter3",
                "text_file": "/tmp/ch3.txt",
                "status": "pending",
                "estimated_duration_seconds": 600
            }
        ]
    }