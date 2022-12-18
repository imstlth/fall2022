import re

file = open("base.py", "r")
code = file.read()
file.close()

remplaced_code = re.sub("print", "gs.game_print", re.sub("input", "gs.game_input", code))
header = """# Created by adapt.py
# Don't change it
import gameserver as gs
gs.gen_map()
gs.gen_starting()

# Real code :"""

file = open("ai.py", "w"
