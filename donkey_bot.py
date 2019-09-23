import discord
from discord.ext import commands
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
allfeeds = []

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	with open('feeds.csv','r') as file:
		readCSV = csv.reader(file, delimiter=delim)
		for row in readCSV:
			feed = {
			'name': row[1],
			'link': row[2],
			'inclusion': row[3],
			'type': row[0]
			}
			allfeeds.append(feed)
		print('Saved feeds loaded from feeds.csv')
	bot.loop.create_task(fetch_subs())
	
@bot.event
async def on_message(message):
	await bot.process_commands(message)
	if message.author == bot.user:
		return

@bot.command()
async def exit(ctx):
	await save()
	await bot.close()

async def save():
	with open('feeds.csv','w') as file:
		for feed in allfeeds:
			file.write(feed['type'] + delim + feed['name'] + delim + feed['link'] + delim + feed['inclusion'] + "\n")
			
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
		for f in allfeeds:
			if f['name'] == fName.lower():              #checks rows until it comes to the requested feed
				feed = feedparser.parse(f['link'])         #sets the feed to the feedlink
				i = ""                                  #creates a string to eventually hold a post
				if f['inclusion'] == "null":					#if there is no title inclusion value, sets the post to the latest entry
					i = feed.entries[0]
				else:									#otherwise... find the latest post with the wanted title	
					iterate = 0
					for iter in feed.entries:
						if iter.title == f['inclusion']:		#is the title of this particular post in this particular feed, the title I asked for?
							i = feed.entries[iterate]	#this post will be the particular post I get the title, link and description from
							break
						iterate = iterate + 1
				await channel.send(i.link)				#post the link to the latest post
				await channel.send(i.title + " " + i.published) #post the title and datetime
				if f['type'] != "yt" and descr != "no":            #if description is wanted
					if len(i.description) < 2000:					#not all feed descriptions include a full post. Sometimes it's the summary.
						await channel.send(re.sub('<[^>]+>', '', i.description)) #send the description, sans some unwanted characters.
					else:										
						text = re.sub('<[^>]+>', '', i.description)
						await channel.send(text[:2001])
						if len(text) > 2000:
							await channel.send(text[2001:4001])
							if len(text) > 4000:
								await channel.send(text[4001:6001])
								if len(text) > 10000:
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
async def add(ctx, link:str, name:str, inclusion="null"):
	for f in allfeeds:
		if f['name'] == name.lower():
			print("There's already a feed with that name!")
			return
	if link.startswith('https://www.youtube.com') or link.startswith('www.youtube.com'):
		type = "yt"
		link = link.replace('channel/', 'feeds/videos.xml?channel_id=')	
	else:
		type = "text"	
	feed = {
	'name': name.lower(),
	'link': link,
	'inclusion': inclusion,
	'type': type
	}
	allfeeds.append(feed)
	await save()	
		
@bot.command()
async def sub(ctx, name:str):
	copy = "empty"
	l = ""
	for f in allfeeds:
		if f['name'] == name:
			copy = f['type']+delim+f['name']+delim+f['link']
			l = f['link']

	with open('subs.csv','a') as f:
		f.write(copy + delim + str(ctx.channel.id) + "\n")
	lastposts[name] = await post(0, "none", "send_nothing", l)
	
@bot.command()
async def unsub(ctx, name:str):
	subs = []
	with open('subs.csv','r') as f:
		readCSV = csv.reader(f, delimiter=delim)
		for row in readCSV:
			if row[1] != name:
				subs.append(row)
	with open('subs.csv','w') as f:
		for s in subs:
			f.write(s[0]+delim+s[1]+delim+s[2]+delim+s[3]+"\n")

@bot.command()
async def remove(ctx, name:str):
	for f in allfeeds:
		if f['name'] == name:
			allfeeds.remove(f)
	await save()	
		
async def fetch_subs():
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
					await post(int(row[3]), row[1])
					lastposts[row[1]] = newpost
					
# @bot.command() # I'm not sure I'll ever get this working. There doesn't appear to be sufficient documentation online with solid examples and guiding, only API refernece.
# async def playsound(ctx):                    #since i cleaned up some stuff im not using because this is commented out, here's
	# #chan = ctx.message.author.voice.channel #what i removed
	# vc = ctx.message.author.voice.channel	   #from discord.voice_client import VoiceClient
	# vclient.play(source)					   #vclient = discord.VoiceClient
	# while not player.is_done():			   #song = discord.FFmpegPCMAudio('fx/announcer_well_done.mp3',executable='ffmpeg')
		# await asyncio.sleep(1)
	# player.stop()
	
bot.run(BOT_TOKEN)