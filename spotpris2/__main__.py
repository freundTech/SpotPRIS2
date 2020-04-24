from gi.repository import GLib
from pydbus import SessionBus
from spotipy import SpotifyOAuth, Spotify
from appdirs import AppDirs
from configparser import ConfigParser
from http.server import HTTPServer, BaseHTTPRequestHandler

from .BusManager import SingleBusManager, MultiBusManager
from . import MediaPlayer2
import pkg_resources
import webbrowser
import argparse

ifaces = ["org.mpris.MediaPlayer2",
          "org.mpris.MediaPlayer2.Player"]  # , "org.mpris.MediaPlayer2.Playlists", "org.mpris.MediaPlayer2.TrackList"]
dirs = AppDirs("spotpris2", "freundTech")
scope = "user-modify-playback-state,user-read-playback-state,user-read-currently-playing"


def main():
    parser = argparse.ArgumentParser(description="Control Spotify Connect devices using MPRIS2")
    parser.add_argument('-d', '--devices', nargs='+', metavar="DEVICE",
                        help="Only create interfaces for the listed devices")
    parser.add_argument('-i', '--ignore', nargs='+', metavar="DEVICE", help="Ignore the listed devices")
    parser.add_argument('-a', '--auto', action="store_true", help="Automatically control the active device")
    parser.add_argument('-l', '--list', nargs='?', choices=["name", "id"], const="name",
                        help="List available devices and exit")
    parser.add_argument('-s', '--steal-bus', action="store_true", help="Steal the dbus bus name from spotify to prevent "
                        "it from also offering an MPRIS2 interface. If --auto is used use the spotify bus name as own "
                        "bus name (experimental)")
    args = parser.parse_args()

    MediaPlayer2.dbus = [pkg_resources.resource_string(__name__, f"mpris/{iface}.xml").decode('utf-8') for iface in
                         ifaces]

    loop = GLib.MainLoop()

    oauth = authenticate()
    sp = Spotify(oauth_manager=oauth)

    if args.list:
        devices = sp.devices()
        for devices in devices["devices"]:
            print(devices[args.list])
        return

    exclusive_count = 0
    for arg in [args.devices, args.ignore, args.auto]:
        if arg:
            exclusive_count += 1
    if exclusive_count >= 2:
        parser.error("Only one of --devices, --ignore and --auto can be used at the same time")
        return

    if args.steal_bus:
        bus = SessionBus()
        try:
            # This sets the bus name for the SessionBus singleton which is also used by SingleBusManager
            bus.request_name("org.mpris.MediaPlayer2.spotify", allow_replacement=False, replace=True)
        except RuntimeError:
            print("Failed to steal spotify bus name. You need to start spotPRIS2 before spotify")
            exit(1)

    if not args.auto:
        manager = MultiBusManager(sp, args.devices, args.ignore)
    else:
        if args.steal_bus:
            manager = SingleBusManager(sp, bus=bus)
        else:
            manager = SingleBusManager(sp)

    def timeout_handler():
        manager.main_loop()
        return True

    GLib.timeout_add_seconds(1, timeout_handler)

    try:
        loop.run()
    except KeyboardInterrupt:
        pass


def authenticate():
    class RequestHandler(BaseHTTPRequestHandler):
        callbackUri = None

        def do_GET(self):
            self.send_response(200, "OK")
            self.end_headers()

            self.wfile.write(pkg_resources.resource_string(__name__, "html/success.html"))
            RequestHandler.callbackUri = self.path

    config = get_config()

    oauth = SpotifyOAuth(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri="http://localhost:8000",
        scope=scope,
        cache_path=dirs.user_cache_dir,
    )

    token_info = oauth.get_cached_token()

    if not token_info:
        url = oauth.get_authorize_url()
        webbrowser.open(url)

        server = HTTPServer(('', 8000), RequestHandler)
        server.handle_request()

        code = oauth.parse_response_code(RequestHandler.callbackUri)
        oauth.get_access_token(code, as_dict=False)
    return oauth


def get_config():
    config = ConfigParser()
    config.read(f"{dirs.user_config_dir}.cfg")
    if "spotpris2" not in config:
        config["spotpris2"] = {}
    section = config["spotpris2"]
    if section.get("client_id") is None or section.get("client_secret") is None:
        print("To use this software you need to provide your own spotify developer credentials. Go to "
              "https://developer.spotify.com/dashboard/applications, create a new client id and add "
              "http://localhost:8000 to the redirect URIs.")
        section["client_id"] = input("Enter client id: ")
        section["client_secret"] = input("Enter client secret: ")
        with open(f"{dirs.user_config_dir}.cfg", 'w+') as f:
            config.write(f)
    return config["spotpris2"]


if __name__ == '__main__':
    main()
