"""
Connection Manager

Handles USB initialization and HID device connection for the GameCube controller.
Supports multi-device enumeration and path-targeted open for multi-controller setups.
"""

from typing import Optional, Callable, List

import hid
import usb.core
import usb.util

from .controller_constants import (
    VENDOR_ID,
    PRODUCT_ID,
    DEFAULT_REPORT_DATA,
    SET_LED_DATA,
)
from .i18n import _ as _t


class ConnectionManager:
    """Manages USB initialization and HID connection."""

    def __init__(
        self, on_status: Callable[[str], None], on_progress: Callable[[int], None]
    ):
        self._on_status = on_status
        self._on_progress = on_progress
        self.device: Optional[hid.device] = None
        self.device_path: Optional[bytes] = None

    @staticmethod
    def enumerate_devices() -> List[dict]:
        """Return a list of HID device info dicts for all connected GC controllers."""
        return hid.enumerate(VENDOR_ID, PRODUCT_ID)

    @staticmethod
    def enumerate_usb_devices() -> list:
        """Return a list of all USB device objects matching the GC controller VID/PID."""
        try:
            devices = usb.core.find(
                find_all=True, idVendor=VENDOR_ID, idProduct=PRODUCT_ID
            )
            return list(devices) if devices else []
        except Exception:
            # pyusb backend not available (e.g. missing libusb on Windows)
            return []

    def initialize_via_usb(self, usb_device=None) -> bool:
        """Initialize controller via USB.

        If usb_device is provided, use it directly instead of scanning.
        """
        try:
            self._on_status(_t("Looking for device..."))
            self._on_progress(10)

            dev = (
                usb_device
                if usb_device is not None
                else usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
            )
            if dev is None:
                self._on_status(_t("Device not found"))
                return False

            self._on_status(_t("Device found"))
            self._on_progress(30)

            try:
                if dev.is_kernel_driver_active(1):
                    dev.detach_kernel_driver(1)
            except (usb.core.USBError, NotImplementedError):
                pass

            try:
                dev.set_configuration()
            except usb.core.USBError:
                pass  # May already be configured

            try:
                usb.util.claim_interface(dev, 1)
            except usb.core.USBError:
                pass  # May already be claimed

            self._on_progress(50)

            self._on_status(_t("Sending initialization data..."))
            dev.write(0x02, DEFAULT_REPORT_DATA, 2000)

            self._on_progress(70)

            self._on_status(_t("Sending LED data..."))
            dev.write(0x02, SET_LED_DATA, 2000)

            self._on_progress(90)

            try:
                usb.util.release_interface(dev, 1)
            except usb.core.USBError:
                pass

            # Release pyusb resources so the handle is fully closed before
            # HIDAPI opens the device — prevents conflicts on Windows where
            # WinUSB and HID class driver can't share the device.
            try:
                usb.util.dispose_resources(dev)
            except Exception:
                pass

            self._on_status(_t("USB initialization complete"))
            return True

        except Exception as e:
            self._on_status(_t("USB initialization failed: {}").format(e))
            return False

    def init_hid_device(self, device_path: Optional[bytes] = None) -> bool:
        """Initialize HID connection.

        If device_path is provided, open that specific device by path.
        Otherwise, open the first matching VID/PID device.
        """
        try:
            self._on_status(_t("Connecting via HID..."))

            self.device = hid.device()
            if device_path:
                self.device.open_path(device_path)
            else:
                self.device.open(VENDOR_ID, PRODUCT_ID)

            if self.device:
                self.device_path = device_path
                self._on_status(_t("Connected via HID"))
                self._on_progress(100)
                return True
            else:
                self._on_status(_t("Failed to connect via HID"))
                return False

        except Exception as e:
            self._on_status(_t("HID connection failed: {}").format(e))
            return False

    def connect(self, usb_device=None, device_path: Optional[bytes] = None) -> bool:
        """Full connection sequence: USB init then HID.

        Optionally target a specific USB device and/or HID device path.
        """
        if not self.initialize_via_usb(usb_device=usb_device):
            return False
        return self.init_hid_device(device_path=device_path)

    def send_rumble(self, state: bool) -> bool:
        """Send a rumble ON/OFF command.

        Tries pyusb first (endpoint 0x02 on interface 1), then falls back
        to HIDAPI write for Windows where pyusb/libusb is unavailable.
        """
        cmd = bytes(
            [
                0x0A,
                0x91,
                0x00,
                0x02,
                0x00,
                0x04,
                0x00,
                0x00,
                0x01 if state else 0x00,
                0x00,
                0x00,
                0x00,
            ]
        )

        # Try pyusb (works on Linux/macOS)
        try:
            dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
            if dev is not None:
                try:
                    try:
                        usb.util.claim_interface(dev, 1)
                    except usb.core.USBError:
                        pass
                    dev.write(0x02, cmd, 1000)
                    try:
                        usb.util.release_interface(dev, 1)
                    except usb.core.USBError:
                        pass
                    return True
                except Exception:
                    pass
                finally:
                    try:
                        usb.util.dispose_resources(dev)
                    except Exception:
                        pass
        except Exception:
            pass

        return False

    def disconnect(self):
        """Close and release the HID device."""
        if self.device:
            try:
                self.device.close()
            except Exception:
                pass
            self.device = None
            self.device_path = None
