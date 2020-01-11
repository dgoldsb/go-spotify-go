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
    def enrich_track(self, track: Track) -> Track:
        r = self._spotipy.track(track.identifier)

        artists = []
        for artist_obj in r["artists"]:
            artists.append(self.get_artist(artist_obj["id"]))

        track.artists = artists

        r = self._spotipy.audio_features([track.identifier])

        track.key = r[0]["key"]
        track.mode = r[0]["mode"]
        track.time_signature = r[0]["time_signature"]
        track.acousticness = r[0]["acousticness"]
        track.danceability = r[0]["danceability"]
        track.energy = r[0]["energy"]
        track.instrumentalness = r[0]["instrumentalness"]
        track.liveness = r[0]["liveness"]
        track.loudness = r[0]["loudness"]
        track.speechiness = r[0]["speechiness"]
        track.valence = r[0]["valence"]
        track.tempo = r[0]["tempo"]

        return track

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
            yield Artist(
                name=artist_obj["name"],
                identifier=artist_obj["id"],
                popularity=artist_obj["popularity"],
            )

    def get_top_tracks(self, artist_id: str) -> Generator[Track, None, None]:
        r = self._spotipy.artist_top_tracks(artist_id)

        for track_obj in r["tracks"]:
            yield Track(
                duration=track_obj["duration_ms"],
                explicit=track_obj["explicit"],
                identifier=track_obj["id"],
                name=track_obj["name"],
                popularity=track_obj["popularity"],
            )

    @lru_cache(1000)
    def get_track(self, track_id: str) -> Track:
        r = self._spotipy.track(track_id)

        artists = []
        for artist_obj in r["artists"]:
            artists.append(self.get_artist(artist_obj["id"]))

        return self.enrich_track(Track(
            artists=artists,
            duration=r["duration_ms"],
            explicit=r["explicit"],
            identifier=r["id"],
            name=r["name"],
            popularity=r["popularity"],
        ))

    def store_playlist(self, playlist: Playlist):
        raise NotImplementedError
