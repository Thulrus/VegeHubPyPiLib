"""VegeHub API access library."""

import logging
from typing import Any
import aiohttp

_LOGGER = logging.getLogger(__name__)


class VegeHub():
    """Vegehub class will contain all properties and methods necessary for contacting the Hub."""

    def __init__(self, ip_address: str, mac_address: str = "") -> None:
        self._ip_address = ip_address
        self._mac_address = mac_address
        self._info: dict[Any, Any] | None = None

    @property
    def ip_address(self) -> str:
        """Property to retrieve IP address"""
        return self._ip_address

    @property
    def mac_address(self) -> str | None:
        """Property to retrieve MAC address"""
        return self._mac_address

    @property
    def info(self) -> dict | None:
        """Property to retrieve IP address"""
        return self._info

    async def request_update(self) -> bool:
        """Request an update of data from the Hub"""
        return await self._request_update()

    async def retrieve_mac_address(self) -> bool:
        """Start the process of retrieving the MAC address from the Hub"""
        return await self._get_device_mac()

    async def set_actuator(self, state: int, slot: int,
                           duration: int) -> bool:
        """Set the target actuator to the target state for the intended duration."""
        return await self._set_actuator(state, slot, duration)

    async def actuator_states(self)->list:
        """Grab the states of all actuators on the Hub and return a list of JSON data on them."""
        return await self._get_actuator_info()

    async def setup(self, api_key: str, server_address: str) -> bool:
        """Set the API key and target server on the Hub."""
        # Fetch current config from the device
        config_data = await self._get_device_config()

        # Modify the config with the new API key and server address
        modified_config = self._modify_device_config(config_data, api_key,
                                                     server_address)

        # Send the modified config back to the device
        ret = await self._set_device_config(modified_config)

        if ret is not None:
            self._info = await self._get_device_info()

        return ret

    async def _get_device_info(self) -> dict | None:
        """Fetch the current configuration from the device."""
        url = f"http://{self._ip_address}/api/info/get"

        payload: dict[Any, Any] = {"hub": []}
        async with (
                aiohttp.ClientSession() as session,
                session.post(url, json=payload) as response,
        ):
            if response.status != 200:
                _LOGGER.error("Failed to get config from %s: HTTP %s", url,
                              response.status)
                return None

            # Parse the response JSON
            info_data = await response.json()
            _LOGGER.info("Received info from %s", self._ip_address)
            return info_data

    async def _get_device_config(self) -> dict | None:
        """Fetch the current configuration from the device."""
        url = f"http://{self._ip_address}/api/config/get"

        payload: dict[Any, Any] = {"hub": [], "api_key": []}

        async with (
                aiohttp.ClientSession() as session,
                session.post(url, json=payload) as response,
        ):
            if response.status != 200:
                _LOGGER.error("Failed to get config from %s: HTTP %s", url,
                              response.status)
                return None

            # Parse the response JSON
            return await response.json()

    def _modify_device_config(self, config_data: dict | None, new_key: str,
                              server_url: str) -> dict | None:
        """Modify the device config by adding or updating the API key."""
        error = False

        if config_data is None:
            return None

        # Assuming the API key should be added to the 'hub' section, modify as necessary
        if "api_key" in config_data:
            config_data["api_key"] = new_key
        else:
            error = True

        # Modify the server_url in the returned JSON
        if "hub" in config_data:
            config_data["hub"]["server_url"] = server_url
            config_data["hub"]["server_type"] = 3
        else:
            error = True

        if error:
            return None
        return config_data

    async def _set_device_config(self, config_data: dict | None) -> bool:
        """Send the modified configuration back to the device."""
        url = f"http://{self._ip_address}/api/config/set"

        if config_data is None:
            return False

        async with (
                aiohttp.ClientSession() as session,
                session.post(url, json=config_data) as response,
        ):
            if response.status != 200:
                _LOGGER.error("Failed to set config at %s: HTTP %s", url,
                              response.status)
                return False
        return True

    async def _request_update(self) -> bool:
        """Ask the device to send in a full update of data to Home Assistant."""
        url = f"http://{self._ip_address}/api/update/send"

        async with aiohttp.ClientSession() as session, session.get(
                url) as response:
            if response.status != 200:
                _LOGGER.error("Failed to ask for update from %s: HTTP %s", url,
                              response.status)
                return False
        return True

    async def _get_device_mac(self) -> bool:
        """Fetch the MAC address by sending a POST request to the device's /api/config_get."""
        url = f"http://{self._ip_address}/api/info/get"

        # Prepare the JSON payload for the POST request
        payload: dict[Any, Any] = {"wifi": []}

        # Use aiohttp to send the POST request with the JSON body
        async with (
            aiohttp.ClientSession() as session,
            session.post(url, json=payload) as response,
        ):
            if response.status != 200:
                _LOGGER.error("Failed to get config from %s: HTTP %s", url,
                              response.status)
                return False
            # Parse the JSON response
            config_data = await response.json()
            mac_address = config_data.get("wifi", {}).get("mac_addr")
            if not mac_address:
                _LOGGER.error(
                    "MAC address not found in the config response from %s",
                    self._ip_address)
                return False
            _LOGGER.info("%s MAC address: %s", self._ip_address, mac_address)
            self._mac_address = mac_address.replace(":", "").upper()
        return True

    async def _set_actuator(self, state: int, slot: int,
                            duration: int) -> bool:
        url = f"http://{self._ip_address}/api/actuators/set"
        _LOGGER.info("Setting actuator %s on %s", slot, self._ip_address)

        # Prepare the JSON payload for the POST request
        payload = {
            "target": slot,
            "duration": duration,
            "state": state,
        }

        # Use aiohttp to send the POST request with the JSON body
        async with (
            aiohttp.ClientSession() as session,
            session.post(url, json=payload) as response,
        ):
            if response.status != 200:
                _LOGGER.error(
                    "Failed to set actuator state on %s: HTTP %s",
                    url,
                    response.status,
                )
                raise ConnectionError
            return True

    async def _get_actuator_info(self) -> list:
        """Fetch the current status of the actuators."""
        url = f"http://{self._ip_address}/api/actuators/status"
        _LOGGER.info("Retrieving actuator status from %s", self._ip_address)

        # Use aiohttp to send the POST request with the JSON body
        async with aiohttp.ClientSession() as session, session.get(
            url) as response:
            if response.status != 200:
                _LOGGER.error("Failed to status from %s: HTTP %s", url,
                              response.status)
                raise ConnectionError

            # Parse the JSON response
            config_data = await response.json()
            actuators = config_data.get("actuators", [])
            if not actuators:
                _LOGGER.error(
                    "MAC address not found in the config response from %s",
                    self._ip_address)
                raise AttributeError
            return actuators
