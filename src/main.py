#
# main.py - Основной запускаемый файл программы.
#


""" Управление:
    ЛКМ - Поставить клетку (удерживание).
    ПКМ - Удалить клетку (удерживание).

    S - Сохранить мир в файл.
    L - Загрузить мир из файла.

    G - Показать/Скрыть сетку для удобства.
    SPACE - Остановить/Возобновить симуляцию.
    N - Следующий шаг симуляции.

    Выбор материалов (клавиши 1-4).
    1 - Материал "СТЕНА".
    2 - Материал "ВОДА".
    3 - Материал "ПЕСОК".
    4 - Материал "ГАЗ".
"""


# Импортируем:
import os
import sys
import json
import time
import pygame
import random


# Конфигурация игры:
config = {
    "fps": 100,
    "cell-size": 8,
    "grid-size": [64, 64],
    "is-pause": False,
    "grid-enable": False,
    "clear-color": [0, 0, 0],
    "grid-color": [128, 128, 128],
    "save-load-file": "data/mapsave.sbx",

    "material-colors": {
        "wall": [92, 92, 92],
        "water": [0, 0, 255],
        "sand": [255, 128, 0],
        "gas": [32, 32, 32]
    }
}


# Если конфигурация есть, загружаем её:
if os.path.isfile("data/sand-config.json"):
    with open("data/sand-config.json", "r+", encoding="utf-8") as f:
        config = json.load(f)
