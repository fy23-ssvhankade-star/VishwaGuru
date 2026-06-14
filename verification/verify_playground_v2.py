from playwright.sync_api import sync_playwright
import time
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # 1. Navigate to Home
    print("Navigating to Home (/home)...")
    try:
        page.goto("http://localhost:5173/home")
        time.sleep(5) # Wait for load
    except Exception as e:
        print(f"Navigation error: {e}")
        return

    # Screenshot Home
    if not os.path.exists("verification"):
        os.makedirs("verification")
    page.screenshot(path="verification/home_v2_screenshot.png")
    print("Home screenshot saved.")

    # 2. Find and Click 'Playground' button
    print("Clicking 'Playground' button...")
    # Try get_by_text first
    playground_btn = page.get_by_text("Playground").first
    if playground_btn.is_visible():
        playground_btn.click()
        print("Clicked 'Playground' button.")
    else:
        print("Playground button NOT visible.")
        return

    # 3. Verify Navigation
    try:
        page.wait_for_url("**/playground", timeout=10000)
        print("Navigated to /playground")
    except Exception as e:
        print(f"Navigation failed: {e}")
        return

    # 4. Verify Title
    print("Verifying title...")
    try:
        # Wait for the title to appear
        title = page.wait_for_selector("text=Playground Safety Check", timeout=10000)
        if title:
            print("Title 'Playground Safety Check' is visible.")
    except Exception as e:
        print(f"Title not found: {e}")

    # 5. Take Screenshot
    screenshot_path = "verification/playground_verification.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
