"""Testing my new package."""
import asyncio
import socket

from vegehub.vegehub import VegeHub

async def supaloop():
    """Main loop."""
    hub = VegeHub("192.168.0.102")
    print(hub.ip_address)
    await hub.retrieve_mac_address()
    print(hub.mac_address)
    
    server_address = f"http://{get_local_ip()}:8123/api/vegehub/update"
    print(server_address)
    await hub.setup(hub.simple_mac_address, server_address)
    print(hub.info)
    print("cool")

def get_local_ip():
    """ Use a dummy connection to determine the local IP address."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))  # Google DNS server, no data is actually sent
        return s.getsockname()[0]

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(supaloop())
        loop.close()
    except KeyboardInterrupt:
        pass
