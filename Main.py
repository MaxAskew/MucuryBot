import discord
import datetime
import io
import json
from discord.ext import commands
import matplotlib.pyplot as plt
prefix =">"
bot = commands.Bot(command_prefix=prefix)
bot.remove_command("help")

f = open("token.txt", "r")
token = f.readline()
token.strip()


@bot.event
async def on_ready():
    print("Murcury Bot is online!")
    for m in bot.get_all_members():
        register(m)
    
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Murcury Bot", description="A bot for all things Murcury.", color=0xEEE657
    )
    embed.add_field(
        name=prefix+"arrows", value="Shows who owes who what", inline=False
    )
    embed.add_field(
        name=prefix+"graph", value="Shows your graph of profit/loss", inline=False
    )
    embed.add_field(
        name=prefix+"debt @SENDER @RECIEVER X",
        value="Adds debt from @SENDER to @RECIVER by the amount X. To pay off debt leave the money ammount positive and flip the order of usernames.",
        inline=False,
    )
    embed.add_field(
        name=prefix+"register", value="Registers you on the system.", inline=False
    )
    embed.add_field(
        name=prefix+"reset", value="Wipes entire system. **!USE AT OWN RISK!**", inline=False
    )
    
    await ctx.send(embed=embed)


@bot.command()
async def graph(ctx):
    with open("history.json", "r") as h_json:
        history = json.loads(h_json.read())
        sender_name = str(ctx.message.author)
        sender_history = history[sender_name]
        
        plt.scatter(range(len(sender_history)),sender_history)
        plt.plot(range(len(sender_history)),sender_history,)
        plt.gca().axes.get_xaxis().set_visible(False)
        plt.ylabel("£ Money")
        buffer = io.BytesIO()
        plt.savefig(buffer,format="png")
        plt.clf()
        buffer.seek(0)
        await ctx.send(file=discord.File(buffer,"graph.png"))

@bot.command()
async def arrows(ctx):
    d = fileToDict("debt.json")
    arrows = "```_Debt_\n"
    for name, amm in d.items():
        amount = int(amm)
        if amount < 0:
            for name2, amm2 in d.items():
                amount2 = int(amm2)
                if name != name2:
                    if amount2 > 0:
                        arrows = (
                            arrows + "\n" + name + " --> " + name2 + " " + str(amount2)
                        )
                        d[name] = int(d[name]) + int(amount2)
                        d[name2] = int(d[name2]) - int(amount2)

    await ctx.send(arrows + "```")

@bot.command()
async def debt(ctx, sender: discord.User, reciever: discord.User, amount: int):
    d = fileToDict("debt.json")
    if str(sender)not in d:
        registerPlayer(sender)
    if str(reciever)not in d:
        registerPlayer(reciever)
    if sender.id != reciever.id:
        if amount <= 0:
            await ctx.send("Cannot have zero or negative debt!")
        else:
            
            if (str(sender) in d) != True:
                d[str(sender)] = "0"
            if (str(reciever) in d) != True:
                d[str(reciever)] = "0"

            d[str(sender)] = int(d[str(sender)]) - int(amount)
            d[str(reciever)] = int(d[str(reciever)]) + int(amount)

    dictToFile("debt.json", d)
    #Whenever a debt is added , update the history 
    updateHistory(d)
    await ctx.send(f"{sender.mention} now owes {amount} to {reciever.mention}")

@bot.command()
async def reset(ctx):
    dictToFile("debt.json", {})
    dictToFile("history.json", {})
    for m in bot.get_all_members():
        register(m)
    

def register(user):
    d = fileToDict("debt.json")
    h = fileToDict("history.json")
    name = str(user)

    if name not in d:
        d[name] = "0"
        dictToFile("debt.json", d)
    if name not in h:
        h[name] = [0]
        dictToFile("history.json", h)
        

def fileToDict(fileName):
    f = open(fileName, "r")
    diction = json.loads(f.read())
    return diction
def updateHistory(new_info):
    print(new_info)
    with open("history.json", "r") as f:
        # Load history file as json
        dictionary = json.loads(f.read())
        for user in dictionary:
            for new_user, amount in new_info.items():
                # Loop through history and current debt dict to find current user
                if user == new_user:
                    # Update the history with the users debt amount
                    dictionary[user].append(amount)
        dictToFile("history.json",dictionary)
def dictToFile(fileName, diction):
    f = open(fileName, "w+")
    f.write(json.dumps(diction))










bot.run(token)
