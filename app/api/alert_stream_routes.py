"""
S39 - Alert Streaming Routes

SSE and WebSocket endpoints for real-time alert streaming.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.ops.dashboard_service import AlertSeverity
from app.streaming.alert_streamer import (
    AlertEvent,
    AlertEventType,
    AlertStreamer,
    get_alert_streamer,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/alerts/stream", tags=["alert-stream"])


# Request/Response models

class SubscribeRequest(BaseModel):
    """Request to subscribe to alerts."""
    severities: Optional[List[str]] = Field(
        default=None,
        description="Filter by severities (info, warning, error, critical)"
    )
    components: Optional[List[str]] = Field(
        default=None,
        description="Filter by component names"
    )


class SubscriptionResponse(BaseModel):
    """Response with subscription info."""
    subscription_id: str
    severities: List[str]
    components: List[str]
    stream_url: str


class FireAlertStreamRequest(BaseModel):
    """Request to fire alert via streaming API."""
    name: str
    severity: str
    message: str
    component: str
    metadata: Optional[Dict[str, Any]] = None


class AcknowledgeStreamRequest(BaseModel):
    """Request to acknowledge alert via streaming API."""
    acknowledged_by: str


class EscalateRequest(BaseModel):
    """Request to escalate alert."""
    new_severity: str
    reason: str


# Endpoints

@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe_to_alerts(body: SubscribeRequest):
    """
    Subscribe to real-time alert events.

    Returns a subscription ID and stream URL for SSE connection.
    """
    streamer = await get_alert_streamer()

    # Parse severities
    severities: Set[AlertSeverity] = set()
    if body.severities:
        for sev in body.severities:
            try:
                severities.add(AlertSeverity(sev))
            except ValueError:
                raise HTTPException(400, f"Invalid severity: {sev}")

    # Parse components
    components = set(body.components) if body.components else set()

    subscription_id = await streamer.subscribe(
        severities=severities if severities else None,
        components=components if components else None,
    )

    return SubscriptionResponse(
        subscription_id=subscription_id,
        severities=[s.value for s in severities] if severities else [],
        components=list(components),
        stream_url=f"/api/v1/alerts/stream/sse/{subscription_id}",
    )


@router.delete("/subscribe/{subscription_id}")
async def unsubscribe_from_alerts(subscription_id: str):
    """Unsubscribe from alert events."""
    streamer = await get_alert_streamer()
    success = await streamer.unsubscribe(subscription_id)

    if not success:
        raise HTTPException(404, f"Subscription {subscription_id} not found")

    return {"success": True, "subscription_id": subscription_id}


@router.get("/sse/{subscription_id}")
async def stream_alerts_sse(subscription_id: str):
    """
    Stream alerts via Server-Sent Events (SSE).

    Connect to this endpoint after subscribing to receive real-time alerts.
    """
    streamer = await get_alert_streamer()

    subscription = streamer.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(404, f"Subscription {subscription_id} not found")

    async def event_generator():
        # Send initial connection event
        connected_event = {
            "event_id": "connected",
            "event_type": "connected",
            "subscription_id": subscription_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        yield f"event: connected\ndata: {json.dumps(connected_event)}\n\n"

        # Stream events
        async for sse_data in streamer.stream_sse(subscription_id):
            yield sse_data

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.websocket("/ws/{subscription_id}")
async def stream_alerts_websocket(websocket: WebSocket, subscription_id: str):
    """
    Stream alerts via WebSocket.

    Alternative to SSE for bidirectional communication.
    """
    streamer = await get_alert_streamer()

    subscription = streamer.get_subscription(subscription_id)
    if not subscription:
        await websocket.close(code=4004, reason="Subscription not found")
        return

    await websocket.accept()

    # Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "subscription_id": subscription_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    try:
        # Stream events
        async for event in streamer.stream_events(subscription_id):
            await websocket.send_json({
                "type": "event",
                "data": event.to_dict(),
            })
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {subscription_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {subscription_id}: {e}")
    finally:
        await streamer.unsubscribe(subscription_id)


@router.post("/fire")
async def fire_alert_streaming(body: FireAlertStreamRequest):
    """
    Fire an alert and notify all subscribers.

    This endpoint fires the alert and broadcasts to all
    subscribed clients in real-time.
    """
    streamer = await get_alert_streamer()

    try:
        severity = AlertSeverity(body.severity)
    except ValueError:
        raise HTTPException(400, f"Invalid severity: {body.severity}")

    event = await streamer.fire_alert(
        name=body.name,
        severity=severity,
        message=body.message,
        component=body.component,
        metadata=body.metadata,
    )

    return {
        "success": True,
        "event": event.to_dict(),
    }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert_streaming(
    alert_id: str,
    body: AcknowledgeStreamRequest,
):
    """
    Acknowledge an alert and notify subscribers.

    Broadcasts acknowledgment event to all subscribers.
    """
    streamer = await get_alert_streamer()

    event = await streamer.acknowledge_alert(
        alert_id=alert_id,
        acknowledged_by=body.acknowledged_by,
    )

    if not event:
        raise HTTPException(404, f"Alert {alert_id} not found")

    return {
        "success": True,
        "event": event.to_dict(),
    }


@router.post("/{alert_id}/escalate")
async def escalate_alert_streaming(
    alert_id: str,
    body: EscalateRequest,
):
    """
    Escalate an alert to higher severity.

    Broadcasts escalation event to all subscribers.
    """
    streamer = await get_alert_streamer()

    try:
        new_severity = AlertSeverity(body.new_severity)
    except ValueError:
        raise HTTPException(400, f"Invalid severity: {body.new_severity}")

    event = await streamer.escalate_alert(
        alert_id=alert_id,
        new_severity=new_severity,
        reason=body.reason,
    )

    if not event:
        raise HTTPException(404, f"Alert {alert_id} not found")

    return {
        "success": True,
        "event": event.to_dict(),
    }


@router.delete("/{name}/{component}")
async def resolve_alert_streaming(name: str, component: str):
    """
    Resolve an alert and notify subscribers.

    Broadcasts resolution event to all subscribers.
    """
    streamer = await get_alert_streamer()

    event = await streamer.resolve_alert(
        name=name,
        component=component,
    )

    return {
        "success": event is not None,
        "name": name,
        "component": component,
        "event": event.to_dict() if event else None,
    }


@router.get("/stats")
async def get_stream_stats():
    """Get streaming statistics."""
    streamer = await get_alert_streamer()
    return streamer.get_stats()


@router.get("/active")
async def get_active_alerts_stream(
    severity: Optional[str] = Query(None),
):
    """Get currently active alerts."""
    streamer = await get_alert_streamer()

    sev = None
    if severity:
        try:
            sev = AlertSeverity(severity)
        except ValueError:
            raise HTTPException(400, f"Invalid severity: {severity}")

    alerts = streamer.get_active_alerts(sev)

    return {
        "alerts": [a.to_dict() for a in alerts],
        "total": len(alerts),
    }


@router.get("/buffer")
async def get_buffered_events(
    since: Optional[str] = Query(None, description="ISO timestamp"),
    subscription_id: Optional[str] = Query(None),
):
    """
    Get buffered events since a timestamp.

    Useful for reconnecting clients to catch up on missed events.
    """
    streamer = await get_alert_streamer()

    if since:
        try:
            # Handle URL encoding where + becomes space
            normalized = since.replace(" ", "+").replace("Z", "+00:00")
            since_dt = datetime.fromisoformat(normalized)
        except ValueError:
            raise HTTPException(400, f"Invalid timestamp: {since}")
    else:
        # Default to last 5 minutes
        since_dt = datetime.now(timezone.utc).replace(
            second=0, microsecond=0
        )

    subscription = None
    if subscription_id:
        subscription = streamer.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(404, f"Subscription {subscription_id} not found")

    events = streamer.get_buffered_events(since_dt, subscription)

    return {
        "events": [e.to_dict() for e in events],
        "total": len(events),
        "since": since_dt.isoformat(),
    }
