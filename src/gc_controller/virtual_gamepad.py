"""
Virtual Gamepad Platform Abstraction Layer

Provides a unified interface for controller emulation:
- Dolphin pipe mode: macOS (named pipe / FIFO)
"""

import errno
import os
import stat
import time
import threading
from abc import ABC, abstractmethod
from enum import Enum, auto

from .i18n import _ as _t


class GamepadButton(Enum):
    """Platform-independent button constants for Xbox 360 controller."""

    A = auto()
    B = auto()
    X = auto()
    Y = auto()
    LEFT_SHOULDER = auto()
    RIGHT_SHOULDER = auto()
    LEFT_THUMB = auto()
    RIGHT_THUMB = auto()
    START = auto()
    BACK = auto()
    GUIDE = auto()
    DPAD_UP = auto()
    DPAD_DOWN = auto()
    DPAD_LEFT = auto()
    DPAD_RIGHT = auto()


class VirtualGamepad(ABC):
    """Abstract base class for virtual Xbox 360 controller emulation."""

    @abstractmethod
    def left_joystick(self, x_value: int, y_value: int) -> None:
        """Set left joystick position. Values in range [-32767, 32767]."""

    @abstractmethod
    def right_joystick(self, x_value: int, y_value: int) -> None:
        """Set right joystick position. Values in range [-32767, 32767]."""

    @abstractmethod
    def left_trigger(self, value: int) -> None:
        """Set left trigger value. Range [0, 255]."""

    @abstractmethod
    def right_trigger(self, value: int) -> None:
        """Set right trigger value. Range [0, 255]."""

    @abstractmethod
    def press_button(self, button: GamepadButton) -> None:
        """Press a button."""

    @abstractmethod
    def release_button(self, button: GamepadButton) -> None:
        """Release a button."""

    @abstractmethod
    def update(self) -> None:
        """Flush buffered events to the virtual device."""

    @abstractmethod
    def reset(self) -> None:
        """Reset all inputs to neutral."""

    @abstractmethod
    def close(self) -> None:
        """Destroy the virtual device and release resources."""

    def set_rumble_callback(self, callback) -> None:
        """Set callback(large_motor: int, small_motor: int) for FF events. Optional."""
        pass

    def stop_rumble_listener(self) -> None:
        """Stop any background rumble listener thread. Called from close()."""
        pass


def _get_real_home() -> str:
    """Get the real user's home directory."""
    return os.path.expanduser("~")


_REAL_HOME = _get_real_home()


def _get_all_dolphin_user_dirs() -> list[str]:
    """Return all detected Dolphin user directories that exist on disk.

    Returns the macOS Dolphin user directory if it exists.
    """
    d = os.path.join(_REAL_HOME, "Library/Application Support/Dolphin")
    return [d] if os.path.isdir(d) else []


def ensure_dolphin_pipe(pipe_name: str = "gc_controller") -> list[str]:
    """Create the Dolphin named-pipe FIFO in every detected Dolphin user dir.

    Call this early (e.g. at app startup) so the pipe file is visible in
    Dolphin's controller device list before emulation is started.

    Returns a list of all pipe paths that were created / verified.
    """
    user_dirs = _get_all_dolphin_user_dirs()
    if not user_dirs:
        # No existing Dolphin dirs — fall back to the macOS default.
        user_dirs = [os.path.join(_REAL_HOME, "Library/Application Support/Dolphin")]

    pipe_paths: list[str] = []
    for user_dir in user_dirs:
        pipe_dir = os.path.join(user_dir, "Pipes")
        try:
            os.makedirs(pipe_dir, exist_ok=True)
            pipe_path = os.path.join(pipe_dir, pipe_name)

            if not os.path.exists(pipe_path):
                os.mkfifo(pipe_path)
            elif not stat.S_ISFIFO(os.stat(pipe_path).st_mode):
                continue  # skip non-FIFO files without failing

            pipe_paths.append(pipe_path)
        except OSError:
            continue  # skip dirs we can't write to

    if not pipe_paths:
        raise RuntimeError(
            _t(
                "Could not create Dolphin pipe '{}' in any detected Dolphin directory."
            ).format(pipe_name)
        )

    return pipe_paths


