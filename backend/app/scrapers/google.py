import asyncio
import re
from typing import Any
from urllib.parse import urlparse, parse_qs, unquote

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

from app.scrapers.base import SearchScraper


class GoogleScraper(SearchScraper):
    """Google search scraper using Playwright for JavaScript rendering."""

    def __init__(self):
        super().__init__()
        self._browser: Browser | None = None

    async def _get_browser(self) -> Browser:
        """Get or create browser instance."""
        if self._browser is None or not self._browser.is_connected():
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ],
            )
        return self._browser

    async def _create_page(self) -> Page:
        """Create a new page with anti-detection settings."""
        browser = await self._get_browser()
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        # Mask webdriver detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        return page

    async def close(self) -> None:
        """Close browser instance."""
        if self._browser:
            await self._browser.close()
            self._browser = None

    def _build_search_query(self, niche: str, location: str | None = None) -> str:
        """Build Google search query for finding Shopify stores."""
        # Search for Shopify stores in a niche
        query_parts = [f'"{niche}"']

        # Shopify indicators
        query_parts.append('(site:myshopify.com OR "Powered by Shopify" OR "shopify")')

        if location:
            query_parts.append(f'"{location}"')

        return " ".join(query_parts)

    def _extract_urls_from_results(self, page_content: str) -> list[str]:
        """Extract URLs from Google search results."""
        urls = []

        # Match URLs in search result links
        # Google wraps URLs in /url?q= or displays them directly
        url_pattern = r'href="(/url\?q=([^"&]+)|https?://[^"]+)"'
        matches = re.findall(url_pattern, page_content)

        for match in matches:
            full_match, extracted_url = match
            if extracted_url:
                # URL was in /url?q= format
                url = unquote(extracted_url)
            else:
                # Direct URL
                url = full_match.replace('href="', '').rstrip('"')

            # Filter out Google's own URLs and common non-store URLs
            if self._is_valid_result_url(url):
                urls.append(url)

        return list(dict.fromkeys(urls))  # Remove duplicates, preserve order

    def _is_valid_result_url(self, url: str) -> bool:
        """Check if URL is a valid search result (not Google internal)."""
        if not url.startswith("http"):
            return False

        excluded_domains = [
            "google.com",
            "google.",
            "gstatic.com",
            "googleapis.com",
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

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for excluded in excluded_domains:
            if excluded in domain:
                return False

        return True

    async def search(self, query: str, max_results: int = 50) -> list[str]:
        """
        Search Google for URLs matching the query.

        Args:
            query: Search query (use _build_search_query for Shopify searches)
            max_results: Maximum number of URLs to return

        Returns:
            List of URLs found
        """
        page = await self._create_page()
        all_urls = []

        try:
            # Navigate to Google
            await page.goto("https://www.google.com", wait_until="networkidle")
            await self.delay()

            # Handle cookie consent if present
            try:
                accept_btn = page.locator('button:has-text("Accept all")')
                if await accept_btn.is_visible(timeout=2000):
                    await accept_btn.click()
                    await self.delay()
            except PlaywrightTimeout:
                pass

            # Enter search query
            search_input = page.locator('textarea[name="q"], input[name="q"]')
            await search_input.fill(query)
            await search_input.press("Enter")
            await page.wait_for_load_state("networkidle")
            await self.delay()

            # Collect results from multiple pages
            pages_scraped = 0
            max_pages = (max_results // 10) + 1

            while len(all_urls) < max_results and pages_scraped < max_pages:
                # Get page content
                content = await page.content()
                urls = self._extract_urls_from_results(content)
                all_urls.extend(urls)

                # Try to go to next page
                try:
                    next_btn = page.locator('a#pnnext, a[aria-label="Next"]')
                    if await next_btn.is_visible(timeout=3000):
                        await next_btn.click()
                        await page.wait_for_load_state("networkidle")
                        await self.delay()
                        pages_scraped += 1
                    else:
                        break
                except PlaywrightTimeout:
                    break

            return list(dict.fromkeys(all_urls))[:max_results]

        finally:
            await page.context.close()

    async def search_shopify_stores(
        self,
        niche: str,
        location: str | None = None,
        max_results: int = 50,
    ) -> list[str]:
        """
        Search for Shopify stores in a specific niche.

        Args:
            niche: Business niche/category
            location: Optional geographic location
            max_results: Maximum number of URLs to return

        Returns:
            List of potential Shopify store URLs
        """
        query = self._build_search_query(niche, location)
        return await self.search(query, max_results)

    async def scrape(self, url: str) -> dict[str, Any]:
        """Scrape a URL and return page content."""
        page = await self._create_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await self.delay()

            return {
                "url": url,
                "html": await page.content(),
                "title": await page.title(),
            }
        finally:
            await page.context.close()

    async def validate(self, url: str) -> bool:
        """Validate URL is accessible."""
        try:
            page = await self._create_page()
            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                return response is not None and response.ok
            finally:
                await page.context.close()
        except Exception:
            return False
