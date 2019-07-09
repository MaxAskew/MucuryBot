import discord
import datetime
import io
import json
from discord.ext import commands
import matplotlib.pyplot as plt

bot = commands.Bot(command_prefix=">")
bot.remove_command("help")

f = open("token.txt", "r")
token = f.readline()
token.strip()


@bot.event
async def on_ready():
    print("Murcury Bot is ready!")


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
        name=">register", value="Registers you on the system.", inline=False
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
        plt.scatter(sender_history[1],sender_history)
        plt.plot(sender_history[1],sender_history[0])
        plt.ylabel("Money")
        plt.xlabel("Date")
        buffer = io.BytesIO()
        plt.savefig(buffer,format="png")
        plt.clf()
        buffer.seek(0)
        await ctx.send(file=discord.File(buffer,"graph.png"))



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
                    dictionary[user][0].append(amount)
                    dictionary[user][1].append(datetime.datetime.today().date())
        dictToFile("history.json",dictionary)


# Writes dictionary to a file in the form USER,DEBT
def dictToFile(fileName, diction):
    f = open(fileName, "w+")
    f.write(json.dumps(diction))


@bot.command()
async def debtArrows(ctx):
    d = fileToDict("debt.json")
    arrows = "```_Debt_\n"
    for name, amount in d.items():
        if amount < 0:
            for name2, amount2 in d.items():
                if name != name2:
                    if amount2 > 0:
                        arrows = (
                            arrows + "\n" + name + " --> " + name2 + " " + str(amount2)
                        )
                        d[name] = int(d[name]) + int(amount2)
                        d[name2] = int(d[name2]) - int(amount2)

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
    dictToFile("debt.json", {})


@bot.command()
async def register(ctx):
    d = fileToDict("debt.json")
    #Create a history dict with key as name and value as history
    history = fileToDict("history.json")
    name = str(ctx.message.author)
    if name in d or name in history:
        await ctx.send(name + " has already been registered.")
    else:
        print(d)
        d[name] = "0"
        # Initalise with 0 money

        history[name] = ([0],[str(datetime.datetime.now().date())])
        dictToFile("debt.json", d)
        dictToFile("history.json", history)
        print(d)
        await ctx.send(name + " has been registered.")


bot.run(token)
