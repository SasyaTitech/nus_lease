from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests

BASE_URL = "https://www.onemap.gov.sg"


class OneMapError(RuntimeError):
    pass


@dataclass
class OneMapClient:
    access_token: str

    def _request_json(self, method: str, path: str, **kwargs) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": "curl/8.5.0",
            "Authorization": f"Bearer {self.access_token}",
            **kwargs.pop("headers", {}),
        }
        response = requests.request(method, f"{BASE_URL}{path}", headers=headers, timeout=60, **kwargs)
        response.raise_for_status()
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise OneMapError(f"OneMap returned non-JSON for {path}: {response.text[:240]}") from exc

    def reverse_geocode(self, latitude: float, longitude: float, buffer: int = 40, address_type: str = "All") -> list[dict]:
        payload = self._request_json(
            "GET",
            "/api/public/revgeocode",
            params={
                "location": f"{latitude},{longitude}",
                "buffer": buffer,
                "addressType": address_type,
            },
        )
        return payload.get("GeocodeInfo", [])


def authenticate(email: str, password: str) -> str:
    headers = {
        "Accept": "application/json",
        "User-Agent": "curl/8.5.0",
        "Content-Type": "application/json",
    }
    payload = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/api/auth/post/getToken", headers=headers, json=payload, timeout=60)
    if response.status_code >= 400:
        response = requests.post(f"{BASE_URL}/api/auth/post/getToken", headers={"Accept": "application/json", "User-Agent": "curl/8.5.0"}, data=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    token = data.get("access_token")
    if not token:
        raise OneMapError(f"OneMap token request failed: {data}")
    return token


def load_token_from_env() -> str:
    direct = os.environ.get("ONEMAP_API_TOKEN", "").strip()
    if direct:
        return direct

    email = os.environ.get("ONEMAP_EMAIL", "").strip()
    password = os.environ.get("ONEMAP_PASSWORD", "").strip()
    if email and password:
        return authenticate(email, password)

    raise OneMapError(
        "Missing OneMap credentials. Set ONEMAP_API_TOKEN or ONEMAP_EMAIL and ONEMAP_PASSWORD."
    )
