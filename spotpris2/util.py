from gi.repository import Gio
from pydbus import connect

# Creates a new bus. pydbus SessionBus() returns a singleton, but we don't want that
def new_session_bus():
    return new_bus(Gio.BusType.SESSION)


def new_bus(type_):
    return connect(Gio.dbus_address_get_for_bus_sync(type_))
