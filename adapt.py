import re


header = """# Created by adapt.py
# Don't change it
import gameserver as gs
gs.gen_map()
gs.gen_starting()

# Modified original code :
"""

main_function_code = """# Adapted main loop into a function that returns if the program won at the end of the game
def main_function():
"""
win_code = """
        winning_state = gs.game_input()
        if winning_state in ["WIN", "LOSE", "EQUAL"]:
            return winning_state
"""

# filename_in = input("Enter the filename of the code : ")
# filename_out = input("Enter the filename where you want to save to adapted code : ")
def transform(filename_in, filename_out):
    file = open(filename_in, "r")
    code = file.read()
    file.close()

    remplaced_code = re.sub("print", "gs.game_print", re.sub("input", "gs.game_input", code))
    adapted_code = ""
    main_function = False
    for line in remplaced_code.split("\n"):
        if "# START MAIN LOOP" in line:
            main_function = True
            adapted_code += main_function_code
            line += win_code
        elif line == "# END MAIN LOOP":
            main_function = False
        line = "    " + line + "\n" if main_function else line + "\n"
        adapted_code += line


    file = open(filename_out, "w")
    file.write(header + adapted_code)
    file.close()
