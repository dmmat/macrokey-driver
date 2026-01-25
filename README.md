# Macro Keyboard Driver

Cross-platform driver for configuring a 6-button macro keyboard with rotary encoder.

## Hardware

| Property | Value |
|----------|-------|
| Vendor ID | `1189` (Acer Communications & Multimedia) |
| Product ID | `8890` |
| Buttons | 6 |
| Rotary Encoder | 1 (with click and rotation) |
| Connection | USB |

## Features

- Configure any of the 6 buttons to any key
- Configure rotary knob click and rotation directions
- Support for modifier keys (Ctrl, Shift, Alt, Win/Cmd)
- Configuration stored in device firmware (persists across reboots)
- Works on Linux, macOS, and Windows (via WSL2)

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd mcrokeydriver

# Install pyusb (required for configuration)
pip install pyusb
```

## Quick Start (Windows + WSL2)

### 1. Attach keyboard to WSL2 for configuration

Open **PowerShell as Administrator**:

```powershell
# List USB devices to find your keyboard
usbipd list

# Bind the device (first time only, may need --force)
usbipd bind --busid <BUSID> --force

# Attach to WSL2
usbipd attach --wsl --busid <BUSID>
```

### 2. Configure your buttons in WSL2

```bash
# Set button 1 to 'z'
sudo python3 driver.py set button1 z

# Set button 2 to Ctrl+C (copy)
sudo python3 driver.py set button2 c --mod ctrl

# Set button 3 to Ctrl+V (paste)
sudo python3 driver.py set button3 v --mod ctrl

# Set knob click to Enter
sudo python3 driver.py set knob_click enter
```

### 3. Detach keyboard back to Windows

In **PowerShell as Administrator**:

```powershell
# Unbind to release device back to Windows
usbipd unbind --busid <BUSID>
```

If the keyboard doesn't appear in Windows, unplug and replug it.

**Your configuration is now saved in the keyboard's firmware and will work on any computer!**

## Usage

### Configure a single button

```bash
sudo python3 driver.py set <control> <key> [--mod <modifier>]
```

**Examples:**

```bash
# Simple key assignment
sudo python3 driver.py set button1 a
sudo python3 driver.py set button2 enter
sudo python3 driver.py set button3 f5

# With modifier keys
sudo python3 driver.py set button1 c --mod ctrl      # Ctrl+C (copy)
sudo python3 driver.py set button2 v --mod ctrl      # Ctrl+V (paste)
sudo python3 driver.py set button3 z --mod ctrl      # Ctrl+Z (undo)
sudo python3 driver.py set button4 s --mod ctrl      # Ctrl+S (save)
sudo python3 driver.py set button5 tab --mod alt     # Alt+Tab
sudo python3 driver.py set button6 f4 --mod alt      # Alt+F4

# Rotary knob
sudo python3 driver.py set knob_click enter          # Click = Enter
sudo python3 driver.py set knob_cw volumeup          # Clockwise = Volume Up
sudo python3 driver.py set knob_ccw volumedown       # Counter-clockwise = Volume Down
```

### List available options

```bash
# List all available keys
python3 driver.py list-keys

# List all controls (buttons, knob)
python3 driver.py list-controls
```

### Monitor raw input (debugging)

```bash
sudo python3 driver.py monitor
```

## Controls

| Name | Description |
|------|-------------|
| `button1` | Button 1 |
| `button2` | Button 2 |
| `button3` | Button 3 |
| `button4` | Button 4 |
| `button5` | Button 5 |
| `button6` | Button 6 |
| `knob_cw` | Rotary knob clockwise rotation |
| `knob_ccw` | Rotary knob counter-clockwise rotation |
| `knob_click` | Rotary knob push/click |

## Modifiers

| Name | Description |
|------|-------------|
| `none` | No modifier (default) |
| `ctrl` | Control key |
| `shift` | Shift key |
| `alt` | Alt key |
| `gui` | Windows/Command key |
| `ctrl_shift` | Ctrl + Shift |
| `ctrl_alt` | Ctrl + Alt |
| `ctrl_shift_alt` | Ctrl + Shift + Alt |

## Available Keys

**Letters:** a-z

**Numbers:** 0-9

**Function keys:** f1-f12

**Special keys:**
- `enter`, `escape`, `backspace`, `tab`, `space`
- `insert`, `delete`, `home`, `end`, `pageup`, `pagedown`
- `up`, `down`, `left`, `right`
- `printscreen`, `scrolllock`, `pause`, `capslock`
- `minus`, `equal`, `leftbrace`, `rightbrace`, `backslash`
- `semicolon`, `apostrophe`, `grave`, `comma`, `dot`, `slash`
- `mute`, `volumeup`, `volumedown`

## WSL2 Setup (Detailed)

USB devices must be passed through to WSL2 using `usbipd-win`.

### Install usbipd-win (Windows)

```powershell
winget install usbipd
```

### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         WINDOWS                                  │
│                                                                  │
│  1. usbipd list              # Find your keyboard's BUSID       │
│  2. usbipd bind --busid X-Y --force   # Bind (first time)       │
│  3. usbipd attach --wsl --busid X-Y   # Send to WSL2            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          WSL2                                    │
│                                                                  │
│  4. sudo python3 driver.py set button1 z   # Configure keys     │
│  5. sudo python3 driver.py set button2 c --mod ctrl             │
│     ... (configure all buttons)                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         WINDOWS                                  │
│                                                                  │
│  6. usbipd unbind --busid X-Y   # Release back to Windows       │
│  7. (Unplug/replug if needed)                                   │
│  8. Use your configured keyboard!                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Troubleshooting

**Device not found in WSL2:**
```bash
lsusb | grep 1189
# Should show: Bus 001 Device 002: ID 1189:8890 Acer Communications & Multimedia
```

**Permission denied:**
```bash
# Run with sudo
sudo python3 driver.py set button1 z
```

**Device doesn't appear in Windows after unbind:**
```powershell
# Force unbind
usbipd unbind --busid X-Y --force

