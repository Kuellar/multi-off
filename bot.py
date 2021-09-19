import os
import random
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from dotenv import load_dotenv
from db import db
from osu import osu
from utils import get_beatmap_id, fill_string, only_fill, get_tableform, get_introduction

load_dotenv()

# Discord connection
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='mo!', intents=intents)

# Database connection
db_host = os.getenv('db_host')
db_user = os.getenv('db_user')
db_database = os.getenv('db_database')
mo_db = db(db_host, db_user, "", db_database)

# Osu connection
osu_id= os.getenv('osu_id')
osu_secret= os.getenv('osu_secret')
mo_osu = osu(osu_id, osu_secret)
print(mo_osu.token.get("access_token"))  # TEST

######################
## COMMANDS SECTION ##
######################

@bot.event
async def on_guild_join(guild):
    mo_db.save_server(guild.id, guild.name)
    print(f'Adding server: "{guild.name}-{guild.id}" to the db')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


@bot.command(name='join', help='Join to Multi-off')
async def mo_join(ctx, username: str):
    user_db = mo_db.get_user(ctx.guild.id, ctx.author.id)
    if user_db:
        await ctx.send('This user already exist')
        return

    osu_player = mo_osu.get_user(username)
    author = ctx.author.name + '#'+ ctx.author.discriminator
    if osu_player.get('discord') == author:
        mo_db.save_user(
            server_id=ctx.guild.id,
            id=ctx.author.id,
            name=author,
            osu_id=osu_player.get('id'),
            osu_name=osu_player.get('username'),
        )
        print(f'Adding user: "{author}" to the db')
        await ctx.send(f'{username} joined successfully')
    else:
        await ctx.send('Sorry, some kind of error has occurred')


@bot.command(name='add', help='Add new beatmap to the play-list')
async def mo_add(ctx, beatmap: str):
    user = mo_db.get_user(ctx.guild.id, ctx.author.id)
    if not user:
        await ctx.send('Join to multi-off with `mo!join "osu-username"`')
        return

    beatmap_id = get_beatmap_id(beatmap)
    if not beatmap_id:
        await ctx.send('Invalid beatmap format, try `https://osu.ppy.sh/beatmapsets/[...]#osu/[...]`')
        return

    beatmap_db = mo_db.get_beatmap(beatmap_id, ctx.guild.id)
    if beatmap_db:
        await ctx.send('This beatmap already exist')
        return

    beatmap_score_json = mo_osu.get_user_beatmap_score(user[4], beatmap_id)
    if 'error' in beatmap_score_json:
        await ctx.send('Sorry, some kind of error has occurred')
        return

    if beatmap_score_json['score']['rank'] not in ['B', 'A', 'SH', 'S', 'SSH', 'SS']:
        await ctx.send('You need at least B rank')
        return

    mo_db.save_beatmap(beatmap_id, user[1], ctx.guild.id)
    await ctx.send('Beatmap added to the play-list!')


@bot.command(name='playlist', help='Show playlist')
async def mo_playlist(ctx):
    playlist = [mo_osu.get_beatmap(beatmap[0]) for beatmap in mo_db.get_beatmaps(ctx.guild.id)]
    tableform = get_tableform()
    res = tableform[0]
    for map in playlist:
        res += f'║ {fill_string(map["beatmapset"]["title"], 20)} '
        res += f'║ {fill_string(str(map["difficulty_rating"]), 5)} '
        res += f'║ {fill_string(str(map["accuracy"]), 4)} '
        res += f'║ {fill_string(str(map["ar"]), 4)} '
        res += f'║ {fill_string(str(map["bpm"]), 4)} '
        res += f'║ {fill_string(str(map["total_length"]), 6)} '
        res += f'║ https://osu.ppy.sh/beatmaps/{only_fill(str(map["id"]), 7)} ║{tableform[1]}'
    res += tableform[2]
    await ctx.send(res)


@bot.command(name='start', help='Start Multi-Off!')
async def mo_start(ctx):
    channel = discord.utils.get(ctx.guild.channels, name='multi-off')
    if not channel:
        await ctx.guild.create_text_channel('multi-off')
    mo_db.update_channel(channel.id, ctx.guild.id)
    await channel.purge(limit=100)  # Clean channel
    await channel.send(get_introduction())

    # Pick and Show actual beatmap
    beatmap_id = mo_db.get_random_beatmap(ctx.guild.id)[0]
    endtime = datetime.now() + timedelta(minutes=5)
    mo_db.save_play(server_id=ctx.guild.id, beatmap_id=beatmap_id, end=endtime)

    await ctx.send('Not implemented yet :(')
    pass


@bot.command(name='update', help='Update Scores')
async def mo_update(ctx):

    await ctx.send('Not implemented yet :(')
    pass


bot.run(TOKEN)
