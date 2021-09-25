import os
import random
import time
from datetime import datetime, timedelta

import lightbulb
import hikari
import logging
from dotenv import load_dotenv
from db import db
from osu import osu
from utils import get_beatmap_id, fill_string, only_fill, get_tableform, get_introduction

load_dotenv()

# Discord connection
TOKEN = os.getenv('DISCORD_TOKEN')
bot = lightbulb.Bot(token=TOKEN, prefix="mo!", logs="DEBUG")

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


# COMMANDS SECTION


"""
@bot.event
async def on_guild_join(guild):
    mo_db.save_server(guild.id, guild.name)
    print(f'Adding server: "{guild.name}-{guild.id}" to the db')
"""


@bot.command(name='join', help='Join to Multi-off')
async def mo_join(ctx, username: str):
    user_db = mo_db.get_user(int(ctx.guild_id), int(ctx.author.id))
    if user_db:
        await ctx.respond('This user already has an osu account assigned')
        return

    osu_player = mo_osu.get_user(username)
    author = ctx.author.username + '#'+ ctx.author.discriminator
    if osu_player.get('discord') == author:
        mo_db.save_user(
            server_id=int(ctx.guild_id),
            id=int(ctx.author.id),
            name=str(author),
            osu_id=int(osu_player['id']),
            osu_name=str(osu_player['username']),
        )
        print(f'Adding user: "{author}" to the db')
        await ctx.respond(f'{username} joined successfully')
    else:
        await ctx.respond('Sorry, some kind of error has occurred')


@bot.command(name='add', help='Add new beatmap to the play-list')
async def mo_add(ctx, beatmap: str):
    user = mo_db.get_user(int(ctx.guild_id), int(ctx.author.id))
    if not user:
        await ctx.respond('Join to multi-off with `mo!join "osu-username"`')
        return

    beatmap_id = get_beatmap_id(str(beatmap))
    if not beatmap_id:
        await ctx.respond('Invalid beatmap format, try `https://osu.ppy.sh/beatmapsets/[...]#osu/[...]`')
        return

    beatmap_db = mo_db.get_beatmap(int(beatmap_id), int(ctx.guild_id))
    if beatmap_db:
        await ctx.respond('This beatmap already exist')
        return

    beatmap_score_json = mo_osu.get_user_beatmap_score(int(user[4]), int(beatmap_id))
    if 'error' in beatmap_score_json:
        await ctx.respond('Sorry, some kind of error has occurred')
        return

    if beatmap_score_json['score']['rank'] not in ['B', 'A', 'SH', 'S', 'SSH', 'SS']:
        await ctx.respond('You need at least B rank')
        return

    mo_db.save_beatmap(int(beatmap_id), int(user[1]), int(ctx.guild_id))
    await ctx.respond('Beatmap added to the play-list!')


@bot.command(name='playlist', help='Show playlist')
async def mo_playlist(ctx):
    playlist = [mo_osu.get_beatmap(beatmap[0]) for beatmap in mo_db.get_beatmaps(int(ctx.guild_id))]
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
    await ctx.respond(res)


@bot.command(name='start', help='Start Multi-Off!')
async def mo_start(ctx):
    channels = {}
    for guild_id in ctx.get_guild().get_channels():
        ch = ctx.get_guild().get_channel(guild_id)
        if isinstance(ch , hikari.channels.GuildTextChannel):
            channels[ch.name] = ch

    channel = channels.get("multi-off")
    if not channel:
        channel = await ctx.get_guild().create_text_channel(name='multi-off')

    mo_db.update_channel(int(channel.id), int(ctx.guild_id))

    # Clean channel
    history = await channel.fetch_history()
    await channel.delete_messages(history)
    await channel.send(get_introduction())

    # Pick and Show actual beatmap
    beatmap_id = mo_db.get_random_beatmap(int(ctx.guild_id))[0]
    endtime = datetime.now() + timedelta(minutes=5)
    mo_db.save_play(server_id=int(ctx.guild_id), beatmap_id=beatmap_id, end=endtime)

    await ctx.respond('Not implemented yet :(')
    pass


@bot.command(name='update', help='Update Scores')
async def mo_update(ctx):

    await ctx.respond('Not implemented yet :(')
    pass


#  CHANGE AT DEPLOY
bot.run(
    asyncio_debug=True,
    coroutine_tracking_depth=20,
    propagate_interrupts=True,
)
