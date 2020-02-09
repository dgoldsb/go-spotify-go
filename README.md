# Spotify similar artists chain

A tool that, when provided with an artist or song, will create a playlist by hopping from artist to artist through similar artists.
The tool will prefer more popular artists and more popular tracks, to prevent it from walking into obscure corners of Spotify.
The result is a playlist that will take you gradually from artist to artist without wild genre jumps.

This tool can be considered as a semi-random walker that is drawn to more popular artists, and cannot visit the exact same place twice.

## TO DO

- Use a similarity metric (song metadata) instead of only weighing using popularity, now the jumps can still be pretty radical
- Add a "direction", e.g. higher BPM, most dis-similar yet still related artist
- Making a PIP-installable command line tool would be neat
- Filter on correct market availability
- Have a Dockerfile that makes sense, as currently user input is required, maybe run a small webserver that you provide your token and preferred settings to
