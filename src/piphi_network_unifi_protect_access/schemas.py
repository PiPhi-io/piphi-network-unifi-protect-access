from __future__ import annotations

from piphi_runtime_kit_python import RuntimeConfig


class DeviceConfig(RuntimeConfig):
    host: str
    alias: str | None = None
    api_key: str | None = None
    verify_tls: bool = True
    application_scope: str = "both"
    poll_interval_seconds: int = 60
    actions_enabled: bool = False
