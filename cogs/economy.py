import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import os
from itertools import cycle
import requests
import json
import random
from dotenv import load_dotenv

load_dotenv()

#-----VARIABLES-----#
cogsPath = os.getenv('COG_PATH')
bankFile = "mainbank.json"


os.chdir(cogsPath)
item_images = [
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

# List of dictionaries, items that will be in the shop. Should put these in a JSON file instead
mainshop = [
    {"name": "pc98 Vintage Card", "price": 50,
        "description": "A step into the nostalgia of Gameboy and pc98"}
]

#-----HELPER FUNCTIONS-----#


async def validate_user():
    return True


async def open_account(user):
    # loads bank users
    users = await bank_data()
    # If user already has an account, return false
    # If not, creates account and adds to mainbank.json, then return true
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open(bankFile, "w") as f:
        json.dump(users, f)
    return True


async def bank_data():
    # Opens json file and loads users
    with open(bankFile, "r") as f:
        users = json.load(f)
    return users


async def update_bank(user, change=0, mode="wallet"):
    users = await bank_data()
    users[str(user.id)][mode] += change

    with open(bankFile, "w") as f:
        json.dump(users, f)

    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
    return bal


async def buy_item(user, item_name, amount):
    # makes all lowercase for easier comparisons
    item_name = item_name.lower()
    name_ = None
    # cycles through shop items to find desired item, if item in shop, sets to price. If not, returns error code 1
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break
    if name_ == None:
        return [False, 1]

    # pulls user bank data, wallet and bank amount
    cost = price * amount
    users = await bank_data()
    bal = await update_bank(user)

    # If user doesn't have enough money
    if bal[0] < cost:
        return [False, 2]

    # checks if item is already in user inventory, if so, updates amount
    # if item not already in Inventory, adds item to Inventory
    # if no inventory, creates inventory for user and adds item
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["Inventory"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old+amt + amount
                users[str(user.id)]["Inventory"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["Inventory"].append(obj)
    except:
        obj = {"item": item_name, "amount": amount}
        users[str(user.id)]["Inventory"] = [obj]

    # updates mainbank file
    with open(bankFile, "w") as f:
        json.dump(users, f)

    # updates user wallet amount to reflect purchase
    await update_bank(user, cost*-1, "wallet")
    return [True, "Worked"]


async def sell_this(user, item_name, amount, price=None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price == None:
                price = item["price"]
            break

    if name_ == None:
        return [False, 1]
    cost = price * amount

    users = await bank_data()
    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["Inventory"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False, 2]
            users[str(user.id)]["Inventory"][index]["amount"] = new_amt
            t = 1
            break
        index += 1
        if t == None:
            return [False, 3]

    except:
        return [False, 3]
    with open(bankFile, "w") as f:
        json.dump(users, f)

    await update_bank(user, cost, "wallet")

    return [True, "Worked"]

#-----CLASS METHODS-----#


class economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    #---BANK METHODS---#
    @commands.command()
    async def balance(self, ctx):
        # Could also store in a variable for checking if user has an account
        # Calls open account for the message author
        await open_account(ctx.author)
        # Sets user to the author
        user = ctx.author
        # Pulls all bank users
        users = await bank_data()

        # Sets wallet and bank amount to their values
        wallet_amt = users[str(user.id)]["wallet"]
        bank_amt = users[str(user.id)]["bank"]

        # Creates an embed displaying all of this information
        em = discord.Embed(title=f"{ctx.author.name}'s Rupees <:rupee:817983579849752586>",
                           color=discord.Color.from_rgb(252, 83, 230))
        em.add_field(name="Pocket:", value=wallet_amt, inline=True)
        em.add_field(name="Storage:", value=bank_amt, inline=True)
        em.set_footer(icon_url=self.client.user.avatar_url,
                      text=f"Use these to buy shop items -{self.client.user.name}")
        # await ctx.channel.purge(limit = 1)
        await ctx.send(embed=em)

    @commands.command()
    async def withdraw(self, ctx, amount=None):
        await open_account(ctx.author)

        if amount == None:
            await ctx.send("You didn't specify an amount :/")
            return
        bal = await update_bank(ctx.author)

        amount = int(amount)
        if amount > bal[1]:
            await ctx.send("That's more than you have!!")
            return
        if amount < 0:
            await ctx.send("Haha you can't withdraw negatives " + random.choice(custEmoji))
            return

        await update_bank(ctx.author, amount)
        await update_bank(ctx.author, -1 * amount, "bank")

        await ctx.send(f"{amount} rupees moved to pocket!! <:rupee:817983579849752586>")

    @commands.command()
    async def deposit(self, ctx, amount=None):
        await open_account(ctx.author)

        if amount == None:
            await ctx.send("You didn't specify an amount :/")
            return
        bal = await update_bank(ctx.author)

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send("That's more than you have!!")
            return
        if amount < 0:
            await ctx.send("Haha you can't deposit negatives " + random.choice(custEmoji))
            return

        await update_bank(ctx.author, -1 * amount)
        await update_bank(ctx.author, amount, "bank")

        await ctx.send(f"{amount} rupees put in storage!! <:rupee:817983579849752586>")

    @commands.command()
    async def send(self, ctx, member: discord.Member, amount=None):
        await open_account(ctx.author)
        await open_account(member)

        if amount == None:
            await ctx.send("You didn't specify an amount :/")
            return
        bal = await update_bank(ctx.author)
        if amount == "all":
            amount = bal[0]

        amount = int(amount)
        if amount > bal[1]:
            await ctx.send("That's more than you have!!")
            return
        if amount < 0:
            await ctx.send("Haha you can't deposit negatives " + random.choice(custEmoji))
            return

        await update_bank(ctx.author, -1 * amount, "bank")
        await update_bank(member, amount, "bank")

        await ctx.send(f"{ctx.author} sent {member} {amount} rupees!!" + random.choice(custEmoji))

    @commands.command()
    @commands.check(validate_user())
    async def slots(self, ctx, amount=None):
        await open_account(ctx.author)

        if amount == None:
            await ctx.send("You didn't specify an amount :/")
            return
        bal = await update_bank(ctx.author)

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send("That's more than you have!!")
            return
        if amount < 0:
            await ctx.send("Haha you can't deposit negatives " + random.choice(custEmoji))
            return

        final = []
        for i in range(3):
            a = random.choice(custEmoji)
            final.append(a)

        em = discord.Embed(
            title=f"SLOTS", color=discord.Color.from_rgb(252, 83, 230))
        em.add_field(name="results", value=final, inline=True)
        await ctx.send(embed=em)
        if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
            await update_bank(ctx.author, 2*amount)
            await ctx.send("You won the slots!! Double ur betsss" + random.choice(custEmoji))
            await ctx.send(f"{2*amount} rupees deposited <:rupee:817983579849752586>")
        else:
            await update_bank(ctx.author, -1 * amount)
            await ctx.send("You got it next time, maybe...")

    # should be used by the bot or restricted with checks

    @commands.command()
    @commands.check(validate_user())
    async def gift(self, ctx):
        await open_account(ctx.author)
        user = ctx.author
        users = await bank_data()

        # sets gift amount to random int between 0 and 15
        earnings = random.randrange(15)
        await ctx.send(f"Kaede gave you {earnings} rupees!! <:rupee:817983579849752586>")

        # adds the gift to wallet
        users[str(user.id)]["wallet"] += earnings

        # updates/saves the info
        with open(bankFile, "w") as f:
            json.dump(users, f)

    @commands.command()
    async def rob(self, ctx, member: discord.Member):
        await open_account(ctx.author)
        await open_account(member)

        bal = await update_bank(member)

        if bal[0] < 50:
            await ctx.send("They barely have any rupees!!")
            return

        earnings = random.randrange(10, 25)

        await update_bank(ctx.author, earnings)
        await update_bank(member, -1 * earnings)

        await ctx.send(f"{ctx.author} stole {earnings} rupees from {member}!!" + random.choice(custEmoji))

    #---SHOP METHODS---#
    @commands.command()
    async def shop(self, ctx):
        em = discord.Embed(title="<:spacebottle:818680206797701131> DAILY SHOP <:spacebottle:818680206797701131>",
                           color=discord.Color.from_rgb(255, 122, 253))

        for item in mainshop:
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            em.add_field(
                name=name, value=f"{price} <:rupee:817983579849752586> | {desc}")
            em.set_image(url=random.choice(item_images))

        em.set_footer(icon_url=ctx.author.avatar_url,
                      text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=em)

    @commands.command()
    async def buy(self, ctx, item, amount=1):
        await open_account(ctx.author)

        res = await buy_item(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That's not in the shop!! " + random.choice(custEmoji))
            if res[1] == 2:
                await ctx.send(f"Haha you know you don't have enough money to buy {amount} of those, right? " + random.choice(custEmoji))
                return

        await ctx.send(f"{ctx.author} just bought {amount} {item}!!" + random.choice(custEmoji))

    @commands.command()
    async def sell(self, ctx, item, amount=1):
        await open_account(ctx.author)

        # can manipulate the parameters to "use" an item, then make it disappear, leaving the user with nothing
        res = await sell_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That item isn't there!! " + random.choice(custEmoji))
                return
            if res[1] == 2:
                await ctx.send(f"You don't have {amount} {item} in your Inventory " + random.choice(custEmoji))
                return
            if res[1] == 3:
                await ctx.send(f"You don't have {item} in your Inventory " + random.choice(custEmoji))
                return

            await ctx.send(f"{ctx.author} just sold {amount} {item}!! " + random.choice(custEmoji))

    @commands.command()
    async def inventory(self, ctx):
        await open_account(ctx.author)
        user = ctx.author
        users = await bank_data()
        em = discord.Embed(title=f"{ctx.author.name}'s Inventory",
                           color=discord.Color.from_rgb(104, 102, 204))
        em.set_thumbnail(url=ctx.author.avatar_url)

        try:
            inv = users[str(user.id)]["Inventory"]
        except:
            inv = []
            em.add_field(
                name='Empty', value='There are no items in your inventory!')

        for item in inv:
            name = item["item"]
            amount = item["amount"]

            em.add_field(name=name, value=amount)

        await ctx.send(embed=em)

    @commands.command()
    async def leaderboard(self, ctx, x=3):
        users = await bank_data()
        leader_board = {}
        total = []
        for user in users:
            name = int(user)
            total_amount = users[user]["wallet"] + users[user]["bank"]
            leader_board[total_amount] = name
            total.append(total_amount)

        total = sorted(total, reverse=True)

        em = discord.Embed(title=f"<:rupee:817983579849752586> WEALTHIEST {x} GUILD MEMBERS <:rupee:817983579849752586>",
                           description=f"Decided by member's total rupee holdings {random.choice(custEmoji)} -{self.client.user.name}", color=discord.Color.from_rgb(218, 165, 32))
        index = 1
        for amt in total:
            id_ = leader_board[amt]
            member = self.client.get_user(id_)
            name = member
            em.add_field(
                name=f"{index}. {name.name}                 {amt} rupees", value='.', inline=False)
            #em.add_field(name = f"{index}. {name.name}                 {amt} rupees", value = f"{amt} rupees", inline = False)
            if index == x:
                break
            else:
                index += 1
        id_ = leader_board[amt]
        member = self.client.get_user(id_)
        #em.set_thumbnail(url = member.avatar_url)
        await ctx.send(embed=em)


def setup(client):
    client.add_cog(economy(client))
