import time
from playwright.sync_api import sync_playwright, expect

def run_dynamic(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Mutable state for mock
    issue_response = {
        "status": "processing" # Initial state representation, or just missing action_plan
    }

    # Mock get specific issue
    def handle_issue_get(route):
        if issue_response["status"] == "done":
             route.fulfill(
                status=200,
                content_type="application/json",
                body='{"id": 123, "action_plan": {"whatsapp": "Hello", "email_subject": "Sub", "email_body": "Body", "x_post": "Tweet"}}'
            )
        else:
             route.fulfill(
                status=200,
                content_type="application/json",
                body='{"id": 123, "action_plan": null}'
            )

    # Mock create response
    page.route("**/api/issues", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"id": 123, "message": "success", "action_plan": null}'
    ))

    # Mock specific issue endpoint
    page.route("**/api/issues/123", handle_issue_get)

    # Mock detection status/others
    page.route("**/api/ml-status", lambda route: route.fulfill(status=200, body='{"status":"ok"}'))
    page.route("**/api/issues/recent", lambda route: route.fulfill(status=200, body='[]'))

    print("Navigating...")
    # Navigate directly to report or action if possible, but let's follow flow
    page.goto("http://localhost:5173/report")

    print("Filling form...")
    page.fill('textarea', 'Test issue')
    page.click('button[type="submit"]')

    print("Waiting for Generating state...")
    expect(page.get_by_text("Generating Action Plan...")).to_be_visible(timeout=5000)
    page.screenshot(path="verification/generating_state.png")
    print("Generating state captured")

    # Change mock response to simulate completed AI task
    print("Simulating AI completion...")
    issue_response["status"] = "done"

    print("Waiting for polling update...")
    expect(page.get_by_text("Action Plan Generated!")).to_be_visible(timeout=8000)
    page.screenshot(path="verification/done_state.png")
    print("Done state captured")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run_dynamic(playwright)
