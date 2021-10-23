import os
from datetime import datetime, timedelta
import random

import hikari
import lightbulb
from dotenv import load_dotenv

from sqlalchemy import create_engine, MetaData, desc
from sqlalchemy.orm import sessionmaker

from osu import osu
from utils import (fill_string, get_beatmap_id, get_beatmap_info,
                   get_introduction, get_table_grank, get_table_rank_empty,
                   get_tableform, only_fill)

from model import Server, User, Beatmap, Play

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

DATABSE_URI=f'mysql+mysqlconnector://{db_user}:{""}@{db_host}/{db_database}'
engine = create_engine(DATABSE_URI)
connection = engine.connect()
metadata = MetaData()

# Osu connection
osu_id= os.getenv('osu_id')
osu_secret= os.getenv('osu_secret')
mo_osu = osu(osu_id, osu_secret)
token_expiration = datetime.now() + timedelta(seconds=mo_osu.token.get('expires_in'))
print(mo_osu.token.get("access_token"))  # TEST


# COMMANDS SECTION
@bot.listen(hikari.GuildAvailableEvent)
async def on_guild_join(eventguild):
    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            server_db = session.query(Server).filter_by(id=int(eventguild.guild.id)).all()
            if not server_db:
                new_server = Server(
                    id=int(eventguild.guild.id),
                    name=str(eventguild.guild.name)
                )
                session.add(new_server)
        finally:
            session.commit()
            session.close()


@bot.command(name='join')
async def mo_join(ctx, username: str):
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            user_db = session.query(User).filter_by(id=int(ctx.author.id), server_id=int(ctx.guild_id)).all()
            if user_db:
                await ctx.respond('This user already has an osu account assigned')
                return

            osu_player = mo_osu.get_user(username)
            author = ctx.author.username + '#'+ ctx.author.discriminator
            if osu_player.get('discord') == author:
                new_user = User(
                    id=int(ctx.author.id),
                    server_id=int(ctx.guild_id),
                    name=author,
                    osu_id=int(osu_player['id']),
                    osu_name=osu_player['username'],
                )
                session.add(new_user)

                print(f'Adding user: "{author}" to the db')
                await ctx.respond(f'{username} joined successfully')
            else:
                await ctx.respond('Sorry, some kind of error has occurred')
        finally:
            session.commit()
            session.close()


@bot.command(name='add')
async def mo_add(ctx, beatmap: str):
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            user = session.query(User).filter_by(id=int(ctx.author.id), server_id=int(ctx.guild_id)).all()
            if not user:
                await ctx.respond('Join to multi-off with `mo!join "osu-username"`')
                return
            user = user[0]

            beatmap_id = get_beatmap_id(str(beatmap))
            if not beatmap_id:
                await ctx.respond('Invalid beatmap format, try `https://osu.ppy.sh/beatmapsets/[...]#osu/[...]`')
                return

            beatmap_db = session.query(Beatmap).filter_by(id=beatmap_id, server_id=user.server_id).all()
            if beatmap_db:
                await ctx.respond('This beatmap already exist')
                return

            beatmap_score_json = mo_osu.get_user_beatmap_score(int(user.osu_id), beatmap_id)
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

            new_beatmap = Beatmap(
                id=beatmap_id,
                user_id=user.id,
                server_id=user.server_id,
            )
            session.add(new_beatmap)
            await ctx.respond('Beatmap added to the play-list!')
        finally:
                session.commit()
                session.close()


@bot.command(name='playlist')
async def mo_playlist(ctx):
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            beatmap_db = session.query(Beatmap).filter_by(server_id=int(ctx.guild_id)).all()
            playlist = [mo_osu.get_beatmap(beatmap.id) for beatmap in beatmap_db]
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
        finally:
            session.commit()
            session.close()


@bot.command(name='start')
async def mo_start(ctx, hours=0, minutes=0):
    hours = int(hours)
    minutes = int(minutes)
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            if hours==0 and minutes==0:
                await ctx.respond('Try `mo!start <hours> <optional:minutes>`')
                return

            # Check valid time
            if hours<0 or minutes<0:
                await ctx.respond('Invalid time')
                return

            # Check players
            users = session.query(User).filter_by(server_id=int(ctx.guild_id)).all()
            if not users:
                await ctx.respond('First try `mo!join <osu-username>`')
                return

            # Check beatmap
            beatmaps = session.query(Beatmap).filter_by(server_id=int(ctx.guild_id)).all()
            if not beatmaps:
                await ctx.respond('First try `mo!add <link-beatmap>`')
                return

            # Check active play
            play = session.query(Play).filter_by(server_id=int(ctx.guild_id), active=True).all()
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

            server = session.query(Server).filter_by(id=int(ctx.guild_id)).first()
            server.channel_id = channel.id

            # Clean channel
            history = await channel.fetch_history()
            await channel.delete_messages(history)
            await channel.send(get_introduction())

            # Pick and Show actual beatmap
            beatmap = random.choice(beatmaps)
            starttime = datetime.now()
            endtime = starttime + timedelta(hours=hours, minutes=minutes)

            new_play = Play(
                    server_id=int(ctx.guild_id),
                    beatmap_id=beatmap.id,
                    end=endtime,
                )
            session.add(new_play)

            beatmap = mo_osu.get_beatmap(beatmap.id)
            info = get_beatmap_info(beatmap)
            await channel.send(info)

            rank_array = get_table_rank_empty(start=starttime, delta=str(endtime-starttime), end=endtime, left=f"{hours}:{minutes}")
            rank = rank_array[0] + rank_array[1]
            message = await channel.send(rank)
            server.message_id = message.id

            await ctx.respond('Game on!')

        finally:
            session.commit()
            session.close()


