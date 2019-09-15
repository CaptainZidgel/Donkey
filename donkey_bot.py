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
async def get(ctx, fName:str, incl_desc:str="yes"):
	await post(ctx.channel.id, fName.lower(), incl_desc.lower())
	
async def post(c, fName, descr="yes", t_o_feed=""):
	if descr == "send_nothing":				#this is used to return the title for the susbcription command
		feed = feedparser.parse(t_o_feed)
		return feed.entries[0].title
	else:	
		channel = bot.get_channel(c)
		with open('feeds.csv','r') as f:
			readCSV = csv.reader(f, delimiter=delim)
			for row in readCSV:
				if row[1] == fName.lower():                         #checks rows until it comes to the requested feed
					feed = feedparser.parse(row[2])         #sets the feed to the feedlink
					i = ""                                  #creates a string to eventually hold a post
					if row[4] == "null":					#if there is no title inclusion value, sets the post to the latest entry
						i = feed.entries[0]
					else:									#otherwise... find the latest post with the wanted title	
						iterate = 0
						for iter in feed.entries:
							if iter.title == row[4]:		#is the title of this particular post in this particular feed, the title I asked for?
								i = feed.entries[iterate]	#this post will be the particular post I get the title, link and description from
								break
							iterate = iterate + 1
					await channel.send(i.link)				#post the link to the latest post
					await channel.send(i.title + " " + i.published) #post the title and datetime
					if row[0] != "yt" and descr != "no":            #if description is wanted
						if row[3] == "no":							#if post is expected to be long. I may at some point make this automatic with len().
							await channel.send(re.sub('<[^>]+>', '', html.unescape(i.description))) #send the description, sans some unwanted characters.
						else:										
							text = re.sub('<[^>]+>', '', html.unescape(i.description))
							await channel.send(text[:2001])
							await channel.send(text[2001:4001])
							await channel.send(text[4001:6001])
							await channel.send(text[6001:10001])
					break
					
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
async def add(ctx, link:str, name:str, long:str = "no", inclusion="null"):
	f = open('feeds.csv','r')
	readCSV = csv.reader(f, delimiter=delim)
	for row in readCSV:
		if row[1] == name:
			ctx.send("Hey a feed already exists with that name. I don't know how to ask you for confirmation within a command so you'll need to +remove the feed!")
			return "Found a dupe!"
	f.close()	
		
	if link.startswith('https://www.youtube.com') or link.startswith('www.youtube.com'):
		type = "yt"
	else:
		type = "text"
	with open('feeds.csv', 'a') as f:
		if type == "yt":
			link = link.replace('channel/', 'feeds/videos.xml?channel_id=')
		f.write(type +delim + name.lower() + delim+ link +delim+long+delim+inclusion+ "\n")
	print("Printed something to feeds")
		
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

@bot.command()
async def remove(ctx, name:str): #look ive spent about the past 6 hours working on this and I can't get it to work.
	the_line = 0					#I'll keep working on it in the future.
	with open('feeds.csv','r+') as f:
		line = 0
		readCSV = csv.reader(f, delimiter=delim)
		writeCSV = csv.writer(f, delimiter=delim)
		for row in readCSV:
			line = line + 1
			print("Line")
			if row[1] == name:
				row[0] = "Wowee!" #This is where the row would be deleted. For testing purposes I just tried to change the first value.
				writeCSV.writerow(row) #I've also tried seek() and right()
				break
		
async def task():
	while True:
		await asyncio.sleep(30)
		print("30 seconds have elapsed")
		with open('subs.csv','r') as f:
			subscriptions = csv.reader(f, delimiter=delim)
			for row in subscriptions:
				newpost = await post(0, "none", "send_nothing", row[2])
				if not row[1] in lastposts:
					lastposts[row[1]] = newpost
				if lastposts[row[1]] == newpost:
					print("Last post same")
				else:
					await post(int(row[4]), row[1])
					lastposts[row[1]] = newpost
			
# @bot.command() # I'm not sure I'll ever get this working. There doesn't appear to be sufficient documentation online with solid examples and guiding, only API refernece.
# async def playsound(ctx):                    #since i cleaned up some stuff im not using because this is commented out, here's
	# #chan = ctx.message.author.voice.channel #what i removed
	# vc = ctx.message.author.voice.channel	   #from discord.voice_client import VoiceClient
	# vclient.play(source)					   #vclient = discord.VoiceClient
	# while not player.is_done():			   #song = discord.FFmpegPCMAudio('fx/announcer_well_done.mp3',executable='ffmpeg')
		# await asyncio.sleep(1)
	# player.stop()
	
bot.run(token)