import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import os
from itertools import cycle
import requests
import json
import random
# Integrating nueral network
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from dotenv import load_dotenv

load_dotenv()

#-----VARIABLES-----#
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbotmodel.h5')

galleryUrl = 'https://postimg.cc/gallery/qtZsvK8'
quotesUrl = "https://zenquotes.io/api/random"
botName = os.getenv('BOT_NAME')

convoTag = '-'

custEmoji = [
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
objEmoji = [
    '<:flower:817984275332071444>',
    '<:crescent:818679835835891732>',
    '<:spacebottle:818680206797701131>',
    '<:planet:818680114283675649>',
    '<:cherryblossom:818679923597377566>'
]
actEmoji = [
    '<:backhug:818679634739986443>',
    '<:cats:818679736125227008>',
    '<:chill:818680046847393822>',
    '<:cuddle:818679562690494524>',
    '<:withu:818679987858178058>',
    '<:hug:817984488754642944>',
    '<:cutebear:817992591563685999>',
    '<:bearlove:817992135084605450>'
]


itemImages = [
    "https://i.postimg.cc/J07ysb3Q/cityalley.png",
    "https://i.postimg.cc/nrsJSrnJ/classroom.png",
    "https://i.postimg.cc/9fWj5Jc1/croissant.png",
    "https://i.postimg.cc/Jn0Vt0Dk/itachi.png",
    "https://i.postimg.cc/85Y8vGMn/magicalsky.png",
    "https://i.postimg.cc/TYgwTNXX/mcdonalds.png",
    "https://i.postimg.cc/667qm5jq/mountainroad.png",
    "https://i.postimg.cc/T15zqsc2/mysticalsky.png",
    "https://i.postimg.cc/LhdryVyt/nap.png",
    "https://i.postimg.cc/pLvdrQ25/nightcity.png",
    "https://i.postimg.cc/WpQzLLCn/nightisland.png",
    "https://i.postimg.cc/mgSgHcDX/nightpyramids.png",
    "https://i.postimg.cc/d0ttmqZq/overgrowncity.png",
    "https://i.postimg.cc/CKPMcWbb/pinksky.png",
    "https://i.postimg.cc/Kz1GwJ5w/redsky.png",
    "https://i.postimg.cc/435smjWr/relax.png",
    "https://i.postimg.cc/bwfhLqM7/shower.png",
    "https://i.postimg.cc/RVHmcWP1/siblings.png",
    "https://i.postimg.cc/0QyxmZ3r/templenight.png",
    "https://i.postimg.cc/5yZMhJtF/tokyosubs.png",
    "https://i.postimg.cc/G3Nr8Fjh/waterfall.png",
    "https://i.postimg.cc/85XGbMQ4/windowclassroom.png"
]
thankStatements = [
    "Thanksss" + random.choice(actEmoji),
    "Thank you! uwu",
    "Thank u sm" + random.choice(actEmoji)
]
coin = [
    "Heads <:cutebear:817992591563685999>",
    "Tails <:cutebear:817992591563685999>"
]
encouragements = [
    "It's okay :/",
    "You're a great person!" + random.choice(actEmoji),
    "Keep pushing through!",
    "It's okay, you're strong, you can make it through" +
    random.choice(actEmoji),
    "Don't worry... i'm sure things will get better" + random.choice(actEmoji),
    "I beleive in you" + random.choice(actEmoji)
]


#-----HELPER FUNCTIONS-----#
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # Sort by probability in reverse order, highest probability first
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    # return list full of intents and probabilities
    return return_list


def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']

    # added code to test if pieces of code work - successful. many more capabilities.
    if tag == "exit":
        print("Going offline.")
        quit()

    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


def get_quote(self):
    response = requests.get(quotesUrl)
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

#-----CLASS METHODS-----#


class socFunc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def inspire(self, ctx):
        quote = get_quote(self)
        await ctx.send("<:flower:817984275332071444> Here's some inspiration <:flower:817984275332071444>")
        await ctx.send(quote)

    @commands.command()
    async def thank(self, ctx, user):
        await ctx.send(f'{random.choice(thankStatements)} {user}')

    @commands.command()
    async def coinflip(self, ctx):
        await ctx.send("The coinflip is:\n" + random.choice(coin))

    @commands.command()
    async def encourage(self, ctx, user=''):
        await ctx.send(f'{random.choice(encouragements)} {user}')

    @commands.command()
    async def pc98(self, ctx):
        embed = discord.Embed(color=discord.Color.blue())
        # Sends an embedded image, using the url
        embed.set_image(url=random.choice(itemImages))
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        # makes then entire message lowercase
        msg = message.content.lower()

        # neural network
        if msg.startswith(convoTag):
            msg = msg.split(convoTag)
            msg = msg[1]
            ints = predict_class(msg)
            res = get_response(ints, intents)
            await message.channel.send(res)

        if botName in message.content.lower():
            await message.add_reaction(random.choice(objEmoji))

        # overwriting on_message stops commands from being processes, this line fixes that
        # await self.client.process_commands(message)


def setup(client):
    client.add_cog(socFunc(client))
