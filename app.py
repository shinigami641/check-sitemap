from view.socket.api import init_socket
from utils.api_response import APP_ERROR_CODES
from utils.api_response import error_response
from flask import Flask
from view.routes import register_blueprints
from config.socket import socketio

app = Flask(__name__)

# Register all routes
register_blueprints(app)
init_socket(app)

if __name__ == '__main__':
    @app.errorhandler(404)
    def not_found(e):
        return error_response("Not Found", http_status=404, app_code=APP_ERROR_CODES["NOT_FOUND"])
    
    @app.errorhandler(500)
    def server_error(e):
        # jangan leak exception detail di production
        return error_response("Internal server error", http_status=500, app_code=APP_ERROR_CODES["SERVER_ERROR"])
    
    # Jalankan melalui SocketIO agar namespace '/notifications' aktif
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)