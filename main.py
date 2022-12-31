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
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
POINTS = []
PLAYER, KEY, CAMERA = None, None, None
LEVEL = 'menu'
ALL_SPRITES = pygame.sprite.Group()
TILES_GROUP, DEADLY_TILES_GROUP = pygame.sprite.Group(), pygame.sprite.Group()
GATES_GROUP = pygame.sprite.Group()
RIGHT_DOORS, WRONG_DOORS, WIN_DOORS = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
PLAYER_GROUP, ENEMY_GROUP = pygame.sprite.Group(), pygame.sprite.Group()
LOCK_GROUP = pygame.sprite.Group()
PLAYER_SHOOT_GROUP, SHOOT_GROUP = pygame.sprite.Group(), pygame.sprite.Group()
FIRST_SCORE, SECOND_SCORE, AIMED = 0, 0, 0
JUMP_POWER = 5
GRAVITY = 0.15
left = right = up = False
TILE_IMAGES = {
    'wall': [load_image('block_1.png'), load_image('block_1.png'), load_image('block_2.png')],
    'vert_horn': [load_image('spike_d-u.png'), load_image('spike_d-u_1.png')],
    'gate': [load_image('right_door.png'), load_image('wrong_door.png')],
    'hor_horn': load_image('spike_f.png'),
    'win_gate': load_image('win_gate.png'),
    'enemy': load_image('enemy.png'),
    'enemy_shoot': load_image('enemy_shoot.png'),
    'player_shoot': load_image('player_shoot.png')
}
PLAYER_IMAGE = [load_image('ufo.png'), load_image('r_rob.png')]
FIRST_COMPLETE, SECOND_COMPLETE = False, False
tile_width = tile_height = 25
# ----------------------------- Глобальные переменные --------------------------------------

# ----------------------------- Камера --------------------------------------


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        global LEVEL
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if LEVEL == 'first':
            if obj.rect.x <= -25:
                obj.kill()

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
# ----------------------------- Камера --------------------------------------


