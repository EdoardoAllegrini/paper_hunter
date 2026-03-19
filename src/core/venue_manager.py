"""Venue management functionality."""

import json
import os
from typing import Any, Dict, List


class VenueManager:
    """Manages venue database (DBLP venues and their acronyms) and saved search queues."""

    def __init__(self, config_path: str = "config/venues.json", presets_path: str = "config/presets.json"):
        """
        Initialize venue manager.

        Args:
            config_path: Path to venues.json file
            presets_path: Path to presets.json file for saved search queues
        """
        self.config_path = config_path
        self.presets_path = presets_path
        self._venues = self._load_json(self.config_path)
        self._presets = self._load_json(self.presets_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        """Generic loader for JSON files."""
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_json(self, data: Dict[str, Any], path: str) -> None:
        """Generic saver for JSON files."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    # --- Venue Management ---
    def get_all(self) -> Dict[str, str]:
        """Get all venues as dictionary."""
        return self._venues.copy()

    def get_acronym(self, venue_name: str) -> str | None:
        """Get acronym for a venue."""
        return self._venues.get(venue_name)

    def add(self, name: str, acronym: str) -> None:
        """Add a new venue."""
        self._venues[name.strip()] = acronym.strip().lower()
        self._save_json(self._venues, self.config_path)

    def delete(self, name: str) -> bool:
        """Delete a venue."""
        if name in self._venues:
            del self._venues[name]
            self._save_json(self._venues, self.config_path)
            return True
        return False

    def exists(self, name: str) -> bool:
        """Check if venue exists."""
        return name in self._venues

    # --- Preset (Saved Queues) Management ---
    def get_presets(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all saved search queues."""
        return self._presets.copy()

    def save_preset(self, preset_name: str, queue: List[Dict[str, str]]) -> None:
        """Save a current search queue as a preset."""
        # Save a copy of the list to avoid reference mutation issues
        self._presets[preset_name.strip()] = [dict(item) for item in queue]
        self._save_json(self._presets, self.presets_path)

    def delete_preset(self, preset_name: str) -> bool:
        """Delete a saved search queue preset."""
        if preset_name in self._presets:
            del self._presets[preset_name]
            self._save_json(self._presets, self.presets_path)
            return True
        return False
