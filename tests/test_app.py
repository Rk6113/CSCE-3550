import unittest
import requests

BASE_URL = "http://127.0.0.1:8080"

class JWKSAppTest(unittest.TestCase):
    def test_auth_token(self):
        response = requests.post(f"{BASE_URL}/auth")
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_auth_expired_token(self):
        response = requests.post(f"{BASE_URL}/auth?expired=true")
        # Expect a 404 if no expired keys available, else a token
        self.assertIn(response.status_code, [200, 404])

    def test_jwks(self):
        response = requests.get(f"{BASE_URL}/jwks")
        self.assertEqual(response.status_code, 200)
        self.assertIn('keys', response.json())

if __name__ == '__main__':
    unittest.main()

