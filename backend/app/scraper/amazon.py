from playwright.async_api import Page
from .base import BaseScraper, ScrapedProduct
import logging

class AmazonScraper(BaseScraper):
    def verify_url(self, url: str) -> bool:
        return "amazon" in url

    async def scrape(self, page: Page, url: str) -> ScrapedProduct:
        logging.info(f"Scraping Amazon URL: {url}")
        # Add random delay/mouse movement simulation here in future if needed
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        try:
            # Try multiple selectors for title
            title = "Unknown Product"
            try:
                title_el = await page.wait_for_selector("#productTitle", timeout=15000)
                if title_el:
                    title = await title_el.inner_text()
                    title = title.strip()
            except:
                logging.warning("Main title selector failed, trying backup")
                # Backup selector
                title_el = await page.query_selector("h1")
                if title_el:
                     title = await title_el.inner_text()

            # Price handling is tricky on Amazon (Deal price, regular price, etc.)
            # We try a few common selectors
            price_text = ""
            price_selectors = [
                ".a-price-whole", 
                "#priceblock_ourprice", 
                "#priceblock_dealprice", 
                ".a-offscreen",
                "#corePriceDisplay_desktop_feature_div .a-price-whole"
            ]
            
            for selector in price_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        text = await el.inner_text()
                        # prioritizing visible prices
                        if text and any(char.isdigit() for char in text):
                            price_text = text
                            break
                except:
                    continue
            
            # Clean price text (remove currency symbols, commas)
            cleaned_price = "".join([c for c in price_text if c.isdigit() or c == '.'])
            price = float(cleaned_price) if cleaned_price else 0.0
            
            # Availability
            availability_el = await page.query_selector("#availability")
            availability_text = await availability_el.inner_text() if availability_el else ""
            in_stock = "out of stock" not in availability_text.lower() and "currently unavailable" not in availability_text.lower()

            return ScrapedProduct(
                title=title,
                price=price,
                currency="INR", # Defaulting to INR for now, could be extracted
                url=url,
                availability=in_stock
            )

        except Exception as e:
            logging.error(f"Error scraping Amazon: {e}")
            raise e
