from pydbus.generic import signal
from pydbus import Variant
import re

from .util import ms_to_us, get_recursive_path, float_to_percent, percent_to_float, track_id_to_path, us_to_ms, \
    time_millis


class MediaPlayer2:
    propertyMap = {
        ("repeat_state",): "LoopStatus",
        ("shuffle_state",): "Shuffle",
        ("is_playing",): "PlaybackStatus",
        ("device", "volume_percent"): "Volume",
        ("item", "id"): "Metadata"
    }
    uriFormats = [
        re.compile("spotify:(?P<type>[a-z]*):(?P<id>[a-zA-Z0-9]*)"),
        re.compile("https?://open.spotify.com/(?P<type>[a-z]*)/(?P<id>[a-zA-Z0-9]*)"),
    ]

    def __init__(self, spotify, current_playback, device_id=None):
        self.spotify = spotify
        self.device_id = device_id
        self.request_time = time_millis()
        self.current_playback = current_playback
        self.position_offset = 0

    def Raise(self):
        pass

    def Quit(self):
        pass

    @property
    def CanQuit(self):
        return False

    @property
    def CanRaise(self):
        return False

    @property
    def HasTrackList(self):
        return False  # Maybe in the future

    @property
    def Identity(self):
        return self.current_playback["device"]["name"]

    @property
    def SupportedUriSchemes(self):
        return ["spotify"]

    @property
    def SupportedMimeTypes(self):
        return []

    def Next(self):
        self.spotify.next_track(device_id=self.device_id)

    def Previous(self):
        self.spotify.previous_track(device_id=self.device_id)

    def Pause(self):
        self.spotify.pause_playback(device_id=self.device_id)

    def PlayPause(self):
        if self.current_playback["is_playing"]:
            self.Pause()
        else:
            self.Play()

    def Stop(self):
        self.spotify.pause_playback(device_id=self.device_id)

    def Play(self):
        if self.current_playback["device"] is not None and self.current_playback["device"]["is_active"]:
            self.spotify.start_playback(device_id=self.device_id)
        else:
            if self.device_id is None:
                device_id = self.spotify()["devices"][0]["id"]
            else:
                device_id = self.device_id
            self.spotify.transfer_playback(device_id=device_id, force_play=True)

    def Seek(self, offset):
        if self.current_playback["item"] is None:
            return
        position = self.current_playback["progress_ms"]
        new_position = max(position + us_to_ms(offset), 0)
        self.spotify.seek_track(new_position, device_id=self.device_id)

    def SetPosition(self, track_id, position):
        if self.current_playback["item"] is None:
            return
        if track_id != track_id_to_path(self.current_playback["item"]["uri"]):
            print("Stale set position request. Ignoring.")
            return
        if position < 0 or position > ms_to_us(self.current_playback["item"]["duration_ms"]):
            return
        self.spotify.seek_track(us_to_ms(position), device_id=self.device_id)

    def OpenUri(self, uri):
        uri = uri.strip()
        match = None
        for format_ in self.uriFormats:
            match = format_.fullmatch(uri)
            if match:
                break

        if not match:
            print("Tried to open invalid uri. Ignoring.")

        type_ = match.group('type')
        id_ = match.group('id')

        new_uri = f"spotify:{type_}:{id_}"

        if type_ in ['album', 'artist', 'playlist', 'show']:
            self.spotify.start_playback(context_uri=new_uri, device_id=self.device_id)
        else:
            self.spotify.start_playback(uris=[new_uri], device_id=self.device_id)

    Seeked = signal()

    @property
    def PlaybackStatus(self):
        if self.current_playback["item"] is None:
            return "Stopped"
        elif self.current_playback["is_playing"]:
            return "Playing"
        else:
            return "Paused"

    @property
    def LoopStatus(self):
        status = self.current_playback["repeat_state"]
        if status == "off":
            return "None"
        elif status == "track":
            return "Track"
        elif status == "context":
            return "Playlist"
        else:
            raise Exception(f"Unhandled case: Repeat state {status} returned by spotify api")

    @LoopStatus.setter
    def LoopStatus(self, loopstatus):
        if loopstatus == "None":
            status = "off"
        elif loopstatus == "Track":
            status = "track"
        elif loopstatus == "Playlist":
            status = "context"
        else:
            print("Gotten invalid loop status from MPRIS2. Ignoring")
            return

        self.spotify.repeat(status, device_id=self.device_id)

    @property
    def Rate(self):
        return 1.0

    @Rate.setter
    def Rate(self, rate):
        if rate != 1.0:
            print("Gotten invalid rate from MPRIS2. Ignoring")

    @property
    def Shuffle(self):
        return self.current_playback["shuffle_state"]

    @Shuffle.setter
    def Shuffle(self, shuffle):
        self.spotify.shuffle(shuffle, device_id=self.device_id)

    @property
    def Metadata(self):
        if self.current_playback["item"] is None:
            return {"mpris:trackid": Variant('o', "/org/mpris/MediaPlayer2/TrackList/NoTrack")}

        item = self.current_playback["item"]

        metadata = {"mpris:trackid": Variant('o', track_id_to_path(item["uri"])),
                    "mpris:length": Variant('x', ms_to_us(item["duration_ms"])),
                    "mpris:artUrl": Variant('s', item["album"]["images"][0]["url"]),
                    "xesam:album": Variant('s', item["album"]["name"]),
                    "xesam:albumArtist": Variant('as', [artist["name"] for artist in item["album"]["artists"]]),
                    "xesam:artist": Variant('as', [artist["name"] for artist in item["artists"]]),
                    "xesam:contentCreated": Variant('s', item["album"]["release_date"]),
                    "xesam:discNumber": Variant('i', item["disc_number"]),
                    "xesam:title": Variant('s', item["name"]),
                    "xesam:trackNumber": Variant('i', item["track_number"]),
                    "xesam:url": Variant('s', item["external_urls"]["spotify"]),
                    }

        return metadata

    @property
    def Volume(self):
        if self.current_playback["device"] is None:
            return 1.0
        return percent_to_float(self.current_playback["device"]["volume_percent"])

    @Volume.setter
    def Volume(self, volume):
        volume = max(min(volume, 1.0), 0.0)
        self.spotify.volume(float_to_percent(volume), device_id=self.device_id)

    @property
    def Position(self):
        if self.current_playback is None:
            return 0
        return ms_to_us(self.current_playback["progress_ms"])

    @property
    def MinimumRate(self):
        return 1.0

    @property
    def MaximumRate(self):
        return 1.0

    @property
    def CanGoNext(self):
        return True

    @property
    def CanGoPrevious(self):
        return True

    @property
    def CanPlay(self):
        return True

    @property
    def CanPause(self):
        return True

    @property
    def CanSeek(self):
        return True

    @property
    def CanControl(self):
        return True

    PropertiesChanged = signal()

    def event_loop(self, current_playback):
        old_playback = self.current_playback
        self.current_playback = current_playback
        old_request_time = self.request_time
        self.request_time = time_millis()
        changed = {}

        for path, property_ in self.propertyMap.items():
            if get_recursive_path(old_playback, path) != get_recursive_path(self.current_playback, path):
                changed[property_] = getattr(self, property_)

        # emit signal if song progress is out of sync with time
        progress = self.current_playback["progress_ms"] - old_playback["progress_ms"]
        expected = self.request_time - old_request_time if self.current_playback["is_playing"] else 0
        if "Metadata" in changed or "PlaybackStatus" in changed:
            self.position_offset = 0
        else:
            self.position_offset += progress - expected

        if abs(self.position_offset) > 100:
            self.position_offset = 0
            self.Seeked.emit(ms_to_us(self.current_playback["progress_ms"]))

        if changed:
            self.PropertiesChanged.emit("org.mpris.MediaPlayer2.Player", changed, [])

        if self.current_playback["device"]["name"] != old_playback["device"]["name"]:
            self.PropertiesChanged.emit("org.mpris.MediaPlayer2", {"Identity": self.Identity}, [])
