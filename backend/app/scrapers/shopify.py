import re
import json
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper, DataExtractor


class ShopifyDetector:
    """Detect if a website is a Shopify store."""

    SHOPIFY_INDICATORS = [
        # Meta tags and scripts
        r'cdn\.shopify\.com',
        r'shopify\.com/s/',
        r'Shopify\.theme',
        r'Shopify\.routes',
        r'"shopify"',
        r'myshopify\.com',

        # Footer text
        r'Powered by Shopify',
        r'powered by shopify',

        # Common Shopify paths
        r'/collections/',
        r'/products/',
        r'/cart\.js',
    ]

    @classmethod
    def is_shopify(cls, html: str, url: str) -> bool:
        """Check if HTML content indicates a Shopify store."""
        # Check URL first
        if "myshopify.com" in url:
            return True

        # Check HTML content for indicators
        for pattern in cls.SHOPIFY_INDICATORS:
            if re.search(pattern, html, re.IGNORECASE):
                return True

        return False


class ShopifyExtractor(DataExtractor):
    """Extract data from Shopify store pages."""

    async def extract(self, html: str, url: str) -> dict[str, Any]:
        """Extract store information from Shopify store HTML."""
        soup = BeautifulSoup(html, "lxml")
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")

        data = {
            "url": url,
            "domain": domain,
            "store_name": self._extract_store_name(soup, domain),
            "description": self._extract_description(soup),
            "email": self._extract_email(html, soup),
            "phone": self._extract_phone(html, soup),
            "country": self._extract_country(soup, html),
            "social_links": self._extract_social_links(soup),
        }

        return data

    def _extract_store_name(self, soup: BeautifulSoup, domain: str) -> str:
        """Extract store name from page."""
        # Try meta tags first
        og_site = soup.find("meta", property="og:site_name")
        if og_site and og_site.get("content"):
            return og_site["content"].strip()

        # Try title tag
        title = soup.find("title")
        if title and title.string:
            # Often formatted as "Page Title – Store Name" or "Store Name | Page"
            title_text = title.string.strip()
            separators = [" – ", " - ", " | ", " · "]
            for sep in separators:
                if sep in title_text:
                    parts = title_text.split(sep)
                    # Usually store name is last or first
                    return parts[-1].strip() if len(parts[-1]) > 2 else parts[0].strip()
            return title_text

        # Fallback to domain
        return domain.split(".")[0].title()

    def _extract_description(self, soup: BeautifulSoup) -> str | None:
        """Extract store description."""
        # Try meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()

        # Try OG description
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()

        return None

    def _extract_email(self, html: str, soup: BeautifulSoup) -> str | None:
        """Extract email address."""
        # Look for mailto links
        mailto_links = soup.find_all("a", href=re.compile(r"^mailto:", re.I))
        for link in mailto_links:
            email = link["href"].replace("mailto:", "").split("?")[0].strip()
            if self._is_valid_email(email):
                return email

        # Regex search in HTML
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, html)

        # Filter out common non-contact emails
        excluded = ["example.com", "email.com", "domain.com", "shopify.com", "sentry.io"]
        for match in matches:
            if not any(ex in match.lower() for ex in excluded):
                if self._is_valid_email(match):
                    return match

        return None

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _extract_phone(self, html: str, soup: BeautifulSoup) -> str | None:
        """Extract phone number."""
        # Look for tel links
        tel_links = soup.find_all("a", href=re.compile(r"^tel:", re.I))
        for link in tel_links:
            phone = link["href"].replace("tel:", "").strip()
            if len(phone) >= 10:
                return phone

        # Regex search for phone patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US/CA
            r'\+?[0-9]{1,3}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}',  # International
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                cleaned = re.sub(r'[^\d+]', '', match)
                if 10 <= len(cleaned) <= 15:
                    return match.strip()

        return None

    def _extract_country(self, soup: BeautifulSoup, html: str) -> str | None:
        """Try to detect store country."""
        # Look for currency indicators
        currency_country_map = {
            "USD": "United States",
            "CAD": "Canada",
            "GBP": "United Kingdom",
            "EUR": "Europe",
            "AUD": "Australia",
            "NZD": "New Zealand",
        }

        # Check for Shopify currency in scripts
        currency_match = re.search(r'"currency"\s*:\s*"([A-Z]{3})"', html)
        if currency_match:
            currency = currency_match.group(1)
            if currency in currency_country_map:
                return currency_country_map[currency]

        # Check for country in address or footer
        country_patterns = [
            r'United States|USA|U\.S\.A',
            r'Canada',
            r'United Kingdom|UK|U\.K\.',
            r'Australia',
            r'Germany|Deutschland',
            r'France',
        ]

        for pattern in country_patterns:
            if re.search(pattern, html, re.I):
                return pattern.split("|")[0]

        return None

    def _extract_social_links(self, soup: BeautifulSoup) -> dict[str, str | None]:
        """Extract social media links."""
        social = {
            "instagram": None,
            "tiktok": None,
            "facebook": None,
            "twitter": None,
        }

        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link["href"].lower()

            if "instagram.com" in href and not social["instagram"]:
                social["instagram"] = self._extract_social_handle(link["href"], "instagram")

            elif "tiktok.com" in href and not social["tiktok"]:
                social["tiktok"] = self._extract_social_handle(link["href"], "tiktok")

            elif "facebook.com" in href and not social["facebook"]:
                social["facebook"] = self._extract_social_handle(link["href"], "facebook")

            elif ("twitter.com" in href or "x.com" in href) and not social["twitter"]:
                social["twitter"] = self._extract_social_handle(link["href"], "twitter")

        return social

    def _extract_social_handle(self, url: str, platform: str) -> str | None:
        """Extract username/handle from social media URL."""
        try:
            parsed = urlparse(url)
            path = parsed.path.strip("/")

            if not path:
                return None

            # Remove common path prefixes
            path = re.sub(r'^(user|profile|pages|p)/', '', path)

            # Get first path segment (username)
            username = path.split("/")[0].split("?")[0]

            if username and len(username) > 1:
                return f"@{username}" if not username.startswith("@") else username

        except Exception:
            pass

        return None


class ShopifyScraper(BaseScraper):
    """Complete Shopify store scraper."""

    def __init__(self):
        super().__init__()
        self._browser: Browser | None = None
        self.extractor = ShopifyExtractor()

    async def _get_browser(self) -> Browser:
        """Get or create browser instance."""
        if self._browser is None or not self._browser.is_connected():
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage", "--no-sandbox"],
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
        return await context.new_page()

    async def close(self) -> None:
        """Close browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None

    async def validate(self, url: str) -> bool:
        """Check if URL is a Shopify store."""
        page = await self._create_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            html = await page.content()
            return ShopifyDetector.is_shopify(html, url)
        except Exception:
            return False
        finally:
            await page.context.close()

    async def scrape(self, url: str) -> dict[str, Any]:
        """Scrape Shopify store data."""
        page = await self._create_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await self.delay()

            html = await page.content()

            # Verify it's actually Shopify
            if not ShopifyDetector.is_shopify(html, url):
                return {"error": "Not a Shopify store", "url": url}

            # Extract store data
            data = await self.extractor.extract(html, url)
            data["is_shopify"] = True

            return data

        except Exception as e:
            return {"error": str(e), "url": url}

        finally:
            await page.context.close()
