import requests
from datetime import datetime, timedelta

class osu:
    def __init__(self, id, secret):
        self.id=id
        self.secret=secret
        self.token = requests.post(
            url='https://osu.ppy.sh/oauth/token',
            headers={
                "Content-Type": "application/json"
            },
            json={
                'client_id': id,
                'client_secret': secret,
                'grant_type': 'client_credentials',
                'scope': 'public'
            },
        ).json()

    def update_token(self):
        self.token = requests.post(
            url='https://osu.ppy.sh/oauth/token',
            headers={
                "Content-Type": "application/json"
            },
            json={
                'client_id': self.id,
                'client_secret': self.secret,
                'grant_type': 'client_credentials',
                'scope': 'public'
            },
        ).json()
        print("TOKEN UPDATED")

    def get_user(self, username):
        return requests.get(
            url=f'https://osu.ppy.sh/api/v2/users/{username}/osu?key=username',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token.get('access_token')}",
            },
        ).json()

    def get_beatmap(self, beatmap):
        return requests.get(
            url=f'https://osu.ppy.sh/api/v2/beatmaps/{beatmap}',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token.get('access_token')}",
            },
        ).json()

    def get_user_beatmap_score(self, user, beatmap):
        return requests.get(
            url=f'https://osu.ppy.sh/api/v2/beatmaps/{beatmap}/scores/users/{user}',
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token.get('access_token')}",
            },
        ).json()

    def get_rank_beatmap_play(self, beatmap, user_list_db, start, end, play_id, mo_db):
        res = {}
        start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S") # Check
        end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M:%S") # Check
        for user in user_list_db:
            best = {}
            # Check cached data
            if user.cache_play_id == play_id:
                best = {
                    "user_id": user.id,
                    "user_discord": user.name,
                    "user_osu": user.osu_name,
                    "combo": user.cache_combo,
                    "acc": user.cache_acc,
                    "score": user.cache_score,
                    "rank": user.cache_rank,
                    "time": user.cache_time,
                }
            plays = requests.get(
                    url=f'https://osu.ppy.sh/api/v2/users/{user.osu_id}/scores/recent?mode=osu&limit=3000',
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self.token.get('access_token')}",
                        },
                    ).json()
            for play in plays:
                if play["beatmap"]["id"] == beatmap:
                    time_dt = datetime.strptime(play["created_at"], "%Y-%m-%dT%H:%M:%S+00:00") - timedelta(hours=3)
                    if not best or play["score"] > best["score"]:
                        if time_dt >= start_dt and time_dt <= end_dt:
                            best = {
                                "user_id": user.id,
                                "user_discord": user.name,
                                "user_osu": user.osu_name,
                                "combo": play["max_combo"],
                                "acc": play["accuracy"],
                                "score": play["score"],
                                "rank": play["rank"],
                                "time": time_dt,
                            }
                        else:
                            # Check cambios de horas ...
                            # No deberian caer muchos casos en este else
                            # si las partidas duran más de 24hrs
                            print("-----------")
                            print(time_dt)
                            print(end_dt)
                            print(start_dt)

            if best:
                user.cache_play_id = play_id
                user.cache_score = best["score"]
                user.cache_combo = best["combo"]
                user.cache_acc = best["acc"]
                user.cache_rank = best["rank"]
                user.cache_time = best["time"]
                mo_db.commit()
                # Evita scores repetidos
                tmp = best["score"]
                while res.get(tmp):
                    tmp += 1
                res[tmp] = best

        return res
