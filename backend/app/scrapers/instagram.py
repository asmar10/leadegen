import re
import json
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper


class InstagramScraper(BaseScraper):
    """Scrape Instagram profiles for bio links and business info."""

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
        """Create a new page with mobile user agent (better for Instagram)."""
        browser = await self._get_browser()
        context = await browser.new_context(
            viewport={"width": 430, "height": 932},
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
        )
        page = await context.new_page()

        # Anti-detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        return page

    async def close(self) -> None:
        """Close browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None

    def _normalize_handle(self, handle: str) -> str:
        """Normalize Instagram handle to username only."""
        handle = handle.strip().lstrip("@")

        # If it's a URL, extract username
        if "instagram.com" in handle:
            parsed = urlparse(handle)
            path = parsed.path.strip("/")
            handle = path.split("/")[0]

        return handle

    def _build_profile_url(self, handle: str) -> str:
        """Build Instagram profile URL."""
        username = self._normalize_handle(handle)
        return f"https://www.instagram.com/{username}/"

    async def validate(self, url: str) -> bool:
        """Check if URL/handle is a valid Instagram profile."""
        try:
            handle = self._normalize_handle(url)
            if not handle or len(handle) < 1:
                return False

            profile_url = self._build_profile_url(handle)
            page = await self._create_page()

            try:
                response = await page.goto(profile_url, wait_until="domcontentloaded", timeout=15000)
                if not response or not response.ok:
                    return False

                # Check if profile exists (not 404 page)
                content = await page.content()
                return "Sorry, this page isn't available" not in content

            finally:
                await page.context.close()

        except Exception:
            return False

    async def scrape(self, url: str) -> dict[str, Any]:
        """
        Scrape Instagram profile for bio and links.

        Args:
            url: Instagram handle (@username) or full URL

        Returns:
            Profile data including bio link if present
        """
        handle = self._normalize_handle(url)
        profile_url = self._build_profile_url(handle)
        page = await self._create_page()

        try:
            await page.goto(profile_url, wait_until="networkidle", timeout=30000)
            await self.delay()

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            data = {
                "handle": f"@{handle}",
                "url": profile_url,
                "name": None,
                "bio": None,
                "bio_link": None,
                "followers": None,
                "is_business": False,
                "category": None,
                "email": None,
            }

            # Try to extract data from page content
            data.update(self._extract_from_html(html, soup))

            # Try to extract from JSON-LD or embedded data
            json_data = self._extract_json_data(html)
            if json_data:
                data.update(json_data)

            return data

        except Exception as e:
            return {"error": str(e), "handle": f"@{handle}", "url": profile_url}

        finally:
            await page.context.close()

    def _extract_from_html(self, html: str, soup: BeautifulSoup) -> dict[str, Any]:
        """Extract data from HTML content."""
        data = {}

        # Try to find bio link
        # Instagram often puts bio links in specific elements
        link_patterns = [
            r'href="(https?://[^"]+)"[^>]*>(?:[^<]*linktr\.ee|[^<]*link\s*in\s*bio)',
            r'"external_url"\s*:\s*"([^"]+)"',
            r'"biography_with_entities"[^}]*"external_url"\s*:\s*"([^"]+)"',
        ]

        for pattern in link_patterns:
            match = re.search(pattern, html, re.I)
            if match:
                url = match.group(1)
                # Unescape JSON encoding
                url = url.replace(r'\/', '/').replace(r'\\u0026', '&')
                if self._is_valid_bio_link(url):
                    data["bio_link"] = url
                    break

        # Extract bio text
        bio_match = re.search(r'"biography"\s*:\s*"([^"]*)"', html)
        if bio_match:
            bio = bio_match.group(1)
            # Unescape
            bio = bio.encode().decode('unicode_escape')
            data["bio"] = bio

        # Extract name
        name_match = re.search(r'"full_name"\s*:\s*"([^"]*)"', html)
        if name_match:
            data["name"] = name_match.group(1)

        # Extract follower count
        follower_match = re.search(r'"edge_followed_by"\s*:\s*\{\s*"count"\s*:\s*(\d+)', html)
        if follower_match:
            data["followers"] = int(follower_match.group(1))

        # Check if business account
        if '"is_business_account":true' in html:
            data["is_business"] = True

        # Extract category
        cat_match = re.search(r'"category_name"\s*:\s*"([^"]*)"', html)
        if cat_match:
            data["category"] = cat_match.group(1)

        # Look for email in bio
        if data.get("bio"):
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', data["bio"])
            if email_match:
                data["email"] = email_match.group(0)

        return data

    def _extract_json_data(self, html: str) -> dict[str, Any] | None:
        """Try to extract data from embedded JSON."""
        data = {}

        # Look for shared data JSON
        patterns = [
            r'window\._sharedData\s*=\s*(\{.+?\});</script>',
            r'window\.__additionalDataLoaded\([^,]+,\s*(\{.+?\})\);',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    parsed = json.loads(json_str)

                    # Navigate to user data
                    user = None
                    if "entry_data" in parsed:
                        profile_page = parsed.get("entry_data", {}).get("ProfilePage", [{}])
                        if profile_page:
                            user = profile_page[0].get("graphql", {}).get("user")

                    if user:
                        if user.get("external_url"):
                            data["bio_link"] = user["external_url"]
                        if user.get("biography"):
                            data["bio"] = user["biography"]
                        if user.get("full_name"):
                            data["name"] = user["full_name"]
                        if user.get("is_business_account"):
                            data["is_business"] = True
                        if user.get("business_email"):
                            data["email"] = user["business_email"]
                        if user.get("edge_followed_by", {}).get("count"):
                            data["followers"] = user["edge_followed_by"]["count"]

                except (json.JSONDecodeError, KeyError, TypeError):
                    continue

        return data if data else None

    def _is_valid_bio_link(self, url: str) -> bool:
        """Check if URL is a valid bio link (not Instagram internal)."""
        if not url.startswith("http"):
            return False

        excluded = [
            "instagram.com",
            "facebook.com",
            "fb.com",
        ]

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for ex in excluded:
            if ex in domain:
                return False

        return True

    async def get_bio_link(self, handle: str) -> str | None:
        """Quick method to just get the bio link."""
        result = await self.scrape(handle)
        return result.get("bio_link")
