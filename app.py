import json
import time
import uuid
from flask import Flask, jsonify, request
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jwt

app = Flask(__name__)

# Global variables for keys storage
keys = []
expired_keys = []

# Function to generate RSA key pairs
def generate_rsa_keypair():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_key, public_key

# Function to create a key with kid and expiry
def create_key(expiry_duration=600):
    private_key, public_key = generate_rsa_keypair()
    kid = str(uuid.uuid4())
    expiry = int(time.time()) + expiry_duration  # Key expires in `expiry_duration` seconds
    return {
        "kid": kid,
        "private_key": private_key.decode('utf-8'),
        "public_key": public_key.decode('utf-8'),
        "expiry": expiry
    }

# Endpoint to get JWKS (Public keys only)
@app.route('/jwks', methods=['GET'])
def jwks():
    jwks_keys = []
    current_time = int(time.time())
    for key in keys:
        if key['expiry'] > current_time:
            jwks_keys.append({
                "kid": key["kid"],
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": jwt.utils.base64url_encode(key['public_key'].encode()).decode(),
            })
    return jsonify({"keys": jwks_keys})

# Endpoint to authenticate and return a JWT
@app.route('/auth', methods=['POST'])
def auth():
    expired = request.args.get('expired')
    current_time = int(time.time())
    key_to_use = None

    if expired == 'true':
        # Use an expired key for JWT signing
        for key in expired_keys:
            if key['expiry'] <= current_time:
                key_to_use = key
                break
    else:
        # Use a valid, unexpired key for JWT signing
        for key in keys:
            if key['expiry'] > current_time:
                key_to_use = key
                break
    
    if key_to_use:
        # Create JWT with the chosen key
        token = jwt.encode(
            {"user": "fake_user", "exp": current_time + 300},  # 5 min expiry for the token
            key_to_use['private_key'],
            algorithm="RS256",
            headers={"kid": key_to_use['kid']}
        )
        return jsonify({"token": token})
    return jsonify({"error": "No available key"}), 500

# Initialize keys (one valid, one expired for demonstration)
keys.append(create_key(expiry_duration=600))  # Valid key, expires in 10 mins
expired_keys.append(create_key(expiry_duration=-600))  # Expired key, expired 10 mins ago

# Run the server on port 8080
if __name__ == '__main__':
    app.run(port=8080)

