import random

# Les statistiques de génération du scrap amount
scrap_poss = [0, 4, 6, 8, 9, 10]
scrap_poss_weight = [3, 7, 6, 8, 4, 4]
# Les variables globales
# Le scrap_amount pour chaque case de la grid
grid_scrap = []
height = 0
width = 0
# Les positions de tous les robots
bots_pos = {
    "ennemi": [],
    "self": []
}
# Le territoire
territory = eval(repr(bots_pos))  # Le "template" est le même que bots_pos


# Return une liste plus son symétrique (utile pour la génération de la map)
def symetry(liste):
    return liste + liste[::-1]


# Génére la map (le scrap_amount)
def gen_map():
    global height, width, grid_scrap
    height = random.randint(6, 12)
    # On fait toujours une width paire comme ça c'est plus simple
    width = height * 2
    # On génère la map (le scrap_amount)
    grid_scrap = [symetry([random.choices(scrap_poss, scrap_poss_weight)[0] for _c in range(height)]) for _l in range(height)]


# Génère la position de départ des bots.
def gen_starting():
    global bots_pos
    # On vérifie que les bots n'arrivent sur des cases avec de l'herbe
    while True:
        starting_robots = [random.randint(0, height - 4), random.randint(0, height - 1)]
        # On vérifie chaque case de l'"étoile"
        star = ((-1, 0), (0, -1), (1, 0), (0, 1))  # (0, 0) n'est pas dedans car la case ne contient pas de bots
        for x, y in star + ((0, 0),):
            # Si une des cases est de l'herbe, on relance une tentative
            if grid_scrap[starting_robots[1] + y][starting_robots[0] + x] == 0:
                break
        else:
            bots_pos["self"] = [[starting_robots[0] + x, starting_robots[1] + y] for x, y in star]
            bots_pos["ennemi"] = [[width - bot_x, height - bot_y] for bot_x, bot_y in bots_pos["self"]]
            territory = eval(repr(bots_pos))
            territory["ennemi"].append([width - starting_robots[0], height - starting_robots[1]])
            territory["self"].append([starting_robots[0], starting_robots[1]])
            break
