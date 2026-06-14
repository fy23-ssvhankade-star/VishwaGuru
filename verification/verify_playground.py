from playwright.sync_api import sync_playwright
import time
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    # Mock camera permissions or provide a fake stream if possible, but headless might block it.
    # However, we just want to verify UI elements, not actual camera functionality which is hard in headless.
    # We can grant permissions.
    context.grant_permissions(['camera'], origin='http://localhost:5173')

    page = context.new_page()

    # 1. Navigate to Home
    print("Navigating to Home...")
    page.goto("http://localhost:5173/")
    time.sleep(2) # Wait for load

    # 2. Find and Click 'Playground' button
    # It might be in the categories or quick actions.
    # "Playground" text is used in both.
    print("Clicking 'Playground' button...")
    # Use get_by_role('button', name='Playground')
    # Since there are two, .first should work or specific one.
    playground_btn = page.get_by_role("button", name="Playground").first
    playground_btn.click()

    # 3. Verify Navigation
    print("Verifying navigation...")
    # Expect URL to contain /playground
    page.wait_for_url("**/playground")

    # 4. Verify Title
    print("Verifying title...")
    title = page.get_by_text("Playground Safety Check")
    if title.is_visible():
        print("Title 'Playground Safety Check' is visible.")
    else:
        print("Title 'Playground Safety Check' NOT visible.")

    # 5. Take Screenshot
    if not os.path.exists("verification"):
        os.makedirs("verification")

    screenshot_path = "verification/playground_verification.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
