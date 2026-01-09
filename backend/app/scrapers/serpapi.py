import os
from typing import Any

import httpx

from app.scrapers.base import SearchScraper


class SerpAPIScraper(SearchScraper):
    """
    Google search using SerpAPI (paid service with free tier).

    More reliable than direct scraping, avoids blocks.
    Free tier: 100 searches/month
    """

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, api_key: str | None = None):
        super().__init__()
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SerpAPI key required. Set SERPAPI_KEY env var or pass api_key.")

    def _build_search_query(self, niche: str, location: str | None = None) -> str:
        """Build search query for finding Shopify stores."""
        query_parts = [f'"{niche}"']
        query_parts.append('(site:myshopify.com OR "Powered by Shopify")')

        if location:
            query_parts.append(f'"{location}"')

        return " ".join(query_parts)

    async def search(self, query: str, max_results: int = 100) -> list[str]:
        """
        Search Google via SerpAPI.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of URLs found
        """
        all_urls = []
        start = 0
        results_per_page = 100  # SerpAPI max per request

        async with httpx.AsyncClient() as client:
            while len(all_urls) < max_results:
                params = {
                    "q": query,
                    "api_key": self.api_key,
                    "engine": "google",
                    "num": min(results_per_page, max_results - len(all_urls)),
                    "start": start,
                }

                response = await client.get(self.BASE_URL, params=params)

                if response.status_code != 200:
                    break

                data = response.json()

                # Extract organic results
                organic_results = data.get("organic_results", [])
                if not organic_results:
                    break

                for result in organic_results:
                    url = result.get("link")
                    if url and self._is_valid_url(url):
                        all_urls.append(url)

                # Check if more pages available
                if not data.get("serpapi_pagination", {}).get("next"):
                    break

                start += results_per_page
                await self.delay()

        return list(dict.fromkeys(all_urls))[:max_results]

    async def search_shopify_stores(
        self,
        niche: str,
        location: str | None = None,
        max_results: int = 50,
    ) -> list[str]:
        """Search for Shopify stores in a niche."""
        query = self._build_search_query(niche, location)
        return await self.search(query, max_results)

    def _is_valid_url(self, url: str) -> bool:
        """Filter out non-store URLs."""
        excluded = [
            "google.com",
            "youtube.com",
            "facebook.com",
            "twitter.com",
            "instagram.com",
            "tiktok.com",
            "linkedin.com",
            "pinterest.com",
            "reddit.com",
            "wikipedia.org",
            "amazon.com",
            "ebay.com",
            "etsy.com",
        ]

        url_lower = url.lower()
        for ex in excluded:
            if ex in url_lower:
                return False

        return True

    async def scrape(self, url: str) -> dict[str, Any]:
        """Not applicable for SerpAPI - use for search only."""
        raise NotImplementedError("SerpAPI is for search only. Use ShopifyScraper for scraping.")

    async def validate(self, url: str) -> bool:
        """Not applicable for SerpAPI."""
        return True

    async def get_account_info(self) -> dict[str, Any]:
        """Get SerpAPI account info (remaining searches, etc.)."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://serpapi.com/account",
                params={"api_key": self.api_key},
            )

            if response.status_code == 200:
                return response.json()

            return {"error": "Failed to fetch account info"}
