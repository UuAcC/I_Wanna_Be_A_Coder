import os
import sys
import pygame
import random



def load_image(name, colorkey=None):
    fullname = os.path.join('game_data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# ----------------------------- Глобальные переменные --------------------------------------
FPS = 60
WIDTH = 800
HEIGHT = 600
BTN_SPRITES = pygame.sprite.Group()
SCREEN = pygame.display.set_mode((800, 600))
CLOCK = pygame.time.Clock()
POINTS = []
ALL_SPRITES = pygame.sprite.Group()
TILES_GROUP = pygame.sprite.Group()
PLAYER_GROUP = pygame.sprite.Group()

TILE_IMAGES = {
    'wall': [load_image('block_1.png'), load_image('block_1.png'), load_image('block_2.png')],
    'horn': [[load_image('spike_d-u.png'), load_image('spike_d-u_1.png')], load_image('spike_f.png')],
    'gate': [load_image('right_door.png'), load_image('wrong_door.png')]
}
PLAYER_IMAGE = load_image('ufo.png')

tile_width = tile_height = 25
# ----------------------------- Глобальные переменные --------------------------------------


# ----------------------------- Создание уровней --------------------------------------
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(TILES_GROUP, ALL_SPRITES)
        self.image = TILE_IMAGES[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(PLAYER_GROUP, ALL_SPRITES)
        self.image = PLAYER_IMAGE
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '#':
                Tile(random.choice('wall'), x, y)
            elif level[y][x] == '!':
                Tile(random.choice('horn'[0]), x, y)
            elif level[y][x] == '$':
                Tile('gate'[0], x, y)
            elif level[y][x] == '?':
                tile = pygame.transform.flip(random.choice('horn'[0]), False, True)
                Tile(tile, x, y)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                new_player = Player(x, y)
    return new_player, x, y
# ----------------------------- Создание уровней --------------------------------------


# ----------------------------- Кнопки главного меню --------------------------------------
class Button(pygame.sprite.Sprite):
    images = [load_image('first_btn.png'), load_image('second_btn.png'), load_image('boss_btn.png')]
    c_images = [load_image('first_btn_clicked.png'),
                load_image('second_btn_clicked.png'),
                load_image('boss_btn_clicked.png')]

    def __init__(self, n):
        super().__init__(BTN_SPRITES)
        self.image = Button.images[n]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.topleft = (100, 200 + 120 * n)

    def update(self, pos, button=3):
        x, y = pos
        if self.rect.x <= x <= self.rect.x + 200 and self.rect.y <= y <= self.rect.y + 100:
            if button == 1 and self.rect.y == 200:
                rules_of_first(SCREEN, CLOCK)
            if self.image in Button.images:
                self.image = Button.c_images[Button.images.index(self.image)]
        else:
            if self.image in Button.c_images:
                self.image = Button.images[Button.c_images.index(self.image)]
# ----------------------------- Кнопки главного меню --------------------------------------

# ----------------------------- Анимация внизу окна ---------------------------------------


class Point:
    def __init__(self):
        self.h = 600
        self.w = random.randint(0, 800)
        self.color = (4, 242, 255)

    def update(self):
        self.h -= 2
        if self.h < 500:
            self.color = (0, 0, 0)


def animate(screen, point):
    pygame.draw.line(screen, point.color, (point.w, point.h), (point.w + 1, point.h), 1)


def animation():
    POINTS.append(Point())
    for p in POINTS:
        animate(SCREEN, p)
        p.update()
# ----------------------------- Анимация внизу окна -----------------------------------------

# ----------------------------- Заставка и окна правил --------------------------------------


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen, clock):
    while True:
        SCREEN.fill(pygame.Color('black'))
        fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        animation()
        pygame.display.flip()
        clock.tick(FPS)


def rules_of_first(screen, clock):
    while True:
        SCREEN.fill(pygame.Color('black'))
        fon = pygame.transform.scale(load_image('first_rules.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        animation()
        pygame.display.flip()
        clock.tick(FPS)
# ----------------------------- Заставка и окна правил --------------------------------------


def main():
    global FPS
    pygame.init()

    start_screen(SCREEN, CLOCK)

    label = pygame.sprite.Sprite()
    label.image = load_image('menu_label.png')
    label.rect = label.image.get_rect()
    label.rect.x, label.rect.y = 250, 50
    label.add(BTN_SPRITES)

    running = True
    player, level_x, level_y = generate_level(load_level('_just_run_level.txt'))
    btns = []
    for n in range(3):
        btns.append(Button(n))
    while running:
        SCREEN.fill(pygame.Color('black'))
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION:
                for b in btns:
                    b.update(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in btns:
                    b.update(event.pos, event.button)

        animation()
        ALL_SPRITES.draw(SCREEN)
        BTN_SPRITES.draw(SCREEN)
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
