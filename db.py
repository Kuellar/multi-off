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

    def save_user(self, id:int, server_id:int,name:str, osu_id:int, osu_name:str):
        sql = '''
            INSERT INTO user (id, server_id, name, osu_id, osu_name)
            VALUES (%s, %s, %s, %s, %s)
        '''

        self.cursor.execute(sql, (id, server_id, name, osu_id, osu_name,))
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

    def get_user(self, server_id:int, id:int):
        sql = '''
            SELECT * FROM `user`
            WHERE `server_id`=%s AND `id`=%s
        '''
        self.cursor.execute(sql, (server_id, id,))
        return self.cursor.fetchone()

    def get_users(self, server_id:int):
        sql = '''
            SELECT * FROM `user`
            WHERE `server_id`=%s
        '''
        self.cursor.execute(sql, (server_id,))
        return self.cursor.fetchall()

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

    def get_server(self, server_id:int):
        sql = """
            SELECT * FROM server
            WHERE id = %s;
        """
        self.cursor.execute(sql, (server_id,))
        return self.cursor.fetchone()

    def update_channel(self, channel_id:int, server_id:int):
        sql = """
            UPDATE server
            SET channel_id = '%s'
            WHERE id = %s;
        """
        self.cursor.execute(sql, (channel_id, server_id,))
        self.db.commit()

    def update_message(self, message_id:int, server_id:int):
        sql = """
            UPDATE server
            SET message_id = '%s'
            WHERE id = %s;
        """
        self.cursor.execute(sql, (message_id, server_id,))
        self.db.commit()

    def update_cache_user(self, server_id:int, user_id:int, play_id:int, score:int, combo:int, acc:float, rank:str, time):
        sql = """
            UPDATE user
            SET cache_play_id = %s, cache_score = %s, cache_combo = %s, cache_acc = %s, cache_rank = %s, cache_time = %s
            WHERE server_id = %s AND id = %s;
        """
        self.cursor.execute(sql, (play_id, score, combo, acc, rank, time, server_id, user_id,))
        self.db.commit()

    def end_game(self, server_id:int, end_time):
        sql = '''
            SELECT * FROM `play`
            WHERE `server_id`=%s AND `end`<=%s AND `active`=1
        '''
        self.cursor.execute(sql, (server_id, end_time,))
        ended = self.cursor.fetchall()
        for i in ended:
            sql = """
            UPDATE play
            SET active = '0'
            WHERE id = %s;
            """
            self.cursor.execute(sql, (i[0],))
            self.db.commit()

    def get_active_play(self, server_id:int):
        sql = '''
            SELECT * FROM `play`
            WHERE `server_id`=%s AND `active`=1
        '''
        self.cursor.execute(sql, (server_id,))
        return self.cursor.fetchone()

    def get_last_play(self, server_id:int):
        sql = '''
            SELECT * FROM `play`
            WHERE `server_id`=%s
            ORDER BY `end` DESC
        '''
        self.cursor.execute(sql, (server_id,))
        return self.cursor.fetchone()

    def kill_game(self, server_id:int):
        sql = '''
            SELECT * FROM `play`
            WHERE `server_id`=%s AND `active`=1
        '''
        self.cursor.execute(sql, (server_id,))
        ended = self.cursor.fetchall()
        for i in ended:
            sql = """
            UPDATE play
            SET active = '0'
            WHERE id = %s;
            """
            self.cursor.execute(sql, (i[0],))
            self.db.commit()

    def update_podium_first(self, play_id, user_id):
        sql = """
            UPDATE play
            SET first = %s
            WHERE id = %s;
            """
        self.cursor.execute(sql, (user_id, play_id,))
        self.db.commit()

    def update_podium_second(self, play_id, user_id):
        sql = """
            UPDATE play
            SET second = %s
            WHERE id = %s;
            """
        self.cursor.execute(sql, (user_id, play_id,))
        self.db.commit()

    def update_podium_third(self, play_id, user_id):
        sql = """
            UPDATE play
            SET third = %s
            WHERE id = %s;
            """
        self.cursor.execute(sql, (user_id, play_id,))
        self.db.commit()
