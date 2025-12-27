from .base import BaseScraper
from .amazon import AmazonScraper
from .flipkart import FlipkartScraper
from .myntra import MyntraScraper

class ScraperFactory:
    @staticmethod
    def get_scraper(url: str) -> BaseScraper:
        scrapers = [
            AmazonScraper(),
            FlipkartScraper(),
            MyntraScraper()
        ]
        
        for scraper in scrapers:
            if scraper.verify_url(url):
                return scraper
        
        raise ValueError(f"No scraper found for URL: {url}")
