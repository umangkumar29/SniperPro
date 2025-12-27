from playwright.async_api import Page
from .base import BaseScraper, ScrapedProduct
import logging

class MyntraScraper(BaseScraper):
    def verify_url(self, url: str) -> bool:
        return "myntra" in url

    async def scrape(self, page: Page, url: str) -> ScrapedProduct:
        logging.info(f"Scraping Myntra URL: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        
        try:
            # Myntra is heavily script based, meta tags are often reliable
            title_el = await page.wait_for_selector(".pdp-title", timeout=5000)
            name_el = await page.query_selector(".pdp-name")
            
            brand = await title_el.inner_text() if title_el else ""
            name = await name_el.inner_text() if name_el else ""
            full_title = f"{brand} {name}".strip()
            
            # Price
            price_el = await page.query_selector(".pdp-price strong")
            price_text = await price_el.inner_text() if price_el else "0"
            
            cleaned_price = "".join([c for c in price_text if c.isdigit()])
            price = float(cleaned_price) if cleaned_price else 0.0
            
            # Availability
            # Myntra shows 'Out of stock' in a specific container sometimes
            # or checks if sizes are available. 
            # Simplified check:
            in_stock = True # Default true implementation for now
            
            return ScrapedProduct(
                title=full_title,
                price=price,
                currency="INR",
                url=url,
                availability=in_stock
            )

        except Exception as e:
            logging.error(f"Error scraping Myntra: {e}")
            raise e
