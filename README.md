# Spotify similar artists chain

A tool that, when provided with an artist or song, will create a playlist by hopping from artist to artist through similar artists.
The tool will prefer more popular artists and more popular tracks, to prevent it from walking into obscure corners of Spotify.
The result is a playlist that will take you gradually from artist to artist without wild genre jumps.

## TO DO

- Making a PIP-installable command line tool would be neat
- Use a similarity metric (song metadata) instead of only weighing using popularity
- Select from the pool of artist x songs, not artist then song
- Write my own client, that returns dataclasses?
- Add a "direction", e.g. higher BPM
- Filter on correct market availability
