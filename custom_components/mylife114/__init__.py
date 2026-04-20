"""Mylife114 integration setup."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import Mylife114Api, Mylife114ApiError
from .const import (
    CONF_UID,
    CONF_USER_AGENT,
    DEFAULT_DIRECTION,
    DEFAULT_USER_AGENT,
    DOMAIN,
    SERVICE_OPEN_DOOR,
)
from .coordinator import Mylife114Coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON]

OPEN_DOOR_SCHEMA = vol.Schema(
    {
        vol.Required("controller_sn"): cv.string,
        vol.Required("house_id"): cv.string,
        vol.Optional("direction", default=DEFAULT_DIRECTION): cv.positive_int,
        vol.Optional("uid"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = Mylife114Api(
        session,
        entry.data[CONF_UID],
        user_agent=entry.data.get(CONF_USER_AGENT, DEFAULT_USER_AGENT),
    )

    coordinator = Mylife114Coordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async def handle_open_door(call: ServiceCall) -> None:
        sn: str = call.data["controller_sn"]
        house: str = call.data["house_id"]
        direction: int = call.data.get("direction", DEFAULT_DIRECTION)
        override_uid: str | None = call.data.get("uid")

        client = api
        if override_uid and override_uid != api.uid:
            client = Mylife114Api(
                session,
                override_uid,
                user_agent=entry.data.get(CONF_USER_AGENT, DEFAULT_USER_AGENT),
            )
        try:
            await client.open_door(sn, house, direction)
        except Mylife114ApiError as err:
            _LOGGER.error("open_door service failed: %s", err)
            raise

    if not hass.services.has_service(DOMAIN, SERVICE_OPEN_DOOR):
        hass.services.async_register(
            DOMAIN, SERVICE_OPEN_DOOR, handle_open_door, schema=OPEN_DOOR_SCHEMA
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_OPEN_DOOR)
    return unload_ok