@bot.command(name='update', help='Update Scores')
async def mo_update(ctx):
    if datetime.now() >= token_expiration:
        mo_osu.update_token()

    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            plays = session.query(Play).filter(
                Play.server_id==int(ctx.guild_id),
                Play.active==True,
                Play.end<=datetime.now()
            ).all()
            for play in plays:
                play.active=False
                session.commit()

            server = session.query(Server).filter_by(id=int(ctx.guild_id)).first()
            channel = ctx.get_guild().get_channel(server.channel_id)
            message = await channel.fetch_message(server.message_id)

            play = session.query(Play).filter_by(server_id=int(ctx.guild_id)).order_by(desc(Play.end)).first()

            # Get ranking
            users = session.query(User).filter_by(server_id=int(ctx.guild_id)).all()
            rank_users = mo_osu.get_rank_beatmap_play(
                beatmap=play.beatmap_id,
                user_list_db=users,
                start=str(play.start),
                end=str(play.end),
                play_id=str(play.id),
                mo_db=session
            )

            # Create Table
            rank_array = []
            if play.active:
                rank_array = get_table_rank_empty(start=str(play.start), delta=str(play.end-play.start), end=str(play.end), left=str(play.end-datetime.now()))
            else:
                rank_array = get_table_rank_empty(start=str(play.start), delta=str(play.end-play.start), end=str(play.end), left="0", status="Ended")
            rank = rank_array[0]

            rank_key_sorted = sorted(rank_users)
            count = 0
            for key in rank_key_sorted:
                user_play = rank_users[key]
                if not play.active:
                    if count == 0:
                        play.first = user_play["user_id"]
                    if count == 1:
                        play.second = user_play["user_id"]
                    if count == 2:
                        play.third = user_play["user_id"]
                rank += f'\n║ {fill_string(str(count+1), 4)} '
                rank += f'║ {fill_string(user_play["user_discord"], 13)} '
                rank += f'║ {fill_string(user_play["user_osu"], 9)} '
                rank += f'║ {fill_string(str(user_play["combo"]), 6)} '
                rank += f'║ {fill_string(str(user_play["acc"]), 4)} '
                rank += f'║ {fill_string(str(user_play["score"]), 18)} '
                rank += f'║ {fill_string(user_play["rank"], 4)} '
                rank += f'║{fill_string(str(user_play["time"]), 7)}║'
                count += 1
            rank += rank_array[1]

            await message.edit(content=rank)
            if play.active:
                await ctx.respond('Updated')
            else:
                await ctx.respond('Updated - GameOver')
        finally:
            session.commit()
            session.close()


@bot.command(name='kill', help='Stop current game')
async def mo_kill(ctx):
    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            plays = session.query(Play).filter_by(
                server_id=int(ctx.guild_id),
                active=True,
            ).all()
            for play in plays:
                play.active=False
                session.commit()
            await ctx.respond('Game stopped')
        finally:
            session.close()


@bot.command(name='clean', help='Clean multi-off channel')
async def mo_clean(ctx):
    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            server_data = session.query(Server).filter_by(id=int(ctx.guild_id)).first()
            channel = ctx.get_guild().get_channel(server_data.channel_id)
            masseges = await channel.fetch_history(after=server_data.message_id)
            await channel.delete_messages(masseges)
        finally:
            session.close()


@bot.command(name='ranking', help='Display the global-ranking')
async def mo_ranking(ctx):
    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            ranking = {}

            users = session.query(User).filter_by(server_id=int(ctx.guild_id)).all()
            for user in users:
                ranking[user.id] = {
                    'points': 0,
                    'first': 0,
                    'second': 0,
                    'third': 0,
                    'user': user
                }
            plays = session.query(Play).filter_by(server_id=int(ctx.guild_id)).all()
            for play in plays:
                if play.first:
                    ranking[play.first]['first'] += 1
                    ranking[play.first]['points'] += 3
                    if play.second:
                        ranking[play.second]['second'] += 1
                        ranking[play.second]['points'] += 2
                        if play.third:
                            ranking[play.third]['third'] += 1
                            ranking[play.third]['points'] += 1

            rank_array = get_table_grank()
            rank = rank_array[0]
            count = 0
            for _, user_dic in sorted(ranking.items(), key=lambda x:x[1]["points"]):
                rank += f'║ {fill_string(str(count+1), 4)} '
                rank += f'║ {fill_string(str(user_dic["user"].name), 15)} '
                rank += f'║ {fill_string(str(user_dic["user"].osu_name), 15)} '
                rank += f'║ {fill_string(str(user_dic["first"]), 6)} '
                rank += f'║ {fill_string(str(user_dic["second"]), 6)} '
                rank += f'║ {fill_string(str(user_dic["third"]), 6)} ║\n'
                count += 1
            rank += rank_array[1]
            await ctx.respond(rank)
        finally:
            session.close()


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
