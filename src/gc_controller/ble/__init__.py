"""
BLE Subpackage

Provides Bluetooth Low Energy connectivity for NSO GameCube controllers
using Bleak on macOS.
"""


def is_ble_available() -> bool:
    """Check if BLE support is available (Bleak installed)."""
    try:
        import bleak  # noqa: F401
        return True
    except ImportError:
        return False


def get_ble_unavailable_reason() -> str:
    """Return a human-readable reason why BLE is not available."""
    try:
        import bleak  # noqa: F401
    except ImportError:
        return "The 'bleak' package is not installed. Install with: pip install bleak"
    return ""
