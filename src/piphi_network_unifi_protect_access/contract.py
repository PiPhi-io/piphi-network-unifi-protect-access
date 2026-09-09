from __future__ import annotations

from typing import Any

ENDPOINTS = {
    "health": "/health",
    "diagnostics": "/diagnostics",
    "discover": "/discover",
    "entities": "/entities",
    "state": "/state",
    "config": "/config",
    "config_sync": "/config/sync",
    "deconfigure": "/deconfigure",
    "ui_config": "/ui-config",
    "events": "/events",
    "command": "/command",
}

REQUIRED_ENDPOINTS = ["health", "entities", "command", "config", "ui_config"]

CAPABILITIES: dict[str, dict[str, Any]] = {
    "connected": {"kind": "sensor", "unit": "bool"},
    "refresh": {"kind": "action"},
}

COMMANDS: dict[str, dict[str, Any]] = {
    "refresh": {
        "description": "Refresh the integration state.",
        "timeout_ms": 5000,
    },
}

CONFIG_SCHEMA: dict[str, Any] = {
    "schema": {
        "title": "PiPhi Network UniFi Protect & Access Setup",
        "type": "object",
        "required": ["host"],
        "properties": {
    "host": {
        "type": "string",
        "title": "Console URL"
    },
    "alias": {
        "type": "string",
        "title": "Site Name"
    },
    "api_key": {
        "type": "string",
        "title": "API Key",
        "format": "password",
        "writeOnly": True
    },
    "verify_tls": {
        "type": "boolean",
        "title": "Verify TLS",
        "default": True
    },
    "application_scope": {
        "type": "string",
        "title": "Applications",
        "enum": [
            "protect",
            "access",
            "both"
        ],
        "default": "both"
    },
    "poll_interval_seconds": {
        "type": "integer",
        "title": "Reconciliation Interval Seconds",
        "minimum": 15,
        "default": 60
    },
    "actions_enabled": {
        "type": "boolean",
        "title": "Enable Mutating Actions",
        "default": False
    }
},
    },
    "uiSchema": {
        "host": {"placeholder": "https://192.168.1.1"},
        "alias": {"placeholder": "UniFi Protect & Access Site"},
    },
}

FALLBACK_ENTITY: dict[str, Any] = {
    "id": "unifi-protect-access-site",
    "name": "UniFi Protect & Access Site",
    "device_id": "unifi-protect-access-site",
    "entity_type": "security_site",
    "capabilities": ["connected", "refresh"],
    "available_commands": [
        {"id": "refresh", "label": "Refresh", "kind": "action"},
    ],
    "dashboard": {
        "allowed_widgets": [
    "camera",
    "camera-events-card",
    "access-control-card",
    "device-health-card"
],
        "default_widget": "camera",
    },
}
