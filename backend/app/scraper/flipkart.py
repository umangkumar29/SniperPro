from playwright.async_api import Page
from .base import BaseScraper, ScrapedProduct
import logging

class FlipkartScraper(BaseScraper):
    def verify_url(self, url: str) -> bool:
        return "flipkart" in url

    async def scrape(self, page: Page, url: str) -> ScrapedProduct:
        logging.info(f"Scraping Flipkart URL: {url}")
        
        # Note: page.goto() is called in test_scraper.py before this method
        # We just need to extract data from the already loaded page
        
        try:
            # Wait a bit for any dynamic content
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=30000)
            except:
                pass # Proceed even if timeout, DOM might be ready enough
            
            # Title - try multiple selectors
            title = "Unknown Product"
            title_selectors = [".B_NuCI", ".VU-ZEz", "h1 span", "h1"]
            for selector in title_selectors:
                try:
                    title_el = await page.query_selector(selector)
                    if title_el:
                        text = await title_el.inner_text()
                        if text and len(text.strip()) > 3:
                            title = text.strip()
                            break
                except Exception:
                    continue
            
            # Price - try multiple selectors (Flipkart changes these frequently)
            price = 0.0
            price_selectors = [
                ".hZ3P6w",      # Current main price class
                ".Nx9bqj",      # Alternative price class
                "._30jeq3",     # Legacy price class
                "._16Jk6d",     # Legacy deal price
                "[class*='price']"  # Fallback
            ]
            for selector in price_selectors:
                try:
                    price_el = await page.query_selector(selector)
                    if price_el:
                        price_text = await price_el.inner_text()
                        # Clean price text (remove ₹, commas, etc.)
                        cleaned = "".join([c for c in price_text if c.isdigit()])
                        if cleaned:
                            price = float(cleaned)
                            break
                except Exception:
                    continue
            
            # Availability check
            in_stock = True
            sold_out_selectors = ["._16FRp0", "[class*='sold-out']", "[class*='unavailable']"]
            for selector in sold_out_selectors:
                try:
                    sold_out_el = await page.query_selector(selector)
                    if sold_out_el:
                        text = await sold_out_el.inner_text()
                        if "sold out" in text.lower() or "unavailable" in text.lower():
                            in_stock = False
                            break
                except Exception:
                    continue

            # Image extraction
            image_url = None
            try:
                # Try OG Image first (most reliable for clean full res)
                meta_img = await page.query_selector("meta[property='og:image']")
                if meta_img:
                    image_url = await meta_img.get_attribute("content")
                
                # Fallback to visual element
                if not image_url:
                    img_selectors = ["._396cs4", ".DByuf4", "img[alt*='product']"]
                    for sel in img_selectors:
                        el = await page.query_selector(sel)
                        if el:
                            src = await el.get_attribute("src")
                            if src and "http" in src:
                                image_url = src
                                break
            except Exception:
                pass

            logging.info(f"Extracted - Title: {title[:50]}..., Price: {price}, Image: {image_url}")
            
            return ScrapedProduct(
                title=title,
                price=price,
                currency="INR",
                url=url,
                availability=in_stock,
                image_url=image_url
            )

        except Exception as e:
            logging.error(f"Error scraping Flipkart: {e}")
            raise e
