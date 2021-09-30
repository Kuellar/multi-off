import os
from datetime import datetime, timedelta

import hikari
import lightbulb
from dotenv import load_dotenv

from db import db
from osu import osu
from utils import (fill_string, get_beatmap_id, get_beatmap_info,
                   get_introduction, get_table_grank, get_table_rank_empty,
                   get_tableform, only_fill)

load_dotenv()
DEBUG = os.getenv('DEBUG')

# Discord connection
TOKEN = os.getenv('DISCORD_TOKEN')
bot = lightbulb.Bot(token=TOKEN, prefix="mo!", logs="DEBUG")
bot.remove_command("help")  #  TODO: Use Auto-Generated

# Database connection
db_host = os.getenv('db_host')
db_user = os.getenv('db_user')
db_database = os.getenv('db_database')
mo_db = db(db_host, db_user, "", db_database)

# Osu connection
osu_id= os.getenv('osu_id')
osu_secret= os.getenv('osu_secret')
mo_osu = osu(osu_id, osu_secret)
token_expiration = datetime.now() + timedelta(seconds=mo_osu.token.get('expires_in'))
print(mo_osu.token.get("access_token"))  # TEST


# COMMANDS SECTION
@bot.listen(hikari.GuildAvailableEvent)
async def on_guild_join(eventguild):
    server_db = mo_db.get_server(int(eventguild.guild.id))
    if not server_db:
        mo_db.save_server(int(eventguild.guild.id), str(eventguild.guild.name))


