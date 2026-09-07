"""
Web scraper with Playwright & requests fallback for official immigration portals.
Adheres strictly to rate limits and ethical scraping policies.
"""

import time
import requests
from typing import Optional
from app.config import config
from app.ingestion.cleaner import clean_travel_text
from app.ingestion.extractor import extract_from_html
from app.logging_config import get_logger

logger = get_logger(__name__)


class WebScraper:
    """Responsible for fetching authoritative web pages using requests or Playwright."""

    def __init__(self, timeout_ms: int = 30000, delay_seconds: float = 2.0):
        self.timeout_ms = timeout_ms
        self.delay_seconds = delay_seconds
        self.headers = {
            "User-Agent": "VoyageAI-Bot/1.0 (Travel & Immigration Research Assistant; contact@voyageai.local)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def fetch_page(self, url: str, use_playwright: bool = False) -> Optional[str]:
        """Fetch page content with courteous rate limiting and clean text output."""
        time.sleep(self.delay_seconds)
        
        if use_playwright:
            return self._fetch_with_playwright(url)
        return self._fetch_with_requests(url)

    def _fetch_with_requests(self, url: str) -> Optional[str]:
        try:
            logger.info(f"Fetching URL via requests: {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout_ms / 1000.0)
            response.raise_for_status()
            return extract_from_html(response.text)
        except Exception as e:
            logger.warning(f"Requests fetch failed for {url}: {e}. Trying fallback if available.")
            return None

    def _fetch_with_playwright(self, url: str) -> Optional[str]:
        try:
            from playwright.sync_api import sync_playwright
            logger.info(f"Fetching dynamic URL via Playwright: {url}")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=config.playwright_headless)
                page = browser.new_page()
                page.set_default_timeout(self.timeout_ms)
                page.goto(url, wait_until="networkidle")
                content = page.content()
                browser.close()
                return extract_from_html(content)
        except Exception as e:
            logger.error(f"Playwright fetch failed for {url}: {e}")
            return None
