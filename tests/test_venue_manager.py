"""Tests for venue management."""

import json
import os
import tempfile

import pytest

from src.core.venue_manager import VenueManager


@pytest.fixture
def temp_config():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "USENIX Security": "uss",
                "ACM CCS": "ccs",
            },
            f,
        )
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


def test_load_venues(temp_config):
    """Test loading existing venues."""
    manager = VenueManager(temp_config)
    venues = manager.get_all()

    assert len(venues) == 2
    assert manager.get_acronym("USENIX Security") == "uss"


def test_add_venue(temp_config):
    """Test adding a new venue."""
    manager = VenueManager(temp_config)
    manager.add("IEEE S&P", "sp")

    assert manager.exists("IEEE S&P")
    assert manager.get_acronym("IEEE S&P") == "sp"


def test_delete_venue(temp_config):
    """Test deleting a venue."""
    manager = VenueManager(temp_config)
    assert manager.delete("USENIX Security")
    assert not manager.exists("USENIX Security")


def test_delete_nonexistent():
    """Test deleting non-existent venue."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({}, f)
        temp_path = f.name

    try:
        manager = VenueManager(temp_path)
        result = manager.delete("NonExistent")
        assert result is False
    finally:
        os.unlink(temp_path)
