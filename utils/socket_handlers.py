from flask_socketio import Namespace, emit, join_room, leave_room

class NotificationsNamespace(Namespace):
    """
    General notifications namespace tanpa client_id.
    Mendukung:
    - join/leave room
    - menerima pesan dari client
    - broadcast ke semua atau ke room tertentu
    """

    def on_connect(self):
        print("[WS] Client connected")

    def on_disconnect(self):
        print("[WS] Client disconnected")

    def on_client_message(self, data):
        """
        Event dari client: { 'message': '...' }
        """
        print("[WS] Received from client:", data)
        emit('server_response', {'ok': True})
        # Debug: kirimkan contoh event 'scan_result' agar klien bisa memverifikasi listener-nya
        try:
            emit('scan_result', {
                'job_id': data.get('job_id') or 'debug',
                'message': data.get('message') or 'Debug: scan_result from server'
            })
        except Exception as e:
            print('[WS] Failed to emit debug scan_result:', e)

    def on_join_room(self, data):
        """
        Event dari client untuk join room tertentu: { 'room': 'room_name' }
        """
        room = data.get("room")
        if room:
            join_room(room)
            print(f"[WS] Client joined room: {room}")
            emit("joined", {"room": room})

    def on_leave_room(self, data):
        """
        Event dari client untuk leave room tertentu: { 'room': 'room_name' }
        """
        room = data.get("room")
        if room:
            leave_room(room)
            print(f"[WS] Client left room: {room}")
            emit("left", {"room": room})


def send_ws_event(event_name, data=None, namespace='/notifications', room=None):
    from config.socket import socketio  # import socketio instance

    if data is None:
        data = {}

    ns = namespace if str(namespace).startswith('/') else f'/{namespace}'

    try:
        socketio.emit(event_name, data, namespace=ns)
        print(f"[WS] Emit event='{event_name}' ns='{ns}' data_keys={list(data.keys())}")
    except Exception as e:
        print(f"[WS] Emit failed for event='{event_name}' ns='{ns}': {e}")
