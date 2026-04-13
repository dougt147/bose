"""
Basic discovery script for Bose Soundtouch 20 speaker system.
Uses UPnP to discover devices on the local network.
"""

import socket
import struct
import textwrap
from enum import Enum
from typing import List, Dict, Optional
import requests
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


class SoundtouchDevice:
    """Represents a discovered Soundtouch device."""
    
    def __init__(self, ip: str, port: int = 8090):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.name: Optional[str] = None
        self.model: Optional[str] = None
        self.mac_address: Optional[str] = None
        self.firmware_version: Optional[str] = None
        self.is_reachable = False
    
    def __repr__(self) -> str:
        return (f"SoundtouchDevice(ip={self.ip}, name={self.name}, "
                f"model={self.model}, reachable={self.is_reachable})")
    
    def to_dict(self) -> Dict:
        """Convert device info to dictionary."""
        return {
            "ip": self.ip,
            "port": self.port,
            "name": self.name,
            "model": self.model,
            "mac_address": self.mac_address,
            "firmware_version": self.firmware_version,
            "is_reachable": self.is_reachable,
        }


class SoundtouchDiscovery:
    """Discovers Bose Soundtouch devices on the local network."""
    
    # Bose UPnP Service Type
    UPNP_TARGET = "urn:Bose-com:service:BasicDevice:1"
    
    # SSDP (Simple Service Discovery Protocol) multicast address and port
    SSDP_TARGET = ("239.255.255.250", 1900)
    SSDP_MX = 4  # Search timeout in seconds
    
    def __init__(self, timeout: int = 5):
        """
        Initialize discovery.
        
        Args:
            timeout: Timeout for device discovery in seconds
        """
        self.timeout = timeout
        self.devices: List[SoundtouchDevice] = []
    
    def discover(self) -> List[SoundtouchDevice]:
        """
        Discover Soundtouch devices on the local network.
        
        Returns:
            List of discovered SoundtouchDevice objects
        """
        print("Starting Soundtouch device discovery...")
        print(f"Searching for devices (timeout: {self.timeout}s)...\n")
        
        # Try SSDP discovery
        ssdp_devices = self._ssdp_discovery()
        
        # Try network scan on common ports
        scan_devices = self._network_scan()
        
        # Merge results (avoid duplicates)
        all_devices = {}
        for device in ssdp_devices + scan_devices:
            key = f"{device.ip}:{device.port}"
            all_devices[key] = device
        
        self.devices = list(all_devices.values())
        
        # Get detailed info for each device
        for device in self.devices:
            self._get_device_info(device)
        
        return self.devices
    
    def _ssdp_discovery(self) -> List[SoundtouchDevice]:
        """Discover devices using SSDP protocol."""
        devices = []
        
        try:
            # Create SSDP request
            ssdp_request = (
                f"M-SEARCH * HTTP/1.1\r\n"
                f"HOST: 239.255.255.250:1900\r\n"
                f"MAN: \"ssdp:discover\"\r\n"
                f"MX: {self.SSDP_MX}\r\n"
                f"ST: ssdp:all\r\n"
                f"\r\n"
            )
            
            # Send SSDP request
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(self.timeout)
            
            sock.sendto(ssdp_request.encode('utf-8'), self.SSDP_TARGET)
            
            print("Scanning network via SSDP...")
            discovered_ips = set()
            
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    response = data.decode('utf-8', errors='ignore')
                    
                    # Look for Bose devices
                    if 'bose' in response.lower() or 'soundtouch' in response.lower():
                        # Extract IP and device information
                        if addr[0] not in discovered_ips:
                            discovered_ips.add(addr[0])
                            device = SoundtouchDevice(addr[0])
                            devices.append(device)
                            print(f"  Found device at {addr[0]}")
            
            except socket.timeout:
                pass
            
            sock.close()
        
        except Exception as e:
            print(f"SSDP discovery error: {e}")
        
        return devices
    
    def _network_scan(self) -> List[SoundtouchDevice]:
        """Scan common ports on local network segment."""
        devices = []
        
        try:
            # Get local IP
            local_ip = socket.gethostbyname(socket.gethostname())
            print(f"Local IP: {local_ip}")
            
            # Get network segment (assumes /24 network)
            network_segment = ".".join(local_ip.split(".")[:3])
            print(f"Scanning network segment: {network_segment}.* on port 8090...\n")
            
            # Scan common range (this is simplified - full scan would take longer)
            # Modify the range as needed for your network
            for i in range(1, 50):  # Scan first 50 IPs in the subnet
                ip = f"{network_segment}.{i}"
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((ip, 8090))
                    sock.close()
                    
                    if result == 0:
                        device = SoundtouchDevice(ip)
                        devices.append(device)
                        print(f"  Found open port at {ip}:8090")
                
                except Exception:
                    pass
        
        except Exception as e:
            print(f"Network scan error: {e}")
        
        return devices
    
    def _get_device_info(self, device: SoundtouchDevice) -> None:
        """Fetch device information from Soundtouch API."""
        try:
            # Try to get device info
            response = requests.get(
                f"{device.base_url}/info",
                timeout=2
            )
            
            if response.status_code == 200:
                device.is_reachable = True
                
                # Parse XML response
                try:
                    root = ET.fromstring(response.content)
                    
                    device.name = root.findtext(".//name", "Unknown")
                    device.model = root.findtext(".//model", "Unknown")
                    device.mac_address = root.findtext(".//macAddress", "Unknown")
                    device.firmware_version = root.findtext(".//fwVersion", "Unknown")
                
                except ET.ParseError:
                    device.name = "Unable to parse info"
        
        except requests.exceptions.ConnectionError:
            device.is_reachable = False
        except Exception as e:
            print(f"Error getting info from {device.ip}: {e}")
    
    def print_results(self) -> None:
        """Print discovery results in a formatted way."""
        if not self.devices:
            print("\n❌ No Soundtouch devices found.")
            return
        
        print(f"\n{'='*70}")
        print(f"✅ Found {len(self.devices)} device(s):")
        print(f"{'='*70}\n")
        
        for i, device in enumerate(self.devices, 1):
            status = "✓ Reachable" if device.is_reachable else "✗ Not reachable"
            print(f"Device {i}: {status}")
            print(f"  IP Address:      {device.ip}:{device.port}")
            print(f"  Name:            {device.name or 'Unknown'}")
            print(f"  Model:           {device.model or 'Unknown'}")
            print(f"  MAC Address:     {device.mac_address or 'Unknown'}")
            print(f"  Firmware:        {device.firmware_version or 'Unknown'}")
            print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Discover Bose Soundtouch 20 devices on the local network"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=5,
        help="Discovery timeout in seconds (default: 5)"
    )
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Run discovery
    discovery = SoundtouchDiscovery(timeout=args.timeout)
    devices = discovery.discover()
    
    # Print results
    if args.json:
        import json
        print(json.dumps([d.to_dict() for d in devices], indent=2))
    else:
        discovery.print_results()


if __name__ == "__main__":
    main()
