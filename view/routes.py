from utils.api_response import success_response
from controller.main_controller import process_request, start_scan_job, get_scan_status, get_scan_result
from flask import Blueprint, request, jsonify, current_app

main_bp = Blueprint('main', __name__, url_prefix='/api')

@main_bp.route("/routes")
def list_routes():
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            # "endpoint": rule.endpoint,
            # "methods": list(rule.methods),
            "route": str(rule)
        })
    return {"routes": routes}

def register_blueprints(app):
    """
    Fungsi ini menerima objek Flask `app`
    dan mendaftarkan semua blueprint ke dalamnya.
    """
    app.register_blueprint(main_bp)
    return app

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API is running"}), 200

@main_bp.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        data = request.json
        result = process_request(data)
        return success_response(result, message="Data processed successfully", http_status=200)
    else:
        return jsonify({"message": "Send a POST request with data to process"}), 200

@main_bp.route('/scan', methods=['POST'])
def handle_scan():
    payload = request.json or {}
    # Delegate to controller which returns a Flask response tuple
    return start_scan_job(payload)

@main_bp.route('/scan/status/<job_id>', methods=['GET'])
def handle_scan_status(job_id):
    return get_scan_status(job_id)

@main_bp.route('/scan/result/<job_id>', methods=['GET'])
def handle_scan_result(job_id):
    return get_scan_result(job_id)