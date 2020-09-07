import discord
import requests
import tweepy
from discord.ext import commands
import asyncio
import re
import urllib.request
from discord import utils
import json

#reading json file 
with open("config.json") as file:
    data = json.load(file)


CONSUMER_KEY = data["twitter_consumer_key"]
CONSUMER_SECRET = data["twitter_secret_key"]
ACCESS_KEY = data["twitter_access_key"]
ACCESS_SECRET = data["twitter_access_secret"]

#cretaing the connections with twitter api using tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

#successfully connected, printing the name of the twitter account that has logged in
print("you are running " + api.me().name)

bot = commands.Bot(command_prefix="!")

#estabilishing connection with discord api => printing the name of the bot that has logged in
@bot.event
async def on_ready():
    print(bot.user.name + " is ready!")

@bot.event
async def on_message(message):
#filtering only the messages that are sent in the success channel
    if str(message.channel.name) == "success":
        try:
            #getting all the information needed for the post: author name, the image url and the tweet text
            author = str(message.author.username)
            image_url = message.attachments[0].url
            tweet_text = ('Success by ' + author + " in @" + data["group_name"])
            filename = 'success.jpg'
            r = requests.get(image_url)
            if r.status_code == 200:
                with open(filename, 'wb') as image:
                    for img in r:
                        image.write(img)
                #posting the actual tweet and sending the message embed
                post_tweet = api.update_with_media(filename, status=tweet_text)
                embed = discord.Embed(title=f"Successfully posted your success!", description=f"Success by <@{message.author.id}> \n You can find your tweet [here](https://twitter.com/{api.me().name}/status/{str(post_tweet.id)}) \n React with 🗑️ to this message within the next 5 minutes to delete the post", color=data["embed_color"])
                embed.set_footer(text=f'{data["group_name"]} Success Poster', icon_url=data["footer_image_url"])
                #sending the embed
                msg = await message.channel.send(embed=embed)
                #option to delete the success post
                await msg.add_reaction("🗑️")
                deleted = discord.Embed(title=f"Success Deleted!", description=f"<@{message.author.id}> your tweet has been successfully deleted \n If you think it was an error please open a ticket", color=data["embed_color"])
                deleted.set_footer(text=f'{data["group_name"]} Success Poster', icon_url=data["footer_image_url"])
                #needed to delete the tweet ONLY if the user that posted it wants to delete it otherwise ignore the reactions
                def check(reaction, user):
                    return user == message.author and str(reaction.emoji) == '🗑️' and reaction.message.id == msg.id
                try:
                    #waiting for the user to react with 🗑 within the desired time or passing
                    reaction, user = await bot.wait_for('reaction_add', timeout=data["time_to_delete"], check=check)
                except asyncio.TimeoutError:
                    #exceeded the time to delete the tweet
                    print("Will not delete this success")
                else:
                    #if the user reacts with 🗑 within the desired interval of time, will proceed and delete the tweet
                    api.destroy_status(str(post_tweet.id))
                    #editing the original message letting the user know that the tweet was successfully deleted
                    await msg.edit(embed=deleted)
        except IndexError:
            pass

bot.run(data["bot_token"])
