# SpotifyLinkConverter
A Discord bot to convert Spotify Playlists into youtube links
<hr>

# How to set up SpotifyLinkConverter


- Install python 3 or newer
- If you don't already have a Discord Bot, create one [here](https://discord.com/developers/applications/)
- If you don't already have a Spotify API application, create one [here](https://developer.spotify.com/dashboard/create)
- Clone this repo using `git clone https://github.com/xXxNIKIxXx/SpotifyLinkConverter.git .`
- Create a config.json file that looks like this:
```json
{
    "bot_token": "DISCORD_BOT_TOKEN",
    "spotify_client_id": "SPOTIFY_CLIENT_ID",
    "spotify_client_secret": "SPOTIFY_CLIENT_SECRET",
    "max_message_lenght": 2000,
    "num_processes": 16,
    "split_string": "HOW TO APPEND MULTIPLE LINKS TO YOU PLAYLIST",
    "music_bot_command_prefix": "DISCORD MUSIC BOT COMMAND PREFIX",
    "music_bot_play_playlist_command": "DISCORD MUSIC BOT PLAY PLAYLIST COMMAND",
    "music_bot_create_playlist_command": "DISCORD MUSIC BOT CREATE PLAYLIST COMMAND",
    "music_bot_append_song_playlist_command": "DISCORD MUSIC BOT APPEND SONG TO PLAYLIST COMMAND"
}
```
this struckture can also been seen in `config.json.example`

### Simple Python run
- Install all python requirements using: `pip install --no-cache-dir -r ./requirements.txt`
- Run the Bot using
```sh 
python ./bot.py
```
### Run as Service
- Install all python requirements using: `pip install --no-cache-dir -r ./requirements.txt`

#### Linux
- Create service file using: `nano /etc/systemd/system/SpotifyLinkConverter.service`
- Config your Service. This should look like this:
```ini
[Unit]
Description = Spotify Link Converter
After = network.target
[Service]
Type=simple
User = root
Restart = on-failure
RestartSec = 5
TimeoutStartSec = infinity
TimeoutSec = 7
ExecStart=/usr/bin/python3 PATH TO YOUR CLONED REPO/bot.py
[Install]
WantedBy=multi-user.target
```
- Save and run: `systemctl start SpotifyLinkConverter`

### Running using Docker
- Install Docker
- Set up your compose file or use the provided one
```yaml
version: '3'
services:
   spotify-link-converter:
      build:
         context: https://github.com/xXxNIKIxXx/SpotifyLinkConverter.git
      volumes:
         - PATH TO YOU CONFIG FILE:/app/config.json # Replace the first path with your config path
```
- Run `docker compose up`