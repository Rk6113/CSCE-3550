import unittest
from flask_testing import TestCase
from app import app  # Import the Flask app instance
import requests

# Set up the base URL for direct HTTP calls if needed
BASE_URL = "http://127.0.0.1:8080"

class JWKSAppTest(TestCase):
    def create_app(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        return app

    def test_auth_token(self):
        """Test generating a token with a valid (unexpired) key."""
        # Using Flask's test client to access the endpoint
        response = self.client.post("/auth")
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn("token", data)
        print("Received token:", data["token"])

    def test_auth_expired_token(self):
        """Test generating a token with an expired key."""
        response = self.client.post("/auth?expired=true")
        # Check if a token is generated or an error message if no expired key exists.
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = response.json
            self.assertIn("token", data)
            print("Received expired token:", data["token"])
        else:
            error_data = response.json
            self.assertIn("error", error_data)
            print("Error message:", error_data["error"])

    def test_jwks(self):
        """Test retrieving the JWKS keys."""
        response = self.client.get("/.well-known/jwks.json")
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn("keys", data)
        # Check if the keys list has items and the expected structure
        keys = data["keys"]
        self.assertTrue(isinstance(keys, list))
        if keys:
            key = keys[0]
            self.assertIn("kty", key)
            self.assertIn("use", key)
            self.assertIn("kid", key)
            self.assertIn("n", key)
            self.assertIn("e", key)
        print("JWKS response:", data)

    
if __name__ == '__main__':
    unittest.main()

