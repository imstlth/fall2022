import adapt

adapt.transform("main.py", "script.py")
import script

n_win = 0
n_equal = 0
for i in range(100):
    result = script.main_function()
    if result == "WIN":
        n_win += 1
    elif result == "EQUAL":
        n_equal += 1

print("WIN RATE   =", n_win, "%")
print("LOSE RATE  =", 100 - n_win, "%")
print("EQUAL RATE =", n_equal, "%")
