import os
import discord
bot=discord.Client(intents=discord.Intents.default(),status=discord.Status.offline)
@bot.event
async def on_ready():
	action=input("Action: ")
	match action:
		case"send":
			channel_id=int(input("Channel ID: "))
			channel=await bot.fetch_channel(channel_id)
			assert isinstance(channel,(discord.TextChannel,discord.VoiceChannel)),("Channel is not a text channel or a voice channel.")
			message=input("Message: ")
			await channel.send(message)
		case"spam":
			channel_id=int(input("Channel ID: "))
			channel=await bot.fetch_channel(channel_id)
			assert isinstance(channel,(discord.TextChannel,discord.VoiceChannel)),("Channel is not a text channel or a voice channel.")
			message=input("Message: ")
			amount=int(input("Amount: "))
			for _ in range(amount):
				await channel.send(message)
bot.run(os.getenv("PLUBOT_TOKEN","None"))
