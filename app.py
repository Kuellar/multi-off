import os
from flask import Flask, abort, jsonify
from markupsafe import escape
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, desc
from sqlalchemy.orm import sessionmaker
from model import Server, User, Beatmap, Play

app = Flask(__name__)
load_dotenv()

# Database connection
online = False
try:
    db_host = os.getenv('db_host')
    db_user = os.getenv('db_user')
    db_password = os.getenv('db_password')
    db_database = os.getenv('db_database')
    DATABSE_URI=f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_database}'
    engine = create_engine(DATABSE_URI)
    connection = engine.connect()
    metadata = MetaData()
    online = True
except:
    pass

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/status", methods=['GET'])
def status():
    if online:
        return {"online": True}
    else:
        return {"online": False}

@app.route("/servers", methods=['GET'])
def servers():
    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        res = []
        try:
            servers = session.query(Server).all()
            for server in servers:
                players = len(session.query(User).filter_by(server_id=server.id).all())
                plays = len(session.query(Play).filter_by(server_id=server.id).all())
                beatmaps = len(session.query(Beatmap).filter_by(server_id=server.id).all())
                res.append({
                    "id": server.id,
                    "name": server.name,
                    "players": players,
                    "plays": plays,
                    "beatmaps": beatmaps,
                })
        except:
            return {"error": ":("}
        finally:
            session.close()
            return jsonify(res)

@app.route("/servers/<server_id>", methods=['GET'])
def server(server_id):
    SessionFactory = sessionmaker(engine)
    with SessionFactory() as session:
        try:
            server = session.query(Server).filter_by(id=server_id).all()
            if len(server) != 1:
                raise Exception("Invalid id")
            server = server[0]
            players = len(session.query(User).filter_by(server_id=server.id).all())
            plays = len(session.query(Play).filter_by(server_id=server.id).all())
            beatmaps = len(session.query(Beatmap).filter_by(server_id=server.id).all())
        except:
            return {"error": ":("}
        else:
            res = {
            "name": server.name,
            "players": players,
            "plays": plays,
            "beatmaps": beatmaps,
            }
            return res
        finally:
            session.close()
