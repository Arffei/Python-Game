import random
import os
import json

ROWS = 10
COLS = 10
SAVE_FILE = "save.json"

field = [["." for _ in range(COLS)] for _ in range(ROWS)]
fire_timers = {}

heli_x = 0
heli_y = 0
water = 0
max_water = 3
lives = 3
score = 0
weather = "clear"


def in_bounds(x, y):
    return 0 <= x < ROWS and 0 <= y < COLS


def random_empty_cell():
    while True:
        x = random.randint(0, ROWS - 1)
        y = random.randint(0, COLS - 1)
        if field[x][y] == ".":
            return x, y


def generate_rivers(count):
    for i in range(count):
        x, y = random_empty_cell()
        field[x][y] = "~"


def generate_trees(count):
    for i in range(count):
        x, y = random_empty_cell()
        field[x][y] = "T"


def place_buildings():
    field[0][0] = "S"
    field[ROWS - 1][COLS - 1] = "H"


def start_fire():
    trees = [(x, y) for x in range(ROWS) for y in range(COLS) if field[x][y] == "T"]
    if not trees:
        return
    x, y = random.choice(trees)
    field[x][y] = "F"
    fire_timers[(x, y)] = 3


def spread_fire():
    chance = 0.5 if weather == "storm" else 0.2
    for (x, y) in list(fire_timers.keys()):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and field[nx][ny] == "T" and random.random() < chance:
                field[nx][ny] = "F"
                fire_timers[(nx, ny)] = 3


def burn_trees():
    global score
    for (x, y) in list(fire_timers.keys()):
        if weather == "rain":
            fire_timers[(x, y)] -= 0
        else:
            fire_timers[(x, y)] -= 1
        if fire_timers[(x, y)] <= 0:
            field[x][y] = "."
            score -= 5
            del fire_timers[(x, y)]


def grow_trees():
    if random.random() < 0.3:
        x, y = random_empty_cell()
        field[x][y] = "T"


def update_weather():
    global weather
    weather = random.choice(["clear", "clear", "rain", "storm"])


def extinguish():
    global water, score
    pos = (heli_x, heli_y)
    if pos in fire_timers and water > 0:
        field[heli_x][heli_y] = "."
        score += 10
        water -= 1
        del fire_timers[pos]
        print("Дерево потушено")
    else:
        print("Тушить нечего или нет воды")


def take_water():
    global water
    if field[heli_x][heli_y] == "~" and water < max_water:
        water += 1
        print("Вода набрана")
    else:
        print("Здесь нет реки или бак полон")


def use_hospital():
    global score, lives
    if field[heli_x][heli_y] == "H" and score >= 10:
        score -= 10
        lives += 1
        print("Здоровье восстановлено")
    else:
        print("Недостаточно очков или вы не у госпиталя")


def use_shop():
    global score, max_water
    if field[heli_x][heli_y] == "S" and score >= 15:
        score -= 15
        max_water += 1
        print("Бак увеличен")
    else:
        print("Недостаточно очков или вы не в магазине")


def move(dx, dy):
    global heli_x, heli_y
    nx, ny = heli_x + dx, heli_y + dy
    if in_bounds(nx, ny):
        heli_x, heli_y = nx, ny


def print_field():
    os.system("cls" if os.name == "nt" else "clear")
    print("Погода:", weather, "| Очки:", score, "| Жизни:", lives, "| Вода:", water, "/", max_water)
    for x in range(ROWS):
        line = ""
        for y in range(COLS):
            if x == heli_x and y == heli_y:
                line += "V "
            else:
                line += field[x][y] + " "
        print(line)


def save_game():
    state = {
        "field": field,
        "fire_timers": {f"{k[0]},{k[1]}": v for k, v in fire_timers.items()},
        "heli_x": heli_x,
        "heli_y": heli_y,
        "water": water,
        "max_water": max_water,
        "lives": lives,
        "score": score,
        "weather": weather,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f)
    print("Игра сохранена")


def load_game():
    global field, fire_timers, heli_x, heli_y, water, max_water, lives, score, weather
    with open(SAVE_FILE, "r") as f:
        state = json.load(f)
    field = state["field"]
    fire_timers = {}
    for key, v in state["fire_timers"].items():
        x, y = key.split(",")
        fire_timers[(int(x), int(y))] = v
    heli_x = state["heli_x"]
    heli_y = state["heli_y"]
    water = state["water"]
    max_water = state["max_water"]
    lives = state["lives"]
    score = state["score"]
    weather = state["weather"]
    print("Игра загружена")


def tick():
    update_weather()
    if random.random() < 0.3:
        start_fire()
    spread_fire()
    burn_trees()
    grow_trees()


def main():
    global lives
    generate_rivers(10)
    generate_trees(15)
    place_buildings()

    while lives > 0:
        print_field()
        command = input("Команда (w/a/s/d, e - тушить, t - вода, h - госпиталь, m - магазин, save, load, quit): ")

        if command == "w":
            move(-1, 0)
        elif command == "s":
            move(1, 0)
        elif command == "a":
            move(0, -1)
        elif command == "d":
            move(0, 1)
        elif command == "e":
            extinguish()
        elif command == "t":
            take_water()
        elif command == "h":
            use_hospital()
        elif command == "m":
            use_shop()
        elif command == "save":
            save_game()
        elif command == "load":
            load_game()
        elif command == "quit":
            break

        tick()

    print("Игра окончена. Счёт:", score)


main()