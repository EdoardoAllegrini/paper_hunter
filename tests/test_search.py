"""Tests for the search functionality."""

import pytest

from src.core.models import Paper
from src.core.search import search_papers


@pytest.fixture
def sample_papers():
    """Create sample papers for testing."""
    return [
        Paper(
            title="Fuzzing with Machine Learning",
            authors="John Doe, Jane Smith",
            venue="USENIX Security 2024",
            url="https://example.com/1",
        ),
        Paper(
            title="Learning from Adversarial Examples",
            authors="Alice Johnson",
            venue="USENIX Security 2024",
            url="https://example.com/2",
        ),
        Paper(
            title="Hardware Security in Trusted Execution Environments",
            authors="Bob Williams",
            venue="CCS 2024",
            url="https://example.com/3",
        ),
    ]


def test_search_and_operator(sample_papers):
    """Test AND operator filtering."""
    results = search_papers(sample_papers, "fuzzing, machine learning", "AND")
    assert len(results) == 1
    assert results[0].title == "Fuzzing with Machine Learning"


def test_search_or_operator(sample_papers):
    """Test OR operator filtering."""
    results = search_papers(sample_papers, "fuzzing, adversarial", "OR")
    assert len(results) == 2


def test_search_empty_keywords(sample_papers):
    """Test with empty keywords returns all papers."""
    results = search_papers(sample_papers, "", "AND")
    assert len(results) == len(sample_papers)


def test_search_no_matches(sample_papers):
    """Test search with no matching papers."""
    results = search_papers(sample_papers, "blockchain", "AND")
    assert len(results) == 0
