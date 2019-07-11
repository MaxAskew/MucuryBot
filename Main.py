import discord
import datetime
import io
import json
import time
import asyncio
from discord.ext import commands
import matplotlib.pyplot as plt

bot = commands.Bot(command_prefix=">")
bot.remove_command("help")

f = open("token.txt", "r")
token = f.readline()
token.strip()

def register(m):
    d = fileToDict("debt.json")
    history = fileToDict("history.json")
    name = str(m)
    d[name] = 0
    history[name] = ([0],[str(datetime.datetime.now().date())])
    dictToFile("debt.json", d)
    dictToFile("history.json",history)

@bot.event
async def on_ready():
    print("Murcury Bot is ready!")
    for m in bot.get_all_members():
        register(m)

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Murcury Bot", description="A bot for all things Murcury.", color=0xEEE657
    )
    embed.add_field(
        name=">alldebt",
        value="Shows the current total debt for all Murcury members.",
        inline=False,
    )
    embed.add_field(
        name=">adddebt @SENDER @RECIEVER X",
        value="Adds debt from @SENDER to @RECIVER by the amount X",
        inline=False,
    )
    embed.add_field(
        name=">reset", value="Wipes entire system. **!USE AT OWN RISK!**", inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
async def show_graph(ctx):
    with open("history.json", "r") as h_json:
        history = json.loads(h_json.read())
        sender_name = str(ctx.message.author)
        sender_history = history[sender_name]
        plt.scatter(sender_history[1],sender_history[0])
        plt.plot(sender_history[1],sender_history[0])
        plt.ylabel("Money")
        plt.xlabel("Date")
        buffer = io.BytesIO()
        plt.savefig(buffer,format="png")
        plt.clf()
        buffer.seek(0)
        await ctx.send(file=discord.File(buffer,"graph.png"))

    
async def session(ctx, user: discord.User, amount: float):
    d = fileToDict("debt.json")
    d[str(user)] = float(d[str(user)]) + float(amount)
    dictToFile("debt.json", d)
    if amount < 0:
        await ctx.send(str(user)+" lost "+str(amount)+" on this session.")
    else:
        await ctx.send(str(user)+" won "+str(amount)+" on this session!")
    
@bot.command(pass_context=False)
async def graph_all(ctx):
    with open("history.json", "r") as h_json:
        history = json.loads(h_json.read())
        for m in bot.get_all_members():
                sender_history = history[str(m)]
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
async def all_graphs(ctx):
    with open("history.json","r") as h_json:
        history = json.loads(h_json.read())
        for user,values in history.items():
            plt.scatter(values[1],values[0])
            plt.plot(values[1],values[0],label=user)
            plt.ylabel("Money")
            plt.xlabel("Date")
        buffer = io.BytesIO()
        plt.legend(loc='upper right')
        plt.savefig(buffer,format="png")
        plt.clf()
        buffer.seek(0)
        await ctx.send(file=discord.File(buffer,"all_graph.png"))

def fileToDict(fileName):
    f = open(fileName, "r")
    diction = json.loads(f.read())
    return diction


def updateHistory(new_info):
    with open("history.json", "r") as f:
        # Load history file as json
        dictionary = json.loads(f.read())
        for user in dictionary:
            for new_user, amount in new_info.items():
                # Loop through history and current debt dict to find current user
                if user == new_user:
                    # Update the history with the users debt amount
                    dictionary[user][0].append(amount)
                    dictionary[user][1].append(str(datetime.datetime.today().date()))
        dictToFile("history.json",dictionary)


# Writes dictionary to a file in the form USER,DEBT
def dictToFile(fileName, diction):
    f = open(fileName, "w+")
    f.write(json.dumps(diction,indent=4))

@bot.command()
async def debtArrows(ctx):
    d = fileToDict("debt.json")
    arrows = "```_Debt_\n"
    for name, amount in d.items():
        if amount < 0:
            for name2, amount2 in d.items():
                if name != name2:
                    if amount2 > 0:
                        arrows = (arrows + "\n" + name + " --> " + name2 + " " + str(amount2))
                        d[name] = float(d[name]) + float(amount2)
                        d[name2] = float(d[name2]) - float(amount2)
    
    for name, amm in d.items():
        if(float(amm)!=0):
            await ctx.send("Discrepancy detected. £"+str(float(amm)))
    await ctx.send(arrows + "```")


@bot.command()
async def alldebt(ctx):
    d = fileToDict("debt.json")
    content = ""
    if d:
        for name, amount in d.items():
            content = content + str(name) + ": " + str(amount)
    else:
        content = "There is no debt currently on the system."

    await ctx.send(content)


@bot.command()
async def adddebt(ctx, sender: discord.User, reciever: discord.User, amount: int):
    if sender.id != reciever.id:
        if amount <= 0:
            await ctx.send("Cannot have zero or negative debt!")
        else:
            d = fileToDict("debt.json")
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
    doBackup()
    dictToFile("debt.json", {})
    dictToFile("history.json", {})
    for m in bot.get_all_members():
        register(m)
    await ctx.send("All data has been wiped")
    

async def timedBackup():
    await bot.wait_until_ready()
    while not bot.is_closed():
        doBackup()
        await asyncio.sleep(43200) #backup runs every 12 hours
          

def doBackup():
    d = fileToDict("debt.json")
    h = fileToDict("history.json")
    dictToFile("backups/debt_"+time.strftime("%Y%m%d-%H%M%S")+".json", d)
    dictToFile("backups/history_"+time.strftime("%Y%m%d-%H%M%S")+".json", h)



bot.loop.create_task(timedBackup())
bot.run(token)
