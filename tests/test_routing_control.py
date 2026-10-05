import httpx

from infrai_gateway import RoutingControl


def test_routing_uses_put_and_chat_capability(monkeypatch) -> None:
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.url.path == "/v1/account/routing/set"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.read() == b'{"capability":"ai.chat","exclude":["vendor-a"]}'
        return httpx.Response(200, json={"ok": True, "data": {"saved": True}})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = RoutingControl(client=client).set_chat_routing(exclude=["vendor-a"])

    assert result == {"saved": True}
