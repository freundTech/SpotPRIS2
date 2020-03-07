from time import time

from gi.repository import Gio
from pydbus import connect


# Creates a new bus. pydbus SessionBus() returns a singleton, but we don't want that
def new_session_bus():
    return new_bus(Gio.BusType.SESSION)


def new_bus(type_):
    return connect(Gio.dbus_address_get_for_bus_sync(type_))

def time_millis():
    return int(time() * 1000)


def track_id_to_path(track):
    return '/' + track.replace(':', '/')


def ms_to_us(ms):
    return ms * 1000


def us_to_ms(us):
    return us // 1000


def percent_to_float(percent):
    return percent / 100


def float_to_percent(n):
    return int(n * 100)


def get_recursive_path(data, path):
    try:
        for segment in path:
            data = data[segment]
    except KeyError:
        return None

    return data
