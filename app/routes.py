from flask import Blueprint, jsonify, request
from services.predictor import predict

# Create a Blueprint for routes
bp = Blueprint('main', __name__)

# Define an API endpoint that accepts POST request with data
@bp.route('/predict', methods=['POST'])
def receive_data():
    json_data = request.get_json()  # Get JSON data from request
    response_data = predict(json_data=json_data)
    return response_data