import requests

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