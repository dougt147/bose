#!/usr/bin/env python3
"""
Query current presets from Bose SoundTouch speaker and display their URLs.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
from pathlib import Path

SPEAKER_IP = "192.168.5.197"
SPEAKER_PORT = 8090
BASE_URL = f"http://{SPEAKER_IP}:{SPEAKER_PORT}"


def get_presets() -> List[Dict]:
    """Fetch presets from speaker and extract URL information."""
    try:
        response = requests.get(f"{BASE_URL}/presets", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to fetch presets: HTTP {response.status_code}")
            return []

        presets = []
        root = ET.fromstring(response.content)
        
        for preset_elem in root.findall(".//preset"):
            preset_id = preset_elem.get("id")
            content_item = preset_elem.find(".//ContentItem")
            
            if content_item is not None:
                preset_name = content_item.findtext("itemName", "Unknown")
                source = content_item.get("source", "Unknown")
                location = content_item.get("location", "N/A")
                source_account = content_item.get("sourceAccount", "")
                content_type = content_item.get("type", "Unknown")
                
                presets.append({
                    "id": preset_id,
                    "name": preset_name,
                    "source": source,
                    "location": location,
                    "source_account": source_account,
                    "type": content_type,
                })
        
        return presets
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to speaker at {SPEAKER_IP}:{SPEAKER_PORT}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def display_presets(presets: List[Dict]) -> None:
    """Display presets with their URLs."""
    if not presets:
        print("No presets found or speaker unreachable.")
        return

    print("\n" + "="*90)
    print("SOUNDTOUCH PRESETS - URL INFORMATION")
    print("="*90)
    print(f"{'ID':>3} {'Name':<25} {'Source':<10} {'Type':<12} {'Location/URL':<40}")
    print("-"*90)
    
    for preset in presets:
        preset_id = preset["id"]
        name = preset["name"][:24]
        source = preset["source"]
        ptype = preset["type"]
        location = preset["location"]
        
        print(f"{preset_id:>3} {name:<25} {source:<10} {ptype:<12} {location:<40}")
    
    print("="*90)
    print(f"\nTotal presets: {len(presets)}\n")


def save_to_file(presets: List[Dict], filename: str = "preset_urls.txt") -> None:
    """Save preset URLs to a text file."""
    try:
        with open(filename, "w") as f:
            f.write("SOUNDTOUCH PRESETS - URL INFORMATION\n")
            f.write("="*90 + "\n\n")
            
            for preset in presets:
                f.write(f"Preset {preset['id']}: {preset['name']}\n")
                f.write(f"  Source: {preset['source']}\n")
                f.write(f"  Type: {preset['type']}\n")
                f.write(f"  Location: {preset['location']}\n")
                if preset['source_account']:
                    f.write(f"  Account: {preset['source_account']}\n")
                f.write("\n")
        
        print(f"✅ Preset URLs saved to {filename}")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")


def main():
    """Main entry point."""
    print("Querying SoundTouch presets...")
    presets = get_presets()
    
    if presets:
        display_presets(presets)
        save_to_file(presets)
    else:
        print("Failed to retrieve presets.")


if __name__ == "__main__":
    main()
