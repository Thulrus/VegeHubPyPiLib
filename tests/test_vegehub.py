"""Basic tests for VegeHub package."""

import pytest
from aioresponses import aioresponses
from vegehub.vegehub import VegeHub  # Update import as necessary based on your project structure

IP_ADDR = "192.168.0.100"

@pytest.fixture
def fixture_hub():
    """Fixture for creating a VegeHub instance."""
    return VegeHub(ip_address=IP_ADDR)

@pytest.mark.asyncio
async def test_retrieve_mac_address_success(fixture_hub):
    """Test retrieve_mac_address method retrieves and sets the MAC address successfully."""
    mac_address = "AA:BB:CC:DD:EE:FF"
    with aioresponses() as mocked:
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={
            "wifi": {"mac_addr": mac_address}
        })
        assert IP_ADDR == fixture_hub.ip_address

        ret = await fixture_hub.retrieve_mac_address()
        assert ret is True
        assert fixture_hub.mac_address == mac_address
        assert fixture_hub.simple_mac_address == "aabbccddeeff"
        
@pytest.mark.asyncio
async def test_retrieve_mac_address_failure_response(fixture_hub):
    """Test retrieve_mac_address method retrieves and sets the MAC address successfully."""
    mac_address = "AA:BB:CC:DD:EE:FF"
    with aioresponses() as mocked:
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={
            "wifi": {"mac_addr": mac_address}
        }, status=400)

        ret = await fixture_hub.retrieve_mac_address()
        assert ret is False

@pytest.mark.asyncio
async def test_retrieve_mac_address_failure_data(fixture_hub):
    """Test retrieve_mac_address handles failure to retrieve MAC address."""
    with aioresponses() as mocked:
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={"wifi": {}})

        ret = await fixture_hub.retrieve_mac_address()
        
        assert ret is False
        assert fixture_hub.mac_address == ""
        assert fixture_hub.simple_mac_address == ""

@pytest.mark.asyncio
async def test_setup_success(fixture_hub):
    """Test the setup method sends the correct API key and server address."""
    api_key = "test_api_key"
    server_address = "http://example.com"

    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get", payload={
            "hub": {}, "api_key": api_key
        })
        
        mocked.post(f"http://{IP_ADDR}/api/config/set", status=200)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={"device_name": "VegeHub"})

        await fixture_hub.setup(api_key, server_address)

        assert fixture_hub.info == {"device_name": "VegeHub"}

@pytest.mark.asyncio
async def test_setup_failure_config_get(fixture_hub):
    """Test the setup method sends the correct API key and server address."""
    api_key = "test_api_key"
    server_address = "http://example.com"

    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get", payload={
            "hub": {}, "api_key": api_key
        }, status=400)
        
        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={"device_name": "VegeHub"}, status=200)

        ret = await fixture_hub.setup(api_key, server_address)

        assert ret is False
    
@pytest.mark.asyncio
async def test_setup_failure_config_set(fixture_hub):
    """Test the setup method sends the correct API key and server address."""
    api_key = "test_api_key"
    server_address = "http://example.com"

    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get", payload={
            "hub": {}, "api_key": api_key
        }, status=200)
        
        mocked.post(f"http://{IP_ADDR}/api/config/set", status=400)
        
        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={"device_name": "VegeHub"}, status=200)

        ret = await fixture_hub.setup(api_key, server_address)

        assert ret is False

@pytest.mark.asyncio
async def test_setup_failure_missing_api_key(fixture_hub):
    """Test the setup method sends the correct API key and server address."""
    api_key = "test_api_key"
    server_address = "http://example.com"

    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get", payload={
            "hub": {}
        })
        
        mocked.post(f"http://{IP_ADDR}/api/config/set", status=200)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={"device_name": "VegeHub"}, status=200)

        ret = await fixture_hub.setup(api_key, server_address)

        assert ret is False

@pytest.mark.asyncio
async def test_setup_failure_missing_hub(fixture_hub):
    """Test the setup method sends the correct API key and server address."""
    api_key = "test_api_key"
    server_address = "http://example.com"

    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get", payload={
            "api_key": api_key
        })
        
        mocked.post(f"http://{IP_ADDR}/api/config/set", status=200)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={"device_name": "VegeHub"}, status=200)

        ret = await fixture_hub.setup(api_key, server_address)

        assert ret is False

@pytest.mark.asyncio
async def test_setup_failure_no_info(fixture_hub):
    """Test the setup method sends the correct API key and server address."""
    api_key = "test_api_key"
    server_address = "http://example.com"

    with aioresponses() as mocked:
        # Mock _get_device_config
        mocked.post(f"http://{IP_ADDR}/api/config/get", payload={
            "hub": {}, "api_key": api_key
        })
        
        mocked.post(f"http://{IP_ADDR}/api/config/set", status=200)

        # Mock _get_device_info
        mocked.post(f"http://{IP_ADDR}/api/info/get", payload={"device_name": "VegeHub"}, status=400)

        await fixture_hub.setup(api_key, server_address)

        assert fixture_hub.info is None

@pytest.mark.asyncio
async def test_request_update(fixture_hub):
    """Test the _request_update method sends the update request to the device."""
    with aioresponses() as mocked:
        mocked.get(f"http://{IP_ADDR}/api/update/send", status=200)

        await fixture_hub.request_update()

@pytest.mark.asyncio
async def test_request_update_fail(fixture_hub):
    """Test the _request_update method sends the update request to the device."""
    with aioresponses() as mocked:
        mocked.get(f"http://{IP_ADDR}/api/update/send", status=400)

        await fixture_hub.request_update()