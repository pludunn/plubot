import datetime
import os
import zoneinfo
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
		case"mute":
			guild_id=int(input("Guild ID: "))
			guild=await bot.fetch_guild(guild_id)
			if not guild:
				print("Guild not found.")
				await bot.close()
				return
			member_id=int(input("Member ID: "))
			member=await guild.fetch_member(member_id)
			if not member:
				print("Member not found.")
				await bot.close()
				return
			amount=int(input("Amount of time to mute (in seconds): "))
			reason=(input("Reason for mute: (leave blank for none): ") or "No reason provided")
			until=datetime.datetime.now(zoneinfo.ZoneInfo("UTC"))+datetime.timedelta(seconds=amount)
			await member.timeout(until,reason=reason)
	await bot.close()
bot.run(os.getenv("PLUBOT_TOKEN","None"))