class DolphinPipeGamepad(VirtualGamepad):
    """Dolphin named pipe implementation for macOS.

    Sends controller input to Dolphin Emulator via a Unix FIFO using
    the Dolphin pipe input protocol.  No virtual HID device or special
    drivers are required.
    """

    _BUTTON_MAP = {
        GamepadButton.A: "A",
        GamepadButton.B: "B",
        GamepadButton.X: "X",
        GamepadButton.Y: "Y",
        GamepadButton.START: "START",
        GamepadButton.RIGHT_SHOULDER: "Z",
        GamepadButton.LEFT_SHOULDER: "L",
        GamepadButton.DPAD_UP: "D_UP",
        GamepadButton.DPAD_DOWN: "D_DOWN",
        GamepadButton.DPAD_LEFT: "D_LEFT",
        GamepadButton.DPAD_RIGHT: "D_RIGHT",
    }

    def __init__(
        self,
        pipe_name: str = "gc_controller",
        cancel_event: threading.Event | None = None,
    ):
        pipe_paths = ensure_dolphin_pipe(pipe_name)

        # Poll until Dolphin opens the read end of one of the pipes.
        # With cancel_event, this can be stopped from another thread.
        while True:
            for path in pipe_paths:
                try:
                    fd = os.open(path, os.O_WRONLY | os.O_NONBLOCK)
                    self._pipe_path = path
                    self._pipe = os.fdopen(fd, "w")
                    self._pressed: set[str] = set()
                    return
                except OSError as e:
                    if e.errno != errno.ENXIO:
                        raise

            if cancel_event is not None and cancel_event.is_set():
                path_list = "\n  ".join(pipe_paths)
                raise OSError(
                    errno.ECANCELED, f"Pipe emulation cancelled.\nPipes:\n  {path_list}"
                )

            time.sleep(0.5)

    def left_joystick(self, x_value: int, y_value: int) -> None:
        x = (x_value / 32767 + 1) / 2
        y = (y_value / 32767 + 1) / 2
        self._pipe.write(f"SET MAIN {x:.4f} {y:.4f}\n")

    def right_joystick(self, x_value: int, y_value: int) -> None:
        x = (x_value / 32767 + 1) / 2
        y = (y_value / 32767 + 1) / 2
        self._pipe.write(f"SET C {x:.4f} {y:.4f}\n")

    def left_trigger(self, value: int) -> None:
        self._pipe.write(f"SET L {value / 255:.4f}\n")

    def right_trigger(self, value: int) -> None:
        self._pipe.write(f"SET R {value / 255:.4f}\n")

    def press_button(self, button: GamepadButton) -> None:
        name = self._BUTTON_MAP.get(button)
        if name is None:
            return
        self._pipe.write(f"PRESS {name}\n")
        self._pressed.add(name)

    def release_button(self, button: GamepadButton) -> None:
        name = self._BUTTON_MAP.get(button)
        if name is None:
            return
        self._pipe.write(f"RELEASE {name}\n")
        self._pressed.discard(name)

    def update(self) -> None:
        self._pipe.flush()

    def reset(self) -> None:
        self._pipe.write("SET MAIN 0.5000 0.5000\n")
        self._pipe.write("SET C 0.5000 0.5000\n")
        self._pipe.write("SET L 0.0000\n")
        self._pipe.write("SET R 0.0000\n")
        for name in list(self._pressed):
            self._pipe.write(f"RELEASE {name}\n")
        self._pressed.clear()
        self._pipe.flush()

    def close(self) -> None:
        try:
            self.reset()
        except Exception:
            pass
        try:
            self._pipe.close()
        except Exception:
            pass


def is_emulation_available(mode: str = "xbox360") -> bool:
    """Check whether virtual gamepad emulation is available on this platform."""
    if mode == "dsu":
        return True  # DSU only needs UDP sockets, available everywhere

    if mode == "dolphin_pipe":
        return True

    # Xbox 360 mode — not supported on macOS
    return False


def get_emulation_unavailable_reason(mode: str = "xbox360") -> str:
    """Return a human-readable explanation of why emulation is unavailable."""
    if mode == "dsu":
        return _t("DSU server mode should always be available.")

    if mode == "dolphin_pipe":
        return _t("Dolphin pipe emulation should always be available on macOS.")

    # Xbox 360 mode
    return (
        _t("Xbox 360 controller emulation is not supported on macOS.")
        + "\n"
        + _t(
            "macOS does not allow user-space creation of virtual HID game controllers."
        )
    )


def create_gamepad(
    mode: str = "xbox360",
    slot_index: int = 0,
    cancel_event: threading.Event | None = None,
) -> VirtualGamepad:
    """Factory: create the appropriate VirtualGamepad for the current platform/mode."""
    if mode == "dsu":
        from .dsu_server import DSUGamepad

        return DSUGamepad(slot_index=slot_index)

    if mode == "dolphin_pipe":
        pipe_name = f"gc_controller_{slot_index + 1}"
        return DolphinPipeGamepad(pipe_name=pipe_name, cancel_event=cancel_event)

    # Xbox 360 mode — not supported on macOS
    raise RuntimeError(
        _t("Xbox 360 controller emulation is not supported on macOS.")
        + "\n"
        + _t(
            "macOS does not allow user-space creation of virtual HID game controllers."
        )
        + "\n"
        + _t(
            "Consider using a hardware adapter or alternative input remapping tool."
        )
    )
