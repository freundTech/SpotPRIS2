import sys

from gi.repository import GLib
from spotipy import SpotifyOAuth, Spotify
from appdirs import AppDirs
from configparser import ConfigParser
from http.server import HTTPServer, BaseHTTPRequestHandler

from . import MediaPlayer2, BusManager
import pkg_resources
import webbrowser
import argparse

ifaces = ["org.mpris.MediaPlayer2",
          "org.mpris.MediaPlayer2.Player"]  # , "org.mpris.MediaPlayer2.Playlists", "org.mpris.MediaPlayer2.TrackList"]
dirs = AppDirs("spotpris2", "freundTech")
scope = "user-modify-playback-state,user-read-playback-state,user-read-currently-playing"


def main():
    parser = argparse.ArgumentParser(description="Control Spotify Connect devices using MPRIS2")
    parser.add_argument('-d', '--devices', nargs='+', metavar="DEVICE", help="Only create interfaces for the listed devices")
    parser.add_argument('-i', '--ignore', nargs='+', metavar="DEVICE", help="Ignore the listed devices")
    parser.add_argument('-l', '--list', nargs='?', choices=["name", "id"], const="name", help="List available devices and exit")
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

    if args.devices and args.ignore:
        parser.error("--devices and --ignore can't be used at the same time")
        return

    manager = BusManager(sp, args.devices, args.ignore)

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
