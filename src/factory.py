import random
import typing
import logging
from operator import attrgetter

from client import SpotifyClient
from model import Artist, Track, cartesian_distance

LOG = logging.getLogger(__name__)


class WeightCalculator:
    """
    Base class for a weight calculator, creating a class instance allows for the
    keeping of state, using previous weight calculations to adjust future weights.
    """

    def __init__(self, seed_track):
        self.last_track = None
        self.seed_track = seed_track

    def _calculate_one(self, track: Track, artist: Artist):
        raise NotImplementedError

    def calculate(self, tracks: typing.List[Track], artists: typing.List[Artist]):
        for track, artist in zip(tracks, artists):
            weight = self._calculate_one(track, artist)
            LOG.info("Weight determined to be %s", weight)
            yield weight


class PopularWeight(WeightCalculator):
    """
    Give higher weights to tracks that are more popular, produced by more popular
    artists.
    """

    def _calculate_one(self, track: Track, artist: Artist):
        LOG.info("Artist %s has popularity %s", artist.name, artist.popularity)
        LOG.info("Track %s has popularity %s", track.name, track.popularity)

        return track.popularity * artist.popularity


class SimilarWeight(WeightCalculator):
    """
    Give higher weights to tracks that are more popular, preferring songs similar to
    the previous one.
    """

    def _calculate_one(self, track: Track, artist: Artist):
        if not self.last_track:
            similarity = 1
        else:
            similarity = cartesian_distance(track, self.last_track)

        LOG.info("Artist %s has popularity %s", artist.name, artist.popularity)
        LOG.info("Track %s has popularity %s", track.name, track.popularity)
        LOG.info("Track %s has similarity %s", track.name, similarity)

        return (track.popularity * artist.popularity) / (similarity ** 4)


class DriftingWeight(WeightCalculator):
    """
    Give higher weights to tracks that are more popular, preferring tracks. similar to
    the previous one and dissimilar from the seed track..
    """

    def _calculate_one(self, track: Track, artist: Artist):
        if not self.last_track:
            # If there is no last track we cannot compute a similarity.
            previous_similarity = 1
            # Without a ``previous_similarity`` the drift would be too strong.
            seed_similarity = 1
        else:
            previous_similarity = cartesian_distance(track, self.last_track)
            seed_similarity = cartesian_distance(track, self.seed_track)

        LOG.info("Artist %s has popularity %s", artist.name, artist.popularity)
        LOG.info("Track %s has popularity %s", track.name, track.popularity)
        LOG.info(
            "Track %s has similarity %s with the previous track",
            track.name,
            previous_similarity,
        )
        LOG.info(
            "Track %s has similarity %s with the seed track",
            track.name,
            seed_similarity,
        )

        return (track.popularity * artist.popularity) * (
            seed_similarity / previous_similarity ** 2
        )


class ArtistChainFactory:
    """
    For fun, this will be an iterable.
    """

    MAX_ARTISTS = 25
    MAX_SONGS = 3

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

    def _get_candidate_tracks(self, artist: Artist):
        candidate_tracks = []
        for track in self._client.get_top_tracks(artist.identifier):
            LOG.debug("Fetched track %s", str(track))

            # Skip this track if it is already in the playlist, and the user
            # requested unique tracks.
            if self._unique_tracks and track in self._tracks:
                continue

            candidate_tracks.append(track)

        if not candidate_tracks:
            raise RuntimeError("No songs to select from.")

        random.shuffle(candidate_tracks)

        choices = [
            self._client.enrich_track(c) for c in candidate_tracks[: self.MAX_SONGS]
        ]
        LOG.info("Selected %s tracks for artist %s", len(choices), str(artist))
        return choices

    def _get_next_track(self):
        tracks_artists = list(self._get_related_tracks(self._next_track.artists[0]))
        selected_track = _select_track(
            [t for t, a in tracks_artists],
            [a for t, a in tracks_artists],
            self._weight_calculator,
        )
        self._weight_calculator.last_track = selected_track

        return selected_track

    def _get_related_tracks(self, artist: Artist):
        yield_count = 0

        # Sort related artists by descending popularity, as we might not be able to
        # loop over all artists.
        related_artists = self._client.get_related_artists(artist.identifier)
        related_artists = sorted(related_artists, key=attrgetter("popularity"))[::-1]
        LOG.info(
            "Artist popularities are %s", str([a.popularity for a in related_artists])
        )

        # Iterate over the artists, and add a song to the pool of potential songs.
        for related_artist in related_artists:
            # Skip this artist if it already has track(s) in the playlist, and the
            # user requested unique artists.
            if self._unique_artists and related_artist in self._artists:
                continue

            try:
                for track in self._get_candidate_tracks(related_artist):
                    yield track, related_artist
            except RuntimeError:
                pass

            yield_count += 1
            if yield_count == self.MAX_ARTISTS:
                LOG.info(
                    "Reached artist cap of %d, skipping the rest", self.MAX_ARTISTS
                )
                break


def _select_track(
    tracks: typing.List[Track],
    artists: typing.List[Artist],
    weight_calculator: WeightCalculator,
):
    """Selects a track randomly, using weight calculator to calculate each weight."""
    weights = list(weight_calculator.calculate(tracks, artists))
    choice = random.choices(tracks, weights, k=1)[0]  # avoid importing numpy
    LOG.info("Chose track %s", str(choice))

    return choice
