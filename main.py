from discord.ext import commands, tasks
from discord import app_commands, FFmpegPCMAudio
import discord
import yt_dlp
import os
import asyncio
import traceback
import json
import requests
from datetime import timedelta
import time
import threading
import yt_dlp
import pymongo
import subprocess
from pymongo import MongoClient
from dotenv import load_dotenv
import functools
import random
from bson.objectid import ObjectId
load_dotenv()


Client = MongoClient(os.getenv("mongodb"), serverSelectionTimeoutMS=500)
collection = Client["Synapse"]
users = collection["users"]
verify = collection["ToVerify"]
serverStats = collection["serverStats"]
serverStatsObjectID = ObjectId("6a2524a7f207d7e2755a85b5")

#? load bot config
with open("BotSettings.json", "r") as SettingsFile:
    BotConfig = json.load(SettingsFile)


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), description="idk", owner_id=948646639961255936)

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after:discord.VoiceState):
    UserDBEntry = users.find_one({"_id": int(member.id)})

    if member.bot:
        return
    print(UserDBEntry)
    print(f"member: {member}, before: {before.channel}, after: {after.channel}")
    if UserDBEntry:
        if not UserDBEntry["canAccessVC"]:
            await member.edit(voice_channel=None)
            await member.send("Due to your suspension of using voice chat in my server, you cannot access voice chats. contact <@948646639961255936> if you think this is unusual and you didn't do anything.")
    else:
        users.insert_one(
            {
                "_id": int(member.id),
                "level": 1,
                "username": member.name,
                "xp": 0,
                "CanReceiveXP": True,
                "warnings": 0,
                "canAccessVC": True
            },
        )


CurrentNum = 0
NextNum = 1
LastUser = 0 
HasResponded = False

@bot.event
async def on_message(message: discord.Message):
    global CurrentNum
    global NextNum
    global LastUser
    global HasResponded
    print(f"CurrentNum: {CurrentNum}, NextNum: {NextNum}, LastUser: {LastUser}")
    if message.author.bot:
        return
    HasResponded = False
    if message.channel.id == 1512151683507945654:
        MaxMathStreak = serverStats.find_one({"_id": serverStatsObjectID})["MaxMathStreak"]
        try:
            message_content = int(message.content)
        except ValueError:
            message_content = None

        print(message_content)
        if message_content != NextNum and not HasResponded and isinstance(message_content, int):
            NextNum = 1
            CurrentNum = 0
            await message.add_reaction("❌")
            await message.channel.send(f"Lost the streak! current highest server streak: {MaxMathStreak} | the next number is {NextNum}")
            HasResponded = True

        
        if message.author.id == LastUser and not HasResponded and isinstance(message_content, int):
            NextNum = 1
            CurrentNum = 0
            LastUser = None
            await message.channel.send("You can't count by yourself! Reseting..")
            await message.add_reaction("❌")
            HasResponded = True

        if message_content == NextNum and not HasResponded and isinstance(message_content, int):
            NextNum += 1
            CurrentNum += 1
            LastUser = message.author.id
            await message.add_reaction("✅")
            HasResponded = True

        if MaxMathStreak <= CurrentNum:
            serverStats.update_one(
                {"_id": serverStatsObjectID},
                {"$inc": {"MaxMathStreak": CurrentNum}}
            )
    if "@everyone" in message.content:
        if message.author.id == bot.owner_id:
           return
        await message.delete()
        await message.channel.send(f"Please don't use the everyone mention even if its without a ping.")



    
    userID = int(message.author.id)
    username = str(message.author.name)
    user = users.find_one({"_id": userID})



    for unwantedlink in BotConfig["unwantedlinks"]:
        if unwantedlink in message.content:
            await message.delete()
            break

    hasGivenXP = False
    if user is None and not hasGivenXP:
        users.update_one(
            {"_id": userID},
            {
                "$set": {
                    "level": 1,
                    "username": username,
                    "CanReceiveXP": True,
                    "warnings": 0,
                    "canAccessVC": True,
                    "AcceptedGifTerms": False
                },
                "$inc": {"xp": 5}
            },
            upsert=True
        )
        hasGivenXP = True
    
    if not hasGivenXP and user["CanReceiveXP"]:
        print("giving xp..")
        users.update_one({"_id": userID},{"$inc": {"xp": 5}})
        hasGivenXP = True

    tenrole = message.guild.get_role(1502276813089673466)  
    twentyrole = message.guild.get_role(1502276809981431888)
    thirtyrole = message.guild.get_role(1502276809075462174)
    fourtyrole = message.guild.get_role(1502276806563070012)
    fiftyrole = message.guild.get_role(1502276803840970832)

    if user["level"] >= 9 and tenrole not in message.author.roles:
        await message.author.send("You've been awarded with role 'Rookie', Congrats! 🎉")
        await message.author.add_roles(tenrole)
    if user["level"] >= 19 and twentyrole not in message.author.roles:
        await message.author.send("You've been awarded with role 'Apprentice', Congrats! 🎉")
        await message.author.add_roles(twentyrole)
    if user["level"] >= 29 and thirtyrole not in message.author.roles:
        await message.author.send("You've been awarded with role 'Expert', Congrats! 🎉")
        await message.author.add_roles(thirtyrole)
    if user["level"] >= 39 and fourtyrole not in message.author.roles:
        await message.author.send("You've been awarded with role 'Veteran', Congrats! 🎉")
        await message.author.add_roles(fourtyrole)
    if user["level"] >= 49 and fiftyrole not in message.author.roles:
        await message.author.send("You've been awarded with role 'Ancient', Congrats! 🎉")
        await message.author.add_roles(fiftyrole)
    
    if users.find_one({"_id": message.author.id})["xp"] >= 200:
        users.update_one(
            {"_id": message.author.id},
            {
                "$inc": {"level": 1},
                "$set": {"xp": 0},
            },
        )
        levelup_embed = discord.Embed(
            title="**Level UP!**",
            description=f"{message.author.mention}, has leveled up to level {users.find_one({'_id': message.author.id})['level']}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        levelup_embed.set_author(
            name="Synapse", 
            icon_url=bot.user.avatar.url
        )
        levelup_embed.set_footer(
            text=f"level up embed, made by Synapse and its dev 'Kulisekxd'"
        )
        levelup_embed.set_thumbnail(
            url=message.author.avatar.url
        )
        await bot.get_channel(1352971415397072988).send(embed=levelup_embed)

    if message.channel.id == 1512151683507945654:
        pass

    await bot.process_commands(message)



