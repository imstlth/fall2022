import re

filename_in = input("Enter the filename of the code : ")
file = open(filename_in, "r")
code = file.read()
file.close()

remplaced_code = re.sub("print", "gs.game_print", re.sub("input", "gs.game_input", code))
header = """# Created by adapt.py
# Don't change it
import gameserver as gs
gs.gen_map()
gs.gen_starting()

# Modified original code :
"""

main_function_win = """def main_function():
    winning_state = gs.game_input()
    if winning_state == "WIN":
        return "WIN"
"""

adapted_code = ""
main_function = False
for line in remplaced_code.split("\n"):
    if line == "# START MAIN LOOP":
        main_function = True
        adapted_code += main_function_win
    elif line == "# END MAIN LOOP":
        main_function = False
    line = "    " + line + "\n" if main_function else line + "\n"
    adapted_code += line


filename_out = input("Enter the filename where you want to save to adapted code : ")
file = open(filename_out, "w")
file.write(header + remplaced_code)
file.close()
