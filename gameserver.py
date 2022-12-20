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
    # Pas les coordonnées des limites de la map
    # -> Le nombre de case
    height = random.randint(7, 13)
    width = height * 2
    # On génère la map (le scrap_amount)
    half = []
    for _col in range(height):
        half.append([random.choices(scrap_poss, scrap_poss_weight)[0] for _line in range(height)])
    grid_scrap = eval(repr(half))
    for n_line in range(len(half)):
        grid_scrap[n_line] += half[-n_line - 1][::-1]


# Génère la position de départ des bots.
def gen_starting():
    global bots_pos, territory
    # On vérifie que les bots n'arrivent sur des cases avec de l'herbe
    while True:
        starting_robots = [random.randint(1, height - 3), random.randint(1, height - 2)]  # Il y a minimum 2 d'écart avec la ligne du milieu
        # On vérifie chaque case de l'"étoile"
        for x, y in star + ((0, 0),):
            # Si une des cases est de l'herbe, on relance une tentative
            if grid_scrap[starting_robots[1] + y][starting_robots[0] + x] == 0:
                break
        else:
            # On rajoute chacune des positions de l'étoile (autour du point central)
            bots_pos["self"] = [[starting_robots[0] + x, starting_robots[1] + y] for x, y in star]
            # Les bots ennemis sont sur le même y, mais à l'opposé au niveau de x
            bots_pos["ennemi"] = [[width - bot_x - 1, height - bot_y - 1] for bot_x, bot_y in bots_pos["self"]]
            # Les emplacements des bots sont forcément dans le territoire
            territory = eval(repr(bots_pos))
            # On rajoute la case centrale (starting_robots)
            territory["self"].append([starting_robots[0], starting_robots[1]])
            territory["ennemi"].append([width - starting_robots[0] - 1, height - starting_robots[1] - 1])
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

    # On augmente le compteur mais on le remet à 0 lorsque toutes les cases de la map ont été faites + 1 pour la quantité de matière + 1 pour savoir si le jeu est fini
    input_count = (input_count + 1) % (width * height + 2)

    if input_count == 0:
        if print_count >= 200 or territory["self"] == [] or territory["ennemi"] == []:  # Il faudrait que l'on fasse la situation où 20 tours ce sont passés sans que rien n'ait bougé -> TODO si c'est trop lent
            if len(territory["self"]) > len(territory["ennemi"]):
                return "WIN"
            elif len(territory["ennemi"]) > len(territory["self"]):
                return "LOSE"
            else:
                return "EQUAL"
        else:
            return "RUNNING"


    elif input_count == 1:
        return str(matter["self"]) + " " + str(matter["ennemi"])

    # On calcule à partir du compteur, la ligne et la colonne de la case.
    # On fait - 1 parce que 0 est pris pour renvoyer la quantité de matière
    line = (input_count - 2) // width
    col = (input_count - 2) % width

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
    # La case est libre si : c'est pas de l'herbe, ni un recycleur
    return grid_scrap[case[0]][case[1]] != 0 and case not in recyclers["self"] and case not in recyclers["ennemi"]

# La fonction qui permet de trouver un chemin entre un point A et B avec l'algorithme beam
def beam(beam_size, start, goal):
    # La liste des cases à expand
    buffer = [start]
    # Toutes les cases visitées et avec la profondeur à laquelle elles ont été visitées (la profondeur dans l'arbre)
    visited = {tuple(start): 0}
    deep = 0
    # Une fonction qui renvoie la distance entre un point et le goal
    def distance(from_coords, to_coords=goal):
        # Cette distance revient à ajouter les différences des coords
        # Parce que c'est une grille où on ne peut pas aller en diagonale.
        return abs(from_coords[0] - to_coords[0]) + abs(from_coords[1] - to_coords[1])

    # La boucle principale.
    # Elle ne s'arrête que lorsque la fin a été trouvée ou que l'algo a exploré toutes les cases
    while True:
        expand_cases = []
        # On expand les cases premières cases du buffer
        for _i in range(min([beam_size, len(buffer)])):
            case = buffer.pop(0)
            # expand revient à la remplacer par toutes les cases à côté (star) disponibles et non visitées.
            for add in star:
                next_case = [case[0] + add[0], case[1] + add[1]]
                if tuple(next_case) not in visited.keys() and free(next_case):
                    expand_cases.append(next_case)
                    visited[tuple(next_case)] = deep
                # Si une des cases est le goal, on fait le backtracing
                if next_case == goal:
                    return backtrace(deep, visited, goal)

        # On remplace les 4 cases qui ont pop par leurs cases expand
        # Les cases sont triées par leur distance avec le goal
        buffer = sorted(expand_cases, key=distance) + buffer
        # Si à ce moment là, le buffer est vide, cela veut dire qu'on a expand toutes les cases possibles.
        if buffer == []:
            return [start]  # On retourne la case de départ
        deep += 1

