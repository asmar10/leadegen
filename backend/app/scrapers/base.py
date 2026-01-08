from abc import ABC, abstractmethod
from typing import Any, Optional
import asyncio
import random

from app.core.config import get_settings


class BaseScraper(ABC):
    """Abstract base class for all scrapers (SOLID: Open/Closed, Liskov Substitution)."""

    def __init__(self):
        self.settings = get_settings()

    async def delay(self) -> None:
        """Random delay between requests to avoid rate limiting."""
        delay_time = random.uniform(
            self.settings.scrape_delay_min,
            self.settings.scrape_delay_max,
        )
        await asyncio.sleep(delay_time)

    @abstractmethod
    async def scrape(self, url: str) -> dict[str, Any]:
        """
        Scrape data from the given URL.

        Args:
            url: The URL to scrape

        Returns:
            Dictionary containing scraped data
        """
        pass

    @abstractmethod
    async def validate(self, url: str) -> bool:
        """
        Validate that the URL is scrapeable by this scraper.

        Args:
            url: The URL to validate

        Returns:
            True if the URL can be scraped by this scraper
        """
        pass


class SearchScraper(BaseScraper):
    """Base class for search engine scrapers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 100) -> list[str]:
        """
        Search for URLs matching the query.

        Args:
            query: Search query string
            max_results: Maximum number of URLs to return

        Returns:
            List of URLs found
        """
        pass


class DataExtractor(ABC):
    """Base class for data extractors (SOLID: Interface Segregation)."""

    @abstractmethod
    async def extract(self, html: str, url: str) -> dict[str, Any]:
        """
        Extract structured data from HTML content.

        Args:
            html: Raw HTML content
            url: Source URL

        Returns:
            Dictionary containing extracted data
        """
        pass
