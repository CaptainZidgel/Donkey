import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.utils import get
import feedparser
import html
import re
import csv

token = open("token.txt","r").read()

prefix = "+"
#client = discord.Client()
vclient = discord.VoiceClient
guild = discord.Guild
#song = discord.FFmpegPCMAudio('fx/announcer_well_done.mp3',executable='ffmpeg')

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
			i = feed.entries[0]
			await ctx.send(i.link)                  
			await ctx.send(i.title + " " + i.published)
			await ctx.send(multireplace(["<p>", "</p>", "<br />"],"", html.unescape(i.content[0].value)))
		elif game == "news":
			feed = feedparser.parse('news feed') # You can put a very long news feed here, this code will enable up to 10,000 characters to be pasted via 4 messages.
			i = feed.entries[0]
			await ctx.send(i.link)                  
			await ctx.send(i.title + " " + i.published)
			text = multireplace(["<p>", "</p>", "<br />"],"", html.unescape(i.content[0].value)) # unfortunately depending on the feed there are too many things to cut out.
			if len(text) > 2000:
				await ctx.send(text[:2001])
				await ctx.send(text[2001:4001])
				await ctx.send(text[4001:6001])
				await ctx.send(text[6001:10001])
			else:
				await ctx.send(text)
		else:
			with open('feeds.csv','r') as f:
				readCSV = csv.reader(f, delimiter=',')
				for row in readCSV:
					if row[1] == game:
						feed = feedparser.parse(row[2])
						i = feed.entries[0]
						await ctx.send(i.link)                  
						await ctx.send(i.title + " " + i.published)
						if row[0] != "yt":
							if row[3] != "yes":
								await ctx.send(re.sub('<[^>]+>', '', html.unescape(i.content[0].value)))
							else:
								text = re.sub('<[^>]+>', '', html.unescape(i.content[0].value))
								await ctx.send(text[:2000])
								await ctx.send(text[2000:4000])
								await ctx.send(text[4000:6000])
								await ctx.send(text[6000:10000])
						break
					else:
						print("False")
@bot.command()
async def join(ctx):
	channel = ctx.message.author.voice.channel
	await channel.connect()

@bot.command()
async def leave(ctx):
	channel = ctx.message.author.voice.channel
	voice = ctx.guild.voice_client
	await voice.disconnect()

@bot.command()
async def add(ctx, link:str, name:str, long:str = "no"):
		if link.startswith('https://www.youtube.com') or link.startswith('www.youtube.com'):
			type = "yt"
		else:
			type = "text"
		with open('feeds.csv', 'a') as f:
			if type == "yt":
				link = link.replace('channel/', 'feeds/videos.xml?channel_id=')
			f.write(type + "," + name + "," + link + "," + long + "\n")
			
# @bot.command() # I'm not sure I'll ever get this working. There doesn't appear to be sufficient documentation online with solid examples and guiding, only API refernece.
# async def playsound(ctx):
	# #chan = ctx.message.author.voice.channel
	# vc = ctx.message.author.voice.channel
	# vclient.play(source)
	# while not player.is_done():
		# await asyncio.sleep(1)
	# player.stop()

bot.run(token)

