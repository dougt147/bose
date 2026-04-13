# Bose Soundtouch 20 Management System

Python scripts for discovering and managing Bose Soundtouch 20 speaker systems via the Web API.

## Overview

The Soundtouch API allows you to:
- Discover devices on your network
- Control playback (play, pause, skip)
- Manage presets and sources
- Get device information and status
- Control volume and power

## Files

### `soundtouch_discovery.py`
Basic discovery script that finds Bose Soundtouch devices on your local network.

**Features:**
- SSDP protocol discovery (multicast)
- Network port scanning (port 8090)
- Device information retrieval
- Connection testing
- JSON output support

**Usage:**

```bash
# Basic discovery
python soundtouch_discovery.py

# With custom timeout (in seconds)
python soundtouch_discovery.py --timeout 10

# Output as JSON
python soundtouch_discovery.py --json

# Get help
python soundtouch_discovery.py --help
```

**Example Output:**
```
======================================================================
✅ Found 1 device(s):
======================================================================

Device 1: ✓ Reachable
  IP Address:      192.168.1.100:8090
  Name:            Living Room Speaker
  Model:           SoundTouch 20
  MAC Address:     AABBCCDDEEFF
  Firmware:        14.2.0
```

## Bose Soundtouch API Reference

### Base URL
```
http://<device-ip>:8090
```

### Common Endpoints

#### Device Information
- `GET /info` - Get device info (name, model, firmware, MAC)
- `GET /status` - Get current playback status

#### Playback Control
- `POST /key` - Send key commands
  - Keys: `PLAY`, `PAUSE`, `RESUME`, `STOP`, `NEXT`, `PREV`

#### Volume
- `POST /volume` - Set volume (0-100)
- `GET /volume` - Get current volume

#### Presets
- `GET /presets` - List saved presets
- `POST /key` - Play preset (with preset parameter)

#### Sources
- `GET /sources` - Get available sources
- `POST /select` - Select a source

## Requirements

- Python 3.6+
- `requests` library
- Local network access to Soundtouch devices
- Device must be powered on and connected to WiFi

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Ensure your Soundtouch device is:
1. On and connected to the same network
2. Connected to WiFi
3. Not behind a firewall that blocks port 8090

## Future Enhancements

Planned additional scripts:
- `soundtouch_control.py` - Full playback and volume control
- `soundtouch_presets.py` - Preset management
- `soundtouch_monitor.py` - Real-time device monitoring

## References

- [Bose Soundtouch API Documentation](https://www.bose.com/support)
- UPnP/SSDP Protocol
- REST API over HTTP

## Notes

- The API uses XML for responses
- Port 8090 is the default Soundtouch API port
- Devices are discovered via UPnP/SSDP multicast
- The script performs a network scan on the local subnet
- Discovery works best when devices are powered on
