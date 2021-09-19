def get_beatmap_id(beatmap:str):
    if 'osu.ppy.sh/beatmapsets' in beatmap:
        return beatmap.split('#osu/')[1]
    return False

def fill_string(word, length):
    res = word[0:20]
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
    return """Aquí va una introducción al juego..."""