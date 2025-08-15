# app/services/playwright_client.py

import os
from playwright.async_api import async_playwright

TRADINGVIEW_USERNAME = os.getenv("TV_USERNAME")
TRADINGVIEW_PASSWORD = os.getenv("TV_PASSWORD")

async def fetch_data_with_playwright(symbol: str, interval: str):
    print(f"[Playwright] Scraping data for {symbol} at interval {interval}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Login (adjust selectors as needed)
        await page.goto("https://www.tradingview.com/")
        await page.click('text=Sign In')
        await page.click('text=Email')
        await page.fill('input[name="username"]', TRADINGVIEW_USERNAME)
        await page.fill('input[name="password"]', TRADINGVIEW_PASSWORD)
        await page.click('button[type="submit"]')

        # Wait for login to complete
        await page.wait_for_timeout(3000)

        # Go to chart
        chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}"
        await page.goto(chart_url)

        # Wait for price to load
        await page.wait_for_selector(".tv-symbol-price-quote__value")  # Adjust selector if needed
        price = await page.inner_text(".tv-symbol-price-quote__value")

        await browser.close()

        return {
            "price": float(price.replace(',', '')),
            "symbol": symbol,
            "interval": interval
        }
