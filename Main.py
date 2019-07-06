import discord
import datetime
import json
from discord.ext import commands

bot = commands.Bot(command_prefix='>')
bot.remove_command('help')

f = open("token.txt", 'r')
token = f.readline()
token.strip()


@bot.event
async def on_ready():
    print("Murcury Bot is ready!")

@bot.command()
async def help(ctx):
	embed = discord.Embed(title="Murcury Bot", description="A bot for all things Murcury.", color=0xeee657)
	embed.add_field(name=">alldebt", value="Shows the current total debt for all Murcury members.", inline=False)
	embed.add_field(name=">adddebt @SENDER @RECIEVER X", value="Adds debt from @SENDER to @RECIVER by the ammount X" , inline=False)
	embed.add_field(name=">register", value="Registers you on the system." , inline=False)
	embed.add_field(name=">reset", value="Wipes entire system. **!USE AT OWN RISK!**" , inline=False)
	await ctx.send(embed=embed)
    
#Creates a dictionary in the form USER:DEBT
def fileToDict(fileName):
	f = open(fileName, 'r')
	diction = json.loads(f.read())
	return diction
	

#Writes dictionary to a file in the form USER,DEBT
def dictToFile(fileName, diction):
 	f = open(fileName, 'w+')
 	f.write(json.dumps(diction))
	
@bot.command()
async def debtArrows(ctx):
	d = fileToDict("debt.txt")
	arrows="```_Debt_\n"
	for name, ammount in d.items():
		
		if(ammount < 0):
			for name2, ammount2 in d.items():
				if(name!=name2):
					if(ammount2>0):
						arrows = arrows + "\n"+name+" --> "+name2+" "+str(ammount2)
						d[name] = int(d[name]) + int(ammount2)
						d[name2] = int(d[name2]) - int(ammount2)
						
	await ctx.send(arrows+"```")	
	

@bot.command()
async def alldebt(ctx):
	d = fileToDict("debt.txt")
	content=""
	if(d):
		for name, ammount in d.items():
			content = content + str(name)+": "+str(ammount)
		
	else:
		content = "There is no debt currently on the system."
		
	await ctx.send(content)

@bot.command()
async def adddebt(ctx, sender : discord.User, reciever : discord.User, ammount : int):
	if(sender.id != reciever.id):
		if(ammount <=0):
			await ctx.send("Cannot have zero or negative debt!")
		else:
			d = fileToDict("debt.txt")
			if((str(sender) in d) != True ):
				d[str(sender)] = "0"
			if((str(reciever) in d) != True ):
				d[str(reciever)] = "0"

			d[str(sender)] = int(d[str(sender)]) - int(ammount)
			d[str(reciever)] =  int(d[str(reciever)]) + int(ammount) 
			
	dictToFile("debt.txt",d)
	await ctx.send(f'{sender.mention} now owes {ammount} to {reciever.mention}')
	

@bot.command()
async def reset(ctx):
	dictToFile("debt.txt",{})

@bot.command()
async def register(ctx):
	d = fileToDict("debt.txt")
	name = str(ctx.message.author)
	if(name in d):
		await ctx.send(name+" has already been registered.")
	else:
		print(d)
		d[name] = "0"
		dictToFile("debt.txt",d)
		print(d)
		await ctx.send(name+" has been registered.")
	
	


bot.run(token)
