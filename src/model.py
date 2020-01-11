import typing
from dataclasses import dataclass, field


@dataclass
class Artist:
    identifier: str
    name: str
    popularity: int

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __repr__(self):
        return f"<Artist instance at {id(self)}, {self.name} ({self.identifier})>"

    def __str__(self):
        return repr(self)


@dataclass
class Track:
    duration: int
    explicit: bool
    identifier: str
    name: str
    popularity: int

    artists: typing.List[Artist] = field(default_factory=lambda: list())
    key: int = None
    mode: int = None
    time_signature: int = None
    acousticness: float = None
    danceability: float = None
    energy: float = None
    instrumentalness: float = None
    liveness: float = None
    loudness: float = None
    speechiness: float = None
    valence: float = None
    tempo: float = None

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __repr__(self):
        return f"<Track instance at {id(self)}, {self.name} ({self.identifier})>"

    def __str__(self):
        return repr(self)


class Playlist(list):
    def __setitem__(self, key, value):
        if not isinstance(value, Track):
            raise TypeError("You can only store Track instances in a Playlist")
        super().__setitem__(key, value)

    def __repr__(self):
        return f"<Playlist instance at {id(self)}, {self.duration} ms, {len(self.artists)} artists, {len(self.tracks)} tracks>"

    def __str__(self):
        return repr(self)

    @property
    def duration(self) -> int:
        """Duration in milliseconds of the playlist."""
        return sum([x.duration for x in self])

    @property
    def artists(self) -> typing.Set[Artist]:
        artists = set()
        for track in self:
            artists = artists.union(set(track.artists))

        return artists

    @property
    def tracks(self) -> typing.Set[Track]:
        return set(self)
