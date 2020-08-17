import json

MAPPINGS = {
    "red": "R",
    "green": "G",
    "blue": "B",
    "yellow": "Y",
    "magic_staff": "M",
    "helmet": "H",
    "dagger": "D",
    "axe": "A" 
}
KNIGHTS = {
    "R": {
        "Attack": 1,
        "Defence": 1,
        "equiped_item": None,
        "coordinates": [0, 0],
        "status": "LIVE",
    },  # top left
    "B": {
        "Attack": 1,
        "Defence": 1,
        "equiped_item": None,
        "coordinates": [7, 0],
        "status": "LIVE",
    },  # top right
    "G": {
        "Attack": 1,
        "Defence": 1,
        "equiped_item": None,
        "coordinates": [7, 7],
        "status": "LIVE",
    },  # bottom left
    "Y": {
        "Attack": 1,
        "Defence": 1,
        "equiped_item": None,
        "coordinates": [0, 7],
        "status": "LIVE",
    },  # bottom right
}

BONUS_ITEMS = {
    "A": {"Attack": 2, "Defence": 0, "coordinates": [2, 2], "is_equiped": False},
    "D": {"Attack": 1, "Defence": 0, "coordinates": [2, 5], "is_equiped": False},
    "M": {"Attack": 1, "Defence": 0, "coordinates": [5, 2], "is_equiped": False},
    "H": {"Attack": 1, "Defence": 1, "coordinates": [5, 5], "is_equiped": False},
}
ORDERED_BONUS_ITEMS = ["A", "M", "D", "H"]

FINAL_STATE = {
    "red": [],
    "green": [],
    "blue": [],
    "yellow": [],
    "magic_staff": [],
    "helmet": [],
    "dagger": [],
    "axe": [],
}

def move_rules(coordinates, direction):
    temp = tuple(coordinates)
    if direction == "N":
        coordinates[0] = coordinates[0] - 1
    elif direction == "E":
        coordinates[1] = coordinates[1] + 1
    elif direction == "W":
        coordinates[1] = coordinates[1] - 1
    elif direction == "S":
        coordinates[0] = coordinates[0] + 1
    for coord in coordinates:
        if coord < 0 or coord > 7:
            return {"coordinates": temp, "status": "DROWNED"}

    return {"coordinates": coordinates, "status": "LIVE"}


def drop_equiped_item_by_defeated_knight(knight):
    item = KNIGHTS[knight]["equiped_item"]
    if item is not None:
        BONUS_ITEMS[item]["is_equiped"] = False
        BONUS_ITEMS[item]["coordinates"] = KNIGHTS[knight]["coordinates"]


def update_defeated_or_drowned_knight(knight, status):
    drop_equiped_item_by_defeated_knight(knight)
    if status == "DROWNED":
        KNIGHTS[knight]["coordinates"] = None
    KNIGHTS[knight]["equiped_item"] = None
    KNIGHTS[knight]["status"] = status
    KNIGHTS[knight]["Attack"] = 0
    KNIGHTS[knight]["Defence"] = 0


def update_knights_after_fight(attacker, defender):
    attacker_knight = KNIGHTS[attacker]
    defender_knight = KNIGHTS[defender]
    if attacker_knight["coordinates"] == defender_knight[
        "coordinates"
    ] and defender_knight["status"] not in ["DROWNED", "DEAD"]:
        attacker_knight["Attack"] = attacker_knight["Attack"] + 0.5
        defender_knight["Defence"] = defender_knight["Defence"]
        if attacker_knight["Attack"] > defender_knight["Defence"]:
            update_defeated_or_drowned_knight(defender, "DEAD")
        elif attacker_knight["Attack"] < defender_knight["Defence"]:
            update_defeated_or_drowned_knight(attacker, "DEAD")


def read_moves_from_file(file_name):
    moves = open(file_name).read().splitlines()
    if moves[0] == "GAME-START" and moves[-1] == "GAME-END":
        moves = moves[1:-1]
    return moves


def equip_bonus_by_knight(knight):
    for item in ORDERED_BONUS_ITEMS:
        if (
            KNIGHTS[knight]["coordinates"] == BONUS_ITEMS[item]["coordinates"]
            and BONUS_ITEMS[item]["is_equiped"] == False
            and KNIGHTS[knight]["equiped_item"] is None
        ):
            KNIGHTS[knight]["equiped_item"] = item
            KNIGHTS[knight]["Attack"] = (
                BONUS_ITEMS[item]["Attack"] + KNIGHTS[knight]["Attack"]
            )
            KNIGHTS[knight]["Defence"] = (
                BONUS_ITEMS[item]["Defence"] + KNIGHTS[knight]["Defence"]
            )
            BONUS_ITEMS[item]["is_equiped"] = True
            break
    return None

def write_final_state_to_json(file_name, final_state):
    jsonified = json.dumps(final_state, indent=2)
    with open(file_name,"w") as f:
        f.write(jsonified)


if __name__ == "__main__":

    moves = read_moves_from_file("moves.txt")

    for move in moves:
        knight = move.split(":")[0]
        direction = move.split(":")[1]

        if (
            KNIGHTS[knight]["coordinates"] is not None
            and KNIGHTS[knight]["status"] != "DEAD"
        ):

            res = move_rules(KNIGHTS[knight]["coordinates"], direction)
            KNIGHTS[knight]["coordinates"] = res["coordinates"]
            KNIGHTS[knight]["status"] = res["status"]
            equip_bonus_by_knight(knight)
            if KNIGHTS[knight]["status"] != "DROWNED":
                for k in KNIGHTS:
                    if k != knight:
                        update_knights_after_fight(knight, k)
            elif KNIGHTS[knight]["status"] == "DROWNED":
                update_defeated_or_drowned_knight(knight, KNIGHTS[knight]["status"])


    for key in FINAL_STATE:
        symbol = MAPPINGS[key]
        if symbol in ORDERED_BONUS_ITEMS:
            FINAL_STATE[key] = [
                BONUS_ITEMS[symbol]["coordinates"],
                BONUS_ITEMS[symbol]["is_equiped"]
            ]
        else:
            FINAL_STATE[key] = [
                "null" if KNIGHTS[symbol]["coordinates"] is None else KNIGHTS[symbol]["coordinates"],
                KNIGHTS[symbol]["status"],
                "null" if KNIGHTS[symbol]["equiped_item"] is None else KNIGHTS[symbol]["equiped_item"],
                KNIGHTS[symbol]["Attack"],
                KNIGHTS[symbol]["Defence"]
            ]

    write_final_state_to_json("final_state.json", FINAL_STATE)
