from bs4 import BeautifulSoup, Tag
import requests
from typing import List, Dict, Optional, Any, cast
import time
import random
import re

import re
from time import sleep
from random import uniform

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
import random

class NewsScraper:
    def __init__(self):
        # News sources configuration
        self.sources = {
            'economist': 'https://www.economist.com/united-states',
            'washington_post': 'https://www.washingtonpost.com/politics',
            'nyt': 'https://www.nytimes.com/section/politics',
            'fox': 'https://www.foxnews.com/politics',
            'nbc': 'https://www.nbcnews.com/politics',
            'huffpost': 'https://www.huffpost.com/news/politics'
        }

        # Setup session with retries
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 429]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        # Setup User-Agent rotation
        try:
            self.ua = UserAgent()
        except:
            self.ua = None
            self._setup_fallback_user_agents()

    def _setup_fallback_user_agents(self):
        """Setup fallback user agents if fake-useragent fails"""
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]

    def _get_headers(self):
        """Get randomized headers for each request"""
        # Get random user agent
        if self.ua:
            user_agent = self.ua.random
        else:
            user_agent = random.choice(self.user_agents)

        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""

        # Remove extra whitespace and normalize spaces
        text = re.sub(r'\s+', ' ', text.strip())

        # Fix common concatenation issues
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between lowercase and uppercase
        text = re.sub(r'(?<=[.!?])(?=[A-Za-z])', ' ', text)  # Add space after punctuation

        # Remove any non-printable characters
        text = ''.join(char for char in text if char.isprintable())

        return text.strip()

    def get_headlines(self, source: str, url: str) -> List[str]:
        """Scrape headlines from a news source."""
        try:
            # Add random delay between requests
            sleep(uniform(2, 5))

            # Get fresh headers for each request
            headers = self._get_headers()
            response = None

            # Try with increased timeout and multiple attempts
            for attempt in range(3):
                try:
                    response = self.session.get(
                        url,
                        headers=headers,
                        timeout=30,
                        allow_redirects=True
                    )
                    response.raise_for_status()

                    # Check for common anti-bot responses
                    if any(marker in response.text.lower() for marker in [
                        'access denied', 'captcha', 'robot', 'cloudflare'
                    ]):
                        print(f"Warning: {source} detected bot protection. Retrying...")
                        sleep(uniform(3, 7))
                        continue

                    # Some sites use JavaScript to load content
                    if len(response.text) < 1000:
                        print(f"Warning: {source} returned limited content. Might require JavaScript.")
                        sleep(uniform(2, 5))
                        continue

                    break  # Success

                except requests.RequestException as e:
                    if attempt < 2:  # Don't sleep on last attempt
                        print(f"Attempt {attempt + 1} failed for {source}: {str(e)}")
                        sleep(uniform(5, 10))
                    continue

            if not response:
                print(f"Failed to fetch content from {source} after multiple attempts")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            scrapers = {
                'economist': self._scrape_economist,
                'washington_post': self._scrape_wapo,
                'nyt': self._scrape_nyt,
                'fox': self._scrape_fox,
                'nbc': self._scrape_nbc,
                'huffpost': self._scrape_huffpost
            }

            headlines = []
            if source in scrapers:
                headlines = scrapers[source](soup)

            # Clean and deduplicate headlines
            cleaned_headlines = []
            seen = set()
            for h in headlines:
                cleaned = self.clean_text(h)
                if cleaned and cleaned not in seen:
                    cleaned_headlines.append(cleaned)
                    seen.add(cleaned)

            if not cleaned_headlines:
                print(f"Warning: No headlines found for {source}")

            return cleaned_headlines

        except requests.RequestException as e:
            print(f"Network error scraping {source}: {str(e)}")
            return []
        except Exception as e:
            print(f"Error scraping {source}: {str(e)}")
            return []

    def _extract_text(self, element) -> str:
        """Safely extract text from a BS4 element."""
        try:
            if element and hasattr(element, 'get_text'):
                return element.get_text(separator=' ', strip=True)
            return ""
        except Exception:
            return ""

    def _scrape_economist(self, soup: BeautifulSoup) -> List[str]:
        headlines = []

        # Try multiple selectors
        selectors = [
            ('div', 'css-1q9ni0q'),
            ('span', 'css-1qd2g6q'),
            ('h3', 'css-1pxcqts'),
            ('a', 'headline-link')
        ]

        for tag, class_ in selectors:
            try:
                articles = soup.find_all(tag, class_=class_)
                for article in articles:
                    # Try direct text
                    headline = self._extract_text(article)

                    # If no direct text, try nested elements
                    if not headline:
                        for subtag in ['a', 'h3', 'h2', 'span']:
                            subelement = article.select_one(subtag)
                            if subelement:
                                headline = self._extract_text(subelement)
                                if headline:
                                    break

                    if headline:
                        headlines.append(headline)
            except Exception as e:
                print(f"Error processing {tag}.{class_}: {str(e)}")

        return headlines

    def _scrape_with_selectors(self, soup: BeautifulSoup, selectors: List[tuple[str, str]]) -> List[str]:
        """Generic scraping method using a list of selectors."""
        headlines = []

        for tag, class_ in selectors:
            try:
                articles = soup.find_all(tag, class_=class_)
                for article in articles:
                    # Try direct text
                    headline = self._extract_text(article)

                    # If no direct text, try nested elements
                    if not headline:
                        for subtag in ['a', 'h3', 'h2', 'span']:
                            try:
                                if isinstance(article, Tag):
                                    subelement = article.select_one(subtag)
                                    if subelement:
                                        headline = self._extract_text(subelement)
                                        if headline:
                                            break
                            except Exception:
                                continue

                    if headline:
                        headlines.append(headline)
            except Exception as e:
                print(f"Error processing {tag}.{class_}: {str(e)}")

        return headlines

    def _scrape_wapo(self, soup: BeautifulSoup) -> List[str]:
        selectors = [
            ('div', 'story-headline'),
            ('h2', 'font-md'),
            ('h3', 'font--headline'),
            ('span', 'headline')
        ]
        return self._scrape_with_selectors(soup, selectors)

    def _scrape_nyt(self, soup: BeautifulSoup) -> List[str]:
        selectors = [
            ('h3', 'css-1kv6qi'),
            ('h2', 'css-1qiat4j'),
            ('h2', 'css-13yn3zj'),
            ('a', 'css-9mylee')
        ]
        return self._scrape_with_selectors(soup, selectors)

    def _scrape_fox(self, soup: BeautifulSoup) -> List[str]:
        selectors = [
            ('h3', 'title'),
            ('h2', 'title'),
            ('div', 'info'),
            ('div', 'headline')
        ]
        return self._scrape_with_selectors(soup, selectors)

    def _scrape_nbc(self, soup: BeautifulSoup) -> List[str]:
        selectors = [
            ('h2', 'styles_headline__Y52Jw'),
            ('span', 'headline___3zxS4'),
            ('h3', 'styles_headline'),
            ('a', 'styles_article_link')
        ]
        return self._scrape_with_selectors(soup, selectors)

    def _scrape_huffpost(self, soup: BeautifulSoup) -> List[str]:
        selectors = [
            ('h3', 'card__headline__text'),
            ('div', 'card__headline'),
            ('h2', 'card__title'),
            ('a', 'card__link')
        ]
        return self._scrape_with_selectors(soup, selectors)
