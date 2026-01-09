import re
import json
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper


class TikTokScraper(BaseScraper):
    """Scrape TikTok profiles for bio links and business info."""

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
        """Create a new page."""
        browser = await self._get_browser()
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

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
        """Normalize TikTok handle to username only."""
        handle = handle.strip().lstrip("@")

        # If it's a URL, extract username
        if "tiktok.com" in handle:
            parsed = urlparse(handle)
            path = parsed.path.strip("/")
            # Remove @ prefix if present in path
            handle = path.lstrip("@").split("/")[0]

        return handle

    def _build_profile_url(self, handle: str) -> str:
        """Build TikTok profile URL."""
        username = self._normalize_handle(handle)
        return f"https://www.tiktok.com/@{username}"

    async def validate(self, url: str) -> bool:
        """Check if URL/handle is a valid TikTok profile."""
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

                content = await page.content()
                # Check for 404 indicators
                return "Couldn't find this account" not in content

            finally:
                await page.context.close()

        except Exception:
            return False

    async def scrape(self, url: str) -> dict[str, Any]:
        """
        Scrape TikTok profile for bio and links.

        Args:
            url: TikTok handle (@username) or full URL

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
                "email": None,
            }

            # Extract from HTML
            data.update(self._extract_from_html(html, soup))

            # Try embedded JSON data
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

        # Look for bio link in page
        # TikTok displays links in profile
        link_elements = soup.find_all("a", href=True)
        for link in link_elements:
            href = link.get("href", "")
            if self._is_valid_bio_link(href):
                data["bio_link"] = href
                break

        # Extract from embedded JSON patterns
        patterns = {
            "nickname": r'"nickname"\s*:\s*"([^"]*)"',
            "signature": r'"signature"\s*:\s*"([^"]*)"',
            "bio_link": r'"bioLink"\s*:\s*\{[^}]*"link"\s*:\s*"([^"]*)"',
            "follower_count": r'"followerCount"\s*:\s*(\d+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, html)
            if match:
                value = match.group(1)
                if key == "nickname":
                    data["name"] = value
                elif key == "signature":
                    data["bio"] = value.encode().decode('unicode_escape')
                elif key == "bio_link" and not data.get("bio_link"):
                    data["bio_link"] = value.replace(r'\/', '/')
                elif key == "follower_count":
                    data["followers"] = int(value)

        # Look for email in bio
        if data.get("bio"):
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', data["bio"])
            if email_match:
                data["email"] = email_match.group(0)

        return data

    def _extract_json_data(self, html: str) -> dict[str, Any] | None:
        """Try to extract data from embedded JSON."""
        data = {}

        # Look for SIGI_STATE or similar embedded data
        patterns = [
            r'<script id="SIGI_STATE"[^>]*>(\{.+?\})</script>',
            r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(\{.+?\})</script>',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    parsed = json.loads(json_str)

                    # Navigate to user data (structure varies)
                    user = None

                    # Try different paths
                    if "UserModule" in parsed:
                        users = parsed.get("UserModule", {}).get("users", {})
                        if users:
                            user = list(users.values())[0]

                    if "__DEFAULT_SCOPE__" in parsed:
                        user_detail = parsed.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {})
                        user = user_detail.get("userInfo", {}).get("user")

                    if user:
                        if user.get("nickname"):
                            data["name"] = user["nickname"]
                        if user.get("signature"):
                            data["bio"] = user["signature"]
                        if user.get("bioLink", {}).get("link"):
                            data["bio_link"] = user["bioLink"]["link"]

                        # Stats might be in different place
                        stats = user.get("stats") or parsed.get("UserModule", {}).get("stats", {})
                        if isinstance(stats, dict):
                            stat_values = list(stats.values())[0] if stats else {}
                            if isinstance(stat_values, dict) and stat_values.get("followerCount"):
                                data["followers"] = stat_values["followerCount"]

                except (json.JSONDecodeError, KeyError, TypeError, IndexError):
                    continue

        return data if data else None

    def _is_valid_bio_link(self, url: str) -> bool:
        """Check if URL is a valid bio link."""
        if not url.startswith("http"):
            return False

        excluded = [
            "tiktok.com",
            "facebook.com",
            "fb.com",
            "instagram.com",
            "twitter.com",
            "x.com",
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
