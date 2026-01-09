import random
from dataclasses import dataclass
from typing import Optional
import asyncio


@dataclass
class Proxy:
    """Proxy configuration."""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"

    @property
    def url(self) -> str:
        """Get proxy URL for requests."""
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        return f"{self.protocol}://{auth}{self.host}:{self.port}"

    @property
    def playwright_config(self) -> dict:
        """Get proxy config for Playwright."""
        config = {
            "server": f"{self.protocol}://{self.host}:{self.port}",
        }
        if self.username and self.password:
            config["username"] = self.username
            config["password"] = self.password
        return config


class ProxyRotator:
    """
    Manages proxy rotation for scraping.

    Supports:
    - Round-robin rotation
    - Random selection
    - Marking proxies as failed
    - Automatic retry with different proxy
    """

    def __init__(self, proxies: list[Proxy] | None = None):
        self._proxies: list[Proxy] = proxies or []
        self._failed: set[str] = set()
        self._current_index = 0
        self._lock = asyncio.Lock()

    @classmethod
    def from_list(cls, proxy_strings: list[str]) -> "ProxyRotator":
        """
        Create rotator from list of proxy strings.

        Formats supported:
        - host:port
        - host:port:username:password
        - protocol://host:port
        - protocol://username:password@host:port
        """
        proxies = []
        for proxy_str in proxy_strings:
            proxy = cls._parse_proxy_string(proxy_str)
            if proxy:
                proxies.append(proxy)
        return cls(proxies)

    @staticmethod
    def _parse_proxy_string(proxy_str: str) -> Proxy | None:
        """Parse a proxy string into Proxy object."""
        try:
            proxy_str = proxy_str.strip()
            if not proxy_str:
                return None

            protocol = "http"
            username = None
            password = None

            # Check for protocol prefix
            if "://" in proxy_str:
                protocol, proxy_str = proxy_str.split("://", 1)

            # Check for auth
            if "@" in proxy_str:
                auth, proxy_str = proxy_str.rsplit("@", 1)
                if ":" in auth:
                    username, password = auth.split(":", 1)

            # Parse host:port or host:port:user:pass
            parts = proxy_str.split(":")

            if len(parts) == 2:
                host, port = parts
            elif len(parts) == 4 and not username:
                host, port, username, password = parts
            else:
                return None

            return Proxy(
                host=host,
                port=int(port),
                username=username,
                password=password,
                protocol=protocol,
            )

        except (ValueError, IndexError):
            return None

    def add_proxy(self, proxy: Proxy) -> None:
        """Add a proxy to the rotation."""
        self._proxies.append(proxy)

    def add_proxies(self, proxies: list[Proxy]) -> None:
        """Add multiple proxies."""
        self._proxies.extend(proxies)

    async def get_next(self) -> Proxy | None:
        """Get next proxy in rotation (round-robin)."""
        async with self._lock:
            available = [p for p in self._proxies if p.url not in self._failed]
            if not available:
                return None

            proxy = available[self._current_index % len(available)]
            self._current_index += 1
            return proxy

    async def get_random(self) -> Proxy | None:
        """Get a random proxy."""
        available = [p for p in self._proxies if p.url not in self._failed]
        if not available:
            return None
        return random.choice(available)

    async def mark_failed(self, proxy: Proxy) -> None:
        """Mark a proxy as failed."""
        async with self._lock:
            self._failed.add(proxy.url)

    async def reset_failed(self) -> None:
        """Reset all failed proxies."""
        async with self._lock:
            self._failed.clear()

    @property
    def available_count(self) -> int:
        """Number of available proxies."""
        return len([p for p in self._proxies if p.url not in self._failed])

    @property
    def total_count(self) -> int:
        """Total number of proxies."""
        return len(self._proxies)

    @property
    def has_proxies(self) -> bool:
        """Check if any proxies are available."""
        return self.available_count > 0


class ProxyManager:
    """
    High-level proxy management for scrapers.

    Usage:
        manager = ProxyManager()
        manager.load_from_env()  # or load_from_file

        async with manager.get_proxy() as proxy:
            # Use proxy for request
            # Automatically marked as failed if exception raised
    """

    def __init__(self):
        self.rotator = ProxyRotator()

    def load_from_list(self, proxy_strings: list[str]) -> None:
        """Load proxies from list of strings."""
        self.rotator = ProxyRotator.from_list(proxy_strings)

    def load_from_file(self, filepath: str) -> None:
        """Load proxies from file (one per line)."""
        with open(filepath) as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        self.load_from_list(lines)

    def load_from_env(self, env_var: str = "PROXY_LIST") -> None:
        """Load proxies from environment variable (comma-separated)."""
        import os
        proxy_str = os.getenv(env_var, "")
        if proxy_str:
            proxies = [p.strip() for p in proxy_str.split(",")]
            self.load_from_list(proxies)

    async def get_proxy(self) -> Proxy | None:
        """Get next available proxy."""
        return await self.rotator.get_next()

    async def get_random_proxy(self) -> Proxy | None:
        """Get random available proxy."""
        return await self.rotator.get_random()

    async def report_failure(self, proxy: Proxy) -> None:
        """Report a proxy failure."""
        await self.rotator.mark_failed(proxy)

    @property
    def has_proxies(self) -> bool:
        """Check if proxies are available."""
        return self.rotator.has_proxies
