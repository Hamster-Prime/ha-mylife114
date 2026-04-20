"""API client for the Mylife114 door service."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import (
    API_COMMUNITIES,
    API_COMMUNITY_DOORS,
    API_OPEN_DOOR,
    BASE_URL,
    DEFAULT_DIRECTION,
    DEFAULT_USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


class Mylife114ApiError(Exception):
    """Raised when an API call fails."""


class Mylife114Api:
    """Thin async client around the guard.mylife114.com endpoints."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        uid: str,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self._session = session
        self._uid = str(uid)
        self._user_agent = user_agent

    @property
    def uid(self) -> str:
        return self._uid

    def _headers(self) -> dict[str, str]:
        return {
            "User-Agent": self._user_agent,
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{BASE_URL}/guard_wechat/doors.html",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        url = f"{BASE_URL}{path}"
        try:
            async with self._session.get(
                url, params=params, headers=self._headers(), timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                _LOGGER.debug("GET %s params=%s -> %s", url, params, data)
                return data
        except (aiohttp.ClientError, TimeoutError) as err:
            raise Mylife114ApiError(f"Request to {url} failed: {err}") from err

    async def get_communities(self) -> list[dict[str, Any]]:
        data = await self._get(API_COMMUNITIES, {"uid": self._uid})
        return _extract_list(data)

    async def get_doors(self, community_id: int | str) -> list[dict[str, Any]]:
        data = await self._get(
            API_COMMUNITY_DOORS,
            {"uid": self._uid, "community_id": str(community_id)},
        )
        return _extract_list(data)

    async def open_door(
        self,
        controller_sn: str,
        house_id: int | str,
        direction: int = DEFAULT_DIRECTION,
    ) -> dict[str, Any]:
        data = await self._get(
            API_OPEN_DOOR,
            {
                "controller_sn": controller_sn,
                "uid": self._uid,
                "direction": str(direction),
                "house_id": str(house_id),
            },
        )
        if not _is_success(data):
            msg = _extract_msg(data) or "未知错误"
            raise Mylife114ApiError(f"开门失败: {msg}")
        _LOGGER.info(
            "Door %s opened successfully: %s",
            controller_sn,
            _extract_msg(data) or "",
        )
        return data if isinstance(data, dict) else {}


def _is_success(payload: Any) -> bool:
    # Observed success: {"ref": 0, "msg": "开门成功"}
    # Treat ref==0 OR msg containing 成功 as success; everything else as failure.
    if not isinstance(payload, dict):
        return False
    if payload.get("ref") == 0:
        return True
    msg = payload.get("msg")
    return isinstance(msg, str) and "成功" in msg


def _extract_msg(payload: Any) -> str | None:
    if isinstance(payload, dict):
        msg = payload.get("msg")
        if isinstance(msg, str) and msg:
            return msg
    return None


def _extract_list(payload: Any) -> list[dict[str, Any]]:
    # API response shape is not documented — try common wrappers in order.
    if isinstance(payload, list):
        return [p for p in payload if isinstance(p, dict)]
    if isinstance(payload, dict):
        for key in ("data", "list", "communities", "doors", "result", "items", "rows"):
            value = payload.get(key)
            if isinstance(value, list):
                return [p for p in value if isinstance(p, dict)]
            if isinstance(value, dict):
                for subkey in ("list", "data", "rows", "items"):
                    subvalue = value.get(subkey)
                    if isinstance(subvalue, list):
                        return [p for p in subvalue if isinstance(p, dict)]
    return []
