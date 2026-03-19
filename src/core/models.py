"""Data models for Paper Hunter."""

from dataclasses import dataclass


@dataclass
class Paper:
    """Represents an academic paper from DBLP."""

    title: str
    authors: str
    venue: str
    url: str

    def to_dict(self) -> dict:
        """Convert paper to dictionary."""
        return {
            "Title": self.title,
            "Authors": self.authors,
            "Venue": self.venue,
            "URL": self.url,
        }


@dataclass
class SearchTarget:
    """Represents a search target (venue + year combination)."""

    name: str
    acronym: str
    year: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "acronym": self.acronym,
            "year": self.year,
        }
