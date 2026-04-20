"""Config flow for Mylife114."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import Mylife114Api, Mylife114ApiError
from .const import CONF_UID, CONF_USER_AGENT, DEFAULT_USER_AGENT, DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_UID): str,
        vol.Optional(CONF_NAME, default="Mylife114 门禁"): str,
        vol.Optional(CONF_USER_AGENT, default=DEFAULT_USER_AGENT): str,
    }
)


class Mylife114ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mylife114."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            uid = str(user_input[CONF_UID]).strip()
            await self.async_set_unique_id(f"mylife114_{uid}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = Mylife114Api(
                session, uid, user_agent=user_input[CONF_USER_AGENT]
            )
            try:
                await api.get_communities()
            except Mylife114ApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_UID: uid,
                        CONF_USER_AGENT: user_input[CONF_USER_AGENT],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
            description_placeholders={"known_uid": "127149"},
        )
