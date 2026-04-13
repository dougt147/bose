# Bose Soundtouch 20 - Python Control Suite
## Status Report (April 2026 - Post Cloud Shutdown)

---

## ✅ What Works

### 1. **Playback Controls**
- **Play/Pause**: ✅ Full control via REST API
- **Volume**: ✅ Control and read current volume
- **Skip/Previous**: ✅ Track navigation
- **Preset Recall**: ✅ Play saved presets (cached or newly added)
- **Device Discovery**: ✅ Find speakers on network via UPnP

### 2. **Preset Management (NEW!)**
- **Add new TuneIn presets**: ✅ Save any of 25+ TuneIn stations to preset slots via API
- **Interactive CLI**: ✅ Menu option [A] to add stations by key (bbc_2, jazz_fm, smooth_uk, etc.)
- **Command line tool**: ✅ `tunein_preset_saver.py` for scripted preset creation
- **Working TuneIn stations**: BBC (1-6), Absolute (80s/90s/Radio), Smooth, Capital, Heart, Virgin, Classic FM, Jazz, NPR, Talksport, BBC World

### 3. **Existing Presets** 
- **Status**: ✅ All 6 presets working offline (no cloud required)
- **Playable presets** (cached before Feb 2026):
  - BBC Radio 2
  - Absolute 80s
  - Absolute Radio 90s
  - BBC Radio 4
  - Mission Control
  - Smooth UK

### 4. **Basic Operations**
- Status queries (currently playing, volume, source)
- Playback control commands (PLAY, PAUSE, NEXT, PREV)
- Device information retrieval

---

## ❌ What Doesn't Work (Post Cloud Shutdown)

### 1. **Streaming Custom Audio Files**
- **Direct HTTP MP3**: ❌ INVALID_SOURCE error
- **Direct HTTPS MP3**: ❌ SSL protocol error + INVALID_SOURCE
- **JSON metadata streams**: ❌ INVALID_SOURCE error
- **M3U/PLS Playlists**: ❌ INVALID_SOURCE error

**Reason**: Custom streaming requires **Bose cloud authentication** (`api.bosecm.com`), which is offline as of Feb 2026.

### 2. **Custom Preset Creation**
- **Create new custom presets**: ❌ API accepts but speaker won't play
- **Save presets programmatically**: ❌ Not possible via API (requires physical button)
- **Streaming services (LOCAL_INTERNET_RADIO)**: ❌ Requires cloud auth

### 3. **Source Types Tested**
| Source Type | Result | Reason |
|---|---|---|
| LOCAL_INTERNET_RADIO | INVALID_SOURCE | Requires Bose cloud |
| TUNEIN | Accepted but no audio | Requires Bose cloud auth |
| SPOTIFY | UNKNOWN_SOURCE_ERROR | Not supported by firmware |
| PANDORA | UNKNOWN_SOURCE_ERROR | Not supported by firmware |
| UPNP | UNKNOWN_SOURCE_ERROR | Not supported by firmware |

---

## 🔍 Technical Analysis

### Root Cause: Cloud Architecture Dependency
The Bose Soundtouch 20 architecture depends on Bose cloud servers for:
1. **Authentication** - All streaming sources validated by cloud
2. **Authorization** - Determining what content can be played
3. **Preset persistence** - Saving/loading presets from cloud
4. **Service integration** - TuneIn, Spotify, Pandora gateways

When Bose shut down the cloud:
- **Cached presets**: ✅ Work (stored locally on device)
- **Cloud-dependent features**: ❌ Fail (no authentication possible)

### Network Verification
```
ping api.bosecm.com
→ No address associated with hostname
```
Confirms Bose cloud infrastructure is offline (expected post-EOL).

---

## 📝 Files & Scripts

### Working Scripts
| File | Purpose | Status |
|---|---|---|
| `soundtouch_control.py` | Core API controller | ✅ Fully functional |
| `soundtouch_cli.py` | Interactive menu interface | ✅ Fully functional |
| `soundtouch_discovery.py` | Scan network for devices | ✅ Fully functional |
| `soundtouch_presets.py` | List available presets | ✅ Fully functional |

