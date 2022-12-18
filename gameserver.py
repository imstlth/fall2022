import random

# Les statistiques de génération du scrap amount
scrap_poss = [0, 4, 6, 8, 9, 10]
scrap_poss_weight = [3, 7, 6, 8, 4, 4]
# Les variables globales
# Le scrap_amount pour chaque case de la grid
grid_scrap = []
height = 0
width = 0
# Les variables qui contiennent les infos pour chaque joueur
# Les positions de tous les robots
bots_pos = {
    "ennemi": [],
    "self": []
}
# Le territoire
# Les emplacements des recycleurs (note : seuls ceux du joueur sont envoyés au programme)
# La quantité de matiériaux pour chaque joueur
territory, recyclers = (eval(repr(bots_pos)),) * 2  # Le "template" est le même que bots_pos
matter = {"self": 10, "ennemi": 10}

# Cette variable est l'emplacement des bots au tout départ
# Elle est utile pour plusieurs fonctions.
star = ((-1, 0), (0, -1), (1, 0), (0, 1))  # (0, 0) n'est pas dedans car la case ne contient pas de bots

# Génére la map (le scrap_amount)
def gen_map():
    global height, width, grid_scrap
    height = random.randint(6, 12)
    width = height * 2 + 1
    # On génère la map (le scrap_amount)
    half = []
    for _col in range(height + 1):
        half.append([random.choices(scrap_poss, scrap_poss_weight)[0] for _line in range(height + 1)])
    grid_scrap = eval(repr(half))
    for n_line in range(len(half)):
        grid_scrap[n_line] += half[-n_line - 1][::-1]


# Génère la position de départ des bots.
def gen_starting():
    global bots_pos, territory
    # On vérifie que les bots n'arrivent sur des cases avec de l'herbe
    while True:
        starting_robots = [random.randint(1, height - 2), random.randint(1, height - 1)]  # Il y a minimum 2 d'écart avec la ligne du milieu
        # On vérifie chaque case de l'"étoile"
        for x, y in star + ((0, 0),):
            # Si une des cases est de l'herbe, on relance une tentative
            if grid_scrap[starting_robots[1] + y][starting_robots[0] + x] == 0:
                break
        else:
            # On rajoute chacune des positions de l'étoile (autour du point central)
            bots_pos["self"] = [[starting_robots[0] + x, starting_robots[1] + y] for x, y in star]
            # Les bots ennemis sont sur le même y, mais à l'opposé au niveau de x
            bots_pos["ennemi"] = [[width - bot_x, bot_y] for bot_x, bot_y in bots_pos["self"]]
            # Les emplacements des bots sont forcément dans le territoire
            territory = eval(repr(bots_pos))
            # On rajoute la case centrale (starting_robots)
            territory["self"].append([starting_robots[0], starting_robots[1]])
            territory["ennemi"].append([width - starting_robots[0], starting_robots[1]])
            break

# La fonction qui remplace "input"
# On compte le nombre de fois que cette fonction a été appellée
# afin de renvoyer les informations qui conviennent à chaque fois.
input_count = -1
first_input = True
def game_input():
    global input_count, first_input

    # Le premier input demande toujours le width et le height de la map
    if first_input:
        first_input = False
        return str(width) + " " + str(height)

    # On augmente le compteur mais on le remet à 0 lorsque toutes les cases de la map ont été faites + 1 pour la quantité de matière
    input_count = (input_count + 1) % ((width + 1) * (height + 1) + 1)

    if input_count == 0:
        return str(matter["self"]) + " " + str(matter["ennemi"])

    # On calcule à partir du compteur, la ligne et la colonne de la case.
    # On fait - 1 parce que 0 est pris pour renvoyer la quantité de matière
    line = (input_count - 1) // (width + 1)
    col = (input_count - 1) % (width + 1)

    # On récupère les informations.

    # Si la case est recyclée par un recycler.
    for x, y in star + ((0, 0),):  # De nouveau, on utilise star
        if [col + x, line + y] in recyclers["self"] or [col + x, line + y] in recyclers["ennemi"]:
            is_recycled = "1"
            break
    else:
        is_recycled = "0"

    scrap_amount = grid_scrap[line][col]
    owner = "-1"
    if [col, line] in territory["self"]:
        owner = "1"
        owner_code = "self"
    elif [col, line] in territory["ennemi"]:
        owner = "0"
        owner_code = "ennemi"
    else:
        return str(scrap_amount) + " -1 0 0 0 0 " + is_recycled

    # Les informations pour chaque case
    units = bots_pos[owner_code].count([col, line])
    recycler = "1" if [col, line] in recyclers[owner_code] else "0"
    condition_base = matter["self"] >= 10 and scrap_amount != 0 and [col, line] in territory["self"]
    can_build = "1" if condition_base and units == 0 and not recycler else "0"
    can_spawn = "1" if condition_base and recycler != "1" else "0"

    return f"{str(scrap_amount)} {owner} {str(units)} {recycler} {can_build} {can_spawn} {is_recycled}"


