import random
import asyncio
from playwright_stealth import Stealth

async def get_stealth_context(browser):
    """Create a browser context with stealth mode enabled."""
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-IN',
        timezone_id='Asia/Kolkata',
    )
    return context

async def apply_stealth(page):
    """Apply stealth scripts to a page using playwright-stealth Stealth class."""
    stealth = Stealth()
    await stealth.apply_stealth_async(page)

async def random_delay(min_ms=500, max_ms=2000):
    """Add random human-like delay."""
    delay = random.randint(min_ms, max_ms) / 1000  # Convert to seconds
    await asyncio.sleep(delay)

async def human_like_mouse_move(page):
    """Simulate human-like mouse movement."""
    # Get viewport size
    viewport = page.viewport_size
    if not viewport:
        return
    
    # Move mouse to random positions (simulating browsing)
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, viewport['width'] - 100)
        y = random.randint(100, viewport['height'] - 100)
        await page.mouse.move(x, y)
        await random_delay(100, 300)

async def human_like_scroll(page):
    """Simulate human-like scrolling behavior."""
    # Scroll down slowly
    for _ in range(random.randint(2, 4)):
        scroll_amount = random.randint(100, 400)
        await page.mouse.wheel(0, scroll_amount)
        await random_delay(200, 500)
    
    # Scroll back up a bit (humans do this)
    await page.mouse.wheel(0, -random.randint(50, 150))
    await random_delay(100, 300)

async def simulate_human_behavior(page):
    """Full human behavior simulation before scraping."""
    # Initial delay (page loading time humans would wait)
    await random_delay(1000, 2000)
    
    # Move mouse around
    await human_like_mouse_move(page)
    
    # Scroll the page
    await human_like_scroll(page)
    
    # Final small delay
    await random_delay(300, 700)
