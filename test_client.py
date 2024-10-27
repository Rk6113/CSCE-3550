import requests

BASE_URL = "http://127.0.0.1:8080"

def test_auth_token():
    """Test the /auth endpoint for a valid token generation."""
    try:
        response = requests.post(f"{BASE_URL}/auth")
        if response.status_code == 200:
            print("test_auth_token: PASS")
            print("Received Token:", response.json().get("token"))
        else:
            print("test_auth_token: FAIL")
            print("Status Code:", response.status_code, "| Response:", response.json())
    except Exception as e:
        print("test_auth_token: ERROR", e)

def test_auth_expired_token():
    """Test the /auth endpoint with the 'expired' parameter for an expired token."""
    try:
        response = requests.post(f"{BASE_URL}/auth?expired=true")
        if response.status_code == 200 or response.status_code == 404:
            print("test_auth_expired_token: PASS")
            if response.status_code == 200:
                print("Received Expired Token:", response.json().get("token"))
            else:
                print("Message:", response.json().get("message"))
        else:
            print("test_auth_expired_token: FAIL")
            print("Status Code:", response.status_code, "| Response:", response.json())
    except Exception as e:
        print("test_auth_expired_token: ERROR", e)

def test_jwks():
    """Test the /.well-known/jwks.json endpoint for retrieving the JWKS keys."""
    try:
        response = requests.get(f"{BASE_URL}/.well-known/jwks.json")
        if response.status_code == 200:
            print("test_jwks: PASS")
            print("JWKS Response:", response.json())
        else:
            print("test_jwks: FAIL")
            print("Status Code:", response.status_code, "| Response:", response.json())
    except Exception as e:
        print("test_jwks: ERROR", e)

if __name__ == "__main__":
    print("Running external tests...\n")
    test_auth_token()
    test_auth_expired_token()
    test_jwks()

