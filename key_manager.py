import threading
import time
import jwt
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64
import hashlib
import logging
import sqlite3

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class KeyManager:
    def __init__(self):
        # Initialize SQLite connection
        self.conn = sqlite3.connect('db/totally_not_my_privateKeys.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_database()  # Ensure database table exists

        self.active_keys = {}
        self.expired_keys = {}
        self.lock = threading.Lock()

        # Generate an initial key
        key_pair = self.generate_key_pair(expiry_minutes=5)
        self.save_key_to_db(key_pair)  # Save initial key to the database
        self.active_keys[key_pair['kid']] = key_pair

        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self.cleanup_expired_keys, daemon=True)
        cleanup_thread.start()

    def setup_database(self):
        # Create the keys table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keys (
                kid TEXT PRIMARY KEY,
                private_key BLOB NOT NULL,
                public_key BLOB NOT NULL,
                expiry REAL NOT NULL
            )
        ''')
        self.conn.commit()

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

        # Serialize private and public keys
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Create key pair dictionary
        key_pair = {
            'kid': kid,
            'private_key': private_key_pem,
            'public_key': public_key_pem,
            'expiry': expiry,
        }
        self.save_key_to_db(key_pair)  # Save to database
        return key_pair

    def save_key_to_db(self, key_pair):
        # Insert key into the SQLite database
        self.cursor.execute(
            "INSERT OR REPLACE INTO keys (kid, private_key, public_key, expiry) VALUES (?, ?, ?, ?)",
            (key_pair['kid'], key_pair['private_key'], key_pair['public_key'], key_pair['expiry'].timestamp())
        )
        self.conn.commit()

    def get_jwks(self):
        jwks = {'keys': []}
        now = datetime.datetime.utcnow().timestamp()

        # Fetch non-expired keys from the database
        self.cursor.execute("SELECT kid, public_key FROM keys WHERE expiry >= ?", (now,))
        rows = self.cursor.fetchall()

        for row in rows:
            kid, public_key_pem = row
            public_key = serialization.load_pem_public_key(public_key_pem)

            public_numbers = public_key.public_numbers()
            n = base64.urlsafe_b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')
            e = base64.urlsafe_b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')

            jwk = {
                'kty': 'RSA',
                'use': 'sig',
                'alg': 'RS256',
                'kid': kid,
                'n': n,
                'e': e,
            }
            jwks['keys'].append(jwk)

        return jwks

    def issue_token(self, expired=False):
        now = datetime.datetime.utcnow().timestamp()

        # Fetch either expired or non-expired private key from the database
        if expired:
            self.cursor.execute("SELECT private_key FROM keys WHERE expiry < ?", (now,))
        else:
            self.cursor.execute("SELECT private_key FROM keys WHERE expiry >= ?", (now,))

        row = self.cursor.fetchone()
        if not row:
            return None

        private_key_pem = row[0]
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)

        payload = {"username": "userABC", "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token

    def cleanup_expired_keys(self):
        while True:
            with self.lock:
                now = datetime.datetime.utcnow().timestamp()
                # Delete expired keys from the database
                self.cursor.execute("DELETE FROM keys WHERE expiry < ?", (now,))
                self.conn.commit()
                logging.debug("Expired keys cleaned from the database.")
            time.sleep(60)

