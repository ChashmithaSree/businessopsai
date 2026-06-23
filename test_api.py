import requests
import json

def test_run():
    print("Creating session...")
    try:
        res = requests.post("http://127.0.0.1:8000/apps/app/users/test-user/sessions", json={})
        res.raise_for_status()
        session_id = res.json()["id"]
        print(f"Session created: {session_id}")
    except Exception as e:
        print(f"Session creation failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(e.response.text)
        return

    print("\nTesting /run endpoint...")
    payload = {
        "app_name": "app",
        "user_id": "test-user",
        "session_id": session_id,
        "new_message": {"role": "user", "parts": [{"text": "Hello"}]}
    }
    try:
        res = requests.post("http://127.0.0.1:8000/run", json=payload)
        print(f"Status Code: {res.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(res.json(), indent=2))
        except ValueError:
            print("Response text (not JSON):")
            print(res.text)
    except Exception as e:
        print(f"/run request failed: {e}")

if __name__ == "__main__":
    test_run()
