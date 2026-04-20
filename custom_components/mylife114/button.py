"""Button platform — one button per discovered door."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import Mylife114ApiError
from .const import DOMAIN
from .coordinator import Mylife114Coordinator

_LOGGER = logging.getLogger(__name__)

ICON_BY_DOOR_TYPE = {
    "公共门": "mdi:gate",
    "单元门": "mdi:door-open",
}
DEFAULT_ICON = "mdi:door-open"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: Mylife114Coordinator = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    @callback
    def _refresh() -> None:
        new_entities: list[DoorButton] = []
        for door in coordinator.data or []:
            key = f"{door['controller_sn']}_{door['house_id']}"
            if key in added:
                continue
            added.add(key)
            new_entities.append(DoorButton(coordinator, entry.entry_id, door))
        if new_entities:
            async_add_entities(new_entities)

    _refresh()
    entry.async_on_unload(coordinator.async_add_listener(_refresh))


class DoorButton(CoordinatorEntity[Mylife114Coordinator], ButtonEntity):
    """A press-to-open door button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Mylife114Coordinator,
        entry_id: str,
        door: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._controller_sn: str = door["controller_sn"]
        self._house_id: str = door["house_id"]
        self._direction: int = int(door.get("direction", 1))

        community_id = door.get("community_id", "")
        community_name = door.get("community_name", "") or f"社区 {community_id}"
        door_type = door.get("door_type", "")

        self._attr_unique_id = f"{entry_id}_{self._controller_sn}_{self._house_id}"
        self._attr_name = door.get("name") or f"门 {self._controller_sn}"
        self._attr_icon = ICON_BY_DOOR_TYPE.get(door_type, DEFAULT_ICON)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"community_{community_id}")},
            name=community_name,
            manufacturer="Mylife114",
            model="门禁控制器",
        )
        self._attr_extra_state_attributes = {
            "controller_sn": self._controller_sn,
            "house_id": self._house_id,
            "direction": self._direction,
            "community_id": community_id,
            "community_name": community_name,
            "door_type": door.get("door_type", ""),
        }

    async def async_press(self) -> None:
        event_data = {
            "controller_sn": self._controller_sn,
            "house_id": self._house_id,
            "door_name": self._attr_name,
            "community_name": self._attr_extra_state_attributes.get("community_name", ""),
        }
        try:
            result = await self.coordinator.api.open_door(
                self._controller_sn, self._house_id, self._direction
            )
        except Mylife114ApiError as err:
            _LOGGER.error("Open door %s failed: %s", self._controller_sn, err)
            self.hass.bus.async_fire(
                f"{DOMAIN}_door_event",
                {**event_data, "result": "failed", "msg": str(err)},
            )
            raise
        self.hass.bus.async_fire(
            f"{DOMAIN}_door_event",
            {**event_data, "result": "success", "msg": result.get("msg", "")},
        )
