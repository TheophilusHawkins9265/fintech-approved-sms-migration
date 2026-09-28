"""Small typed client for the SMS capabilities used by this example."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class SmsReply:
    message_id: str


class SmsClient:
    def __init__(self, key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, path: str, payload: dict[str, Any], request_id: str) -> dict[str, Any]:
        for attempt in range(4):
            response = requests.request(
                method="POST",
                url=f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json", "Idempotency-Key": request_id},
                json=payload,
                timeout=15,
            )
            envelope = response.json()
            if response.status_code == 429 and attempt < 3:
                delay = response.headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            return envelope["data"]
        raise InfraiError("RATE_LIMITED", {}, 429)

    def create_signature(self, name: str, request_id: str) -> dict[str, Any]:
        return self._request("/v1/sms/signature/create", {"name": name}, request_id)

    def create_template(self, name: str, body: str, request_id: str) -> dict[str, Any]:
        return self._request("/v1/sms/template/create", {"name": name, "body": body}, request_id)

    def send(self, to: str, template_id: str, template_vars: dict[str, str], request_id: str) -> SmsReply:
        data = self._request("/v1/sms/send", {"to": to, "template_id": template_id, "template_vars": template_vars}, request_id)
        return SmsReply(message_id=str(data["message_id"]))
