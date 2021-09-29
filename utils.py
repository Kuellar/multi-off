def get_beatmap_id(beatmap:str):
    if 'osu.ppy.sh/beatmapsets' in beatmap:
        return beatmap.split('#osu/')[1]
    return False

def fill_string(word, length):
    res = word[0:length]
    return res + ' '*(length-len(res))

def only_fill(word, length):
    res = length-len(word)
    if res>0:
        return word + ' '*res
    return word

def get_tableform():
    a = '''```╔══════════════════════╦═══════╦══════╦══════╦══════╦════════╦═════════════════════════════════════╗
║        Tittle        ║ Stars ║  acc ║  ar  ║  bpm ║ length ║                 url                 ║
╠══════════════════════╬═══════╬══════╬══════╬══════╬════════╬═════════════════════════════════════╣
'''
    b =  '\n╠══════════════════════╬═══════╬══════╬══════╬══════╬════════╬═════════════════════════════════════╣\n'

    c = '╚══════════════════════╩═══════╩══════╩══════╩══════╩════════╩═════════════════════════════════════╝```'

    return [a, b, c]

def get_introduction():
    return """Juega el siguiente beatmap para competir con el resto de los miembros del canal.
Con el comando `mo!update` puedes actualizar la información.
Con el comando `mo!clean` puedes limpiar este canal.
Suerte!"""

def get_beatmap_info(beatmap):
    res = f"""-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-
**Title**:  {beatmap['beatmapset']['title']}  -  {beatmap['beatmapset']['artist']}
__Url:__  https://osu.ppy.sh/beatmaps/{beatmap['id']}
-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-
Mode:  {beatmap['mode']}  -  Status:  {beatmap['status']}
Dificulty Rating:  {beatmap['difficulty_rating']}  -  {beatmap['version']}
Lenght:  {beatmap['total_length']}  -  BPM: {beatmap['bpm']}  -  Count Circles:  {beatmap['count_circles']}  -  Count Sliders:  {beatmap['count_sliders']}
-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-
CS:  {beatmap['cs']}
HP:  {beatmap['drain']}
Accuracy:  {beatmap['accuracy']}
AR:  {beatmap['ar']}
Max Combo:  {beatmap['max_combo']}
-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-
"""
    return res

def get_table_rank_empty(start, delta, end, left, status="Ongoing"):
    a = f"""```╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                    Beatmap Ranking                                   ║
╠══════════════════════╦═══════════════════════════╦════════════════════╦══════════════╣
║ Start Time           ║ {fill_string(str(start), 25)} ║                    ║              ║
╠══════════════════════╬═══════════════════════════╣ Status             ║ {fill_string(status, 12)} ║
║ Delta Time           ║ {fill_string(delta, 25)} ║                    ║              ║
╠══════════════════════╬═══════════════════════════╬════════════════════╬══════════════╣
║ End Time             ║ {fill_string(str(end), 25)} ║ Time Left          ║ {fill_string(left, 12)} ║
╠══════════════════════╬═══════════════════════════╬════════════════════╬══════════════╣
╠══════╦═══════════════╬═══════════╦════════╦══════╬════════════════════╬══════╦═══════╣
║ Rank ║ User[Discord] ║ User[osu] ║ Combo  ║ Acc  ║ Score              ║ Rank ║ Time  ║
╠══════╬═══════════════╬═══════════╬════════╬══════╬════════════════════╬══════╬═══════╣"""

    b = "\n╚══════╩═══════════════╩═══════════╩════════╩══════╩════════════════════╩══════╩═══════╝```"
    return [a, b]

def get_table_grank():
    a = """```╔═════════════════════════════════════════════════════════════════════╗
║                               Ranking                               ║
╠══════╦═══════════════════════════════════╦════════╦════════╦════════╣
║      ║                User               ║        ║        ║        ║
╠══════╬═════════════════╦═════════════════╣   1°   ║   2°   ║   3°   ║
║ Rank ║     Discord     ║       Osu       ║        ║        ║        ║
╠══════╬═════════════════╬═════════════════╬════════╬════════╬════════╣\n"""
    b = "╚══════╩═════════════════╩═════════════════╩════════╩════════╩════════╝```"
    return [a, b]