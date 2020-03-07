from gi.repository import GLib

from .util import new_session_bus
from . import MediaPlayer2


class BusManager:
    def __init__(self, spotify):
        self.spotify = spotify
        self.current_devices = {}

    def main_loop(self):
        devices_ids = [d["id"] for d in self.spotify.devices()["devices"]]
        current_playback = self.spotify.current_playback()
        for device in devices_ids:
            if device not in self.current_devices:
                self._create_device(device)

        for device in list(self.current_devices.keys()):
            if device not in devices_ids:
                self._remove_device(device)
            else:
                self.current_devices[device].player.event_loop(current_playback)

        return True

    def _create_device(self, device_id):
        bus = new_session_bus()
        player = MediaPlayer2(self.spotify, device_id=device_id)
        publication = bus.publish(f"org.mpris.MediaPlayer2.spotpris.device{device_id}",
                                  ("/org/mpris/MediaPlayer2", player))
        self.current_devices[device_id] = PlayerInfo(player, publication)

    def _remove_device(self, device_id):
        player_info = self.current_devices[device_id]
        player_info.publication.unpublish()
        del self.current_devices[device_id]


class PlayerInfo:
    def __init__(self, player, publication):
        self.player = player
        self.publication = publication
