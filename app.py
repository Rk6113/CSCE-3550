from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from key_manager import KeyManager
import jwt
import datetime

app = Flask(__name__)
api = Api(app)

# Initialize the KeyManager
key_manager = KeyManager()

class JWKS(Resource):
    def get(self):
        jwks = key_manager.get_jwks()
        return jsonify(jwks)

class Auth(Resource):
    def post(self):
        expired = request.args.get('expired')
        if expired:
            token = key_manager.issue_token(expired=True)
        else:
            token = key_manager.issue_token()
        if not token:
            return {'message': 'No expired keys available'}, 500
        return jsonify({'token': token})

api.add_resource(JWKS, '/jwks')
api.add_resource(Auth, '/auth')

if __name__ == '__main__':
    app.run(port=8080)
