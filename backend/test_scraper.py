import asyncio
import sys
from playwright.async_api import async_playwright
from app.scraper.factory import ScraperFactory
from app.scraper.utils import get_stealth_context

async def main():
    # Test URL from user report
    url = "https://www.flipkart.com/soami-crafts-engineered-wood-dressing-table/p/itm344415af56e60?pid=DTBGMFCYZQQBFEQQ&lid=LSTDTBGMFCYZQQBFEQQS6UU3F&marketplace=FLIPKART&store=wwe%2Fki7%2Fvh2&srno=b_1_4&otracker=browse&fm=organic&iid=6cc55274-3dc4-456b-a0c1-70733a102c4f.DTBGMFCYZQQBFEQQ.SEARCH&ppt=browse&ppn=browse&ssid=eluhr4ff680000001766741550471"
    
    print(f"Testing Scraper for: {url}")
    
    try:
        scraper = ScraperFactory.get_scraper(url)
        print(f"Scraper: {scraper.__class__.__name__}")
        
        async with async_playwright() as p:
            print("Launching browser...")
            browser = await p.chromium.launch(
                headless=False, 
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = await get_stealth_context(browser)
            page = await context.new_page()
            
            print(f"Navigating to {url}...")
            await page.goto(url, timeout=60000)
            
            print("Scraping...")
            product = await scraper.scrape(page, url)
            
            print("\n----- Scraped Result -----")
            print(f"Title: {product.title}")
            print(f"Price: {product.price}")
            print(f"Availability: {product.availability}")
            print(f"Image URL: {product.image_url}")
            print("--------------------------")
            
            await browser.close()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
