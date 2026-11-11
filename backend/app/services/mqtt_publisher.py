import json
import logging
from typing import Any
from app.core.config import settings

logger = logging.getLogger("terranexus.mqtt_publisher")

def publish_device_command(device: Any, command: Any) -> bool:
    """
    Publishes a hardware command to the provisioned device topic:
    tnx/{org_id}/farm/{farm_id}/device/{device_uid}/commands
    """
    try:
        import paho.mqtt.publish as publish
        topic = f"tnx/{device.organisation_id}/farm/{device.farm_id}/device/{device.device_uid}/commands"
        payload = {
            "command_id": command.id,
            "command_type": command.command_type,
            "payload": command.payload,
            "max_duration_seconds": command.max_execution_duration_sec,
            "dispatched_at": command.dispatched_at.isoformat() if command.dispatched_at else None
        }
        auth = None
        if hasattr(settings, "mqtt_username") and settings.mqtt_username:
            auth = {
                "username": settings.mqtt_username,
                "password": getattr(settings, "mqtt_password", "")
            }
        publish.single(
            topic,
            payload=json.dumps(payload),
            hostname=settings.mqtt_host,
            port=settings.mqtt_port,
            client_id="terranexus_api_publisher",
            auth=auth,
            keepalive=10
        )
        return True
    except Exception as e:
        logger.debug(f"MQTT publish skipped or unreachable: {e}")
        return False
