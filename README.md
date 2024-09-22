Thought for 5 seconds
JWKS Server Implementation

A simple JWKS (JSON Web Key Set) server implemented using Python and Flask. This server generates RSA key pairs with unique Key IDs (kid) and expiry timestamps, serves public keys in JWKS format, and provides an authentication endpoint to issue JWTs (JSON Web Tokens).

Table of Contents

Features
Prerequisites
Installation
Project Structure
Usage
Running the Server
Endpoints
Testing
Unit Tests
Test Client
Linting and Code Quality
Contributing
License
Features

RSA Key Pair Generation: Generates RSA key pairs with unique kid and expiry timestamps.
JWKS Endpoint: Serves unexpired public keys in JWKS format at /jwks.
Authentication Endpoint: Issues JWTs signed with active or expired keys at /auth.
Supports issuing tokens with expired keys using the expired query parameter.
Key Expiry Handling: Automatically moves expired keys from active to expired storage.
Thread-Safe Key Management: Uses threading locks to ensure safe concurrent access.
Unit Tests: Includes a test suite with over 80% coverage.
Test Client: Provides a test_client.py script for blackbox testing.
Prerequisites

Python 3.7 or higher (Python 3.10 recommended)
pip package manager
Virtual Environment (optional but recommended)
Installation

Clone the Repository
bash
Copy code
git clone https://github.com/rk1018/CSCE-3550.git
cd jwks-server
Create a Virtual Environment
bash
Copy code
python3 -m venv venv
source venv/bin/activate
Install Dependencies
bash
Copy code
pip install -r requirements.txt
The requirements.txt includes:

Flask
Flask-RESTful
PyJWT
cryptography
requests (for test_client)
pytest and pytest-cov (for testing)
Project Structure

bash
Copy code
jwks-server/
├── app.py              # Main application file
├── key_manager.py      # Key generation and management
├── test_client.py      # Test client for blackbox testing
├── test_app.py         # Unit tests
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Git ignore file
└── venv/               # Virtual environment directory (excluded from version control)
Usage

Running the Server
Activate the Virtual Environment
bash
Copy code
source venv/bin/activate
Run the Server
bash
Copy code
python app.py
Output:

vbnet
Copy code
 * Serving Flask app 'app'
 * Debug mode: off
 WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
The server will start listening on http://127.0.0.1:8080/.
Endpoints
1. /jwks Endpoint

Method: GET
Description: Retrieves the JWKS containing unexpired public keys.
Usage:
bash
Copy code
curl http://127.0.0.1:8080/jwks
Response:
json
Copy code
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "<key_id>",
      "n": "<base64_encoded_modulus>",
      "e": "<base64_encoded_exponent>"
    }
  ]
}
2. /auth Endpoint

Method: POST
Description: Issues a JWT signed with an active key. If the expired query parameter is provided, it issues a token signed with an expired key.
Usage:
Get a Valid Token:
bash
Copy code
curl -X POST http://127.0.0.1:8080/auth
Get an Expired Token:
bash
Copy code
curl -X POST "http://127.0.0.1:8080/auth?expired=true"
Response:
json
Copy code
{
  "token": "<your_jwt_token_here>"
}
Testing


<img width="1440" alt="Screenshot 2024-09-22 at 4 40 09 PM" src="https://github.com/user-attachments/assets/5e44cc8a-9d3e-4385-8429-ede740c49373">


View Coverage Report
bash
Copy code
coverage html
open htmlcov/index.html
Test Client
Ensure the Server Is Running
bash
Copy code
python app.py
Run the Test Client
bash
Copy code
python test_client.py
Expected Output:
bash
Copy code
Testing /auth endpoint...
Received token:
<your_valid_jwt_token_here>

Fetching JWKS...

<img width="1440" alt="Screenshot 2024-09-22 at 4 40 16 PM" src="https://github.com/user-attachments/assets/5e0fca9d-35e4-4281-bb1c-7fd4c53a3a03">

Decoding and verifying token...
Token is valid. Decoded payload:
{'sub': '1234567890', 'iat': ..., 'exp': ...}

Testing /auth endpoint with expired=true...
Received expired token:
<your_expired_jwt_token_here>

Decoding and verifying expired token...
Token has expired.
Linting and Code Quality

PEP8 Compliance: The code follows PEP8 style guidelines.
Linting: Use flake8 for linting the code.
bash
Copy code
pip install flake8
flake8 .
Formatting: Use black for code formatting.
bash
Copy code
pip install black
black .
Contributing

Contributions are welcome! Please follow these steps:

Fork the Repository
Create a Feature Branch
bash
Copy code
git checkout -b feature/YourFeature
Commit Your Changes
bash
Copy code
git commit -m "Add your message here"
Push to the Branch
bash
Copy code
git push origin feature/YourFeature
Open a Pull Request
License

This project is licensed under the MIT License. See the LICENSE file for details.

Additional Notes

Security Considerations: This project is for educational purposes and does not include authentication mechanisms. In a production environment, ensure proper authentication and security measures are in place.
Python Version: While the code may run on Python 3.12, it is recommended to use Python 3.10 or 3.11 due to potential compatibility issues with third-party libraries.
Dependencies: All dependencies are listed in requirements.txt. Ensure they are installed in your virtual environment.
Known Issues: If you encounter any issues, please create an issue on GitHub.
Contact

For any questions or concerns, please open an issue or contact the repository owner.

Thank you for using the JWKS Server!








ChatGPT can make mistakes. Check important info.