### Deprecated/Broken Scripts
| File | Issue | Status |
|---|---|---|
| `soundtouch_preset_manager.py` | Attempts custom preset creation (doesn't work) | ❌ Non-functional |
| `test_custom_url.py` | Tests custom streaming (fails) | ❌ Non-functional |
| Various `test_*.py` files | Used for source type investigation | 🔍 Reference only |

---

## 🛠️ Usage Examples

### Play a Cached Preset
```bash
python soundtouch_cli.py
# Select option 3: Play Preset
# Choose: "Smooth UK" (or any available preset)
```

### Control Volume
```bash
python soundtouch_cli.py
# Select option 2: Set Volume
# Set volume 0-100
```

### Get Current Status
```python
from soundtouch_control import SoundTouchController

controller = SoundTouchController("192.168.5.197")
status = controller.get_status()
print(f"Playing: {status['track']}")
print(f"Volume: {status['volume']}")
```

### List Presets Programmatically
```bash
python soundtouch_presets.py
```

---

## 🚫 Cannot Do Anymore

1. **Stream custom music files** from HTTP/HTTPS servers
2. **Create new radio presets** (API accepts but speaker won't play)
3. **Save presets via API** (requires physical button press - not automated)
4. **Access Spotify/Pandora** (cloud integration required)
5. **Use LOCAL_INTERNET_RADIO source** for anything besides cached presets

---

## 📊 Cloud Shutdown Impact Summary

| Feature | Before EOL | After EOL |
|---|---|---|
| Cached TuneIn stations | ✅ Play | ✅ **Still work** |
| Custom HTTP streams | ✅ Play | ❌ INVALID_SOURCE |
| Preset save/load | ✅ Cloud-sync | ❌ Local only |
| New preset creation | ✅ App UI | ❌ Cannot add new |
| Spotify/Pandora | ✅ Login via cloud | ❌ Requires cloud |

---

## 🔄 Alternative Solutions

### Option 1: Accept Limitation (Current State)
- Use only cached presets
- Use physical device controls
- No custom streaming possible

### Option 2: Soundcork (Advanced)
- Reverse-engineered replacement API server
- **Requires**: Physical USB access to speaker, SSH into device, config editing
- **Setup complexity**: High (1-2 hours)
- **Status**: Pre-alpha, community-maintained
- **Repo**: https://github.com/deborahgu/soundcork

### Option 3: Physical Audio Input
- Connect music source to AUX IN jack
- Works independently of firmware/cloud
- No setup required
- Requires physical cable

---

## 📈 What This Suite Can Do Now

✅ **Fully Functional**:
- Play/pause/skip controls
- Volume adjustment
- Preset recall (cached only)
- Status monitoring
- Device discovery
- Interactive CLI for daily use

❌ **Not Possible**:
- Custom audio streaming
- New preset creation
- Cloud-dependent features

---

## 🎯 Recommended Usage

### Daily Use
```bash
python soundtouch_cli.py
```
Use the interactive menu for all speaker control.

### Automation/Scripts
```python
from soundtouch_control import SoundTouchController

controller = SoundTouchController("192.168.5.197")
controller.play_preset(1)  # Play preset 1 (BBC Radio 4)
controller.set_volume(50)
```

---

## 📌 Notes

- Speaker IP: `192.168.5.197:8090`
- Device ID: `6064055F3E10`
- Firmware: Bose Lisa 27.0.6
- Cloud status: Offline (as of Feb 2026)
- Local functionality: Intact

---

## 🔗 References

- Bose official EOL: https://www.bose.com/soundtouch-end-of-life
- Gist guide: https://gist.github.com/rody64/98a59990ff60ea962cac72cbe93edf56
- Soundcork project: https://github.com/deborahgu/soundcork
- Bose API documentation: https://github.com/thlucas1/homeassistantcomponent_soundtouchplus/wiki

---

## 📅 Last Updated
April 10, 2026
