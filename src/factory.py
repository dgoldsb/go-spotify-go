import random
import typing
import logging

from client import SpotifyClient
from model import Artist, Track

LOG = logging.getLogger(__name__)


class WeightCalculator:
    """
    Base class for a weight calculator, creating a class instance allows for the
    keeping of state, using previous weight calculations to adjust future weights.
    """
    def calculate(self, tracks: typing.Set[Track]):
        raise NotImplementedError


class PopularWeight(WeightCalculator):
    def calculate(self, tracks: typing.Set[Track]):
        return [track.popularity for track in tracks]


class ArtistChainFactory:
    """
    For fun, this will be an iterable.
    """
    MAX_ARTISTS = 5

    def __init__(
        self,
        client: SpotifyClient,
        seed_track: Track,
        weight_calculator: WeightCalculator,
        unique_artists=True,
        unique_tracks=True,
    ):
        self._artists = set(seed_track.artists)
        self._client = client
        self._next_track = seed_track
        self._tracks = {seed_track}
        self._unique_artists = unique_artists
        self._unique_tracks = unique_tracks
        self._weight_calculator = weight_calculator

    def __iter__(self):
        return self

    def __next__(self):
        track = self._next_track

        # Calculate which track to return next based on the track that is returned now.
        self._next_track = self._get_next_track()

        # Add the new track to the set of visited tracks and artists.
        self._artists = self._artists.union(set(self._next_track.artists))
        self._tracks.add(self._next_track)

        return track

    def reset(self):
        self._artists = set()
        self._tracks = set()

    def _get_candidate_track(self, artist: Artist):
        candidate_tracks = []
        for track in self._client.get_top_tracks(artist.identifier):
            LOG.debug("Fetched track %s", str(track))

            # Skip this track if it is already in the playlist, and the user
            # requested unique tracks.
            if self._unique_tracks and track in self._tracks:
                continue

            candidate_tracks.append(track)

        choice = self._client.enrich_track(random.choice(candidate_tracks))
        LOG.info("Selected track %s for artist %s", str(choice), str(artist))
        return choice

    def _get_next_track(self):
        return _select_track(
            set(self._get_related_tracks(self._next_track.artists[0])),
            self._weight_calculator,
        )

    def _get_related_tracks(self, artist: Artist):
        yield_count = 0
        for related_artist in self._client.get_related_artists(artist.identifier):
            # Skip this artist if it already has track(s) in the playlist, and the
            # user requested unique artists.
            if self._unique_artists and related_artist in self._artists:
                continue

            yield self._get_candidate_track(related_artist)

            yield_count += 1
            if yield_count == self.MAX_ARTISTS:
                LOG.info(
                    "Reached artist cap of %d, skipping the rest", self.MAX_ARTISTS
                )
                break


def _select_track(tracks: typing.Set[Track], weight_calculator: WeightCalculator):
    """Selects a track randomly, using weight calculator to calculate each weight."""
    weights = weight_calculator.calculate(tracks)
    choice = random.choices(list(tracks), weights, k=1)[0]  # avoid importing numpy
    LOG.info("Chose track %s", str(choice))

    return choice
