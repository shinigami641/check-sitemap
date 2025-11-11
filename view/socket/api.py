from utils.socket_handlers import NotificationsNamespace
from config.socket import socketio

def init_socket(app):
    socketio.init_app(app)
    
    socketio.on_namespace(NotificationsNamespace('/notifications'))
    
