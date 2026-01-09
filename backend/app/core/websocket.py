import json
from typing import Dict, Set
from fastapi import WebSocket
import asyncio


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        # Maps search_id to set of connected websockets
        self._search_connections: Dict[int, Set[WebSocket]] = {}
        # All active connections
        self._active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, search_id: int | None = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self._active_connections.add(websocket)

        if search_id:
            if search_id not in self._search_connections:
                self._search_connections[search_id] = set()
            self._search_connections[search_id].add(websocket)

    def disconnect(self, websocket: WebSocket, search_id: int | None = None):
        """Remove a WebSocket connection."""
        self._active_connections.discard(websocket)

        if search_id and search_id in self._search_connections:
            self._search_connections[search_id].discard(websocket)
            if not self._search_connections[search_id]:
                del self._search_connections[search_id]

    async def send_to_search(self, search_id: int, message: dict):
        """Send a message to all connections watching a specific search."""
        if search_id not in self._search_connections:
            return

        dead_connections = set()
        for connection in self._search_connections[search_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self.disconnect(conn, search_id)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        dead_connections = set()
        for connection in self._active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self._active_connections.discard(conn)


# Global connection manager instance
manager = ConnectionManager()


async def notify_search_update(search_id: int, status: str, stores_found: int = 0, error: str | None = None):
    """Send search status update to connected clients."""
    message = {
        "type": "search_update",
        "search_id": search_id,
        "status": status,
        "stores_found": stores_found,
    }
    if error:
        message["error"] = error

    await manager.send_to_search(search_id, message)


async def notify_store_found(search_id: int, store_data: dict):
    """Notify clients when a new store is found."""
    message = {
        "type": "store_found",
        "search_id": search_id,
        "store": store_data,
    }
    await manager.send_to_search(search_id, message)