# La fonction qui permet de faire le backtracing
def backtrace(n, visited, goal):
    backpath = [goal]  # On part du goal pour revenir au start
    for reverse_deep in range(n - 1, -1, -1):  # On remonte la profondeur
        for add in star:
            voisin = [backpath[0][0] + add[0], backpath[0][1] + add[1]]
            try:
                # On voit si une cases voisine est moins profonde et on recommence à remonter à partir de cette case
                if visited[tuple(voisin)] == reverse_deep:
                    backpath.insert(0, voisin)
                    break
            except:
                continue
    return backpath


print_count = 0
# Cette fonction remplace print() dans le code
def game_print(command, owner="self"):
    global matter, recyclers, bots_pos, print_count, territory, grid_scrap
    # Le tour ce fini vraiment, une fois que l'ennemi a dit son action
    # Parce qu'il est toujours appelé une fois que self a fait un game_print
    # C'est pourquoi c'est ici qu'il y a tout le code pour que le jeu soit cohérent
    # Dans l'ordre :
    # Faire combattre les unités (les retirer un par un)
    # Mettre à jour le territoire
    # Réduire le scrap_amount
    # Les cases qui sont devenues de l'herbe suppriment les bots et les recycleurs sur elles
    # +10 à la quantité de matière de chaque joueur.
    if owner == "ennemi":
        print_count += 1  # Permet de compter le nombre de tours

        # Fait combattre les bots (supprime ceux qui sont à la fois dans bots_pos["self"] et bots_pos["ennemi"]
        for bot in bots_pos["self"]:
            if bot in bots_pos["ennemi"]:
                bots_pos["self"].remove(bot)
                bots_pos["ennemi"].remove(bot)

        # Changement de territoire
        owners = ["self", "ennemi"]
        for owner_i in range(1):
            add_matter = 0
            owner = owners[owner_i]
            opposite = owners[owner_i - 1]

            # Pour la position de chaque bot, on la rajoute à son territoire (si elle n'y est pas)
            # et on l'enlève au territoire ennemi si elle y est.
            for bot in bots_pos[owner]:
                if bot not in territory[owner]:
                    territory[owner].append(bot)
                if bot in territory[opposite]:
                    territory[opposite].remove(bot)

            # On réduit le scrap_amount et on enlève tout ce qu'il y a sur la case si il atteint 0
            # On l'enlève aussi du territoire auquel la case appartenait.
            for recycler in recyclers[owner]:
                for add in star + ((0, 0),):
                    recycled_case = [recycler[0] + add[0], recycler[1] + add[1]]
                    case_scrap_amount = grid_scrap[recycled_case[0]][recycled_case[1]]
                    if case_scrap_amount == 0:
                        continue
                    grid_scrap[recycled_case[0]][recycled_case[1]] -= 1
                    add_matter += 1
                    if case_scrap_amount - 1 == 0:
                        for owner in owners:
                            if recycled_case in recyclers[owner]:
                                recyclers[owner].remove(recycled_case)
                            if recycled_case in bots_pos[owner]:
                                # On supprime tous les bots de la case (jusqu'à que .remove renvoie une erreur)
                                while True:
                                    try:
                                        bots_pos[owner].remove(recycled_case)
                                    except:
                                        break
                            if recycled_case in territory[owner]:
                                territory[owner].remove(recycled_case)

            # On ajoute la quantité de matière générée par les recycleurs
            matter[owner] += add_matter + 10

    # Les commandes sont séparées par des ;
    command_list = command.split(";")
    # On organise les commandes pour faire les BUILD d'abord
    for n_cmd in range(len(command_list)):
        if command_list[n_cmd].startswith("BUILD"):
            command_list.insert(0, command_list.pop(n_cmd))

    for cmd in command_list:

        # Chaque action possède des arguments
        args = cmd.split()[1:]
        action = cmd.split()[0]

        if action == "MOVE":
            amount = int(args[0])
            start = [int(args[1]), int(args[2])]
            goal = [int(args[3]), int(args[4])]
            # On calcule le chemin à prendre
            path = beam(2, start, goal)
            # On vérifie qu'il y a bien le bon nombre de bots disponibles sur la case
            real_amount = min([amount, bots_pos[owner].count(start)])
            # On les déplace
            for _i in range(real_amount):
                bots_pos[owner].remove(start)
                bots_pos[owner].append(path[0])

        elif action == "BUILD":
            x = int(args[0])
            y = int(args[1])
            # On check que c'est possible de build sur la case
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
            # Idem
            if matter[owner] >= 10 * amount and \
                    grid_scrap[y][x] != 0 and \
                    [x, y] not in recyclers[owner] and \
                    [x, y] in territory[owner]:
                matter[owner] -= 10 * amount
                bots_pos[owner] += eval(repr([[x, y]] * amount))

    matter[owner] += 10
