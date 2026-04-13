#!/usr/bin/env python3
"""
Find all playable stations on Bose Soundtouch speaker and save to file.
Run as a background task to discover which TuneIn stations work.
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Set
from pathlib import Path

SPEAKER_IP = "192.168.5.197"
SPEAKER_PORT = 8090
OUTPUT_FILE = Path("playable_stations.json")
LOG_FILE = Path("station_discovery.log")

# Comprehensive TuneIn station IDs to test
# These are common stations that may be playable - we'll test each one
STATIONS_TO_TEST = {
    # BBC
    "bbc_1fm": ("BBC Radio 1", "s26240"),
    "bbc_2": ("BBC Radio 2", "s24940"),
    "bbc_3": ("BBC Radio 3", "s25418"),
    "bbc_4": ("BBC Radio 4", "s25419"),
    "bbc_5live": ("BBC Radio 5 Live", "s25420"),
    "bbc_6": ("BBC Radio 6 Music", "s44491"),
    "bbc_world": ("BBC World Service", "s25447"),
    
    # Absolute
    "absolute_80s": ("Absolute 80s", "s333913"),
    "absolute_90s": ("Absolute 90s", "s126362"),
    "absolute_radio": ("Absolute Radio", "s221120"),
    "absolute_classic": ("Absolute Classic Rock", "s309881"),
    "absolute_classic_hits": ("Absolute Classic Hits", "s216896"),
    "absolute_xtreme": ("Absolute Xtreme", "s231046"),
    
    # Heart
    "heart": ("Heart", "s25421"),
    "heart_80s": ("Heart 80s", "s307922"),
    "heart_90s": ("Heart 90s", "s307924"),
    
    # Capital
    "capital_fm": ("Capital FM", "s25426"),
    "capital_xtra": ("Capital XTRA", "s30954"),
    
    # Other UK
    "smooth_uk": ("Smooth UK", "s221117"),
    "piccadilly": ("Piccadilly Radio", "s224016"),
    "talksport": ("TalkSPORT", "s24914"),
    "classic_fm": ("Classic FM", "s24933"),
    
    # US
    "sirius_siriusxm": ("SiriusXM", "s83833"),
}


class StationDiscovery:
    def __init__(self, speaker_ip: str = SPEAKER_IP, port: int = SPEAKER_PORT):
        self.ip = speaker_ip
        self.port = port
        self.base_url = f"http://{speaker_ip}:{port}"
        self.timeout = 5
        self.playable_stations: List[Dict] = []
        self.failed_stations: List[str] = []
    
    def log(self, message: str) -> None:
        """Log message to file and print."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(LOG_FILE, "a") as f:
            f.write(log_msg + "\n")
    
    def test_station(self, station_key: str, station_name: str, station_id: str) -> bool:
        """Test if a station is playable on the speaker."""
        try:
            location = f"/v1/playback/station/{station_id}"
            
            # Build ContentItem XML to test
            test_xml = (
                f'<ContentItem source="TUNEIN" type="stationurl" '
                f'location="{location}" sourceAccount="" isPresetable="true">'
                f'<itemName>{station_name}</itemName>'
                f'</ContentItem>'
            )
            
            # Try to play the station
            response = requests.post(
                f"{self.base_url}/select",
                data=test_xml,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.log(f"✓ PLAYABLE: {station_name} ({station_id})")
                self.playable_stations.append({
                    "key": station_key,
                    "name": station_name,
                    "station_id": station_id,
                    "tested_at": datetime.now().isoformat(),
                    "status": "playable"
                })
                return True
            else:
                self.log(f"✗ NOT PLAYABLE: {station_name} (HTTP {response.status_code})")
                self.failed_stations.append(station_key)
                return False
                
        except requests.exceptions.Timeout:
            self.log(f"✗ TIMEOUT: {station_name}")
            self.failed_stations.append(station_key)
            return False
        except Exception as e:
            self.log(f"✗ ERROR testing {station_name}: {e}")
            self.failed_stations.append(station_key)
            return False
    
    def test_connection(self) -> bool:
        """Test if speaker is reachable."""
        try:
            response = requests.get(f"{self.base_url}/info", timeout=self.timeout)
            return response.status_code == 200
        except:
            return False
    
    def discover_all(self) -> None:
        """Test all stations and save results."""
        self.log(f"\n{'='*70}")
        self.log("STARTING PLAYABLE STATION DISCOVERY")
        self.log(f"Target: {self.ip}:{self.port}")
        self.log(f"Stations to test: {len(STATIONS_TO_TEST)}")
        self.log(f"{'='*70}\n")
        
        # Test connection
        if not self.test_connection():
            self.log("ERROR: Cannot reach speaker at {self.ip}:{self.port}")
            return
        
        self.log("✓ Speaker is reachable\n")
        self.log("Testing stations...\n")
        
        total = len(STATIONS_TO_TEST)
        for idx, (key, (name, sid)) in enumerate(STATIONS_TO_TEST.items(), 1):
            self.log(f"[{idx}/{total}] Testing: {name}...")
            self.test_station(key, name, sid)
            time.sleep(0.5)  # Small delay between tests to avoid overwhelming speaker
        
        self.save_results()
    
    def save_results(self) -> None:
        """Save results to JSON file."""
        results = {
            "discovery_timestamp": datetime.now().isoformat(),
            "speaker_ip": self.ip,
            "speaker_port": self.port,
            "total_tested": len(STATIONS_TO_TEST),
            "playable_count": len(self.playable_stations),
            "failed_count": len(self.failed_stations),
            "playable_stations": self.playable_stations,
            "failed_stations": self.failed_stations,
        }
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)
        
        self.log(f"\n{'='*70}")
        self.log("DISCOVERY COMPLETE")
        self.log(f"{'='*70}")
        self.log(f"✓ Playable stations: {len(self.playable_stations)}")
        self.log(f"✗ Failed stations: {len(self.failed_stations)}")
        self.log(f"📄 Results saved to: {OUTPUT_FILE.absolute()}")
        self.log(f"📝 Log saved to: {LOG_FILE.absolute()}")
        self.log(f"{'='*70}\n")


def main():
    """Run discovery task."""
    discovery = StationDiscovery()
    discovery.discover_all()


if __name__ == "__main__":
    main()
