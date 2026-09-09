from __future__ import annotations

import json

from piphi_network_unifi_protect_access.schemas import DeviceConfig
from piphi_network_unifi_protect_access.state import _split_config, make_entry


def test_api_key_is_kept_out_of_persisted_and_serialized_config() -> None:
    config = DeviceConfig(id="unifi-test", host="unifi.local", api_key="top-secret")

    public, secrets = _split_config(config)
    entry = make_entry(config)

    assert "api_key" not in public
    assert secrets == {"api_key": "top-secret"}
    assert "top-secret" not in json.dumps(entry)