# Unplug and replug the keyboard
```

**USBPcap warning:**
If you have Wireshark/USBPcap installed, you may need `--force` flag:
```powershell
usbipd bind --busid X-Y --force
```

## Technical Details

### USB Interfaces

The device exposes 4 HID interfaces:

| Interface | Endpoint | Type | Purpose |
|-----------|----------|------|---------|
| 0 | EP 1 IN | Keyboard (Boot) | Button input |
| 1 | EP 2 OUT | HID | **Configuration** |
| 2 | EP 3 IN | Keyboard | Media/special keys |
| 3 | EP 2 IN | Mouse (Boot) | Rotary encoder |

### Configuration Protocol

The device is configured by sending 64-byte HID reports to Interface 1.

**Report Format:**

```
Byte 0:     Report ID     = 0x03
Byte 1:     Control ID    = 0x01-0x06 (buttons), 0x0d-0x0f (knob)
Byte 2:     Command       = 0x11 (set key)
Byte 3:     Constant      = 0x01
Byte 4:     Action        = 0x00 (query) / 0x01 (set)
Byte 5:     Modifier      = 0x00 (none), or Ctrl/Shift/Alt flags
Byte 6:     Keycode       = USB HID keycode
Bytes 7-63: Padding       = 0x00
```

**Control IDs:**

| ID | Control |
|----|---------|
| 0x01 | Button 1 |
| 0x02 | Button 2 |
| 0x03 | Button 3 |
| 0x04 | Button 4 |
| 0x05 | Button 5 |
| 0x06 | Button 6 |
| 0x0d | Knob clockwise |
| 0x0e | Knob counter-clockwise |
| 0x0f | Knob click |

**Command Sequence:**

1. **Init**: `03 a1 01 00 00...` (64 bytes)
2. **Query**: `03 XX 11 01 00 00 00...` (XX = control ID)
3. **Set**: `03 XX 11 01 01 MM KK 00...` (MM = modifier, KK = keycode)
4. **Save**: `03 aa aa 00 00...`

**Modifier Flags:**

| Flag | Modifier |
|------|----------|
| 0x00 | None |
| 0x01 | Left Ctrl |
| 0x02 | Left Shift |
| 0x04 | Left Alt |
| 0x08 | Left GUI (Win/Cmd) |

Combine flags for multiple modifiers (e.g., `0x03` = Ctrl+Shift).

### Input Report Format

Button presses are reported as standard HID keyboard reports:

```
[01] [MM] [00] [K1] [K2] [K3] [K4] [K5] [K6]
 │    │    │    └─────────────────────────── Up to 6 simultaneous keycodes
 │    │    └── Reserved
 │    └── Modifier keys
 └── Report ID
```

## Reverse Engineering Notes

The configuration protocol was reverse-engineered by:

1. Capturing USB traffic with Wireshark + USBPcap on Windows
2. Using the vendor's Windows configuration software
3. Analyzing the 64-byte HID reports sent to Interface 1
4. Identifying the command structure through pattern analysis

Key discoveries:
- Interface 1 (EP 2 OUT) is used for configuration (no hidraw device in Linux)
- Configuration is stored in device firmware (persists across power cycles)
- Device uses standard USB HID keycodes
- `0xaa 0xaa` magic bytes indicate "save" command

## Files

```
mcrokeydriver/
├── README.md           # This file
├── driver.py           # Main driver script
└── captures/           # USB captures for protocol analysis (optional)
```

## Dependencies

- Python 3.6+
- pyusb (`pip install pyusb`)

## References

- [USB HID Usage Tables](https://usb.org/sites/default/files/hut1_22.pdf)
- [USB HID Specification](https://www.usb.org/sites/default/files/hid1_11.pdf)
- [usbipd-win](https://github.com/dorssel/usbipd-win)
- [pyusb](https://github.com/pyusb/pyusb)

## License

MIT
