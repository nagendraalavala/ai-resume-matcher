"""Job description scraper - extracts job descriptions from URLs."""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional


def scrape_job_url(url: str) -> Optional[str]:
    """Scrape a job description from a given URL."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
            tag.decompose()

        # Try platform-specific selectors first
        text = _try_platform_selectors(soup, url)

        if not text:
            text = _extract_main_content(soup)

        if not text:
            text = soup.get_text(separator="\n", strip=True)

        # Clean up the text
        text = _clean_text(text)

        if len(text) < 50:
            return None

        # Truncate very long descriptions
        if len(text) > 8000:
            text = text[:8000]

        return text

    except Exception:
        return None


def _try_platform_selectors(soup: BeautifulSoup, url: str) -> Optional[str]:
    """Try platform-specific CSS selectors for common job sites."""
    selectors_map = {
        "linkedin.com": [
            ".description__text",
            ".show-more-less-html__markup",
            ".jobs-description__content",
            '[class*="job-description"]',
            '[class*="description"]',
        ],
        "dice.com": [
            '[data-testid="jobDescriptionHtml"]',
            ".job-description",
            "#jobDescriptionHtml",
        ],
        "indeed.com": [
            "#jobDescriptionText",
            ".jobsearch-jobDescriptionText",
            '[id*="jobDescription"]',
        ],
        "glassdoor.com": [
            ".jobDescriptionContent",
            '[class*="JobDescription"]',
        ],
        "monster.com": [
            '#JobDescription',
            '.job-description',
        ],
    }

    for domain, selectors in selectors_map.items():
        if domain in url:
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(separator="\n", strip=True)

    return None


def _extract_main_content(soup: BeautifulSoup) -> Optional[str]:
    """Extract main content area from generic pages."""
    # Try common content containers
    for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
        element = soup.select_one(selector)
        if element:
            text = element.get_text(separator="\n", strip=True)
            if len(text) > 100:
                return text

    # Try the largest text block
    paragraphs = soup.find_all(["p", "li", "div"])
    if paragraphs:
        texts = []
        for p in paragraphs:
            t = p.get_text(strip=True)
            if len(t) > 20:
                texts.append(t)
        if texts:
            return "\n".join(texts)

    return None


def _clean_text(text: str) -> str:
    """Clean extracted text."""
    # Remove excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Remove common noise
    noise_patterns = [
        r"Sign in.*?account",
        r"Apply now.*?click",
        r"Share this job.*",
        r"Report this job.*",
        r"Cookie.*?policy",
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    return text.strip()
