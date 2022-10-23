import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import requests
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()

#-----VARIABLES-----#
tenorKey = os.getenv('TENOR_KEY')
tenorLink = "https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s"

#-----HELPER FUNCTIONS-----#


def get_gif(self, search):
    apikey = tenorKey
    lmt = 12

    # search
    search_term = f"anime {search}"

    # get the top <lmt> GIFs for the search term
    r = requests.get(tenorLink % (search_term, apikey, lmt))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        gifs = json.loads(r.content)
        gif_url = gifs['results'][random.randint(0, lmt - 1)]['url']
        print(gif_url)
        return gif_url
    else:
        gifs = None

#----CLASS METHODS-----#


class gif(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def gif(self, ctx, search, user):
        gif = get_gif(self, f'{search}')
        await ctx.send(f"{ctx.message.author.mention} {search} {user}")
        await ctx.send(gif)


def setup(client):
    client.add_cog(gif(client))