# ----------------------------- Все объекты --------------------------------------
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, reverse=False):
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
            if reverse:
                self.image = pygame.transform.flip(TILE_IMAGES[tile_type], True, False)
            else:
                self.image = TILE_IMAGES[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Shoot(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, tile_group, reverse=False, speed=3):
        global LEVEL
        super().__init__(SHOOT_GROUP, ALL_SPRITES)
        if reverse:
            self.image = pygame.transform.flip(TILE_IMAGES[tile_group], True, False)
        else:
            self.image = TILE_IMAGES[tile_group]
        self.rect = self.image.get_rect().move(
            pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = speed
        self.tile = tile_group

    def update(self):
        global AIMED
        self.rect.x += self.speed
        for sprite in TILES_GROUP:
            if pygame.sprite.collide_mask(self, sprite):
                self.kill()
        for sprite in ENEMY_GROUP:
            if pygame.sprite.collide_mask(self, sprite):
                self.kill()
        if self.tile == 'player_shoot':
            for bug in ENEMY_GROUP:
                if pygame.sprite.collide_mask(self, bug):
                    AIMED += 1
                    if AIMED == 5:
                        bug.kill()
                        AIMED = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, reverse=False, atts=12, bs=3):
        global LEVEL
        super().__init__(ENEMY_GROUP, ALL_SPRITES)
        self.reverse = False
        if reverse:
            self.image = pygame.transform.flip(TILE_IMAGES['enemy'], True, False)
            self.reverse = True
        else:
            self.image = TILE_IMAGES['enemy']
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.attack_speed = atts
        self.bullet_speed = bs
        self.count = 0

    def update(self):
        self.count += 1
        if self.count == self.attack_speed * 10:
            shoot = Shoot((self.rect.x + 40), (self.rect.y + 5), 'enemy_shoot', self.reverse, self.bullet_speed)
            SHOOT_GROUP.add(shoot)
            self.count = 0
# ----------------------------- Все объекты --------------------------------------


# ----------------------------- Игрок --------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        global LEVEL
        super().__init__(PLAYER_GROUP, ALL_SPRITES)
        if LEVEL == 'first':
            self.image = PLAYER_IMAGE[0]
        else:
            self.image = PLAYER_IMAGE[1]
        self.yvel = 0
        self.xvel = 0
        self.startX = pos_x
        self.startY = pos_y
        self.reverse = False
        self.onGround = False
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def collide(self, xvel, yvel, platforms):
        for sprite in platforms:
            if pygame.sprite.collide_rect(self, sprite):
                if xvel > 0:
                    self.rect.right = sprite.rect.left
                if xvel < 0:
                    self.rect.left = sprite.rect.right
                if yvel > 0:
                    self.rect.bottom = sprite.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = sprite.rect.bottom
                    self.yvel = 0

    def shoot(self):
        shoot = None
        if self.reverse:
            shoot = Shoot((self.rect.left - 23), (self.rect.top + 8), 'player_shoot', False, -7)
        else:
            shoot = Shoot(self.rect.right, (self.rect.top + 8), 'player_shoot', True, 7)
        PLAYER_SHOOT_GROUP.add(shoot)
        SHOOT_GROUP.remove(shoot)

    def update(self):
        global KEY, FIRST_SCORE, FIRST_COMPLETE, LEVEL, JUMP_POWER, GRAVITY, left, right, up
        if LEVEL == 'first':
            self.rect.x += FPS // 20
            if KEY == pygame.K_s:
                self.rect.y += FPS // 12
            elif KEY == pygame.K_w:
                self.rect.y -= FPS // 12
            for sprite in GATES_GROUP:
                if PLAYER_GROUP.sprites()[0].rect.colliderect(sprite.rect):
                    if sprite in WIN_DOORS.sprites():
                        FIRST_COMPLETE = True
                        victory_screen(SCREEN, CLOCK)
                        for elem in ALL_SPRITES:
                            elem.kill()
                        KEY = None
                        return
                    elif sprite in RIGHT_DOORS.sprites():
                        FIRST_SCORE += 1
                    elif sprite in WRONG_DOORS.sprites():
                        FIRST_SCORE -= 1
            for sprite in TILES_GROUP:
                if pygame.sprite.collide_mask(self, sprite):
                    death_screen(SCREEN, CLOCK)
                    for elem in ALL_SPRITES:
                        elem.kill()
                    KEY = None
        else:
            if left:
                self.xvel = -FPS // 12
            if right:
                self.xvel = FPS // 12
            if not (left or right):
                self.xvel = 0
            if KEY == pygame.K_a:
                self.image = pygame.transform.flip(PLAYER_IMAGE[1], True, False)
                self.reverse = True
            elif KEY == pygame.K_d:
                self.image = PLAYER_IMAGE[1]
                self.reverse = False
            if up:
                if self.onGround:
                    self.yvel = -JUMP_POWER
            if not self.onGround:
                self.yvel += GRAVITY
            self.onGround = False
            self.rect.y += self.yvel
            self.collide(0, self.yvel, TILES_GROUP)
            self.rect.x += self.xvel
            self.collide(self.xvel, 0, TILES_GROUP)
            for sprite in DEADLY_TILES_GROUP:
                if pygame.sprite.collide_mask(self, sprite):
                    for elem in ALL_SPRITES:
                        elem.kill()
                    KEY = None
                    left = right = up = False
                    death_screen(SCREEN, CLOCK)
            for sprite in SHOOT_GROUP:
                if pygame.sprite.collide_mask(self, sprite):
                    for elem in ALL_SPRITES:
                        elem.kill()
                    KEY = None
                    left = right = up = False
                    death_screen(SCREEN, CLOCK)
# ----------------------------- Игрок --------------------------------------


# ----------------------------- Создание уровней --------------------------------------
def generate_level(level):
    global PLAYER, LEVEL
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                tile = Tile('vert_horn', x, y)
                if LEVEL == 'second':
                    DEADLY_TILES_GROUP.add(tile)
                    TILES_GROUP.remove(tile)
            elif level[y][x] == '?':
                tile = Tile('vert_horn', x, y, True)
                if LEVEL == 'second':
                    DEADLY_TILES_GROUP.add(tile)
                    TILES_GROUP.remove(tile)
            elif level[y][x] == '=':
                tile = Tile('hor_horn', x, y)
                if LEVEL == 'second':
                    DEADLY_TILES_GROUP.add(tile)
                    TILES_GROUP.remove(tile)
            elif level[y][x] == '-':
                tile = Tile('hor_horn', x, y, True)
                if LEVEL == 'second':
                    DEADLY_TILES_GROUP.add(tile)
                    TILES_GROUP.remove(tile)
            elif level[y][x] == '$':
                tile = Tile('gate', x, y, True)
                GATES_GROUP.add(tile)
                RIGHT_DOORS.add(tile)
                TILES_GROUP.remove(tile)
            elif level[y][x] == '%':
                tile = Tile('gate', x, y)
                GATES_GROUP.add(tile)
                WRONG_DOORS.add(tile)
                TILES_GROUP.remove(tile)
            elif level[y][x] == 'w':
                tile = Tile('win_gate', x, y)
                GATES_GROUP.add(tile)
                WIN_DOORS.add(tile)
                TILES_GROUP.remove(tile)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                PLAYER = Player(x, y)
            elif level[y][x] == '9':
                tile = Enemy(x, y, True)
                ENEMY_GROUP.add(tile)
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
        global LEVEL
        x, y = pos
        if self.rect.x <= x <= self.rect.x + 200 and self.rect.y <= y <= self.rect.y + 100:
            if self.image in Button.images:
                self.image = Button.c_images[Button.images.index(self.image)]
            if button == 1 and self.rect.y == 200:
                LEVEL = 'first'
                player, level_x, level_y = generate_level(load_level('_just_run_level.txt'))
                rules_of_first(SCREEN, CLOCK)
            elif button == 1 and self.rect.y == 320:
                LEVEL = 'second'
                player, level_x, level_y = generate_level(load_level('_platformer_level.txt'))
                rules_of_second(SCREEN, CLOCK)
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
    global LEVEL, CAMERA, SECOND_SCORE
    while True:
        fon = load_image('death.png')
        screen.blit(fon, (250, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                if LEVEL == 'second':
                    CAMERA = None
                    player, level_x, level_y = generate_level(load_level('_platformer_level.txt'))
                    CAMERA = Camera()
                    SECOND_SCORE -= 1
                    return
                else:
                    LEVEL = 'menu'
                    CAMERA = None
                    return
        pygame.display.flip()
        clock.tick(FPS)


def victory_screen(screen, clock):
    global LEVEL, CAMERA
    while True:
        fon = load_image('win.png')
        screen.blit(fon, (100, 75))

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
    global LEVEL, CAMERA, FIRST_SCORE
    while True:
        SCREEN.fill(pygame.Color('black'))
        fon = pygame.transform.scale(load_image('first_rules.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                FIRST_SCORE = 0
                CAMERA = Camera()
                LEVEL = 'first'
                return
        animation()
        pygame.display.flip()
        clock.tick(FPS)


def rules_of_second(screen, clock):
    global LEVEL, CAMERA, SECOND_SCORE
    while True:
        SCREEN.fill(pygame.Color('black'))
        fon = pygame.transform.scale(load_image('second_rules.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                SECOND_SCORE = 30
                CAMERA = Camera()
                return
        animation()
        pygame.display.flip()
        clock.tick(FPS)
# ----------------------------- Заставка, экран смерти и окна правил --------------------------------------


# ----------------------------- Вспомогательные вещи ------------------------------------------------------
def extras():
    global LOCK_GROUP, BTN_SPRITES

    label = pygame.sprite.Sprite()
    label.image = load_image('menu_label.png')
    label.rect = label.image.get_rect()
    label.rect.x, label.rect.y = 250, 50
    label.add(BTN_SPRITES)

    lock = pygame.sprite.Sprite()
    lock.image = load_image('lock.png', -1)
    lock.rect = lock.image.get_rect()
    lock.rect.x, lock.rect.y = 25, 465
    lock.add(LOCK_GROUP)


def scores(SCREEN):
    global FIRST_COMPLETE, FIRST_SCORE, LEVEL
    if FIRST_COMPLETE and LEVEL == 'menu':
        color = None
        if FIRST_SCORE > 25:
            color = (57, 255, 20)
        elif FIRST_SCORE < -25:
            color = (255, 7, 58)
        else:
            color = (255, 255, 255)
        font = pygame.font.SysFont('Orbitron', 30)
        text = font.render(f"Score: {FIRST_SCORE // 25}", True, color)
        SCREEN.blit(text, (400, 230))
    elif LEVEL == 'second':
        color = None
        if SECOND_SCORE > 15:
            color = (57, 255, 20)
        elif SECOND_SCORE < 0:
            color = (255, 7, 58)
        else:
            color = (255, 255, 255)
        font = pygame.font.SysFont('Orbitron', 30)
        text = font.render(f"{SECOND_SCORE}", True, color)
        SCREEN.blit(text, (700, 50))
# ----------------------------- Вспомогательные вещи ------------------------------------------------------


def main():
    global FPS, LEVEL, PLAYER, KEY, FIRST_SCORE, left, right, up
    pygame.init()
    pygame.display.set_caption('I wanna be a CODER (v.0.3.1)')

    start_screen(SCREEN, CLOCK)
    extras()
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

            elif LEVEL == 'first':
                if event.type == pygame.KEYDOWN:
                    KEY = event.key
                if event.type == pygame.KEYUP:
                    KEY = None

            elif LEVEL == 'second':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    KEY = event.key
                    left = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    KEY = event.key
                    right = True
                if event.type == pygame.KEYUP and event.key == pygame.K_d:
                    KEY = event.key
                    right = False
                if event.type == pygame.KEYUP and event.key == pygame.K_a:
                    KEY = event.key
                    left = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    up = True
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    up = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    PLAYER.shoot()

        if LEVEL == 'menu':
            animation()
            BTN_SPRITES.draw(SCREEN)
            scores(SCREEN)
            if not FIRST_COMPLETE or not SECOND_COMPLETE:
                LOCK_GROUP.draw(SCREEN)
        else:
            ALL_SPRITES.draw(SCREEN)
            PLAYER.update()
            if CAMERA:
                CAMERA.update(PLAYER)
                for sprite in ALL_SPRITES:
                    CAMERA.apply(sprite)
            if LEVEL == 'second':
                for bug in ENEMY_GROUP:
                    bug.update()
                for shoot in SHOOT_GROUP:
                    shoot.update()
                for shoot in PLAYER_SHOOT_GROUP:
                    shoot.update()
                scores(SCREEN)
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
