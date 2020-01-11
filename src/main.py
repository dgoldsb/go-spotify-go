import logging
import sys

from client import SpotifyClient
from factory import ArtistChainFactory
from model import Playlist

LOG = logging.getLogger(__name__)


def main():
    size = 10
    track = "7Jh1bpe76CNTCgdgAdBw4Z"

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    client = SpotifyClient()

    seed_track = client.get_track(track)

    factory = ArtistChainFactory(client, seed_track)

    playlist = Playlist()
    for _, track in zip(range(size), factory):
        playlist.append(track)

    print(playlist)


if __name__ == "__main__":
    main()
