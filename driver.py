#!/usr/bin/env python3
"""
Macro Keyboard Driver

Cross-platform driver for configuring a 6-button macro keyboard with rotary encoder.
Device: VID 1189, PID 8890
"""
import os
import sys
import argparse
import time

# Device identifiers
VENDOR_ID = 0x1189
PRODUCT_ID = 0x8890
CONFIG_INTERFACE = 1  # Interface 1 has the OUT endpoint for configuration
CONFIG_ENDPOINT = 0x02  # EP 2 OUT

# Control IDs
CONTROLS = {
    'button1': 0x01,
    'button2': 0x02,
    'button3': 0x03,
    'button4': 0x04,
    'button5': 0x05,
    'button6': 0x06,
    'knob_cw': 0x0d,    # Clockwise rotation
    'knob_ccw': 0x0e,   # Counter-clockwise rotation
    'knob_click': 0x0f, # Knob press
}

# Modifier key flags
MODIFIERS = {
    'none': 0x00,
    'ctrl': 0x01,
    'shift': 0x02,
    'alt': 0x04,
    'gui': 0x08,  # Windows/Command key
    'ctrl_shift': 0x03,
    'ctrl_alt': 0x05,
    'ctrl_shift_alt': 0x07,
}

# USB HID Keycodes (subset - add more as needed)
KEYCODES = {
    # Letters
    'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08, 'f': 0x09,
    'g': 0x0a, 'h': 0x0b, 'i': 0x0c, 'j': 0x0d, 'k': 0x0e, 'l': 0x0f,
    'm': 0x10, 'n': 0x11, 'o': 0x12, 'p': 0x13, 'q': 0x14, 'r': 0x15,
    's': 0x16, 't': 0x17, 'u': 0x18, 'v': 0x19, 'w': 0x1a, 'x': 0x1b,
    'y': 0x1c, 'z': 0x1d,
    # Numbers
    '1': 0x1e, '2': 0x1f, '3': 0x20, '4': 0x21, '5': 0x22,
    '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27,
    # Special keys
    'enter': 0x28, 'escape': 0x29, 'backspace': 0x2a, 'tab': 0x2b,
    'space': 0x2c, 'minus': 0x2d, 'equal': 0x2e, 'leftbrace': 0x2f,
    'rightbrace': 0x30, 'backslash': 0x31, 'semicolon': 0x33,
    'apostrophe': 0x34, 'grave': 0x35, 'comma': 0x36, 'dot': 0x37,
    'slash': 0x38, 'capslock': 0x39,
    # Function keys
    'f1': 0x3a, 'f2': 0x3b, 'f3': 0x3c, 'f4': 0x3d, 'f5': 0x3e, 'f6': 0x3f,
    'f7': 0x40, 'f8': 0x41, 'f9': 0x42, 'f10': 0x43, 'f11': 0x44, 'f12': 0x45,
    # Control keys
    'printscreen': 0x46, 'scrolllock': 0x47, 'pause': 0x48,
    'insert': 0x49, 'home': 0x4a, 'pageup': 0x4b, 'delete': 0x4c,
    'end': 0x4d, 'pagedown': 0x4e, 'right': 0x4f, 'left': 0x50,
    'down': 0x51, 'up': 0x52,
    # Media keys (consumer control - may need different handling)
    'mute': 0x7f, 'volumeup': 0x80, 'volumedown': 0x81,
    'nexttrack': 0xb5, prevtrack: 0xb6, playpause: 0xcd,
}

# Reverse lookup for keycodes
KEYCODE_NAMES = {v: k for k, v in KEYCODES.items()}


def build_report(data: list) -> bytes:
    """Build a 64-byte HID report from data."""
    report = bytearray(64)
    for i, b in enumerate(data):
        report[i] = b
    return bytes(report)


def cmd_init() -> bytes:
    """Build init command."""
    return build_report([0x03, 0xa1, 0x01, 0x00])


def cmd_query(control_id: int) -> bytes:
    """Build query command for a control."""
    return build_report([0x03, control_id, 0x11, 0x01, 0x00])


