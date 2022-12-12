# Init data:
width, height = [int(info) for info in input().split()]

# Boucle principale
while True:
    # À re-remplir à chaque fois
    grid = []
    _score_data = input().split()
    # On cherche à maximiser le score (avoir le plus de territoire par rapport à l'ennemi)
    score = int(_score_data[0]) - int(_score_data[1])
    for line in range(height):
        line_data = []
        for col in range(width):
            case = input().split()
            case_info = {
                "size": int(case[0]),
                "owner": int(case[1]),
                "n_bots": int(case[2]),
                "is_pumper": case[3] == "1",
                "is_pumped": case[6] == "1",
                "can_BUILD": case[4] == "1",
                "can_SPAWN": case[5] == "1"
            }
            line_data.append(case_info)
        grid.append(line_data)

    print("WAIT")
