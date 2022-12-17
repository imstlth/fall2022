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
territory, recyclers, matter = (eval(repr(bots_pos)),) * 3  # Le "template" est le même que bots_pos

# Cette variable est l'emplacement des bots au tout départ
# Elle est utile pour plusieurs fonctions.
star = ((-1, 0), (0, -1), (1, 0), (0, 1))  # (0, 0) n'est pas dedans car la case ne contient pas de bots

# Return une liste plus son symétrique (utile pour la génération de la map)
def symetry(liste):
    return liste + liste[::-1]


# Génére la map (le scrap_amount)
def gen_map():
    global height, width, grid_scrap
    height = random.randint(6, 12) - 1
    # On fait toujours une width paire comme ça c'est plus simple
    width = height * 2 + 1
    # On génère la map (le scrap_amount)
    grid_scrap = [symetry([random.choices(scrap_poss, scrap_poss_weight)[0] for _c in range(height + 1)]) for _l in range(height + 1)]


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
input_count = -2
def game_input():
    global input_count

    # Le premier input demande toujours le width et le height de la map
    if input_count == -2:
        input_count = -1
        return str(width) + " " + str(height)

    else:
        # On augment le compteur mais on le remet à 0 lorsque toutes les cases de la map ont été faites
        input_count = (input_count + 1) % ((width + 1) * (height + 1))

        # On calcule à partir du compteur, la ligne et la colonne de la case.
        line = input_count // (width + 1)
        col = input_count % (width + 1)

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
        can_build = "1" if scrap_amount != 0 and units == 0 and [col, line] in territory["self"] else "0"
        can_spawn = "1" if scrap_amount != 0 and recycler != "1" and [col, line] in territory["self"] else "0"

        return f"{str(scrap_amount)} {owner} {str(units)} {recycler} {can_build} {can_spawn} {is_recycled}"
