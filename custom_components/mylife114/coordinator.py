"""Data update coordinator for Mylife114."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import Mylife114Api, Mylife114ApiError
from .const import DOMAIN, UPDATE_INTERVAL_HOURS

_LOGGER = logging.getLogger(__name__)


class Mylife114Coordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Fetches all doors the user can open, across every community they belong to."""

    def __init__(self, hass: HomeAssistant, api: Mylife114Api) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )
        self.api = api

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            communities = await self.api.get_communities()
        except Mylife114ApiError as err:
            raise UpdateFailed(str(err)) from err

        results: list[dict[str, Any]] = []
        seen_sn: set[str] = set()
        for community in communities:
            community_id = _first(community, ("id", "community_id", "root_id"))
            community_name = _first(community, ("name", "community_name", "title")) or ""
            if community_id is None:
                continue
            try:
                doors = await self.api.get_doors(community_id)
            except Mylife114ApiError as err:
                _LOGGER.warning("Failed to fetch doors for community %s: %s", community_id, err)
                continue
            for door in doors:
                controller_sn = _first(
                    door, ("controller_sn", "door_sn", "sn", "device_sn")
                )
                house_id = _first(door, ("house_id", "houseId", "hid"))
                if not controller_sn or not house_id:
                    _LOGGER.debug("Skipping door missing sn/house_id: %s", door)
                    continue
                sn_str = str(controller_sn)
                # Same door is returned once per house_id the user belongs to —
                # keep the first occurrence so we get one button per physical door.
                if sn_str in seen_sn:
                    continue
                seen_sn.add(sn_str)
                direction = _first(door, ("direction", "dir")) or 1
                name = (
                    _first(door, ("name", "door_name", "title", "alias"))
                    or f"门 {controller_sn}"
                )
                door_type = _first(door, ("door_type", "type")) or ""
                results.append(
                    {
                        "community_id": str(community_id),
                        "community_name": community_name,
                        "controller_sn": sn_str,
                        "house_id": str(house_id),
                        "direction": int(direction),
                        "name": name,
                        "door_type": door_type,
                    }
                )
        _LOGGER.debug("Discovered %d door(s)", len(results))
        return results


def _first(d: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None
