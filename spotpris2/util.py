from typing import TypeVar, List, Any, Dict

from time import time

from gi.repository import Gio
from pydbus import connect
from pydbus.bus import Bus


# Creates a new bus. pydbus SessionBus() returns a singleton, but we don't want that
def new_session_bus() -> Bus:
    return new_bus(Gio.BusType.SESSION)


def new_bus(type_) -> Bus:
    return connect(Gio.dbus_address_get_for_bus_sync(type_))


def time_millis() -> int:
    return int(time() * 1000)


def track_id_to_path(track: str) -> str:
    return '/' + track.replace(':', '/')


def ms_to_us(ms: int) -> int:
    return ms * 1000


def us_to_ms(us: int) -> int:
    return us // 1000


def percent_to_float(percent: int) -> float:
    return percent / 100


def float_to_percent(n: float) -> int:
    return int(n * 100)


T = TypeVar('T')


def get_recursive_path(data: Dict[T, Any], path: List[T]) -> Any:
    try:
        for segment in path:
            data = data[segment]
    except (KeyError, TypeError):
        return None

    return data


def create_playback_state(current_playback: Dict[str, Any], device: Dict[str, Any]) -> Dict[str, Any]:
    if current_playback is None:
        return {
            'device': device,
            'item': None,
            'context': None,
            'is_playing': False,
            'progress_ms': 0,
            # Not ideal, but no way to get the real values while nothing is playing
            'repeat_state': "off",
            'shuffle_state': False,
        }
    elif current_playback["device"]["id"] == device["id"]:
        return current_playback
    else:
        current_playback = current_playback.copy()
        current_playback["is_playing"] = False
        current_playback["device"] = device
        return current_playback
