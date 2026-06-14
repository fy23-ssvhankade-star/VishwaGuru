import requests
import json

BASE_URL = "http://localhost:8000"

def test_text_category():
    print("\nTesting Text Category Detection...")
    text = "There is a large pothole on Main Street causing traffic."
    try:
        response = requests.post(f"{BASE_URL}/api/detect-category-text", json={"text": text})
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data}")
            if data.get('category') == 'road':
                print("PASS: Category correctly identified as road")
            else:
                print(f"FAIL: Category identified as: {data.get('category')}")
        else:
            print(f"FAIL: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_get_issue():
    print("\nTesting Get Issue...")
    try:
        response = requests.get(f"{BASE_URL}/api/issues/recent")
        if response.status_code == 200:
            issues = response.json()
            if issues:
                issue_id = issues[0]['id']
                print(f"Found issue ID {issue_id} in recent list, fetching details...")
                detail_resp = requests.get(f"{BASE_URL}/api/issues/{issue_id}")
                if detail_resp.status_code == 200:
                    detail = detail_resp.json()
                    print(f"Success: Got issue {issue_id}")
                    # Check fields
                    if 'reference_id' in detail:
                        print(f"PASS: Reference ID found: {detail['reference_id']}")
                    else:
                        print("FAIL: Reference ID missing")
                else:
                    print(f"FAIL: Failed to get issue {issue_id}: {detail_resp.status_code} - {detail_resp.text}")
            else:
                print("WARN: No recent issues to test with.")
        else:
            print(f"FAIL: Failed to get recent issues: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_text_category()
    test_get_issue()
