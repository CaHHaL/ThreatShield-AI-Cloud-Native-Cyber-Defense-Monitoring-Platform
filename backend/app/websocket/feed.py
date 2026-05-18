"""
WebSocket connection manager for broadcasting real-time attack events
to all connected dashboard clients.
"""

import json
import asyncio
from typing import Set
from fastapi import WebSocket


class ConnectionManager:
    """Manages all active WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and register it."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        print(f"[WS] Client connected. Total active: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        async with self._lock:
            self.active_connections.discard(websocket)
        print(f"[WS] Client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        """
        Send a JSON message to all connected clients.
        Dead connections are pruned automatically.
        """
        if not self.active_connections:
            return

        message = json.dumps(data, default=str)
        dead: Set[WebSocket] = set()

        async with self._lock:
            connections = set(self.active_connections)

        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception as e:
                print(f"[WS] Failed to send to client: {e}")
                dead.add(ws)

        # Prune dead connections
        if dead:
            async with self._lock:
                self.active_connections -= dead


# Singleton manager used across the entire application
manager = ConnectionManager()


async def broadcast_event(event: dict):
    """
    Global helper called by log_watcher to push events to all dashboard clients.

    Event shape:
    {
        "type": "new_session" | "credential_attempt" | "suspicious_command" |
                "malware_download" | "web_login_attempt",
        "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
        "message": str,
        "ip": str,
        "country": str | None,
        "timestamp": ISO8601 string,
    }
    """
    await manager.broadcast(event)
