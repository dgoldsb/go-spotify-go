import random
import typing
import logging

from client import SpotifyClient
from model import Track

LOG = logging.getLogger(__name__)


class ArtistChainFactory:
    """
    For fun, this will be an iterable.
    """
    def __init__(
        self,
        client: SpotifyClient,
        seed_track: Track,
        unique_artists=True,
        unique_tracks=True,
    ):
        self._artists = set(seed_track.artists)
        self._client = client
        self._next_track = seed_track
        self._tracks = {seed_track}
        self._unique_artists = unique_artists
        self._unique_tracks = unique_tracks

    def __iter__(self):
        return self

    def __next__(self):
        track = self._next_track
        self._next_track = self._get_next_track()

        self._artists = self._artists.union(set(self._next_track.artists))
        self._tracks.add(self._next_track)

        return track

    def reset(self):
        self._artists = set()
        self._tracks = set()

    def _get_next_track(self):
        # TODO: Split up.
        # TODO: Not all related artists.
        related_artists = self._client.get_related_artists(self._next_track.artists[0].identifier)
        target_tracks = set()
        for related_artist in related_artists:
            LOG.info("Fetching tracks for %s", str(related_artist))

            # Skip this artist if it already has track(s) in the playlist, and the
            # user requested unique artists.
            if self._unique_artists and related_artist in self._artists:
                continue

            for track in self._client.get_top_tracks(related_artist.identifier):
                LOG.debug("Fetched track %s with popularity %s", str(track), track.popularity)

                # Skip this track if it is already in the playlist, and the user
                # requested unique tracks.
                if self._unique_tracks and track in self._tracks:
                    continue

                target_tracks.add(track)

            break # TODO

        chosen_track = _select_track(target_tracks)
        LOG.info("Chose track %s", str(chosen_track))

        return chosen_track


def _select_track(tracks: typing.Set[Track]):
    """Selects a track randomly, using the track popularity as a weight."""
    weights = [track.popularity for track in tracks]
    choices = random.choices(list(tracks), weights, k=1)

    return choices[0]
