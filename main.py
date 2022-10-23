# uses python 3.9.2 64 bit Interpreter libraries
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import os
from itertools import cycle
import requests
import json
import random
import mysql.connector
from mysql.connector import Error
import youtube_dl
from time import sleep
from dotenv import load_dotenv

load_dotenv()

#-----VARIABLES-----#
# Connection to discord
client = commands.Bot(command_prefix='#', intents=discord.Intents.all())
client.remove_command("help")

kirstenId = os.getenv('KURSE_ID')
botToken = os.getenv('TOKEN')
guildName = os.getenv('GUILD')
channelName = os.getenv('CHANNEL')
cogsPath = './cogs'
pythonExt = '.py'

customEmoji = [
    '<:bearlove:817992135084605450>',
    '<:cutebear:817992591563685999>',
    '<:flower:817984275332071444>',
    '<:check:817983160323014718>',
    '<:hug:817984488754642944>',
    '<:rupee:817983579849752586>',
    '<:withu:818679987858178058>',
    '<:crescent:818679835835891732>',
    '<:really:818680816552509460>',
    '<:spacebottle:818680206797701131>',
    '<:planet:818680114283675649>',
    '<:cuteghost:818679486576721950>',
    '<:bonk:818680348589555714>',
    '<:cuddle:818679562690494524>',
    '<:chill:818680046847393822>',
    '<:cherryblossom:818679923597377566>',
    '<:cats:818679736125227008>',
    '<:backhug:818679634739986443>',
]

statements = [
    "I wonder what it's like outside " + random.choice(customEmoji),
    "This is hard :/",
    "I feel like i'm learning new things everyday..." +
    random.choice(customEmoji),
    "I wonder what my friends are doing...",
    "Listening to Lofi makes me feel warm inside " +
    random.choice(customEmoji),
]

acts = [
    discord.Game('Minecraft'),
    discord.Activity(type=discord.ActivityType.listening,
                     name="'Sons of the Dew' Spotify"),
    discord.Activity(type=discord.ActivityType.watching,
                     name="'Attack on Titan' on CrunchyRoll"),
    discord.Game('Stardew valley'),
    discord.Activity(type=discord.ActivityType.listening,
                     name="'Lofi Hip Hop Music' on Spotify"),
    discord.Activity(type=discord.ActivityType.watching,
                     name="'Black Mirror' on Netflix"),
    discord.Game('Genshin Impact'),
    discord.Activity(type=discord.ActivityType.listening, name="Soundcloud"),
    discord.Activity(type=discord.ActivityType.watching, name="Disney+"),
    discord.Game('League of Legends'),
    discord.Activity(type=discord.ActivityType.watching, name="Hulu"),
    discord.Game('Roblox'),
    discord.Activity(type=discord.ActivityType.listening,
                     name="'Lofi Fruits Music' on Spotify"),
    discord.Game('Tiny Royale'),
    discord.Activity(type=discord.ActivityType.watching,
                     name="'Jujutsu Kaisen' on CrunchyRoll"),
    discord.Game('Valorant'),
]


#-----ON CONNECT-----#
@client.event
async def on_ready():
    # Starts the task loop
    change_task.start()
    print('{0.user} is now online.'.format(client))
    random_statement.start()

#-----COMMANDS-----#
# HELP - Display the available commands


@client.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(
        title="Commands", description="A list of everything I know how to do:", color=ctx.author.color)
    em.add_field(name="Moderation",
                 value="kick, ban, unban, ping, clear, user, version")
    em.add_field(
        name="Social", value="inspire, thank, coinflip, encourage, pc98")
    em.add_field(
        name="Music", value="connect, disconnect, song, play, pause, stop, current, songlist, catalog")
    em.add_field(
        name="Gifs", value="punch, slap, kiss, hug, cuddle, pet, stab")
    em.add_field(
        name="Economy", value="balance, withdraw, deposit, send, slots, gift, rob, shop, buy, sell, inventory, leaderboard")
    em.add_field(name="Main", value="l, u, r")

    await ctx.send(embed=em)

# COGs allow for the creation and inclusion/editing of functions without rerunning main file (would cause bot to go offline temporarily)


# Load specified cog
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} loaded!')

# Unload specified cog


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} unloaded!')

# Reload specified cog


@client.command()
async def reload(ctx, extension):
    client.reload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} reloaded!')

# loads all cog extensions
for filename in os.listdir(cogsPath):
    if filename.endswith(pythonExt):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f'Extensions loaded!')

#-----TASK LOOPS-----#
# Updates task


@tasks.loop(minutes=random.randint(10, 30))
async def change_task():
    await client.change_presence(activity=random.choice(acts))

# Sends a random message


@tasks.loop(minutes=random.randint(30, 100))
async def random_statement():
    for guild in client.guilds:
        if str(guild) == guildName:
            for channel in guild.channels:
                if str(channel) == channelName:
                    await channel.send(random.choice(statements))

# To run in terminal, use command: python <filename>
client.run(botToken)
