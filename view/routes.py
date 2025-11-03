from flask import Blueprint, request, jsonify
from controller.main_controller import process_request

main_bp = Blueprint('main', __name__)

def register_routes(app):
    """Register all blueprints/routes with the Flask application"""
    app.register_blueprint(main_bp)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API is running"}), 200

@main_bp.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        data = request.json
        result = process_request(data)
        return jsonify(result), 200
    else:
        return jsonify({"message": "Send a POST request with data to process"}), 200