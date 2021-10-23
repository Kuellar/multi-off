from sqlalchemy import (DateTime, Float, BigInteger,
                        Column, Integer, String,
                        ForeignKey, Integer, Boolean)
from sqlalchemy.orm import declarative_base
import datetime

base = declarative_base()
class Server(base):
    __tablename__ = 'server'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50))
    max_players = Column(Integer, default=1000)
    premium = Column(Boolean, default=False)
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger)

class User(base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    server_id = Column(BigInteger, ForeignKey("server.id"), primary_key=True)
    name = Column(String(50))
    admin = Column(Boolean, default=False)
    osu_id = Column(BigInteger)
    osu_name = Column(String(11))
    cache_play_id = Column(BigInteger)
    cache_score = Column(BigInteger)
    cache_combo = Column(Integer)
    cache_acc = Column(Float)
    cache_rank = Column(String(4))
    cache_time = Column(DateTime)

class Beatmap(base):
    __tablename__ = 'beatmap'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), primary_key=True)
    server_id = Column(BigInteger, ForeignKey("server.id"), primary_key=True)
    ban = Column(Integer, default=False)
    active = Column(Boolean, default=True)

class Play(base):
    __tablename__ = 'play'

    id = Column(BigInteger, primary_key=True)
    server_id = Column(BigInteger, ForeignKey("server.id"), primary_key=True)
    beatmap_id = Column(BigInteger, ForeignKey("beatmap.id"), primary_key=True)
    active = Column(Boolean, default=True)
    start = Column(DateTime, default=datetime.datetime.now())
    end = Column(DateTime, default=datetime.datetime.now())
    first = Column(BigInteger)
    second = Column(BigInteger)
    third = Column(BigInteger)