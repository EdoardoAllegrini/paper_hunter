"""Venue management functionality."""

import json
import os
from typing import Dict


class VenueManager:
    """Manages venue database (DBLP venues and their acronyms)."""

    def __init__(self, config_path: str = "config/venues.json"):
        """
        Initialize venue manager.

        Args:
            config_path: Path to venues.json file
        """
        self.config_path = config_path
        self._venues = self._load_venues()

    def _load_venues(self) -> Dict[str, str]:
        """Load venues from JSON file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_venues(self) -> None:
        """Save venues to JSON file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self._venues, f, indent=4)

    def get_all(self) -> Dict[str, str]:
        """Get all venues as dictionary."""
        return self._venues.copy()

    def get_acronym(self, venue_name: str) -> str | None:
        """Get acronym for a venue."""
        return self._venues.get(venue_name)

    def add(self, name: str, acronym: str) -> None:
        """
        Add a new venue.

        Args:
            name: Full venue name (e.g., "USENIX Security")
            acronym: DBLP acronym (e.g., "uss")
        """
        self._venues[name.strip()] = acronym.strip().lower()
        self._save_venues()

    def delete(self, name: str) -> bool:
        """
        Delete a venue.

        Args:
            name: Venue name to delete

        Returns:
            True if deleted, False if not found
        """
        if name in self._venues:
            del self._venues[name]
            self._save_venues()
            return True
        return False

    def exists(self, name: str) -> bool:
        """Check if venue exists."""
        return name in self._venues
