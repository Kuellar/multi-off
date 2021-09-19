import mysql.connector

class db:
    def __init__(self, host, user, password, database):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        self.cursor = self.db.cursor(buffered=True)

    def save_server(self, id:int, name:str):
        sql = '''
            INSERT INTO server (id, name)
            VALUES (%s, %s)
        '''

        self.cursor.execute(sql, (id, name,))
        self.db.commit()

    def save_user(self, server_id:int, id:int, name:str, osu_id:int, osu_name:str):
        sql = '''
            INSERT INTO user (server_id, id, name, osu_id, osu_name)
            VALUES (%s, %s, %s, %s, %s)
        '''

        self.cursor.execute(sql, (server_id, id, name, osu_id, osu_name,))
        self.db.commit()

    def save_beatmap(self, id:int, user_id:int, server_id:int):
        sql = '''
            INSERT INTO beatmap (id, user_id, server_id)
            VALUES (%s, %s, %s)
        '''

        self.cursor.execute(sql, (id, user_id, server_id,))
        self.db.commit()

    def save_play(self, server_id:int, beatmap_id:int, end):
        sql = '''
            INSERT INTO play (server_id, beatmap_id, end)
            VALUES (%s, %s, %s)
        '''
        self.cursor.execute(sql, (server_id, beatmap_id, end,))
        self.db.commit()

    def get_user(self, server_id:int, id):
        sql = '''
            SELECT * FROM `user`
            WHERE `server_id`=%s AND `id`=%s
        '''
        self.cursor.execute(sql, (server_id, id,))
        return self.cursor.fetchone()

    def get_beatmap(self, id:int, server_id:int):
        sql = '''
            SELECT * FROM `beatmap`
            WHERE `id`=%s AND `server_id`=%s
        '''
        self.cursor.execute(sql, (id, server_id,))
        return self.cursor.fetchone()

    def get_random_beatmap(self, server_id:int):
        sql = '''
            SELECT * FROM `beatmap`
            WHERE `server_id`=%s
            ORDER BY RAND()
        '''
        self.cursor.execute(sql, (server_id,))
        return self.cursor.fetchone()

    def get_beatmaps(self, server_id:int):
        sql = '''
            SELECT * FROM `beatmap`
            WHERE `server_id`=%s
        '''
        self.cursor.execute(sql, (server_id,))
        return self.cursor.fetchall()

    def get_servers(self):
        sql = """
            SELECT name FROM server
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update_channel(self, channel_id:int, server_id:int, ):
        sql = """
            UPDATE server
            SET channel_id = '%s'
            WHERE id = %s;
        """
        self.cursor.execute(sql, (channel_id, server_id,))
        self.db.commit()