@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Developed by Kulisek!"))
    print("Bot is ready!")



@bot.tree.command(name="play", description="Play music")
async def play(interaction:discord.Interaction, url: str = None):
    
    if BotConfig["testingmode"] is True:
        if interaction.channel.id != 1457378020817113162:
            await interaction.followup.send("bot is in testing mode, request access in <#1466807521741111297>")
            return
    
    
    #? if no url is specified kindly KINDLY ask the user to specify one
    if not url:
        return await interaction.response.send_message("Specify url!")
    
    bot_vc_client = interaction.guild.voice_client

    if not interaction.user.voice:
        return await interaction.response.send_message("you must be in a voice channel to use voice chat related commands!")
    
    if url.startswith("http://"):
        return await interaction.response.send_message("Insecure sites aren't allowed! check your link and make sure it has https://")
    if bot_vc_client:
        isplaying = interaction.guild.voice_client.is_playing()
            
        if isplaying:
            return await interaction.response.send_message("Synapse is already playing something.")
        
        if url.startswith("https://"):
            if url.startswith("https://www.tiktok.com"):
                await interaction.channel.send("TikTok links sometimes do work, but sometimes they don't. If it doesn't work, try using a YouTube link instead.")
            opts = {
                "outtmpl": "downloads/%(title)s.%(ext)s",
                "format": "bestaudio/best",
                "noplaylist": True,
                "cookiefile": "cookies.txt",
                "js_runtimes": {"node": {}},
                "remote_components": "ejs:github",
            }

            await interaction.response.defer()
            with yt_dlp.YoutubeDL(opts) as ydl:
                Video_info = ydl.extract_info(url, download=False)
                title = Video_info.get("title")
                Uploader = Video_info.get("uploader")
                duration = Video_info.get("duration")
                duration_mins = duration // 60
                filepath = ydl.prepare_filename(Video_info)
                thumbnail = Video_info.get("thumbnail")
                download_function = functools.partial(ydl.download, [url])
                await asyncio.get_event_loop().run_in_executor(None, download_function)
                formatted_duration = str(timedelta(seconds=duration))
                embed = discord.Embed(
                    title="🎶 Now Playing",
                    description=f"[{title}]({url})",
                    color=discord.Color.from_rgb(88, 101, 242) 
                )
                embed.set_thumbnail(url=thumbnail)
                embed.add_field(name="👤 Uploader", value=f"`{Uploader}`", inline=True)
                embed.add_field(name="⏱️ Duration", value=f"`{formatted_duration}`", inline=True)
                embed.add_field(name="🙋 Requested By", value=interaction.user.mention, inline=True)
                embed.set_footer(text="Music Bot System • 2026", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                await interaction.followup.send(embed=embed)
                bot_vc_client.play(FFmpegPCMAudio(filepath))
        else:
            return await interaction.followup.send("The URL is invalid, Example of link: 'https://link.com/ID'")
    else:
        return await interaction.followup.send("the bot isn't in a voice channel")
        





@bot.tree.command(name="join", description="Join a channel")
async def join(i: discord.Interaction):
    if i.user.bot:
        return
    bot_vc_client = i.guild.voice_client
    if not i.user.voice.channel:
        return await i.response.send_message("in order to connect synapse to a channel you need to be in one too! without it Synapse won't know where to join!")
    if bot_vc_client:
        return await i.response.send_message("Synapse is already connected to a channel!")
    
    if i.user.voice.channel and not bot_vc_client:
        bot_vc_client = await i.user.voice.channel.connect()
        
    return await i.response.send_message("connected successfully without issues")

    

        
@bot.tree.command(name="pause", description="Pause currently playing music")
async def pause(i: discord.Interaction):
    if BotConfig["testingmode"] is True:
        if i.channel.id != 1457378020817113162:
            await i.response.send_message("bot is in testing mode, request access in <#1466807521741111297>")
            return
    if i.user.bot:
        return
    bot_vc_client = i.guild.voice_client
    if i.user.voice.channel:
        if bot_vc_client:   
            if bot_vc_client.is_playing(): 
                if bot_vc_client.is_paused():
                    return await i.followup.send("Synapse is already paused so there isn't anything to pause or there isn't anything playing.")
                bot_vc_client.pause()
                return await i.response.send_message("Paused!")
            else:
                return await i.followup.send("Synapse isn't playing anything.")
        else:
            return await i.followup.send("Synapse isn't in a voice channel!")
    return await i.followup.send("you must be in a voice channel to use voice chat related commands!")


@bot.tree.command(name="resume", description="resume currently playing music")
async def resume(i: discord.Interaction):
    if BotConfig["testingmode"] is True:
        if i.channel.id != 1457378020817113162:
            await i.response.send_message("bot is in testing mode, request access in <#1466807521741111297>")
            return
    if i.user.bot:
        return
    bot_vc_client = i.guild.voice_client
    if i.user.voice.channel:
        if bot_vc_client:   
            if not bot_vc_client.is_playing(): 
                if not bot_vc_client.is_paused():
                    return await i.followup.send("nothing to resume since there is not anything paused bruh nga.")
                bot_vc_client.resume()
                return await i.response.send_message("Resumed!")
            else:
                return await i.followup.send("Synapse isn't playing anything.")
        else:
            return await i.followup.send("Synapse isn't in a voice channel!")
    else:
        return await i.followup.send("you must be in a voice channel to use voice chat related commands!")




@bot.tree.command(name="leave", description="leave the channel")
async def leave(i: discord.Interaction):
    bot_vc_client = i.guild.voice_client
    

    if i.user.voice.channel:
        if bot_vc_client:   
            await bot_vc_client.disconnect()
            await i.followup.send("Successfully left without issues")
        else:
            return await i.followup.send("Synapse isn't in a voice channel!")
    else:
        return await i.followup.send("you must be in a voice channel to use voice chat related commands!")

@bot.tree.command(name="stop", description="stop what's playing")
async def stop(i: discord.Interaction):
    bot_vc_client = i.guild.voice_client
    
    if i.user.bot:
        return
    if i.user.voice.channel:
        if bot_vc_client:   
            bot_vc_client.stop()
            await i.response.send_message("stopped.")
        else:
            return await i.followup.send("Synapse isn't in a voice channel!")
    else:
        return await i.followup.send("you must be in a voice channel to use voice chat related commands!")


@bot.event
async def on_member_join(member:discord.Member):
    zerorole = member.guild.get_role(1502276826947653632)
    join_embed = discord.Embed(
        title="👋 New Member Joined",
        description=f"Welcome to the server, {member.mention}!",
        timestamp=discord.utils.utcnow(),
        color=discord.Color.brand_green()
    )

    join_embed.set_author(
        name="Synapse Welcome",
        icon_url=bot.user.display_avatar.url
    )

    join_embed.set_thumbnail(
        url=member.display_avatar.url
    )

    join_embed.add_field(
        name="Account Age", 
        value=f"<t:{int(member.created_at.timestamp())}:R>", 
        inline=True
    )

    join_embed.add_field(
        name="Member Count", 
        value=f"**` {member.guild.member_count} `**", 
        inline=True
    )

    join_embed.set_footer(
        text=f"ID: {member.id} • Made by Synapse"
    )
    join_channel = bot.get_channel(1352971409588224030)
    await join_channel.send(embed=join_embed)
    try:
        await member.send(f"Welcome to the server, {member.mention}! Please make sure to read the rules and enjoy your stay! \n\n If you want to verify yourself, use /verify in <#1502388965259481088> to get access to the rest of the server!")
    except discord.Forbidden:
        print(f"Couldn't send DM to {member.name} ({member.id})")
@bot.event
async def on_member_remove(member:discord.Member):
    leave_embed = discord.Embed(
        title="🏃 Member Left",
        description=f"**{member.mention}** ({member.name}) has left the server.",
        timestamp=discord.utils.utcnow(),
        color=discord.Color.red()
    )

    leave_embed.set_author(
        name="Synapse Logging",
        icon_url=bot.user.display_avatar.url
    )

    leave_embed.set_thumbnail(
        url=member.display_avatar.url
    )

    leave_embed.add_field(
        name="Member Count", 
        value=f"**` {member.guild.member_count} `**", 
        inline=True
    )

    leave_embed.add_field(
        name="Account Created", 
        value=f"<t:{int(member.created_at.timestamp())}:R>", 
        inline=True
    )

    leave_embed.set_footer(
        text=f"ID: {member.id} • Made by Synapse"
    )
    join_channel = bot.get_channel(1352971409588224030)
    await join_channel.send(embed=leave_embed)



@bot.tree.command(name="level", description="show your or another user's current level")
async def level(i:discord.Interaction, user: discord.Member = None):
    if user is None:
        user = i.user

    UserName = user.name
    UserID = user.id
    userEntry = users.find_one({"_id": UserID})
    
    embed_color = user.color if hasattr(user, "color") else discord.Color.blue()

    final_embed = discord.Embed(
        title=f"📊 {user.display_name}'s Stats",
        color=embed_color
    )

    final_embed.set_thumbnail(url=user.display_avatar.url)

    final_embed.add_field(
        name="Level", 
        value=f"**` {userEntry['level']} `**", 
        inline=True
    )
    final_embed.add_field(
        name="XP", 
        value=f"**` {userEntry['xp']} `**", 
        inline=True
    )

    final_embed.set_footer(
        text=f"Requested by {i.user.display_name}", 
        icon_url=i.user.display_avatar.url
    )
    return await i.response.send_message(embed=final_embed)


@bot.tree.command(name="levelleaderboard", description="displays a level leaderboard")
async def levelleaderboard(i:discord.Interaction):
    sorted_levels = users.find().sort("level", -1).to_list()
    
    levels_embed = discord.Embed(
        title="levels Leaderboard",
        description=f"This shows a leaderboard on this server \n the top level currently is <@{sorted_levels[0]['_id']}>",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow(),
    )
    
    index = 0
    for _ in sorted_levels:
        if index >= 5:
            break
        levels_embed.add_field(name=f"{_['username']}", value=f"{_['level']}", inline=False)
        index += 1
        
    await i.response.send_message(embed=levels_embed)

@bot.tree.command(name="verify", description="verify yourself!")
async def VerifyCMD(i: discord.Interaction, code: int = None):
    MemberRole = i.guild.get_role(1502276813089673466)
    VerifyCode = int(random.randint(100000,999999))
    if MemberRole not in i.user.roles:
        entry = verify.find_one({"_id": i.user.id})
        if entry and code is not None:
            if code == entry["VerifyCode"]:
                if entry["hasVerified"]:
                    guild : discord.Guild = bot.get_guild(1345844941397557270)
                    verifiedrole : discord.Role = guild.get_role(1502276826947653632)
                    member : discord.Member = await guild.fetch_member(entry["_id"])
                    await member.add_roles(verifiedrole)
                    verify.delete_one({"_id": entry["_id"]})
                    return await i.response.send_message("Verification successful!", delete_after=20)
        if entry:
            return await i.user.send(f"Verification process is already in progress! if you lost the code, here it is. **{entry['VerifyCode']}**", delete_after=20)
        
        verify.insert_one(
            {
                "_id": i.user.id,
                "username": str(i.user.name),
                "hasVerified": False,
                "VerifyCode": int(VerifyCode)
            }
        )
        try:
            await i.user.send(f"Your verification code is: **{VerifyCode}**, use /verify 123456 in <#1502388965259481088> (replace 123456 with the provided code.)")
        except discord.Forbidden:
            return await i.response.send_message("I couldn't send you a DM. Please make sure your DMs are open.", delete_after=20)
    return await i.response.send_message(f"I have sent you a code into DM's. ", delete_after=20)


        
@bot.tree.command(name="credits", description="Giving credits where it's due.")
async def credits(i: discord.Interaction):
    credits_embed = discord.Embed(
        title="✨ Project Credits",
        description="Meet the team behind the development and creation of this project!",
        color=0x5865F2
    )
    
    credits_embed.add_field(
        name="🤖 Bot Development", 
        value="**Kulisek** (Server Owner)", 
        inline=False
    )
    credits_embed.add_field(
        name="🎨 Embed Design", 
        value="**Gemini** (AI Assistant)", 
        inline=False
    )
    
    credits_embed.set_footer(text=f"Requested by {i.user.display_name}", icon_url=i.user.display_avatar.url)
    
    await i.response.send_message(embed=credits_embed)

@bot.command()
async def question(ctx, *, question: str):
    if question:
        choices = ["Yes", "No", "Maybe", "Probably", "Maybe yes", "Maybe no"]
        bot_choice = random.choice(choices)
        return await ctx.send(bot_choice)
    else:
        return await ctx.send("Please, ask.")

@bot.tree.command(name="vcban", description="ban users from joining vc (admins)")
async def vcban(i:discord.Interaction, user: discord.User = None):
    if not user:
        return i.response.send_message("Please specify a member!")

    if not i.user.id == bot.owner_id:
        return i.response.send_message("You don't have the permission to execute this command!")

    user_entry = users.find_one({"_id": int(user.id)})
    if not user_entry:
        return i.response.send_message("The person isn't in my database.")

    users.update_one(
        {"_id": int(user.id)},
        {"$set": {"canAccessVC": False}}
    )
    return i.response.send_message(f"Successfully restricted vc access for {i.user.name}!")
    

@bot.tree.command(name="purge", description="purge messages (for admins)")
async def purge(i:discord.Interaction, amount: int):
    if i.user.id == bot.owner_id:
        await i.channel.purge(limit=amount + 1)
        await i.channel.send("Done!")
    else:
        await i.response.send_message("you lack permissions!")

try:
    if BotConfig["testingmode"]:
        bot.owner_id = BotConfig["OwnerID"]
        bot.command_prefix = BotConfig["CommandPrefix"]
        if __name__ == "__main__":
            bot.run(token=os.getenv("testing"), reconnect=BotConfig["Reconnect"])
    bot.owner_id = BotConfig["OwnerID"]
    bot.command_prefix = BotConfig["CommandPrefix"]
    if __name__ == "__main__":
        bot.run(token=os.getenv("tkn"), reconnect=BotConfig["Reconnect"])

except Exception:
    

    WebhookData = {
        "content": f"Error while running bot. \n ```{traceback.format_exc()}```",
        "username":"Synapse Error Handler Webhook"
    }
    if "Session is closed" in traceback.format_exc():
        exit(1)
    print(f"Error while running bot. \n ```{traceback.format_exc()}```")

    Send_Webhook = requests.post(url=os.getenv("webhook"), json=WebhookData)
    if Send_Webhook.status_code == 204:
        print("Sent webhook about error.")
        exit(1)
    else:
        print("Failed to send webhook, very likely discord's fault.")
        exit(1)

