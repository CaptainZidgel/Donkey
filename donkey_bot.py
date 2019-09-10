import discord
from discord.ext import commands
import feedparser
token = open("token.txt","r").read()

prefix = "+"
#client = discord.Client()

bot = commands.Bot(command_prefix=prefix) 
tf2feed = feedparser.parse('http://www.teamfortress.com/rss.xml')

def multireplace(r, s, t):
	for i in r:
		t = t.replace(i, "")
	return t

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	
@bot.event
async def on_message(message):
	await bot.process_commands(message)
	if message.author == bot.user:
		return

@bot.command()
async def exit(ctx):
	await bot.close()
	
@bot.command()
async def ping(ctx):
	await ctx.send("pong")

@bot.command()
async def hello(ctx):
	await ctx.send("Hello!")
	
@bot.command()
async def say(ctx, *, content:str):
	await ctx.send(content)
	
@bot.command()
async def get(ctx, game:str):
		if game == "TF2":
			for i in tf2feed.entries:
				if i.title == "Team Fortress 2 Update Released":
					await ctx.send(i.link)                  
					await ctx.send(i.title + " " + i.published)
					await ctx.send(multireplace(["<ul>", "<li>", "</ul>", "<br/>"], "", i.description))
					break
bot.run(token)

