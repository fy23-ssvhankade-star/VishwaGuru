from playwright.sync_api import sync_playwright
import time
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Listen for console logs
    page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
    page.on("pageerror", lambda exc: print(f"PAGE ERROR: {exc}"))

    print("Navigating to Home...")
    try:
        page.goto("http://localhost:5173/")
        time.sleep(10) # Wait longer
    except Exception as e:
        print(f"Navigation error: {e}")

    # Screenshot Home
    if not os.path.exists("verification"):
        os.makedirs("verification")
    page.screenshot(path="verification/home_debug.png")
    print("Home screenshot saved.")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
