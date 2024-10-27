from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from key_manager import KeyManager

# Initialize Flask app and API
app = Flask(__name__)
api = Api(app)

# Initialize KeyManager
key_manager = KeyManager()

# Define JWKS Resource
class JWKS(Resource):
    def get(self):
        jwks = key_manager.get_jwks()
        return jsonify(jwks)

# Define Auth Resource
class Auth(Resource):
    def post(self):
        expired = request.args.get('expired', 'false').lower() == 'true'
        token = key_manager.issue_token(expired=expired)
        if not token:
            return {'message': 'No suitable keys available'}, 404
        return jsonify({'token': token})

# Add resources to the API
api.add_resource(JWKS, '/jwks')
api.add_resource(Auth, '/auth')

# Run the app
if __name__ == '__main__':
    app.run(port=8080)

