from functools import lru_cache
from typing import Generator

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from model import Artist, Playlist, Track


class SpotifyClient:
    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials()
        self._spotipy = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    @lru_cache(1000)
    def get_artist(self, artist_id: str) -> Artist:
        r = self._spotipy.artist(artist_id)

        return Artist(
            name=r["name"],
            identifier=r["id"],
            popularity=r["popularity"]
        )

    def get_related_artists(self, artist_id: str) -> Generator[Artist, None, None]:
        r = self._spotipy.artist_related_artists(artist_id)

        for artist_obj in r["artists"]:
            yield self.get_artist(artist_obj["id"])

    def get_top_tracks(self, artist_id: str) -> Generator[Track, None, None]:
        r = self._spotipy.artist_top_tracks(artist_id)

        for track_obj in r["tracks"]:
            yield self.get_track(track_obj["id"])

    @lru_cache(1000)
    def get_track(self, track_id: str) -> Track:
        r = self._spotipy.track(track_id)

        artists = []
        for artist_obj in r["artists"]:
            artists.append(self.get_artist(artist_obj["id"]))

        return Track(
            artists=artists,
            duration=r["duration_ms"],
            explicit=r["explicit"],
            identifier=r["id"],
            name=r["name"],
            popularity=r["popularity"],
        )

    def store_playlist(self, playlist: Playlist):
        raise NotImplementedError
