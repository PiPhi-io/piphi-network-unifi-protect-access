from __future__ import annotations

from typing import Any
import httpx


class UnifiProtectError(RuntimeError):
    pass


PROTECT_RESOURCES = ("cameras", "sensors", "lights", "sirens", "relays", "speakers", "chimes", "viewers")


class UnifiProtectClient:
    def __init__(self, *, base_url: str, api_key: str, verify_tls: bool = True, transport: httpx.AsyncBaseTransport | None = None):
        if not base_url.startswith("https://"):
            raise ValueError("UniFi controller URL must use HTTPS")
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"), headers={"X-API-Key": api_key}, verify=verify_tls,
            timeout=15, transport=transport,
        )

    async def close(self):
        await self._client.aclose()

    async def discover(self) -> list[dict[str, Any]]:
        devices = []
        for resource in PROTECT_RESOURCES:
            response = await self._client.get(f"/proxy/protect/integration/v1/{resource}")
            if response.status_code == 404:
                continue
            payload = _body(response)
            items = payload if isinstance(payload, list) else payload.get("data", [])
            if isinstance(items, list):
                devices.extend(normalize_device(item, resource.removesuffix("s")) for item in items if isinstance(item, dict))
        return [item for item in devices if item["id"]]

    async def snapshot(self, camera_id: str) -> bytes:
        response = await self._client.get(f"/proxy/protect/integration/v1/cameras/{camera_id}/snapshot")
        _raise(response)
        if not response.headers.get("content-type", "").startswith("image/"):
            raise UnifiProtectError("UniFi snapshot response was not an image")
        return response.content


def normalize_device(item: dict[str, Any], kind: str) -> dict[str, Any]:
    identifier = str(item.get("id") or "")[:128]
    state = {
        "id": identifier,
        "name": str(item.get("name") or item.get("marketName") or f"UniFi {kind}")[:128],
        "device_type": kind,
        "model": item.get("type") or item.get("modelKey") or item.get("marketName"),
        "mac": item.get("mac"),
        "connected": bool(item.get("isConnected", item.get("isAdopted", False))),
        "firmware": item.get("firmwareVersion"),
    }
    mappings = {
        "isRecording": "recording", "isMotionDetected": "motion_detected",
        "isDark": "dark", "lastMotion": "last_motion_at", "isOpened": "opened",
        "isTamperingDetected": "tampering_detected", "batteryStatus": "battery_status",
        "lightOn": "light_on", "volume": "volume_percent",
    }
    for source, target in mappings.items():
        if source in item:
            state[target] = item[source]
    channels = item.get("channels")
    if isinstance(channels, list):
        state["streams"] = [
            {key: channel.get(key) for key in ("id", "name", "isRtspEnabled", "rtspAlias", "width", "height", "fps") if key in channel}
            for channel in channels if isinstance(channel, dict)
        ]
    return state


def _body(response: httpx.Response) -> Any:
    _raise(response)
    try:
        return response.json()
    except ValueError as exc:
        raise UnifiProtectError("UniFi returned invalid JSON") from exc


def _raise(response: httpx.Response) -> None:
    if response.status_code in {401, 403}:
        raise UnifiProtectError("UniFi API-key authorization failed")
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise UnifiProtectError(f"UniFi Protect failed with HTTP {response.status_code}") from exc

