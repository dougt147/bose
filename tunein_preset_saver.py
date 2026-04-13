#!/usr/bin/env python3
"""
TuneIn preset saver with built-in station database.
Use known TuneIn station IDs to save presets to Soundtouch.
"""

import requests
import xml.etree.ElementTree as ET
import sys

SPEAKER_IP = "192.168.5.197"
SPEAKER_PORT = 8090

# Common UK/US radio stations with their TuneIn IDs
# Only includes verified working stations (tested 2026-04-10 with real-time stream validation)
STATION_DATABASE = {
    "absolute_80s": ("Absolute 80s", "s333913"),
    "absolute_90s": ("Absolute 90s", "s126362"),
    "absolute_radio": ("Absolute Radio", "s221120"),
    "bbc_2": ("BBC Radio 2", "s24940"),
    "bbc_4": ("BBC Radio 4", "s25419"),
    "bbc_6": ("BBC Radio 6 Music", "s44491"),
    "piccadilly": ("Piccadilly Radio", "s224016"),
    "smooth_uk": ("Smooth UK", "s221117"),
}


def save_preset(station_name, station_id, preset_slot, logo_url=""):
    """Save a TuneIn station as a Soundtouch preset."""
    try:
        import time
        location = f"/v1/playback/station/{station_id}"
        timestamp = str(int(time.time()))
        
        preset_xml = (
            f'<preset id="{preset_slot}" createdOn="{timestamp}" updatedOn="{timestamp}">'
            f'<ContentItem source="TUNEIN" type="stationurl" '
            f'location="{location}" sourceAccount="" isPresetable="true">'
            f'<itemName>{station_name}</itemName>'
            f'<containerArt>{logo_url}</containerArt>'
            f'</ContentItem>'
            f'</preset>'
        )
        
        resp = requests.post(
            f"http://{SPEAKER_IP}:{SPEAKER_PORT}/storePreset",
            data=preset_xml,
            timeout=5
        )
        
        if resp.status_code == 200:
            print(f"✓ Saved '{station_name}' to preset {preset_slot}")
            return True
        else:
            print(f"✗ Failed to save preset: {resp.status_code}")
            print(f"  Response: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ Error saving preset: {e}")
        return False

def list_presets():
    """List all currently saved presets."""
    try:
        resp = requests.get(f"http://{SPEAKER_IP}:{SPEAKER_PORT}/presets", timeout=5)
        root = ET.fromstring(resp.content)
        
        print("\n📻 Current Presets:")
        print("-" * 60)
        for preset in root.findall("preset"):
            preset_id = preset.get("id")
            item = preset.find("ContentItem")
            if item is not None:
                name = item.findtext("itemName", "Unknown")
                source = item.get("source")
                location = item.get("location", "")
                # Extract station ID if TUNEIN
                if source == "TUNEIN" and location.startswith("/v1/playback/station/"):
                    station_id = location.split("/")[-1]
                    print(f"  [{preset_id}] {name}")
                    print(f"       Source: TuneIn ({station_id})")
                else:
                    print(f"  [{preset_id}] {name} ({source})")
        print()
    except Exception as e:
        print(f"Error listing presets: {e}")

def list_available_stations():
    """Show all available stations in database."""
    print("\n📻 Available Stations (by key):")
    print("-" * 60)
    
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
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Save TuneIn radio stations to Soundtouch presets")
        print()
        print("Usage:")
        print("  python tunein_preset_saver.py list              # List saved presets")
        print("  python tunein_preset_saver.py available         # Show all available stations")
        print("  python tunein_preset_saver.py save KEY SLOT     # Save a station to preset slot")
        print()
        print("Examples:")
        print("  python tunein_preset_saver.py available")
        print("  python tunein_preset_saver.py save bbc_2 4")
        print("  python tunein_preset_saver.py save smooth_uk 5")
        print()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_presets()
    
    elif command == "available":
        list_available_stations()
    
    elif command == "save" and len(sys.argv) >= 4:
        station_key = sys.argv[2].lower()
        preset_slot = sys.argv[3]
        
        if station_key not in STATION_DATABASE:
            print(f"❌ Station key '{station_key}' not found")
            print("Use 'python tunein_preset_saver.py available' to see all options")
            sys.exit(1)
        
        station_name, station_id = STATION_DATABASE[station_key]
        print(f"💾 Saving '{station_name}' to preset {preset_slot}...\n")
        
        if save_preset(station_name, station_id, preset_slot):
            import time
            time.sleep(2)
            list_presets()
        else:
            print("Failed to save preset")
    
    else:
        print("❌ Invalid command or arguments")
        sys.exit(1)