else:  # Иначе, сохраняем файл конфигурации:
    with open("data/sand-config.json", "w+", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


# Переменные:
next_phys_step = False
selected = "wall"
delta_time = 1.0/60
cells = 0
fps         = config["fps"]
cell_size   = config["cell-size"]
grid_size   = config["grid-size"]
is_pause    = config["is-pause"]
grid_enable = config["grid-enable"]
clear_color = config["clear-color"]
grid_color  = config["grid-color"]
map_file    = config["save-load-file"]
materials   = config["material-colors"]


# Создание сетки мира:
grid = [["air" for _ in range(grid_size[0])] for _ in range(grid_size[1])]


# Создание окна:
pygame.init()
screen = pygame.display.set_mode((grid_size[0]*cell_size, grid_size[1]*cell_size))
pygame.display.set_caption("SandBox v1.0")
pygame.display.set_icon(pygame.image.load("data/icons/icon.png"))


# Сохранить карту:
def save_map() -> None:
    mapstr = ":".join([grid[y][x] for x in range(len(grid[y])) for y in range(len(grid))])
    with open(map_file, "w+", encoding="utf-8") as f:
        f.write(f"w{grid_size[0]},h{grid_size[1]}:"+mapstr)


# Загрузить карту:
def load_map() -> None:
    global grid, cells
    if not os.path.isfile(map_file): return
    mapdata = []
    with open(map_file, "r+", encoding="utf-8") as f:
        mapdata = f.read().split(":")
    size = mapdata[0].split(",")
    size = int(size[0][1:]), int(size[1][1:])
    mapdata = mapdata[1:]

    # Обнуляем сетку:
    grid = [["air" for _ in range(grid_size[0])] for _ in range(grid_size[1])]

    # Заполняем сетку данными:
    for y in range(size[1]):
        for x in range(size[0]):
            cell = mapdata[y + x*size[0]]
            if (x >= 0 and x < len(grid[0])) and (y >= 0 and y < len(grid)):
                if cell != "air": cells += 1
                grid[y][x] = cell


# Основной цикл программы:
while True:
    start_time = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s: save_map()
            if event.key == pygame.K_l: load_map()
            if event.key == pygame.K_SPACE: is_pause = not is_pause
            if event.key == pygame.K_n: next_phys_step = True
            if event.key == pygame.K_g: grid_enable = not grid_enable

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_x // cell_size, mouse_y // cell_size

    # Выбор материала:
    keys = pygame.key.get_pressed()
    if keys[pygame.K_1]:
        selected = "wall"
    elif keys[pygame.K_2]:
        selected = "water"
    elif keys[pygame.K_3]:
        selected = "sand"
    elif keys[pygame.K_4]:
        selected = "gas"

    # Создать/Удалить клетку:
    if pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x, grid_y = mouse_x // cell_size, mouse_y // cell_size
        if (grid_x >= 0 and grid_x < len(grid[0])) and (grid_y >= 0 and grid_y < len(grid)):
            if grid[grid_y][grid_x] == "air": cells += 1
            grid[grid_y][grid_x] = selected
    elif pygame.mouse.get_pressed()[2]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x, grid_y = mouse_x // cell_size, mouse_y // cell_size
        if (grid_x >= 0 and grid_x < len(grid[0])) and (grid_y >= 0 and grid_y < len(grid)):
            if grid[grid_y][grid_x] != "air": cells -= 1
            grid[grid_y][grid_x] = "air"

    # Очищаем экран:
    screen.fill(clear_color)

    # Рисуем клетки:
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x] == "wall":
                pygame.draw.rect(screen, materials["wall"], (x * cell_size, y * cell_size, cell_size, cell_size))
            if grid[y][x] == "water":
                pygame.draw.rect(screen, materials["water"], (x * cell_size, y * cell_size, cell_size, cell_size))
            elif grid[y][x] == "sand":
                pygame.draw.rect(screen, materials["sand"], (x * cell_size, y * cell_size, cell_size, cell_size))
            elif grid[y][x] == "gas":
                pygame.draw.rect(screen, materials["gas"], (x * cell_size, y * cell_size, cell_size, cell_size))

    # Отрисовка сетки:
    if grid_enable:
        for x in range(0, screen_width, cell_size):
            pygame.draw.line(screen, grid_color, (x, 0), (x, screen_height))
        for y in range(0, screen_height, cell_size):
            pygame.draw.line(screen, grid_color, (0, y), (screen_width, y))

    # Обновление физики:
    if not is_pause or next_phys_step:
        if next_phys_step: next_phys_step = False
        for y in range(len(grid) - 1, -1, -1):  # Обработка снизу вверх (от ny до 0):
            for x in range(len(grid[y])):
                if grid[y][x] == "water":
                    if y < len(grid) - 1 and grid[y + 1][x] in ["air"]:
                        grid[y][x], grid[y + 1][x] = grid[y + 1][x], grid[y][x]
                    else:
                        direction = random.choice([-1, 1])
                        if 0 <= x + direction < len(grid[y]) and grid[y][x + direction] in ["air"]:
                            grid[y][x], grid[y][x + direction] = grid[y][x + direction], grid[y][x]

                if grid[y][x] == "sand":
                    if y < len(grid) - 1 and grid[y + 1][x] in ["air", "water"]:
                        grid[y][x], grid[y + 1][x] = grid[y + 1][x], grid[y][x]
                    elif y < len(grid) - 1:
                        if x > 0 and grid[y + 1][x - 1] in ["air", "water"]:
                            grid[y][x], grid[y + 1][x - 1] = grid[y + 1][x - 1], grid[y][x]
                        elif x < len(grid[y]) - 1 and grid[y + 1][x + 1] in ["air", "water"]:
                            grid[y][x], grid[y + 1][x + 1] = grid[y + 1][x + 1], grid[y][x]

        # Отдельная логика для газа (сверху вниз. От 0 до ny):
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x] == "gas":
                    if y > 0 and grid[y - 1][x] in ["air", "water", "sand"]:
                        grid[y][x], grid[y - 1][x] = grid[y - 1][x], grid[y][x]
                    else:
                        direction = random.choice([-1, 1])
                        if 0 <= x + direction < len(grid[y]) and grid[y][x + direction] in ["air", "water", "sand"]:
                            grid[y][x], grid[y][x + direction] = grid[y][x + direction], grid[y][x]

    # Устанавливаем заголовок окна:
    pygame.display.set_caption(
        f"SandBox | Material: {selected.title()} | Cells: {cells} | FPS: {round(1.0/delta_time, 3)} / {float(fps)}"
    )

    # Обновление экрана:
    pygame.display.flip()

    # Задержка для управления скоростью обновления:
    pygame.time.Clock().tick(fps)

    # Вычисляем дельту времени:
    delta_time = time.time()-start_time
