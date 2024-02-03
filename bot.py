import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.errors import CommandError

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from concurrent.futures import ThreadPoolExecutor

import json
import os
import random

class dataToLong(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(message)

def concatenate_with_limit(input_list: list, max_length: int, separator: str=",", start_string: str="", end_string: str=""):
    """
    Function to split lists into smaller lists, so each list has an max length

    Attributes
    ----------
    input_list : list
        original list with urls or other text in it
    max_length : int
        maximum length of each string in the returned list
    separator : str = ","
        character used to split each element (default ,)
    start_string : str = ""
        string to start each string in the returned list (default None)
    end_string : str = ""
        string to end each string in the returned list (default None)
    """
    start_end_len = len(start_string) + len(end_string)

    if start_end_len >= max_length:
        raise dataToLong("Sorry, the start and end strings are too long for any other data to fit. Please change the start and/or end strings or adjust the max length.\n" + "Your start and end strings are " + str(start_end_len) + " characters long. The max length is " + str(max_length))

    result = []
    current_string = ""

    for element in input_list:
        if len(start_string) + len(current_string) + len(element) + len(separator) + len(end_string) > max_length:
            #raise dataToLong("Your data sting is expected to get to " + str(len(start_string) + len(current_string) + len(element) + len(separator) + len(end_string)) + " characters. The max length is " + str(max_length))
            result.append(start_string + current_string + end_string)
            current_string = ""
        else:
            current_string += separator + element if current_string else element
    
    result.append(start_string + current_string + end_string)

    return result

def get_first_video_url(query):
    videos_search = VideosSearch(query, limit=1)
    results = videos_search.result()

    if results['result']:
        first_video_url = results['result'][0]['link']
        return first_video_url
    else:
        return None

def spotify_api_auth(client_id, client_secret):
    # Set up Spotify API authentication
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_spotify_playlist_name(client_id, client_secret, playlist_link):
    
    playlist_id = playlist_link.split('/')[-1]
    question_mark_index = playlist_id.find('?')
    playlist_id = playlist_id[:question_mark_index]

    sp = spotify_api_auth(client_id, client_secret)    
    return sp.playlist(playlist_id)["name"]

def get_spotify_playlist_tracks(spotify_authorization, playlist_id):
    search_term_list = []
    # Get playlist tracks
    results = spotify_authorization.playlist_tracks(playlist_id)
    # Extract and print track names
    for track in results['items']:
        search_term_list.append(track['track']['artists'][0]['name'] + " " + track['track']['name'])
    
    return search_term_list

def convert_spotify_to_yt(client_id, client_secret, playlist_link, num_processes):
    playlist_id = playlist_link.split('/')[-1]
    question_mark_index = playlist_id.find('?')
    playlist_id = playlist_id[:question_mark_index]

    sp = spotify_api_auth(client_id, client_secret)

    search_term_list = get_spotify_playlist_tracks(sp, playlist_id)
    print(len(search_term_list))
    # Use ThreadPoolExecutor to run the task in a separate thread
    with ThreadPoolExecutor(max_workers=num_processes) as executor:
        yt_list = list(executor.map(get_first_video_url, search_term_list))

    return yt_list

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)
    
    async def on_ready(self):
        print(f"{self.user} is ready and online!")
        
    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)

def load():
    print(os.path.dirname(__file__))
    with open(os.path.dirname(__file__) + "/config.json", "r") as file:
        return json.load(file)

config = load()

bot = Bot()

@bot.hybrid_command(name="ping", description="Sends the bot's latency.", with_app_command=True)
async def ping(ctx):
    await ctx.reply(f"Pong! Latency is {bot.latency}", ephemeral=True)

@bot.tree.command(name="convert", description="Converts Spotify playlist to YouTube URLs.")
@app_commands.describe(playlist_link="Enter an spotify link or playlist link to convert.")
@app_commands.describe(playlist_shuffle="If True the playlist gets shuffled.")
async def convert(interaction: discord.Interaction, playlist_link: str, playlist_shuffle: bool):
    await interaction.response.defer(thinking=True, ephemeral=True)
    try:
        client_id = config["spotify_client_id"]
        client_secret = config["spotify_client_secret"]

        max_length = config["max_message_lenght"]
        num_processes = config["num_processes"]

        command_prefix = config["music_bot_command_prefix"]
        split_string = config["split_string"]
        
        playlist_name = get_spotify_playlist_name(client_id, client_secret, playlist_link)
        
        playlist_name = playlist_name.replace(" ", "_")
        
        start_string = "```" + command_prefix + config["music_bot_append_song_playlist_command"] + " " + playlist_name + " "
        create_playlist_message = "```" + command_prefix + config["music_bot_create_playlist_command"] + " " + playlist_name + "```"
        play_playlist_message = "```" + command_prefix + config["music_bot_play_playlist_command"] + " " + playlist_name + "```"
        
        yt_list = convert_spotify_to_yt(client_id, client_secret, playlist_link, num_processes)
        if playlist_shuffle:
            random.shuffle(yt_list)
        message_list = [create_playlist_message]
        message_list = message_list + concatenate_with_limit(yt_list, max_length, split_string, start_string, "```")
        message_list.append(play_playlist_message)
        for message in message_list:
            await interaction.followup.send(message, ephemeral=True)
    except Exception as e:
        print(e)
        await interaction.followup.send(f"Error: {e}", ephemeral=True)

bot.run(config["bot_token"])