# PATHFINDING ALGO -> BEAM (rayon de 3)
def free(case):
    return grid_scrap[case[0]][case[1]] != 0 and case not in recyclers["self"] and case not in recyclers["ennemi"]

def beam(beam_size, start, goal):
    buffer = [start]
    visited = {tuple(start): 0}
    n = 0
    def distance(from_coords, to_coords=goal):
        return abs(from_coords[0] - to_coords[0]) + abs(from_coords[1] - to_coords[1])
    while True:
        expand_cases = []
        for _i in range(min([beam_size, len(buffer)])):
            case = buffer.pop(0)
            for add in star:
                next_case = [case[0] + add[0], case[1] + add[1]]
                if tuple(next_case) not in visited.keys() and free(next_case):
                    expand_cases.append(next_case)
                    visited[tuple(next_case)] = n
                if next_case == goal:
                    return backtrace(n, visited, goal)
        if buffer == []:
            return [start]
        buffer = sorted(expand_cases, key=distance) + buffer
        n += 1

def backtrace(n, visited, goal):
    backpath = [goal]
    for reverse_n in range(n - 1, -1, -1):
        for add in star:
            voisin = [backpath[0][0] + add[0], backpath[0][1] + add[1]]
            try:
                if visited[tuple(voisin)] == reverse_n:
                    backpath.insert(0, voisin)
                    break
            except:
                continue
    return backpath


# Cette fonction remplace print() dans le code
def game_print(command, owner="self"):
    global matter, recyclers, bots_pos

    command_list = command.split(";")
    for n_cmd in range(len(command_list)):
        if command_list[n_cmd].startswith("BUILD"):
            command_list.insert(0, command_list.pop(n_cmd))

    for cmd in command_list:

        args = cmd.split()[1:]
        action = cmd.split()[0]

        if action == "MOVE":
            amount = int(args[0])
            start = [int(args[1]), int(args[2])]
            goal = [int(args[3]), int(args[4])]
            path = beam(2, start, goal)
            real_amount = min([amount, bots_pos["self"].count(start)])
            for _i in range(real_amount):
                bots_pos["self"].remove(start)
                bots_pos["self"].append(path[0])

        elif action == "BUILD":
            x = int(args[0])
            y = int(args[1])
            if matter[owner] >= 10 and \
                    grid_scrap[y][x] != 0 and \
                    [x, y] not in bots_pos[owner] and \
                    [x, y] in territory[owner]:
                matter[owner] -= 10
                recyclers[owner].append([x, y])

        elif action == "SPAWN":
            amount = int(args[0])
            x = int(args[1])
            y = int(args[2])
            if matter[owner] >= 10 * amount and \
                    grid_scrap[y][x] != 0 and \
                    [x, y] not in recyclers[owner] and \
                    [x, y] in territory[owner]:
                matter[owner] -= 10 * amount
                bots_pos[owner] += eval(repr([[x, y]] * amount))

    matter[owner] += 10

        # TODO:
        # L'action des ennemis
        # Enlever du scrap sur toutes les cases qui sont recylcées
        # Vérifier que les recycleurs ne se détruisent pas
        # Faire combattre les unités
        # Changer le territoire sur des unités
        # Supprimer les robots s'ils sont sur une case qui vient de devenir de l'herbe
