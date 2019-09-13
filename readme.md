Donkey
======

Commands:  
**+exit** - closes the bot (this is useful because the terminal doesn't immediately close via traditional methods)  
**+say** - repeats what you say  
**+get (feed)** - gets the latest post from a feed! Supports TF2 + CSGO update feeds out of the box. params: +get (feed name)  
**+hello** - greets you  
**+ping** - pong  
**+add** - Add a feed to +get, params: "+add (link) (name) <long? default no>"  Requires a feeds.csv file  
Oh I forgot to mention that this is broken unless you're adding a youtube feed. it will only work for one specific site because the site I was testing it with uses an idiosyncratic RSS tree. But if you're using a https://www.youtube.com/channel/xyz link it'll work out! ALWAYS remember the https:// and www. where applicable.  
param key: (required) <optional>  
  
Roadmap
-------
**Long term**  
enable subscriptions to TF2 update messages. This will probably be hard to test because Tf2 doesn't get updated, would have to be tested with a different RSS feed, in which case maybe it would be better to create a general RSS subscription feature?  
enable subscriptions to Minecraft update messages. Need minecraft to fix their RSS first :^)  
enable 24/7 [pizza music](https://www.youtube.com/watch?v=XW0W7j04iRQ) in voice channel. Need to learn voice API first.  
enable subscriptions to youtube channels, (Youtube supports RSS feeds for individual channels so this is in the works! You can +add YT channels)
whatever else I want to put in B^)  
**Short term**  
Error messages/foolproofing  
Some sort of fix for making sure no matter what kind of tree a feed uses, it's readable.  
A flag for showing full post or just the basics for +get  


A lot of what I want(ed) to add seems beyond my ability at this point. This bot was never meant to really have a function, just be functional. So for now you can +ping and +exit the bot to your heart's content. You can even make it +join and +leave voice channels! It just can't do anything there.