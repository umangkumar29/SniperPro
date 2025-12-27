from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
from playwright.async_api import Page

class ScrapedProduct(BaseModel):
    title: str
    price: float
    currency: str
    url: str
    availability: bool
    image_url: Optional[str] = None

class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self, page: Page, url: str) -> Optional[ScrapedProduct]:
        """
        Scrape product details from the given URL using the provided Playwright Page.
        """
        pass

    @abstractmethod
    def verify_url(self, url: str) -> bool:
        """
        Check if this scraper can handle the given URL.
        """
        pass
