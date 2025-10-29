# mDNS Discovery Troubleshooting Guide

## Problem

The integration test isn't detecting your VegeHub device via mDNS discovery, even though you know it's on the network.

## Quick Fix: Manual IP Entry

**The integration test now supports manual IP entry!**

When the test runs and doesn't find any devices, it will prompt you to manually enter the IP address:

```
❌ No VegeHub devices found via mDNS discovery.
   Make sure your VegeHub is powered on and connected to the same network.

💡 Would you like to manually enter a VegeHub IP address instead?
   Enter IP address (or press Enter to quit): 192.168.1.100
```

Just enter your VegeHub's IP address and the tests will proceed.

## Diagnostic Tool

I've created a diagnostic script to help identify the issue:

```bash
poetry run python mdns_diagnostic.py
```

This will:
- Try multiple service name variations (`_vege._tcp.local.`, `_vege._tcp.`, etc.)
- Show all discovered services with detailed information
- Use longer timeout (10 seconds per service type)
- Optionally scan for ALL mDNS services on your network
- Provide specific troubleshooting suggestions

## Common Causes

### 1. **VegeHub Doesn't Support mDNS**

Some firmware versions might not advertise via mDNS. This is why we added manual IP entry.

**Solution**: Use manual IP entry in the integration test.

### 2. **Wrong Service Name**

The test looks for `_vege._tcp.local.` but the actual service name might be different.

**Solution**:
- Run `mdns_diagnostic.py` to see what services are advertised
- If you find VegeHub under a different name, update `integration_test.py` line 75

### 3. **Firewall Blocking mDNS**

mDNS uses UDP port 5353. Some firewalls block this.

**Solution** (Linux):
```bash
# Check if port 5353 is open
sudo netstat -ulpn | grep 5353

# If using ufw
sudo ufw allow 5353/udp

# If using firewalld
sudo firewall-cmd --add-service=mdns --permanent
sudo firewall-cmd --reload
```

### 4. **mDNS Service Not Running**

Your system's mDNS responder might not be running.

**Solution** (Linux):
```bash
# Check Avahi status
systemctl status avahi-daemon

# Start if needed
sudo systemctl start avahi-daemon
sudo systemctl enable avahi-daemon
```

**Solution** (macOS):
mDNS should work automatically via Bonjour.

### 5. **Different Network/VLAN**

VegeHub is on a different network segment or VLAN than your computer.

**Solution**:
- Check your IP address: `ip addr` or `ifconfig`
- Check VegeHub's IP (from router or device display)
- Ensure they're in the same subnet
- Use manual IP entry if on different subnets

### 6. **Docker/VM Networking**

If running in a container or VM, mDNS packets might not be forwarded.

**Solution**:
- Run tests on host machine
- Or use manual IP entry

## Testing mDNS Manually

### Linux (using avahi-browse)

```bash
# Install avahi-utils if needed
sudo apt-get install avahi-utils

# Browse for VegeHub service
avahi-browse -rt _vege._tcp

# Browse all services
avahi-browse -a
```

### macOS (using dns-sd)

```bash
# Browse for VegeHub service
dns-sd -B _vege._tcp

# Browse all services
dns-sd -B _services._dns-sd._udp
```

## Verifying VegeHub Connectivity

If you know the IP address, verify basic connectivity:

```bash
# Test network connectivity
ping 192.168.1.100

# Test HTTP API
curl -X POST http://192.168.1.100/api/info/get \
  -H "Content-Type: application/json" \
  -d '{"hub":[],"wifi":[]}'
```

If the curl command works, the VegeHub is reachable and you can use manual IP entry.

## Next Steps

1. **Try manual IP entry first** - This is the fastest solution
2. **Run mdns_diagnostic.py** - To understand what's being advertised
3. **Check firewall** - Ensure mDNS isn't blocked
4. **Verify mDNS service** - Make sure avahi-daemon is running (Linux)
5. **Test basic connectivity** - Use ping and curl

## Updating the Integration Test

If you discover the VegeHub uses a different service name, you can update it:

Edit `integration_test.py`, find this line (around line 75):

```python
_browser = ServiceBrowser(zeroconf, "_vege._tcp.local.", listener)
```

Change `"_vege._tcp.local."` to whatever service name you discovered with the diagnostic tool.

## Summary

**Quickest solution**: Just use manual IP entry when prompted. The integration test will work exactly the same way.

**For debugging**: Use `mdns_diagnostic.py` to see what's actually on the network.
