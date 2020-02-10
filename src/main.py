import argparse
import logging
import sys

from client import SpotifyClient
from factory import ArtistChainFactory, DriftingWeight
from model import Playlist

LOG = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, help="Size of the generated playlist")
    parser.add_argument("--name", type=str, help="Name of the generated playlist")
    parser.add_argument("--user", type=str, help="User for whom to create the playlist")
    parser.add_argument("--seed", type=str, help="ID of the seed track")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    client = SpotifyClient(args.user)
    seed_track = client.get_track(args.seed)
    factory = ArtistChainFactory(
        client, seed_track, DriftingWeight(seed_track), unique_artists=False
    )

    # If a playlist of this name exists, use it, otherwise create one.
    for playlist_ in client.get_playlists():
        if playlist_.name == args.name:
            playlist = playlist_
            break
    else:
        playlist = Playlist(name=args.name)

    for _, track in zip(range(args.size), factory):
        playlist.append(track)

    LOG.info("Finished generating playlist %s", str(playlist))

    client.store_playlist(playlist)


if __name__ == "__main__":
    main()
