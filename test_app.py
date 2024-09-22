import json
import unittest
from app import app, keys, expired_keys

class JWKSAuthTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.client = app.test_client()
        self.client.testing = True

    def test_jwks_endpoint(self):
        # Test the /jwks endpoint for public keys
        response = self.client.get('/jwks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        # Check if keys are returned
        self.assertIn("keys", data)
        # Check that each key has the necessary fields (kid, kty, alg, use, n)
        if data["keys"]:
            for key in data["keys"]:
                self.assertIn("kid", key)
                self.assertIn("kty", key)
                self.assertIn("alg", key)
                self.assertIn("use", key)
                self.assertIn("n", key)

    def test_auth_endpoint(self):
        # Test the /auth endpoint to get a JWT
        response = self.client.post('/auth')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        # Check if the JWT token is returned
        self.assertIn("token", data)

    def test_expired_auth(self):
        # Test the /auth endpoint with the expired query parameter
        response = self.client.post('/auth?expired=true')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))

        # Check if the JWT token is returned when expired=true
        self.assertIn("token", data)

    def test_no_keys_available(self):
        # Remove all keys to simulate no available key scenario
        keys.clear()
        expired_keys.clear()

        response = self.client.post('/auth')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data.decode('utf-8'))

        # Ensure the error message is returned when no keys are available
        self.assertIn("error", data)
        self.assertEqual(data["error"], "No available key")

if __name__ == '__main__':
    unittest.main()

