import threading
import time
import jwt
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class KeyManager:
    def __init__(self):
        self.active_keys = {}
        self.expired_keys = {}
        self.lock = threading.Lock()
        # Generate an initial key
        key_pair = self.generate_key_pair(expiry_minutes=5)
        self.active_keys[key_pair['kid']] = key_pair
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self.cleanup_expired_keys, daemon=True)
        cleanup_thread.start()

    def generate_key_pair(self, expiry_minutes=5):
        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        # Generate kid
        public_numbers = public_key.public_numbers()
        n = public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')
        kid = base64.urlsafe_b64encode(hashlib.sha256(n).digest()).decode('utf-8').rstrip('=')
        # Set expiry
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes)
        key_pair = {
            'private_key': private_key,
            'public_key': public_key,
            'kid': kid,
            'expiry': expiry,
        }
        logging.debug(f"Generated key pair: {key_pair}")
        return key_pair

    def get_jwks(self):
        jwks = {'keys': []}
        with self.lock:
            for key_pair in self.active_keys.values():
                public_numbers = key_pair['public_key'].public_numbers()
                n = base64.urlsafe_b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')
                e = base64.urlsafe_b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')
                jwk = {
                    'kty': 'RSA',
                    'use': 'sig',
                    'alg': 'RS256',
                    'kid': key_pair['kid'],
                    'n': n,
                    'e': e
                }
                jwks['keys'].append(jwk)
        logging.debug(f"JWKS: {jwks}")
        return jwks

    def issue_token(self, expired=False):
        with self.lock:
            if expired:
                if not self.expired_keys:
                    logging.warning("No expired keys available.")
                    return None
                key_pair = next(iter(self.expired_keys.values()))
                exp_time = key_pair['expiry']
            else:
                if not self.active_keys:
                    logging.info("No active keys available, generating a new key.")
                    key_pair = self.generate_key_pair(expiry_minutes=5)
                    self.active_keys[key_pair['kid']] = key_pair
                else:
                    key_pair = next(iter(self.active_keys.values()))
                exp_time = key_pair['expiry']

            private_key = key_pair['private_key']
            kid = key_pair['kid']

        payload = {
            'sub': '1234567890',
            'iat': datetime.datetime.utcnow(),
            'exp': exp_time,
        }
        headers = {
            'kid': kid
        }
        token = jwt.encode(
            payload,
            private_key,
            algorithm='RS256',
            headers=headers
        )
        logging.debug(f"Issued token: {token} with kid: {kid}, expired: {expired}")
        return token

    def cleanup_expired_keys(self):
        while True:
            with self.lock:
                now = datetime.datetime.utcnow()
                expired_kids = [kid for kid, key in self.active_keys.items() if key['expiry'] < now]
                for kid in expired_kids:
                    self.expired_keys[kid] = self.active_keys.pop(kid)
                    logging.debug(f"Moved key {kid} to expired keys.")
            time.sleep(60)

