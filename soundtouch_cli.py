"""
Interactive CLI for controlling Bose Soundtouch 20 speaker.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List, Tuple
import time

# TuneIn station database (station_key -> (station_name, station_id))
# All stations verified playable (discovered 2026-04-12 with real-time stream validation)
STATION_DATABASE = {
    "bbc_1fm": ("BBC Radio 1", "s26240"),
    "bbc_2": ("BBC Radio 2", "s24940"),
    "bbc_3": ("BBC Radio 3", "s25418"),
    "bbc_4": ("BBC Radio 4", "s25419"),
    "bbc_5live": ("BBC Radio 5 Live", "s25420"),
    "bbc_6": ("BBC Radio 6 Music", "s44491"),
    "bbc_world": ("BBC World Service", "s25447"),
    "absolute_80s": ("Absolute 80s", "s333913"),
    "absolute_90s": ("Absolute 90s", "s126362"),
    "absolute_radio": ("Absolute Radio", "s221120"),
    "absolute_classic": ("Absolute Classic Rock", "s309881"),
    "absolute_classic_hits": ("Absolute Classic Hits", "s216896"),
    "absolute_xtreme": ("Absolute Xtreme", "s231046"),
    "heart": ("Heart", "s25421"),
    "heart_80s": ("Heart 80s", "s307922"),
    "heart_90s": ("Heart 90s", "s307924"),
    "capital_fm": ("Capital FM", "s25426"),
    "capital_xtra": ("Capital XTRA", "s30954"),
    "smooth_uk": ("Smooth UK", "s221117"),
    "piccadilly": ("Piccadilly Radio", "s224016"),
    "talksport": ("TalkSPORT", "s24914"),
    "classic_fm": ("Classic FM", "s24933"),
    "sirius_siriusxm": ("SiriusXM", "s83833"),
}


class SoundtouchCLI:
    """Interactive CLI controller for Soundtouch device."""
    
    def __init__(self, ip: str = "192.168.5.197", port: int = 8090):
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}"
        self.timeout = 5
        self.presets: List[Dict] = []
        self.load_presets()
    
    def load_presets(self) -> None:
        """Load available presets."""
        try:
            response = requests.get(f"{self.base_url}/presets", timeout=self.timeout)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                self.presets = []
                for preset_elem in root.findall(".//preset"):
                    preset_id = preset_elem.get("id")
                    content_item = preset_elem.find(".//ContentItem")
                    if content_item is not None:
                        preset_name = content_item.findtext("itemName", "Unknown")
                        content_item_xml = ET.tostring(content_item, encoding='utf-8').decode()
                    else:
                        preset_name = "Unknown"
                        content_item_xml = None
                    self.presets.append({
                        "id": preset_id,
                        "name": preset_name,
                        "content_item_xml": content_item_xml
                    })
        except Exception as e:
            print(f"Error loading presets: {e}")
    
    def get_volume(self) -> Optional[int]:
        """Get current volume."""
        try:
            response = requests.get(f"{self.base_url}/volume", timeout=self.timeout)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                volume = root.findtext("actualvolume")
                return int(volume) if volume else None
            return None
        except:
            return None
    
    def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)."""
        if not 0 <= volume <= 100:
            print("❌ Volume must be between 0 and 100")
            return False
        
        try:
            body = f"<volume>{volume}</volume>"
            response = requests.post(f"{self.base_url}/volume", data=body, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def get_status(self) -> Optional[Dict]:
        """Get playback status."""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=self.timeout)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                return {
                    "state": root.findtext("state", "Unknown"),
                    "source": root.findtext("source", "Unknown"),
                    "contentItem": root.findtext(".//itemName", "N/A"),
                }
            return None
        except:
            return None
    
    def play(self) -> bool:
        """Play/Resume."""
        return self._send_key("PLAY")
    
    def pause(self) -> bool:
        """Pause."""
        return self._send_key("PAUSE")
    
    def next_track(self) -> bool:
        """Next track."""
        return self._send_key("NEXT")
    
    def previous_track(self) -> bool:
        """Previous track."""
        return self._send_key("PREV")
    
    def play_preset(self, preset_id: int) -> bool:
        """Play preset by posting its ContentItem to /select."""
        try:
            preset = next((p for p in self.presets if p["id"] == str(preset_id)), None)
            if not preset or not preset.get("content_item_xml"):
                print(f"❌ Preset {preset_id} not found")
                return False
            response = requests.post(
                f"{self.base_url}/select",
                data=preset["content_item_xml"],
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def save_tunein_preset(self, station_name: str, station_id: str, preset_slot: int) -> bool:
        """Save a TuneIn station as a preset."""
        try:
            import time
            location = f"/v1/playback/station/{station_id}"
            timestamp = str(int(time.time()))
            
            preset_xml = (
                f'<preset id="{preset_slot}" createdOn="{timestamp}" updatedOn="{timestamp}">'
                f'<ContentItem source="TUNEIN" type="stationurl" '
                f'location="{location}" sourceAccount="" isPresetable="true">'
                f'<itemName>{station_name}</itemName>'
                f'<containerArt></containerArt>'
                f'</ContentItem>'
                f'</preset>'
            )
            response = requests.post(
                f"{self.base_url}/storePreset",
                data=preset_xml,
                timeout=self.timeout
            )
            if response.status_code == 200:
                time.sleep(1)
                self.load_presets()
                return True
            else:
                print(f"  Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def list_tunein_stations(self) -> None:
        """Display available TuneIn stations."""
        print("\n" + "="*70)
        print("AVAILABLE TUNEIN STATIONS")
        print("="*70)
        
        categories = {}
        for key, (name, sid) in STATION_DATABASE.items():
            category = key.split("_")[0].upper()
            if category not in categories:
                categories[category] = []
            categories[category].append((key, name, sid))
        
        for cat in sorted(categories.keys()):
            print(f"\n{cat}:")
            for key, name, sid in sorted(categories[cat]):
                print(f"  {key:20} → {name:30} ({sid})")
        
        print("\n" + "="*70)
    
    def _send_key(self, key: str) -> bool:
        """Send key command."""
        try:
            body = f"<key state='press' sender='Gabbo'>{key}</key>"
            response = requests.post(f"{self.base_url}/key", data=body, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def display_status(self) -> None:
        """Display current device status."""
        print("\n" + "="*60)
        print("SOUNDTOUCH STATUS")
        print("="*60)
        
        # Volume
        vol = self.get_volume()
        print(f"Volume: {vol}%") if vol is not None else print("Volume: Unable to fetch")
        
        # Playback status
        status = self.get_status()
        if status:
            print(f"State: {status['state']}")
            print(f"Source: {status['source']}")
            if status['contentItem'] != "N/A":
                print(f"Playing: {status['contentItem']}")
        
        print("="*60 + "\n")
    
    def display_menu(self) -> None:
        """Display main menu."""
        print("\n" + "="*60)
        print("SOUNDTOUCH CONTROLLER")
        print("="*60)
        print("\n📻 PLAYBACK CONTROL:")
        print("  [P]lay / [Pa] Pause")
        print("  [N]ext track / [Pr] Previous")
        
        print("\n🎙️  PRESETS:")
        for preset in self.presets:
            print(f"  [{preset['id']}] {preset['name']}")
        
        print("\n🔊 VOLUME:")
        vol = self.get_volume()
        print(f"  [V] Set volume (current: {vol}%)")
        print(f"  [+] Volume up / [-] Volume down")
        
        print("\n📊 STATUS:")
        print("  [S] Show status")
        
        print("\n� MANAGE PRESETS:")
        print("  [A] Add new TuneIn station preset")
        print("  [L] List available TuneIn stations")
        
        print("\n�💡 OTHER:")
        print("  [R] Refresh presets")
        print("  [Q] Quit")
        print("="*60 + "\n")
    
    def run(self) -> None:
        """Run interactive CLI."""
        print("\n✅ Connected to Soundtouch at " + self.ip)
        
        while True:
            self.display_menu()
            choice = input("Enter command: ").strip().lower()
            
            if choice == 'q':
                print("\n👋 Goodbye!")
                break
            
            elif choice == 's':
                self.display_status()
            
            elif choice == 'p':
                if self.play():
                    print("▶️  Play")
                else:
                    print("❌ Failed to play")
            
            elif choice == 'pa':
                if self.pause():
                    print("⏸️  Paused")
                else:
                    print("❌ Failed to pause")
            
            elif choice == 'n':
                if self.next_track():
                    print("⏭️  Next")
                else:
                    print("❌ Failed to skip")
            
            elif choice == 'pr':
                if self.previous_track():
                    print("⏮️  Previous")
                else:
                    print("❌ Failed to go back")
            
            elif choice == 'v':
                try:
                    vol = int(input("Enter volume (0-100): "))
                    if self.set_volume(vol):
                        print(f"✅ Volume set to {vol}%")
                    else:
                        print("❌ Failed to set volume")
                except ValueError:
                    print("❌ Invalid volume value")
            
            elif choice == '+':
                vol = self.get_volume()
                if vol is not None:
                    new_vol = min(100, vol + 5)
                    if self.set_volume(new_vol):
                        print(f"🔊 Volume: {vol}% → {new_vol}%")
            
            elif choice == '-':
                vol = self.get_volume()
                if vol is not None:
                    new_vol = max(0, vol - 5)
                    if self.set_volume(new_vol):
                        print(f"🔇 Volume: {vol}% → {new_vol}%")
            
            elif choice == 'r':
                print("🔄 Refreshing presets...")
                self.load_presets()
                print(f"✅ Loaded {len(self.presets)} presets")
            
            elif choice == 'l':
                self.list_tunein_stations()
            
            elif choice == 'a':
                print("\n" + "="*60)
                print("ADD NEW TUNEIN PRESET")
                print("="*60)
                station_key = input("\nEnter station key (e.g., bbc_2, smooth_uk, jazz_fm): ").strip().lower()
                
                if station_key not in STATION_DATABASE:
                    print(f"❌ Station key '{station_key}' not found")
                    print("Use [L] option to see available stations")
                else:
                    station_name, station_id = STATION_DATABASE[station_key]
                    print(f"\nSelected: {station_name}")
                    
                    try:
                        preset_slot = int(input("Enter preset slot (1-6): ").strip())
                        if 1 <= preset_slot <= 6:
                            print(f"💾 Saving '{station_name}' to preset {preset_slot}...")
                            if self.save_tunein_preset(station_name, station_id, preset_slot):
                                print(f"✅ Saved '{station_name}' to preset {preset_slot}")
                            else:
                                print("❌ Failed to save preset")
                        else:
                            print("❌ Preset slot must be 1-6")
                    except ValueError:
                        print("❌ Invalid preset slot")
            
            elif choice in [str(p['id']) for p in self.presets]:
                preset_id = choice
                preset_name = next((p['name'] for p in self.presets if p['id'] == preset_id), "Unknown")
                if self.play_preset(int(preset_id)):
                    print(f"🎶 Playing: {preset_name}")
                else:
                    print("❌ Failed to play preset")
            
            else:
                print("❌ Unknown command")
            
            input("\nPress Enter to continue...")


def main():
    """Main entry point."""
    try:
        cli = SoundtouchCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
