from gi.repository import GLib
from pydbus import SessionBus
from spotipy import SpotifyOAuth, Spotify
from appdirs import AppDirs
from configparser import ConfigParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from . import MediaPlayer2
import pkg_resources
import webbrowser
import pprint

pp = pprint.PrettyPrinter(indent=4)

ifaces = ["org.mpris.MediaPlayer2",
          "org.mpris.MediaPlayer2.Player"]  # , "org.mpris.MediaPlayer2.Playlists", "org.mpris.MediaPlayer2.TrackList"]
dirs = AppDirs("spotpris2", "freundTech")
scope = "user-modify-playback-state,user-read-playback-state,user-read-currently-playing"


def main():
    MediaPlayer2.dbus = [pkg_resources.resource_string(__name__, f"mpris/{iface}.xml").decode('utf-8') for iface in
                         ifaces]
    loop = GLib.MainLoop()

    token = authenticate()
    sp = Spotify(auth=token)
    pp.pprint(sp.current_playback())
    pp.pprint(sp.devices())

    bus = SessionBus()
    player = MediaPlayer2(sp)
    bus.publish("org.mpris.MediaPlayer2.spotpris", ("/org/mpris/MediaPlayer2", player))
    GLib.timeout_add_seconds(1, player.eventLoop)

    loop.run()


def authenticate():
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200, "OK")
            self.end_headers()

            self.wfile.write("Success".encode('utf-8'))
            RequestHandler.callbackUri = self.path

    config = getConfig()

    oauth = SpotifyOAuth(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri="http://localhost:8000",
        scope=scope,
        cache_path=dirs.user_cache_dir,
    )

    token_info = oauth.get_cached_token()

    if token_info:
        return token_info["access_token"]

    url = oauth.get_authorize_url()
    webbrowser.open(url)

    server = HTTPServer(('', 8000), RequestHandler)
    server.handle_request()

    code = oauth.parse_response_code(RequestHandler.callbackUri)
    return oauth.get_access_token(code, as_dict=False)


def getConfig():
    config = ConfigParser()
    config.read(f"{dirs.user_config_dir}.cfg")
    if "spotpris2" not in config:
        config["spotpris2"] = {}
    section = config["spotpris2"]
    if section.get("client_id") is None or section.get("client_secret") is None:
        section["client_id"] = input("Enter client id: ")
        section["client_secret"] = input("Enter client secret: ")
        with open(f"{dirs.user_config_dir}.cfg", 'w+') as f:
            config.write(f)
    return config["spotpris2"]


if __name__ == '__main__':
    main()
