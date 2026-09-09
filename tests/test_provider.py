import httpx
import pytest

from piphi_network_unifi_protect_access.provider import UnifiProtectClient, UnifiProtectError


@pytest.mark.anyio
async def test_discovers_supported_resources_and_negotiates_fields():
    async def handler(request):
        if request.url.path.endswith("/cameras"):
            return httpx.Response(200, json=[{"id":"cam1","name":"Porch","isConnected":True,"isRecording":True,"channels":[{"id":0,"width":1920,"height":1080,"fps":30}]}])
        if request.url.path.endswith("/sensors"):
            return httpx.Response(200, json={"data":[{"id":"sensor1","name":"Door","isOpened":False}]})
        return httpx.Response(404)
    client = UnifiProtectClient(base_url="https://console.local", api_key="secret", transport=httpx.MockTransport(handler))
    devices = await client.discover()
    assert [device["id"] for device in devices] == ["cam1", "sensor1"]
    assert devices[0]["recording"] is True
    assert devices[0]["streams"][0]["width"] == 1920
    assert devices[1]["opened"] is False
    await client.close()


@pytest.mark.anyio
async def test_snapshot_checks_media_type_and_auth_errors_redact_key():
    async def bad_media(request): return httpx.Response(200, headers={"content-type":"text/html"}, content=b"no")
    client = UnifiProtectClient(base_url="https://console.local", api_key="secret", transport=httpx.MockTransport(bad_media))
    with pytest.raises(UnifiProtectError, match="not an image"): await client.snapshot("cam1")
    await client.close()
    async def unauthorized(request): return httpx.Response(401, json={"api_key":"secret"})
    client = UnifiProtectClient(base_url="https://console.local", api_key="secret", transport=httpx.MockTransport(unauthorized))
    with pytest.raises(UnifiProtectError) as caught: await client.discover()
    assert "secret" not in str(caught.value)
    await client.close()


def test_requires_https_controller():
    with pytest.raises(ValueError, match="HTTPS"): UnifiProtectClient(base_url="http://console.local", api_key="x")
