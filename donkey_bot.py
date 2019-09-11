import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.utils import get
import feedparser
import html

token = open("token.txt","r").read()

prefix = "+"
#client = discord.Client()
vclient = discord.VoiceClient
guild = discord.Guild


bot = commands.Bot(command_prefix=prefix) 

def multireplace(r, s, t):
	for i in r:
		t = t.replace(i, s)
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
			feed = feedparser.parse('http://www.teamfortress.com/rss.xml')
			for i in feed.entries:
				if i.title == "Team Fortress 2 Update Released":
					await ctx.send(i.link)                  
					await ctx.send(i.title + " " + i.published)
					await ctx.send(multireplace(["<ul>", "<li>", "</ul>", "<br/>"], "", i.description))
					break
		elif game == "CSGO":
			feed = feedparser.parse('http://blog.counter-strike.net/index.php/category/updates/feed/')
			i = feed.entries[0] #for i in feed.entries:
			await ctx.send(i.link)                  
			await ctx.send(i.title + " " + i.published)
			await ctx.send(multireplace(["<p>", "</p>", "<br />"],"", html.unescape(i.content[0].value)))
					
@bot.command()
async def join(ctx):
	channel = ctx.message.author.voice.channel
	await channel.connect()

@bot.command()
async def leave(ctx):
	channel = ctx.message.author.voice.channel
	voice = ctx.guild.voice_client
	await voice.disconnect()

# @bot.command()
# async def playsound(ctx):
	# user = ctx.message.author
	# voice_channel = user.voice.channel
	# channel = voice_channel.name
	# vc = ctx.message.author.voice.channel
	# player = vc.create_ffmpeg_player('announce_well_done.mp3')
	# player.start()
	# while not player.is_done():
		# await asyncio.sleep(1)
	# player.stop()

bot.run(token)

