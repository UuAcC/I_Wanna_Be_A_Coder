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

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "game_data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# ----------------------------- Глобальные переменные --------------------------------------
FPS = 70
WIDTH = 800
HEIGHT = 600
BTN_SPRITES = pygame.sprite.Group()
SCREEN = pygame.display.set_mode((800, 600))
CLOCK = pygame.time.Clock()
POINTS = []
PLAYER, KEY, CAMERA = None, None, None
LEVEL = 'menu'
ALL_SPRITES = pygame.sprite.Group()
TILES_GROUP = pygame.sprite.Group()
GATES_GROUP = pygame.sprite.Group()
PLAYER_GROUP = pygame.sprite.Group()
FIRST_SCORE = 0
TILE_IMAGES = {
    'wall': [load_image('block_1.png'), load_image('block_1.png'), load_image('block_2.png')],
    'vert_horn': [load_image('spike_d-u.png'), load_image('spike_d-u_1.png')],
    'gate': [load_image('right_door.png'), load_image('wrong_door.png')],
    'hor_horn': load_image('spike_f.png'),
    'win_gate': load_image('win_gate.png')
}
PLAYER_IMAGE = [load_image('ufo.png'), load_image('r_rob.png')]

tile_width = tile_height = 25
# ----------------------------- Глобальные переменные --------------------------------------

# ----------------------------- Камера --------------------------------------


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if obj.rect.x <= -100:
            obj.kill()

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
# ----------------------------- Камера --------------------------------------


# ----------------------------- Создание уровней --------------------------------------
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, reverse=False, flip=False):
        super().__init__(TILES_GROUP, ALL_SPRITES)
        if tile_type == 'wall' or tile_type == 'vert_horn':
            if reverse:
                self.image = pygame.transform.flip(random.choice(TILE_IMAGES[tile_type]), False, True)
            else:
                self.image = random.choice(TILE_IMAGES[tile_type])
        elif tile_type == 'gate':
            if reverse:
                self.image = TILE_IMAGES[tile_type][0]
            else:
                self.image = TILE_IMAGES[tile_type][1]
        elif tile_type == 'win_gate':
            self.image = TILE_IMAGES[tile_type]
        elif tile_type == 'hor_horn':
            if flip:
                self.image = pygame.transform.flip(TILE_IMAGES[tile_type], True, False)
            else:
                self.image = TILE_IMAGES[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(PLAYER_GROUP, ALL_SPRITES)
        self.image = PLAYER_IMAGE[0]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global KEY, FIRST_SCORE
        self.rect.x += FPS // 20
        if KEY == pygame.K_s:
            self.rect.y += FPS // 12
        elif KEY == pygame.K_w:
            self.rect.y -= FPS // 12
        for sprite in GATES_GROUP:
            if pygame.sprite.collide_rect(self, sprite):
                if sprite == TILE_IMAGES['gate'][0]:
                    FIRST_SCORE += 1
                elif sprite == TILE_IMAGES['gate'][1]:
                    FIRST_SCORE -= 1
                elif sprite == TILE_IMAGES['win_gate']:
                    victory_screen(SCREEN, CLOCK)
                    for elem in ALL_SPRITES:
                        elem.kill()
                    KEY = None
        for sprite in TILES_GROUP:
            if pygame.sprite.collide_mask(self, sprite):
                death_screen(SCREEN, CLOCK)
                for elem in ALL_SPRITES:
                    elem.kill()
                KEY = None


def generate_level(level):
    global PLAYER
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile('vert_horn', x, y)
            elif level[y][x] == '?':
                Tile('vert_horn', x, y, True)
            elif level[y][x] == '$':
                tile = Tile('gate', x, y, True)
                GATES_GROUP.add(tile)
                TILES_GROUP.remove(tile)
            elif level[y][x] == '%':
                tile = Tile('gate', x, y)
                GATES_GROUP.add(tile)
                TILES_GROUP.remove(tile)
            elif level[y][x] == 'w':
                tile = Tile('win_gate', x, y)
                GATES_GROUP.add(tile)
                TILES_GROUP.remove(tile)
            elif level[y][x] == '=':
                Tile('hor_horn', x, y)
            elif level[y][x] == '-':
                Tile('hor_horn', x, y, False, True)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                PLAYER = Player(x, y)
    return PLAYER, x, y
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
            if self.image in Button.images:
                self.image = Button.c_images[Button.images.index(self.image)]
            if button == 1 and self.rect.y == 200:
                player, level_x, level_y = generate_level(load_level('_just_run_level.txt'))
                rules_of_first(SCREEN, CLOCK)
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
    pygame.draw.line(screen, point.color, (point.w, point.h), (point.w + FPS // 60, point.h), 1)


def animation():
    POINTS.append(Point())
    for p in POINTS:
        animate(SCREEN, p)
        p.update()
# ----------------------------- Анимация внизу окна -----------------------------------------

# ----------------------------- Заставка, экран смерти и окна правил --------------------------------------


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


def death_screen(screen, clock):
    global LEVEL, CAMERA
    while True:
        fon = load_image('death.png')
        screen.blit(fon, (250, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                LEVEL = 'menu'
                CAMERA = None
                return
        pygame.display.flip()
        clock.tick(FPS)


def victory_screen(screen, clock):
    global LEVEL, CAMERA
    while True:
        fon = load_image('win.png')
        screen.blit(fon, (50, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                LEVEL = 'menu'
                CAMERA = None
                return
        pygame.display.flip()
        clock.tick(FPS)


def rules_of_first(screen, clock):
    global LEVEL, CAMERA
    while True:
        SCREEN.fill(pygame.Color('black'))
        fon = pygame.transform.scale(load_image('first_rules.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                LEVEL = 'first'
                CAMERA = Camera()
                return
        animation()
        pygame.display.flip()
        clock.tick(FPS)
# ----------------------------- Заставка, экран смерти и окна правил --------------------------------------


def main():
    global FPS, LEVEL, PLAYER, KEY
    pygame.init()
    pygame.display.set_caption('I wanna be a CODER (v.0.3.1)')

    start_screen(SCREEN, CLOCK)

    label = pygame.sprite.Sprite()
    label.image = load_image('menu_label.png')
    label.rect = label.image.get_rect()
    label.rect.x, label.rect.y = 250, 50
    label.add(BTN_SPRITES)
    btns = []
    for n in range(3):
        btns.append(Button(n))
    running = True
    while running:
        SCREEN.fill(pygame.Color('black'))
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if LEVEL == 'menu':
                if event.type == pygame.MOUSEMOTION:
                    for b in btns:
                        b.update(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for b in btns:
                        b.update(event.pos, event.button)

            if LEVEL == 'first':
                if event.type == pygame.KEYDOWN:
                    KEY = event.key
                if event.type == pygame.KEYUP:
                    KEY = None

        if LEVEL == 'menu':
            animation()
            BTN_SPRITES.draw(SCREEN)
        elif LEVEL == 'first':
            ALL_SPRITES.draw(SCREEN)
            PLAYER.update()
            if CAMERA:
                CAMERA.update(PLAYER)
                for sprite in ALL_SPRITES:
                    CAMERA.apply(sprite)
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
