import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import os
# allows us to cycle through a list
from itertools import cycle
import requests
import json
import random
import youtube_dl
from dotenv import load_dotenv

load_dotenv()

#-----VARIABLES-----#

current = None
songlistFile = "songlist.json"
songFile = "song.mp3"
vcName = os.getenv('VOICE_CHANNEL')

#-----HELPER FUNCTIONS-----#


async def song_list():
    with open(songlistFile, "r") as f:
        songs = json.load(f)
    return songs

#-----CLASS METHODS-----#


class musicFunc(commands.Cog):
    # allows us to connect to the client by passing in client as argument
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def song(self, ctx, url: str):
        current = url
        await ctx.channel.purge(limit=1)
        await ctx.send("This'll only take a second...")
        song_there = os.path.isfile(songFile)
        try:
            if song_there:
                os.remove(songFile)
        except PermissionError:
            await ctx.send("Wait for the current playing music to end or use the 'stop' command")
            return

        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None:
            await ctx.send("Put me in the voice channel first!!")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, songFile)
        voice.play(discord.FFmpegPCMAudio(songFile))
        await ctx.channel.purge(limit=1)
        await ctx.send(f"Playing - {url}")

    @commands.command()
    async def connect(self, ctx):
        voiceChannel = discord.utils.get(
            ctx.guild.voice_channels, name=vcName)
        await voiceChannel.connect()

    @commands.command()
    async def disconnect(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await voice.disconnect()
            await ctx.channel.purge(limit=1)
        else:
            await ctx.send("I'm not even connected to the voice channel >:(")

    @commands.command()
    async def pause(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
            await ctx.channel.purge(limit=1)
        else:
            await ctx.send("um there's not any audio playing :/")

    @commands.command()
    async def play(self, ctx):
        song_there = os.path.isfile(songFile)
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
            await ctx.channel.purge(limit=1)
        elif song_there:
            voice.play(discord.FFmpegPCMAudio(songFile))
            await ctx.channel.purge(limit=1)
        else:
            await ctx.send("The playback isn't even paused yet >:(")

    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        voice.stop()
        await ctx.channel.purge(limit=1)

    @commands.command()
    async def current(self, ctx):
        if current == None:
            await ctx.send("I haven't loaded a song yet :/")
        else:
            await ctx.send(f"The song that's loaded rn is - {current}")

    @commands.command()
    async def songlist(self, ctx):
        embed = discord.Embed(title="Song List", description="Here's a list of songs I like for easy playback!",
                              color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        songs = await song_list()
        #songs = sorted(songs, reverse = True)
        for song in songs:
            title = song
            url = songs[song]
            embed.add_field(name=f"{title}", value=f"{url}", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def catalog(self, ctx, url: str, *, title=None):
        # loads songs
        songs = await song_list()
        # checks if song already entered
        # if not, adds song
        if title in songs:
            return False
        else:
            songs[title] = url

        with open(songlistFile, "w") as f:
            json.dump(songs, f)
        await ctx.send(f"{title} added!!")

    @commands.command()
    async def loop(self, ctx, amount=5):
        song_there = os.path.isfile(songFile)
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        x = amount
        while x > 0:
            if song_there:
                voice.play(discord.FFmpegPCMAudio(songFile))
                await ctx.channel.purge(limit=1)
                while voice.is_playing():
                    pass
                x -= 1
            else:
                await ctx.send("There's no song loaded!!")
        await ctx.send("Loop finished!")


def setup(client):
    client.add_cog(musicFunc(client))
