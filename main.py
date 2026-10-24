from discord.ext import commands, tasks
from discord import app_commands, FFmpegPCMAudio
import discord
import os
import traceback
import json
import requests
import time
from pymongo import MongoClient
from dotenv import load_dotenv
import random
from asyncio import sleep
from bson.objectid import ObjectId
from Functions.db import updateVar, AddUser, DelUser
from discord.ext.commands import Context
load_dotenv()


DBClient = MongoClient(os.getenv("mongodb"), serverSelectionTimeoutMS=500)
SynapseCollections = DBClient["Synapse"]
UsersCollection = SynapseCollections["users"]

#? load bot config
with open("BotSettings.json", "r") as SettingsFile:
    BotConfig = json.load(SettingsFile)


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), description="idk", owner_id=948646639961255936)



@bot.event
async def on_message(message: discord.Message):

    if message.author.bot:
        return

    if "musor" in message.content:
        return await message.channel.send("https://c.tenor.com/dPIc4uRgPLcAAAAd/tenor.gif")

    if "@everyone" in message.content:
        if message.author.id == bot.owner_id:
           return
        await message.channel.send(f"{message.author.mention}, please don't use the everyone mention.", delete_after=5)
        await message.delete()
        

    
    userID = int(message.author.id)
    user = UsersCollection.find_one({"_id": userID})


    for unwantedlink in BotConfig["unwantedlinks"]:
        if unwantedlink in message.content:
            await message.delete()
            break


    level_roles = {
        "ten": {"id": 1502276813089673466, "lvl": 10},
        "twenty": {"id": 1502276813089673466, "lvl": 20},
        "thirty": {"id": 1502276813089673466, "lvl": 30},
        "fourty": {"id": 1502276813089673466, "lvl": 40},
        "fifty": {"id": 1502276813089673466, "lvl": 50},
    }

    roles = []
    for role in message.author.roles:
        roles.append(role.id)


    for role in level_roles.values():

        if role["id"] in roles:
            continue

        if user["xp"] > role["lvl"]:
            await message.author.add_roles(message.guild.get_role(role["id"]))

    if user:
        if user["xp"] > 200:
            levelup_embed = discord.Embed(
                title="**Level UP!**",
                description=f"{message.author.mention}, has leveled up to level {UsersCollection.find_one({'_id': message.author.id})['level']}",
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
            await bot.get_channel(1562077347337998416).send(embed=levelup_embed)

        if user["CanReceiveXP"]:
            result = updateVar(
                collection=UsersCollection,
                _id=userID,
                operation="add",
                var_name="xp",
                value="xd"
            )
            if result["error"]:
                await sendErr(result["msg"])

    await bot.process_commands(message)



@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Developed by Kulisek!"))
    print("Bot is ready!")




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
    userEntry = UsersCollection.find_one({"_id": UserID})
    
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
    sorted_levels = UsersCollection.find().sort("level", -1).to_list()
    
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
async def VerifyCMD(i: discord.Interaction):
    MemberRole = i.guild.get_role(1502276813089673466)
    if MemberRole not in i.user.roles:
        await i.user.add_roles(MemberRole)
        await i.message.delete()


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
        return await i.response.send_message("Please specify a member!")

    if not i.user.id == bot.owner_id:
        return await i.response.send_message("You don't have the permission to execute this command!")

    user_entry = UsersCollection.find_one({"_id": int(user.id)})
    if not user_entry:
        return await i.response.send_message("The person isn't in my database.")

    UsersCollection.update_one(
        {"_id": int(user.id)},
        {"$set": {"canAccessVC": False}}
    )
    return await i.response.send_message(f"Successfully restricted vc access for {user.name}!")

@bot.tree.command(name="revokevcban", description="revoke ban from vc (admins)")
async def revokevcban(i:discord.Interaction, user: discord.User = None):
    if not user:
        return await i.response.send_message("Please specify a member!")

    if not i.user.id == bot.owner_id:
        return await i.response.send_message("You don't have the permission to execute this command!")

    user_entry = UsersCollection.find_one({"_id": int(user.id)})
    if not user_entry:
        return await i.response.send_message("The person isn't in my database.")

    UsersCollection.update_one(
        {"_id": int(user.id)},
        {"$set": {"canAccessVC": False}}
    )
    return await i.response.send_message(f"Successfully restricted vc access for {user.name}!")

@bot.tree.command(name="purge", description="purge messages (for admins)")
async def purge(i:discord.Interaction, amount: int):
    if i.user.id == bot.owner_id:
        await i.channel.purge(limit=amount + 1)
        await i.channel.send("Done!")
    else:
        await i.response.send_message("you lack permissions!")

@bot.tree.command(name="spin", description="spin a virtual slot lmao why not XD XD ASDOHAHSJIKDAHGSJKDHLJASK")
async def spin(i:discord.Interaction):
    # 🍒 🍋 🍊 🍇 🍉 🔔 💎 7️⃣
    fruitslist = ["cherry", "lemon", "orange", "grape", "melon", "bell", "diamond", "seven"]
    fruitMultipliers = {
        "cherry": {"multiplier": 2, "emoji": "🍒"},
        "lemon": {"multiplier": 3, "emoji": "🍋"},
        "orange": {"multiplier": 4, "emoji": "🍊"},
        "grape": {"multiplier": 5, "emoji": "🍇"},
        "melon": {"multiplier": 8, "emoji": "🍉"},
        "bell": {"multiplier": 12, "emoji": "🔔"},
        "diamond": {"multiplier": 25, "emoji": "💎"},
        "seven": {"multiplier": 50, "emoji": "7️⃣"},
    }
    FSlot = random.choice(fruitslist)
    SSlot = random.choice(fruitslist)
    TSlot = random.choice(fruitslist)

    if FSlot == SSlot == TSlot:
        return await i.response.send_message(f"{fruitMultipliers[FSlot]['emoji']}-{fruitMultipliers[SSlot]['emoji']}-{fruitMultipliers[TSlot]['emoji']}  \n YOU WON {10 * fruitMultipliers[FSlot]['multiplier']} COINS!!!")
    else:
        return await i.response.send_message(f"{fruitMultipliers[FSlot]['emoji']}-{fruitMultipliers[SSlot]['emoji']}-{fruitMultipliers[TSlot]['emoji']} ,You lost :-(")
        
@bot.command()
async def flashdance(ctx: Context):
    if not ctx.author.voice:
        return await ctx.reply("You have to be in a voice channel!")
    vc = await ctx.author.voice.channel.connect()
    vc.play(FFmpegPCMAudio("flashbangdance.mp3"))
    await sleep(9)
    await ctx.voice_client.disconnect()

async def sendErr(message: str = None):
    guild_id = 1345844941397557270
    err_embed = discord.Embed(
        title="⚠️ Error",
        description=(f"**{message}**"),
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow(),
    )
    err_embed.set_footer(text="Error report")
    await bot.get_guild(guild_id).get_channel(1352971422410084382).send(embed=err_embed)


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CODE ENDS HERE!

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