@bot.command(name='join', help='Join to Multi-off')
async def mo_join(ctx, username: str):
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

    user_db = mo_db.get_user(int(ctx.guild_id), int(ctx.author.id))
    if user_db:
        await ctx.respond('This user already has an osu account assigned')
        return

    osu_player = mo_osu.get_user(username)
    author = ctx.author.username + '#'+ ctx.author.discriminator
    if osu_player.get('discord') == author:
        mo_db.save_user(
            id=int(ctx.author.id),
            server_id=int(ctx.guild_id),
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
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

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
        await ctx.respond("You need to pass this level before adding it")
        return

    if beatmap_score_json['score']['beatmap']['status'] != 'ranked':
        await ctx.respond('Beatmap need to be ranked')
        return

    if beatmap_score_json['score']['score'] <= 0:
        await ctx.respond("You need to pass this level before adding it")
        return

    if beatmap_score_json['score']['rank'] not in ['B', 'A', 'SH', 'S', 'SSH', 'SS']:
        await ctx.respond('You need at least B rank')
        return

    mo_db.save_beatmap(int(beatmap_id), int(user[0]), int(ctx.guild_id))
    await ctx.respond('Beatmap added to the play-list!')


@bot.command(name='playlist', help='Show playlist')
async def mo_playlist(ctx):
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

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
async def mo_start(ctx, hours=0, minutes=0):
    hours = int(hours)
    minutes = int(minutes)
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

    if hours==0 and minutes==0:
        await ctx.respond('Try `mo!start <hours> <optional:minutes>`')
        return

    # Check valid time
    if hours<0 or minutes<0:
        await ctx.respond('Invalid time')
        return

    # Check players
    if not mo_db.get_users(int(ctx.guild_id)):
        await ctx.respond('First try `mo!join <osu-username>`')
        return

    # Check beatmap
    if not mo_db.get_beatmaps(int(ctx.guild_id)):
        await ctx.respond('First try `mo!add <link-beatmap>`')
        return

    # Check active play
    play = mo_db.get_active_play(int(ctx.guild_id))
    if play:
        await ctx.respond('Game in progress, try `mo!update`')
        return

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
    starttime = datetime.now()
    endtime = starttime + timedelta(hours=hours, minutes=minutes)
    mo_db.save_play(server_id=int(ctx.guild_id), beatmap_id=beatmap_id, end=endtime)

    beatmap = mo_osu.get_beatmap(beatmap_id)
    info = get_beatmap_info(beatmap)
    await channel.send(info)

    rank_array = get_table_rank_empty(start=starttime, delta=str(endtime-starttime), end=endtime, left=f"{hours}:{minutes}")
    rank = rank_array[0] + rank_array[1]
    message = await channel.send(rank)

    mo_db.update_message(int(message.id), int(ctx.guild_id))

    await ctx.respond('Game on!')


@bot.command(name='update', help='Update Scores')
async def mo_update(ctx):
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

    mo_db.end_game(int(ctx.guild_id), datetime.now())
    server_data = mo_db.get_server(int(ctx.guild_id))
    channel = ctx.get_guild().get_channel(server_data[4])
    message = await channel.fetch_message(server_data[5])
    play = mo_db.get_last_play(int(ctx.guild_id))

    # Get ranking
    users = mo_db.get_users(int(ctx.guild_id))
    rank_users = mo_osu.get_rank_beatmap_play(
        beatmap=play[2],
        user_list_db=users,
        start=str(play[4]),
        end=str(play[5]),
        play_id=str(play[0]),
        mo_db=mo_db
    )

    # Create Table
    rank_array = ""
    if play[3]:
        rank_array = get_table_rank_empty(start=play[4], delta=str(play[5]-play[4]), end=play[5], left=str(play[5]-datetime.now()))
    else:
        rank_array = get_table_rank_empty(start=play[4], delta=str(play[5]-play[4]), end=play[5], left="0", status="Ended")
    rank = rank_array[0]

    rank_users = dict(sorted(rank_users.items()))
    for idx, user_key in enumerate(rank_users):
        user = rank_users[user_key]
        if idx == 0:
            mo_db.update_podium_first(play_id=str(play[0]), user_id=user["user_id"])
        if idx == 1:
            mo_db.update_podium_second(play_id=str(play[0]), user_id=user["user_id"])
        if idx == 2:
            mo_db.update_podium_third(play_id=str(play[0]), user_id=user["user_id"])
        rank += f'\n║ {fill_string(str(idx+1), 4)} '
        rank += f'║ {fill_string(user["user_discord"], 13)} '
        rank += f'║ {fill_string(user["user_osu"], 9)} '
        rank += f'║ {fill_string(str(user["combo"]), 6)} '
        rank += f'║ {fill_string(str(user["acc"]), 4)} '
        rank += f'║ {fill_string(str(user["score"]), 18)} '
        rank += f'║ {fill_string(user["rank"], 4)} '
        rank += f'║{fill_string(str(user["time"]), 7)}║'
    rank += rank_array[1]

    await message.edit(content=rank)
    await ctx.respond('Updated')


@bot.command(name='kill', help='Stop current game')
async def mo_kill(ctx):
    mo_db.kill_game(int(ctx.guild_id))
    await ctx.respond('Game stopped')


@bot.command(name='clean', help='Clean multi-off channel')
async def mo_clean(ctx):
    server_data = mo_db.get_server(int(ctx.guild_id))
    channel = ctx.get_guild().get_channel(server_data[4])
    masseges = await channel.fetch_history(after=server_data[5])
    await channel.delete_messages(masseges)


@bot.command(name='ranking', help='Display the global-ranking')
async def mo_ranking(ctx):
    ranking = mo_db.get_ranking(int(ctx.guild_id))
    rank_array = get_table_grank()
    rank = rank_array[0]
    for pos, user in enumerate(ranking):
        rank += f'║ {fill_string(str(pos+1), 4)} '
        rank += f'║ {fill_string(str(user[1]), 15)} '
        rank += f'║ {fill_string(str(user[2]), 15)} '
        rank += f'║ {fill_string(str(user[3]), 6) if user[3] else fill_string("-", 6)} '
        rank += f'║ {fill_string(str(user[4]), 6) if user[4] else fill_string("-", 6)} '
        rank += f'║ {fill_string(str(user[5]), 6) if user[5] else fill_string("-", 6)} ║\n'
    rank += rank_array[1]
    await ctx.respond(rank)


HELP_MESSAGE = """
> __**Bot help**__

>>> **Commands Available:**
`join <osu-username>` - Join to Multi-off
`add <link-beatmap>` - Add new beatmap to the play-list
`playlist` - Show playlist
`start` - Start Multi-Off!
`update` - Update Scores
`kill` - Stop current game
`clean` - Clean multi-off channel
`ranking` - Display the global ranking
`help` - Displays this message
"""
@bot.command()
async def help(ctx):
    await ctx.respond(HELP_MESSAGE)



if DEBUG:
    bot.run(
    asyncio_debug=True,
    coroutine_tracking_depth=20,
    propagate_interrupts=True,
)

else:
    bot.run()
