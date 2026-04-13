"""
Get a list of saved presets from Bose Soundtouch device.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict


class SoundtouchPresets:
    """Manager for Soundtouch presets."""
    
    def __init__(self, ip: str = "192.168.5.197", port: int = 8090):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.timeout = 5
    
    def get_presets(self) -> List[Dict]:
        """Get list of saved presets."""
        try:
            response = requests.get(
                f"{self.base_url}/presets",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return self._parse_presets(response.content)
            else:
                print(f"Error: HTTP {response.status_code}")
                return []
        
        except Exception as e:
            print(f"Error fetching presets: {e}")
            return []
    
    def _parse_presets(self, content: bytes) -> List[Dict]:
        """Parse presets XML response."""
        presets = []
        try:
            root = ET.fromstring(content)
            
            # Iterate through preset elements
            for preset_elem in root.findall(".//preset"):
                preset_id = preset_elem.get("id")
                
                # The name is in ContentItem/itemName
                content_item = preset_elem.find(".//ContentItem")
                if content_item is not None:
                    preset_name = content_item.findtext("itemName", "Unknown")
                else:
                    preset_name = "Unknown"
                
                preset = {
                    "id": preset_id,
                    "name": preset_name
                }
                presets.append(preset)
            
            return presets
        
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return []


def main():
    """Display current presets."""
    print("Fetching presets from Soundtouch device...\n")
    
    presets_mgr = SoundtouchPresets()
    presets = presets_mgr.get_presets()
    
    if not presets:
        print("No presets found or unable to fetch presets.")
        return
    
    print(f"{'='*60}")
    print(f"Saved Presets: {len(presets)}")
    print(f"{'='*60}\n")
    
    for preset in presets:
        preset_id = preset.get("id", "?")
        preset_name = preset.get("name", "Unknown")
        print(f"Preset {preset_id}: {preset_name}")
    
    print()


if __name__ == "__main__":
    main()
