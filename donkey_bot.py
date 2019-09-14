import discord
from discord.ext import commands
from discord.utils import get
import feedparser
import html
import re
import csv
import asyncio

token = open("token.txt","r").read()
client = discord.Client()
prefix = "+"
guild = discord.Guild
bot = commands.Bot(command_prefix=prefix) 
delim = "|"
lastposts = {}

def multireplace(r, s, t):
	for i in r:
		t = t.replace(i, s)
	return t

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	bot.loop.create_task(task())
	
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
async def get(ctx, fName:str):
	await post(ctx.channel.id, fName)
	
async def post(c, fName, title_only=False, t_o_feed=""):
	if title_only:
		feed = feedparser.parse(t_o_feed)
		for i in feed.entries:
			return i.title
	else:	
		channel = bot.get_channel(c)
		if fName == "TF2":
			feed = feedparser.parse('http://www.teamfortress.com/rss.xml')
			for i in feed.entries:
				if i.title == "Team Fortress 2 Update Released":
					await channel.send(i.link)                  
					await channel.send(i.title + " " + i.published)
					await channel.send(re.sub('<[^>]+>', "", i.description))
					break
		elif fName == "CSGO":
			feed = feedparser.parse('http://blog.counter-strike.net/index.php/category/updates/feed/')
			i = feed.entries[0]
			await channel.send(i.link)                  
			await channel.send(i.title + " " + i.published)
			await channel.send(re.sub('<[^>]+>',"", html.unescape(i.content[0].value)))
		elif fName == "news":
			feed = feedparser.parse('news feed') # You can put a very long news feed here, this code will enable up to 10,000 characters to be pasted via 4 messages.
			i = feed.entries[0]
			await channel.send(i.link)                  
			await channel.send(i.title + " " + i.published)
			text = re.sub('<[^>]+>',"", html.unescape(i.content[0].value)) # the 'content[0].value' part is tailored to my local news site I was using for testing. oops. this is just a template anyway.
			if len(text) > 2000:
				await channel.send(text[:2001])
				await channel.send(text[2001:4001])
				await channel.send(text[4001:6001])
				await channel.send(text[6001:10001])
			else:
				await channel.send(text)
		else:
			with open('feeds.csv','r') as f:
				readCSV = csv.reader(f, delimiter=delim)
				for row in readCSV:
					if row[1] == fName:
						feed = feedparser.parse(row[2])
						i = feed.entries[0]
						await channel.send(i.link)                  
						await channel.send(i.title + " " + i.published)
						if row[0] != "yt":
							await channel.send(re.sub('<[^>]+>', '', html.unescape(i.description)))
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
			f.write(type +delim + name + delim+ link +delim + long + "\n")

@bot.command()
async def sub(ctx, name:str):
	copy = "empty"
	with open('feeds.csv','r') as f:
		readCSV = csv.reader(f, delimiter=delim)
		for row in readCSV:
			if row[1] == name:
				copy = row[0]+delim+row[1]+delim+row[2]+delim+row[3]+delim
	with open('subs.csv','a') as f:
		f.write(copy + str(ctx.channel.id)+delim + "\n")
	lastposts[name] = ""
		
async def task():
	while True:
		await asyncio.sleep(30)
		print("30 seconds have elapsed")
		with open('subs.csv','r') as f:
			subscriptions = csv.reader(f, delimiter=delim)
			for row in subscriptions:
				newpost = await post(0, "none", True, row[2])
				if not row[1] in lastposts:
					lastposts[row[1]] = newpost
				if lastposts[row[1]] == newpost:
					print("Last post same")
					print(newpost)
					print(lastposts[row[1]])
					#continue
				else:
					await post(int(row[4]), row[1])
					lastposts[row[1]] = newpost
					print("I should've posted something just now")
			
# @bot.command() # I'm not sure I'll ever get this working. There doesn't appear to be sufficient documentation online with solid examples and guiding, only API refernece.
# async def playsound(ctx):                    #since i cleaned up some stuff im not using because this is commented out, here's
	# #chan = ctx.message.author.voice.channel #what i removed
	# vc = ctx.message.author.voice.channel	   #from discord.voice_client import VoiceClient
	# vclient.play(source)					   #vclient = discord.VoiceClient
	# while not player.is_done():			   #song = discord.FFmpegPCMAudio('fx/announcer_well_done.mp3',executable='ffmpeg')
		# await asyncio.sleep(1)
	# player.stop()
	
bot.run(token)