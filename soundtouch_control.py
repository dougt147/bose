"""
Direct connection test for Bose Soundtouch 20 speaker.
Connect to a known device address.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List


class SoundtouchDevice:
    """Controller for a Bose Soundtouch device."""
    
    def __init__(self, ip: str, port: int = 8090):
        """
        Initialize device connection.
        
        Args:
            ip: Device IP address
            port: API port (default 8090)
        """
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.timeout = 5
    
    def get_info(self) -> Optional[Dict]:
        """Get device information."""
        try:
            response = requests.get(f"{self.base_url}/info", timeout=self.timeout)
            if response.status_code == 200:
                return self._parse_xml(response.content)
            return None
        except Exception as e:
            print(f"Error getting info: {e}")
            return None
    
    def get_status(self) -> Optional[Dict]:
        """Get current playback status."""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=self.timeout)
            if response.status_code == 200:
                return self._parse_xml(response.content)
            return None
        except Exception as e:
            print(f"Error getting status: {e}")
            return None
    
    def get_volume(self) -> Optional[int]:
        """Get current volume (0-100)."""
        try:
            response = requests.get(f"{self.base_url}/volume", timeout=self.timeout)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                volume = root.findtext("actualvolume")
                return int(volume) if volume else None
            return None
        except Exception as e:
            print(f"Error getting volume: {e}")
            return None
    
    def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)."""
        if not 0 <= volume <= 100:
            print("Volume must be between 0 and 100")
            return False
        
        try:
            body = f"<volume>{volume}</volume>"
            response = requests.post(
                f"{self.base_url}/volume",
                data=body,
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False
    
    def play(self) -> bool:
        """Send play command."""
        return self._send_key("PLAY")
    
    def pause(self) -> bool:
        """Send pause command."""
        return self._send_key("PAUSE")
    
    def resume(self) -> bool:
        """Send resume command."""
        return self._send_key("RESUME")
    
    def next_track(self) -> bool:
        """Send next track command."""
        return self._send_key("NEXT")
    
    def previous_track(self) -> bool:
        """Send previous track command."""
        return self._send_key("PREV")
    
    def power_on(self) -> bool:
        """Power on the device."""
        return self._send_key("POWER_ON")
    
    def power_off(self) -> bool:
        """Power off the device."""
        return self._send_key("POWER_OFF")
    
    def _send_key(self, key: str) -> bool:
        """Send a key command."""
        try:
            body = f"<key state='press' sender='Gabbo'>{key}</key>"
            response = requests.post(
                f"{self.base_url}/key",
                data=body,
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending key '{key}': {e}")
            return False
    
    def play_preset(self, preset_id: int, presets_data: List[Dict] = None) -> bool:
        """
        Play a preset by its ID.
        Requires the presets data from get_presets_list().
        """
        if not presets_data:
            presets_data = self.get_presets_list()
        
        try:
            preset = next((p for p in presets_data if p["id"] == str(preset_id)), None)
            if not preset or not preset.get("content_item_xml"):
                print(f"Preset {preset_id} not found")
                return False
            
            # POST the ContentItem to /select to play it
            response = requests.post(
                f"{self.base_url}/select",
                data=preset["content_item_xml"],
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error playing preset {preset_id}: {e}")
            return False
    
    def get_presets_list(self) -> List[Dict]:
        """Get list of presets with their ContentItem XML."""
        try:
            response = requests.get(f"{self.base_url}/presets", timeout=self.timeout)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                presets = []
                for preset_elem in root.findall(".//preset"):
                    preset_id = preset_elem.get("id")
                    content_item = preset_elem.find(".//ContentItem")
                    if content_item is not None:
                        preset_name = content_item.findtext("itemName", "Unknown")
                        content_item_xml = ET.tostring(content_item, encoding='utf-8').decode()
                    else:
                        preset_name = "Unknown"
                        content_item_xml = None
                    presets.append({
                        "id": preset_id,
                        "name": preset_name,
                        "content_item_xml": content_item_xml
                    })
                return presets
            return []
        except Exception as e:
            print(f"Error getting presets: {e}")
            return []
    
    def _parse_xml(self, content: bytes) -> Dict:
        """Parse XML response into dictionary."""
        try:
            root = ET.fromstring(content)
            result = {}
            for child in root:
                result[child.tag] = child.text
            return result
        except ET.ParseError:
            return {}
    
    def test_connection(self) -> bool:
        """Test device connectivity."""
        try:
            response = requests.get(f"{self.base_url}/info", timeout=self.timeout)
            return response.status_code == 200
        except:
            return False


def main():
    """Test connection to the speaker."""
    SPEAKER_IP = "192.168.5.197"
    
    print(f"Connecting to Soundtouch device at {SPEAKER_IP}...\n")
    
    device = SoundtouchDevice(SPEAKER_IP)
    
    # Test connection
    if not device.test_connection():
        print(f"❌ Cannot reach device at {SPEAKER_IP}")
        return
    
    print(f"✅ Connected to device\n")
    
    # Get device info
    info = device.get_info()
    if info:
        print("Device Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()
    
    # Get status
    status = device.get_status()
    if status:
        print("Playback Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        print()
    
    # Get volume
    volume = device.get_volume()
    if volume is not None:
        print(f"Current Volume: {volume}")
        print()
    
    # Example: Set volume to 50
    print("Setting volume to 50...")
    if device.set_volume(50):
        print("✅ Volume set successfully")
    else:
        print("❌ Failed to set volume")


if __name__ == "__main__":
    main()
