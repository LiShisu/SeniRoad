from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services import LocationService
from typing import Dict

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

@router.websocket("/location/{user_id}")
async def websocket_location(websocket: WebSocket, user_id: str):
    """WebSocket实时位置推送"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await LocationService.update_location(user_id, data)
            await LocationService.push_to_family(user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
