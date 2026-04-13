"""
Create and save custom presets to Bose Soundtouch device.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List
import re
import argparse


class PresetManager:
    """Manage custom presets for Soundtouch device."""
    
    def __init__(self, ip: str = "192.168.5.197", port: int = 8090):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.timeout = 5
    
    def get_presets(self) -> List[Dict]:
        """Get current presets."""
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
                    else:
                        preset_name = "Unknown"
                    presets.append({
                        "id": preset_id,
                        "name": preset_name
                    })
                return presets
            return []
        except Exception as e:
            print(f"Error getting presets: {e}")
            return []
    
    def create_preset_from_tunein(self, station_name: str, station_id: str, preset_slot: int = None) -> bool:
        """
        Create preset from TuneIn station ID.
        
        Args:
            station_name: Display name for the preset
            station_id: TuneIn station ID (e.g., 's254741' for Radio X UK)
            preset_slot: Which preset slot to save to (1-6, optional)
        
        Returns:
            True if successful
        """
        try:
            # Build ContentItem XML for TuneIn station
            content_item_xml = (
                f'<ContentItem source="TUNEIN" type="stationurl" '
                f'location="/v1/playback/station/{station_id}" '
                f'sourceAccount="" isPresetable="true">'
                f'<itemName>{station_name}</itemName>'
                f'<containerArt></containerArt>'
                f'</ContentItem>'
            )
            
            print(f"Creating preset: {station_name}")
            
            # Play it first (this adds it as current)
            response = requests.post(
                f"{self.base_url}/select",
                data=content_item_xml,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to select preset: {response.status_code}")
                return False
            
            # Note about preset saving
            if preset_slot and 1 <= preset_slot <= 6:
                print(f"\n✅ Stream is now PLAYING on your speaker!")
                print(f"\n📌 TO SAVE TO PRESET SLOT {preset_slot}:")
                print(f"   1. Hold down preset button {preset_slot} on your speaker")
                print(f"   2. Hold for 2-3 seconds until you hear a beep")
                print(f"   3. Release\n")
                return True
            else:
                print(f"\n✅ Stream {station_name} is now playing!")
                return True
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def create_preset_from_url(self, station_name: str, stream_url: str, preset_slot: int = None) -> bool:
        """
        Create preset from direct stream URL.
        
        Args:
            station_name: Display name for the preset
            stream_url: Direct stream URL (e.g., http://stream.example.com/station)
            preset_slot: Which preset slot to save to (1-6, optional)
        
        Returns:
            True if successful
        """
        try:
            # Build ContentItem XML for custom URL using LOCAL_INTERNET_RADIO source
            content_item_xml = (
                f'<ContentItem source="LOCAL_INTERNET_RADIO" type="stationurl" '
                f'location="{stream_url}" '
                f'sourceAccount="" isPresetable="true">'
                f'<itemName>{station_name}</itemName>'
                f'<containerArt></containerArt>'
                f'</ContentItem>'
            )
            
            print(f"Creating preset: {station_name}")
            
            # Try to select it
            response = requests.post(
                f"{self.base_url}/select",
                data=content_item_xml,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to create preset: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            # Note about preset saving
            if preset_slot and 1 <= preset_slot <= 6:
                print(f"\n✅ Stream is now PLAYING on your speaker!")
                print(f"\n📌 TO SAVE TO PRESET SLOT {preset_slot}:")
                print(f"   1. Hold down preset button {preset_slot} on your speaker")
                print(f"   2. Hold for 2-3 seconds until you hear a beep")
                print(f"   3. Release\n")
                return True
            else:
                print(f"\n✅ Stream {station_name} is now playing!")
                return True
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def parse_tunein_url(self, url: str) -> Optional[Dict]:
        """
        Parse TuneIn share URL to extract station ID.
        
        Supports formats:
        - https://tunein.com/radio/Station-Name-s123456
        - https://tunein.com/station/s123456
        
        Returns:
            Dict with 'station_id' and 'station_name' or None
        """
        # Extract station ID from URL
        match = re.search(r's(\d+)', url)
        if not match:
            print("❌ Could not find station ID in URL")
            return None
        
        station_id = f"s{match.group(1)}"
        
        # Extract name from URL
        name_match = re.search(r'/radio/([^/\?]+)', url)
        if name_match:
            # Clean up the name
            station_name = name_match.group(1).replace('-', ' ')
        else:
            station_name = f"TuneIn Station {station_id}"
        
        return {
            "station_id": station_id,
            "station_name": station_name
        }
    
    def display_presets(self) -> None:
        """Display current presets."""
        presets = self.get_presets()
        
        if not presets:
            print("\n❌ No presets found")
            return
        
        print(f"\n{'='*60}")
        print(f"Saved Presets: {len(presets)}")
        print(f"{'='*60}\n")
        
        for preset in presets:
            print(f"Preset {preset['id']}: {preset['name']}")


def interactive_menu():
    """Interactive preset creation menu."""
    mgr = PresetManager()
    
    while True:
        print("\n" + "="*60)
        print("SOUNDTOUCH PRESET MANAGER")
        print("="*60)
        print("\n[1] View current presets")
        print("[2] Create preset from TuneIn station ID")
        print("[3] Create preset from TuneIn share URL")
        print("[4] Create preset from custom stream URL")
        print("[5] Exit")
        print()
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            mgr.display_presets()
        
        elif choice == '2':
            print("\nExample: Radio X UK has ID 's254741'")
            station_id = input("Enter TuneIn station ID (e.g., s123456): ").strip()
            station_name = input("Enter preset name: ").strip()
            slot = input("Enter preset slot (1-6, or press Enter to skip): ").strip()
            
            preset_slot = None
            if slot:
                try:
                    preset_slot = int(slot)
                    if not 1 <= preset_slot <= 6:
                        print("❌ Slot must be 1-6")
                        continue
                except ValueError:
                    print("❌ Invalid slot number")
                    continue
            
            if station_id and station_name:
                mgr.create_preset_from_tunein(station_name, station_id, preset_slot)
            else:
                print("❌ Invalid input")
        
        elif choice == '3':
            print("\nExample: https://tunein.com/radio/Radio-X-UK-s254741")
            url = input("Enter TuneIn share URL: ").strip()
            
            parsed = mgr.parse_tunein_url(url)
            if parsed:
                print(f"✓ Found: {parsed['station_name']} (ID: {parsed['station_id']})")
                confirm = input("Create this preset? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    slot = input("Enter preset slot (1-6, or press Enter to skip): ").strip()
                    preset_slot = None
                    if slot:
                        try:
                            preset_slot = int(slot)
                            if not 1 <= preset_slot <= 6:
                                print("❌ Slot must be 1-6")
                                input("\nPress Enter to continue...")
                                continue
                        except ValueError:
                            print("❌ Invalid slot number")
                            input("\nPress Enter to continue...")
                            continue
                    
                    mgr.create_preset_from_tunein(
                        parsed['station_name'],
                        parsed['station_id'],
                        preset_slot
                    )
            else:
                print("❌ Could not parse URL")
        
        elif choice == '4':
            print("\nExample: https://stream.example.com/mystation.pls")
            stream_url = input("Enter stream URL: ").strip()
            station_name = input("Enter preset name: ").strip()
            slot = input("Enter preset slot (1-6, or press Enter to skip): ").strip()
            
            preset_slot = None
            if slot:
                try:
                    preset_slot = int(slot)
                    if not 1 <= preset_slot <= 6:
                        print("❌ Slot must be 1-6")
                        continue
                except ValueError:
                    print("❌ Invalid slot number")
                    continue
            
            if stream_url and station_name:
                mgr.create_preset_from_url(station_name, stream_url, preset_slot)
            else:
                print("❌ Invalid input")
        
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Create and manage Soundtouch presets"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Launch interactive menu"
    )
    parser.add_argument(
        "--tunein",
        nargs=2,
        metavar=("NAME", "STATION_ID"),
        help="Create TuneIn preset (e.g., --tunein 'Radio X' s254741)"
    )
    parser.add_argument(
        "--url",
        nargs=2,
        metavar=("NAME", "STREAM_URL"),
        help="Create preset from URL (e.g., --url 'My Station' http://stream.example.com/live)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current presets"
    )
    parser.add_argument(
        "--slot",
        type=int,
        metavar="N",
        help="Preset slot to save to (1-6)"
    )
    
    args = parser.parse_args()
    
    mgr = PresetManager()
    
    if args.interactive or not any([args.tunein, args.url, args.list]):
        interactive_menu()
    
    elif args.list:
        mgr.display_presets()
    
    elif args.tunein:
        name, station_id = args.tunein
        mgr.create_preset_from_tunein(name, station_id, args.slot)
    
    elif args.url:
        name, stream_url = args.url
        mgr.create_preset_from_url(name, stream_url, args.slot)


if __name__ == "__main__":
    main()
