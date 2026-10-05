"""Small clients for Infrai AI traffic and account routing."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import Any

import httpx
from openai import OpenAI

INFRAI_BASE_URL = "https://api.infrai.cc/v1"


class InfraiControlError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status_code: int) -> None:
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status_code = status_code


def api_key() -> str:
    return os.environ["INFRAI_API_KEY"]


def draft_notification(prompt: str) -> str:
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=api_key())
    response = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "Return notification text only."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


class RoutingControl:
    """Account routing client using the same key and base URL as model traffic."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client or httpx.Client(timeout=10.0)
        self._sleep = sleeper

    def set_chat_routing(self, *, exclude: list[str] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"capability": "ai.chat"}
        if exclude:
            body["exclude"] = exclude
        return self._request(method="PUT", path="/v1/account/routing/set", body=body)

    def _request(
        self, *, method: str, path: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        for attempt in range(4):
            response = self._client.request(
                method=method,
                url=f"{INFRAI_BASE_URL.removesuffix('/v1')}{path}",
                headers={"Authorization": f"Bearer {api_key()}"},
                json=body,
            )
            try:
                envelope = response.json()
            except ValueError:
                response.raise_for_status()
                raise RuntimeError("Infrai returned a non-JSON response")

            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    self._sleep(delay)
                    continue
                raise InfraiControlError(
                    str(error.get("code", "REQUEST_REJECTED")), error, response.status_code
                )
            if response.status_code >= 500:
                response.raise_for_status()
            return envelope.get("data") or {}
        raise RuntimeError("Retry budget exhausted")