def cmd_set(control_id: int, modifier: int, keycode: int) -> bytes:
    """Build set command for a control."""
    return build_report([0x03, control_id, 0x11, 0x01, 0x01, modifier, keycode])


def cmd_save() -> bytes:
    """Build save command."""
    return build_report([0x03, 0xaa, 0xaa, 0x00])


def configure_key(control: str, key: str, modifier: str = 'none') -> bool:
    """Configure a control to send a specific key using pyusb."""
    try:
        import usb.core
        import usb.util
    except ImportError:
        print("Error: pyusb not installed. Run: pip install pyusb")
        return False

    if control not in CONTROLS:
        print(f"Error: Unknown control '{control}'")
        print(f"Valid controls: {', '.join(CONTROLS.keys())}")
        return False

    if key not in KEYCODES:
        print(f"Error: Unknown key '{key}'")
        print(f"Valid keys: {', '.join(sorted(KEYCODES.keys()))}")
        return False

    if modifier not in MODIFIERS:
        print(f"Error: Unknown modifier '{modifier}'")
        print(f"Valid modifiers: {', '.join(MODIFIERS.keys())}")
        return False

    control_id = CONTROLS[control]
    keycode = KEYCODES[key]
    mod = MODIFIERS[modifier]

    # Find the device
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        print("Error: Device not found. Is it connected?")
        return False

    try:
        # Detach kernel driver if necessary
        if dev.is_kernel_driver_active(CONFIG_INTERFACE):
            dev.detach_kernel_driver(CONFIG_INTERFACE)
            print("Detached kernel driver from interface 1")

        # Set configuration and claim interface
        try:
            dev.set_configuration()
        except usb.core.USBError:
            pass  # May already be configured

        usb.util.claim_interface(dev, CONFIG_INTERFACE)

        # Send configuration sequence
        def send_report(data):
            # Use interrupt OUT transfer
            dev.write(CONFIG_ENDPOINT, data, timeout=1000)
            time.sleep(0.01)  # Small delay between commands

        send_report(cmd_init())
        send_report(cmd_query(control_id))
        send_report(cmd_set(control_id, mod, keycode))
        send_report(cmd_save())

        mod_str = f" + {modifier}" if modifier != 'none' else ""
        print(f"Configured {control} -> {key}{mod_str}")
        return True

    except usb.core.USBError as e:
        print(f"USB Error: {e}")
        return False
    finally:
        usb.util.release_interface(dev, CONFIG_INTERFACE)
        # Reattach kernel driver
        try:
            dev.attach_kernel_driver(CONFIG_INTERFACE)
        except usb.core.USBError:
            pass


def configure_all(config: dict) -> bool:
    """Configure multiple controls at once."""
    try:
        import usb.core
        import usb.util
    except ImportError:
        print("Error: pyusb not installed. Run: pip install pyusb")
        return False

    # Find the device
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        print("Error: Device not found. Is it connected?")
        return False

    try:
        # Detach kernel driver if necessary
        if dev.is_kernel_driver_active(CONFIG_INTERFACE):
            dev.detach_kernel_driver(CONFIG_INTERFACE)

        try:
            dev.set_configuration()
        except usb.core.USBError:
            pass

        usb.util.claim_interface(dev, CONFIG_INTERFACE)

        def send_report(data):
            dev.write(CONFIG_ENDPOINT, data, timeout=1000)
            time.sleep(0.01)

        for control, (key, modifier) in config.items():
            if control not in CONTROLS:
                print(f"Warning: Unknown control '{control}', skipping")
                continue
            if key not in KEYCODES:
                print(f"Warning: Unknown key '{key}', skipping")
                continue

            control_id = CONTROLS[control]
            keycode = KEYCODES[key]
            mod = MODIFIERS.get(modifier, 0x00)

            send_report(cmd_init())
            send_report(cmd_query(control_id))
            send_report(cmd_set(control_id, mod, keycode))
            send_report(cmd_save())

            mod_str = f" + {modifier}" if modifier != 'none' else ""
            print(f"Configured {control} -> {key}{mod_str}")

        return True

    except usb.core.USBError as e:
        print(f"USB Error: {e}")
        return False
    finally:
        usb.util.release_interface(dev, CONFIG_INTERFACE)
        try:
            dev.attach_kernel_driver(CONFIG_INTERFACE)
        except usb.core.USBError:
            pass


def monitor_input():
    """Monitor raw HID input from all interfaces."""
    from selectors import DefaultSelector, EVENT_READ

    # Find available hidraw devices for this keyboard
    hidraw_devices = []
    for i in range(10):
        path = f'/dev/hidraw{i}'
        if os.path.exists(path):
            hidraw_devices.append(path)

    if not hidraw_devices:
        print("No hidraw devices found")
        return

    print("Opening HID devices...\n")

    selector = DefaultSelector()
    files = {}

    for path in hidraw_devices:
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            f = os.fdopen(fd, 'rb', buffering=0)
            selector.register(f, EVENT_READ)
            files[f] = path
            print(f"  Opened {path}")
        except Exception as e:
            print(f"  Failed to open {path}: {e}")

    print("\nPress buttons and turn the knob. Ctrl+C to exit.\n")

    try:
        while True:
            for key, _ in selector.select():
                f = key.fileobj
                try:
                    data = f.read(64)
                    if data:
                        hex_data = ' '.join(f'{b:02x}' for b in data)
                        print(f"{files[f]}: [{hex_data}]")
                except BlockingIOError:
                    pass
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        for f in files:
            f.close()


def list_keys():
    """List all available keycodes."""
    print("Available keys:\n")
    categories = {
        'Letters': [k for k in KEYCODES if len(k) == 1 and k.isalpha()],
        'Numbers': [k for k in KEYCODES if len(k) == 1 and k.isdigit()],
        'Function': [k for k in KEYCODES if k.startswith('f') and k[1:].isdigit()],
        'Special': [k for k in KEYCODES if k not in
                   [x for x in KEYCODES if (len(x) == 1) or (x.startswith('f') and x[1:].isdigit())]]
    }
    for cat, keys in categories.items():
        print(f"  {cat}: {', '.join(sorted(keys))}")
    print(f"\nAvailable modifiers: {', '.join(MODIFIERS.keys())}")


def list_controls():
    """List all available controls."""
    print("Available controls:\n")
    for name, ctrl_id in CONTROLS.items():
        print(f"  {name:12} (0x{ctrl_id:02x})")


def main():
    parser = argparse.ArgumentParser(
        description='Macro Keyboard Driver - Configure your macro keyboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s set button1 a              # Set button 1 to 'a'
  %(prog)s set button1 c --mod ctrl   # Set button 1 to Ctrl+C
  %(prog)s set knob_click enter       # Set knob click to Enter
  %(prog)s set knob_cw volumeup       # Set clockwise rotation to Volume Up
  %(prog)s monitor                    # Monitor raw HID input
  %(prog)s list-keys                  # List available keys
  %(prog)s list-controls              # List available controls
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Set command
    set_parser = subparsers.add_parser('set', help='Set a control to a key')
    set_parser.add_argument('control', help='Control to configure (e.g., button1, knob_click)')
    set_parser.add_argument('key', help='Key to assign (e.g., a, enter, f1)')
    set_parser.add_argument('--mod', '-m', default='none', help='Modifier key (e.g., ctrl, shift, alt)')

    # Monitor command
    subparsers.add_parser('monitor', help='Monitor raw HID input')

    # List commands
    subparsers.add_parser('list-keys', help='List available keys')
    subparsers.add_parser('list-controls', help='List available controls')

    args = parser.parse_args()

    if args.command == 'set':
        success = configure_key(args.control, args.key, args.mod)
        sys.exit(0 if success else 1)
    elif args.command == 'monitor':
        monitor_input()
    elif args.command == 'list-keys':
        list_keys()
    elif args.command == 'list-controls':
        list_controls()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
