import os
import sys
import pygame
import random


def load_image(name, colorkey=None):
    fullname = os.path.join('game_data/sprites', name)
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
# не бейте сильно, пожалуйста! я обязательно разберусь, как без них
FPS = 70
WIDTH = 800
HEIGHT = 600
BTN_SPRITES, SAVE_BTN_SPRITES, CURSOR, BOSS, INTERFACE = pygame.sprite.Group(), pygame.sprite.Group(),\
                                                         pygame.sprite.Group(), pygame.sprite.Group(),\
                                                         pygame.sprite.Group()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
POINTS, SAVES = [], []
PLAYER, KEY, CAMERA, SKULL = None, None, None, None
LEVEL = 'menu'
CHANNEL, SOUND, BOOM_CHANNEL, BUG_CHANNEL, ATTACK_CHANNEL = None, None, None, None, None
ALL_SPRITES, EFFECTS = pygame.sprite.Group(), pygame.sprite.Group()
TILES_GROUP, DEADLY_TILES_GROUP = pygame.sprite.Group(), pygame.sprite.Group()
GATES_GROUP = But = pygame.sprite.Group()
RIGHT_DOORS, WRONG_DOORS, WIN_DOORS = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
PLAYER_GROUP, ENEMY_GROUP = pygame.sprite.Group(), pygame.sprite.Group()
LOCK_GROUP, BONUS_SPRITES, RETURN_SPRITE = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
PLAYER_SHOOT_GROUP, SHOOT_GROUP, ATTACK = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
FIRST_SCORE, SECOND_SCORE, ERROR_TEXT = None, None, False
HEALTH = DIFF = 0
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
    'player_shoot': load_image('player_shoot.png'),
    'skull': [load_image('skull_rev.png'), load_image('skull.png')]
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
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, count, extra=False, bolt=False, saw=False):
        super().__init__(BONUS_SPRITES, ALL_SPRITES)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        if bolt:
            rect = pygame.Rect((12, 0), (26, 120))
            self.rect = rect.move(pos_x, pos_y)
        elif saw:
            if DIFF == 'hard':
                self.image = pygame.transform.scale(self.image, (75, 75))
            self.rect = self.image.get_rect().move(pos_x, pos_y)
        else:
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        self.count = count
        self.bufer = count
        self.extra = extra
        self.bolt = bolt
        self.saw = saw
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.count -= 1
        if self.count == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.saw and DIFF == 'hard':
                self.image = pygame.transform.scale(self.image, (75, 75))
            if self.bolt:
                self.mask = pygame.mask.from_surface(self.image)
            self.count = self.bufer
        if self.extra and self.image == self.frames[-1]:
            self.kill()


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
    def __init__(self, pos_x, pos_y, tile_group, reverse=False, speed=3, boss=False):
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
        self.boss = boss

    def update(self):
        self.rect.x += self.speed
        if not self.boss:
            for sprite in TILES_GROUP:
                if pygame.sprite.collide_mask(self, sprite):
                    self.kill()
                    SOUND.play('boom')
                    if self.tile == 'player_shoot':
                        boom = AnimatedSprite(load_image('player_boom.png'), 7, 1, self.rect.x / 25,
                                          (self.rect.y - 9) / 25, 7, True)
                        BONUS_SPRITES.remove(boom)
                        EFFECTS.add(boom)
                    else:
                        boom = AnimatedSprite(load_image('enemy_boom.png'), 7, 1, self.rect.x / 25,
                                              (self.rect.y - 8) / 25, 7, True)
                        BONUS_SPRITES.remove(boom)
                        EFFECTS.add(boom)
        else:
            if 825 <= self.rect.x <= -25:
                self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(BOSS, ALL_SPRITES)
        self.saw_1, self.saw_2, self.start_pos_1, self.start_pos_2 = None, None, None, None
        self.image = TILE_IMAGES['skull'][1]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 125
        self.process = ''
        self.attacks = ['s', 't', 'b']
        self.count = 500
        self.sp = 0
        self.check = False

    def update(self):
        global DIFF, KEY
        self.count += 1
        SOUND.music_control()
        for bullet in PLAYER_SHOOT_GROUP:
            if pygame.sprite.collide_mask(self, bullet):
                self.hp -= 1
                boom = AnimatedSprite(load_image('player_boom.png'), 7, 1, (bullet.rect.x - 10) / 25,
                                      (bullet.rect.y - 9) / 25, 7, True)
                BONUS_SPRITES.remove(boom)
                EFFECTS.add(boom)
                bullet.kill()
        if self.hp < 60:
            self.image = TILE_IMAGES['skull'][0]
            DIFF = 'hard'
            if self.hp == 0:
                SOUND.music_control(True)
                ending_credits(SCREEN, CLOCK)
                for elem in ALL_SPRITES:
                    elem.kill()
                KEY = None
                return
        if self.count == 700:
            attack = random.choice(self.attacks)
            if random.choice([0, 1]) == 1:
                SOUND.play('pre_attack')
            if attack == 't':
                self.process = 't'
            elif attack == 's':
                self.saw_1 = AnimatedSprite(load_image('saw.png'), 4, 1, 25, 25, 7, False, False, True)
                x, y = (700 if DIFF == 'hard' else 725), (500 if DIFF == 'hard' else 525)
                self.saw_2 = AnimatedSprite(load_image('saw.png'), 4, 1, x, y, 7, False, False, True)
                BONUS_SPRITES.remove(self.saw_1)
                ATTACK.add(self.saw_1)
                BONUS_SPRITES.remove(self.saw_2)
                ATTACK.add(self.saw_2)
                self.check = False
                SOUND.play('saw_attack')
                self.process = 's'
            else:
                self.sp = 0
                self.process = 'b'
            self.count = 0
        if self.process == 't':
            if DIFF == 'hard':
                a = 90
            elif DIFF == 'normal':
                a = 120
            else:
                a = 150
            if self.count % a == 0:
                x = random.randint(25, 725)
                self.thunder_attack(x)
                SOUND.play('bolt_attack')
        elif self.process == 's':
            if DIFF == 'hard':
                a = 7
            elif DIFF == 'normal':
                a = 6
            else:
                a = 5
            self.saw_attack(a, self.saw_1, self.saw_2)
        elif self.process == 'b':
            self.sp += 1
            if DIFF == 'hard':
                a = 7
                sped = 35
            elif DIFF == 'normal':
                a = 5
                sped = 45
            else:
                a = 4
                sped = 50
            if self.sp % sped == 0:
                self.bullet_attack(a, self.sp, sped)

    def saw_attack(self, a, saw_1, saw_2):
        if not self.check:
            if saw_1.rect.bottom < 575 and saw_2.rect.top > 25:
                saw_1.rect.y += a
                saw_2.rect.y -= a
            else:
                if saw_1.rect.right < 775 and saw_2.rect.left > 25:
                    saw_1.rect.x += a
                    saw_2.rect.x -= a
                else:
                    self.check = True
        if self.check:
            if saw_2.rect.bottom < 575 and saw_1.rect.top > 25:
                saw_2.rect.y += a
                saw_1.rect.y -= a
            else:
                if saw_2.rect.right < 775 and saw_1.rect.left > 25:
                    saw_2.rect.x += a
                    saw_1.rect.x -= a
                else:
                    saw_2.kill()
                    saw_1.kill()

    def thunder_attack(self, x):
        bolt = AnimatedSprite(load_image('bolt.png'), 11, 1, x, 25, 5, True, True)
        BONUS_SPRITES.remove(bolt)
        ATTACK.add(bolt)

    def bullet_attack(self, a, coord, sped):
        shoot = Shoot(25, coord - ((coord // sped) * 10), 'enemy_shoot', True, a, True)
        SHOOT_GROUP.add(shoot)
        shoot = Shoot(775, coord - ((coord // sped) * 10) + 25, 'enemy_shoot', False, -1 * a, True)
        SHOOT_GROUP.add(shoot)
        SOUND.play('bug_shoot')


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
        self.hp = 5

    def update(self):
        self.count += 1
        if self.count == self.attack_speed * 10:
            shoot = Shoot((self.rect.x + 40 if self.reverse else self.rect.x),
                          (self.rect.y + 5), 'enemy_shoot',
                          self.reverse, (self.bullet_speed if self.reverse else -self.bullet_speed))
            SHOOT_GROUP.add(shoot)
            SOUND.play('bug_shoot')
            self.count = 0
        for bullet in PLAYER_SHOOT_GROUP:
            if pygame.sprite.collide_mask(self, bullet):
                self.hp -= 1
                boom = AnimatedSprite(load_image('player_boom.png'), 7, 1, (bullet.rect.x - 10) / 25,
                                      (bullet.rect.y - 9) / 25, 7, True)
                BONUS_SPRITES.remove(boom)
                EFFECTS.add(boom)
                bullet.kill()
        if self.hp == 0:
            SOUND.play('bug_death')
            self.kill()


# ----------------------------- Все объекты --------------------------------------


# ----------------------------- Игрок --------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        global LEVEL, SECOND_SCORE
        super().__init__(PLAYER_GROUP, ALL_SPRITES)
        if LEVEL == 'first':
            self.image = PLAYER_IMAGE[0]
        else:
            self.image = PLAYER_IMAGE[1]
        self.yvel = 0
        self.xvel = 0
        if 'boss' in LEVEL:
            if SECOND_SCORE > 15:
                self.hp = 3
            elif SECOND_SCORE < 0:
                self.hp = 1
            else:
                self.hp = 2
        else:
            self.hp = 1
        self.no_damage = 0
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
        if self.reverse:
            shoot = Shoot((self.rect.left - 23), (self.rect.top + 8), 'player_shoot', False, -7)
        else:
            shoot = Shoot(self.rect.right, (self.rect.top + 8), 'player_shoot', True, 7)
        PLAYER_SHOOT_GROUP.add(shoot)
        SHOOT_GROUP.remove(shoot)
        SOUND.play('shoot')

    def update(self, e=False):
        global KEY, FIRST_SCORE, FIRST_COMPLETE, LEVEL, JUMP_POWER, GRAVITY, left, \
            right, up, SECOND_SCORE, SECOND_COMPLETE, But, CAMERA
        if LEVEL == 'first':
            self.rect.x += FPS // 20
            if KEY == pygame.K_s:
                self.rect.y += FPS // 12
            elif KEY == pygame.K_w:
                self.rect.y -= FPS // 12
            for sprite in GATES_GROUP:
                if self.rect.left == sprite.rect.left:
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
                    pygame.mixer.music.stop()
                    SOUND.play('death')
                    death_screen(SCREEN, CLOCK)
                    for elem in ALL_SPRITES:
                        elem.kill()
                    KEY = None
        else:
            if self.no_damage > 0:
                self.no_damage -= 1
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
            if 'boss' in LEVEL:
                interface(self.hp)
            for sprite in DEADLY_TILES_GROUP:
                if pygame.sprite.collide_mask(self, sprite):
                    if self.no_damage == 0:
                        if 'boss' in LEVEL:
                            SOUND.play('damage')
                        self.hp -= 1
                        self.no_damage += 105
            for sprite in ATTACK:
                if pygame.sprite.collide_mask(self, sprite):
                    if self.no_damage == 0:
                        SOUND.play('damage')
                        self.hp -= 1
                        self.no_damage += 105
            for sprite in SHOOT_GROUP:
                if pygame.sprite.collide_mask(self, sprite):
                    if self.no_damage == 0:
                        if 'boss' in LEVEL:
                            SOUND.play('damage')
                        self.hp -= 1
                        self.no_damage += 105
            if self.hp == 0:
                for elem in ALL_SPRITES:
                    elem.kill()
                KEY = None
                left = right = up = False
                pygame.mixer.music.pause()
                SOUND.play('death')
                death_screen(SCREEN, CLOCK)
            for sprite in BONUS_SPRITES:
                if pygame.sprite.collide_mask(self, sprite):
                    SECOND_SCORE += 5
                    SOUND.play('coin')
                    sprite.kill()
            for sprite in But:
                if pygame.sprite.collide_mask(self, sprite) and e:
                    SOUND.now = 'boss'
                    for elem in ALL_SPRITES:
                        elem.kill()
                    CAMERA = None
                    SOUND.play('boss_awoken')
                    generate_level(load_level('_boss_arena.txt'))
            for sprite in WIN_DOORS:
                if pygame.sprite.collide_mask(self, sprite):
                    SECOND_COMPLETE = True
                    victory_screen(SCREEN, CLOCK)
                    for elem in ALL_SPRITES:
                        elem.kill()
                    KEY = None
                    return


# ----------------------------- Игрок --------------------------------------


# ----------------------------- Создание уровней --------------------------------------
def generate_level(level):
    global PLAYER, LEVEL, SKULL
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                tile = Tile('vert_horn', x, y)
                if (LEVEL == 'second') or ('boss' in LEVEL):
                    DEADLY_TILES_GROUP.add(tile)
                    TILES_GROUP.remove(tile)
            elif level[y][x] == '?':
                tile = Tile('vert_horn', x, y, True)
                if (LEVEL == 'second') or ('boss' in LEVEL):
                    DEADLY_TILES_GROUP.add(tile)
                    TILES_GROUP.remove(tile)
            elif level[y][x] == '=':
                tile = Tile('hor_horn', x, y)
                if (LEVEL == 'second') or ('boss' in LEVEL):
                    DEADLY_TILES_GROUP.add(tile)
                    TILES_GROUP.remove(tile)
            elif level[y][x] == '-':
                tile = Tile('hor_horn', x, y, True)
                if (LEVEL == 'second') or ('boss' in LEVEL):
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
            elif level[y][x] == '*':
                AnimatedSprite(load_image('coin.png'), 6, 1, x, y, 10)
            elif level[y][x] == '&':
                but = AnimatedSprite(load_image('boss_lever.png'), 2, 1, x, y, 20)
                BONUS_SPRITES.remove(but)
                But.add(but)
            elif level[y][x] == 's':
                saw = AnimatedSprite(load_image('saw.png'), 4, 1, x, y, 7)
                BONUS_SPRITES.remove(saw)
                DEADLY_TILES_GROUP.add(saw)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                PLAYER = Player(x, y)
            elif level[y][x] == '9':
                tile = Enemy(x, y, True)
                ENEMY_GROUP.add(tile)
            elif level[y][x] == '8':
                tile = Enemy(x, y)
                ENEMY_GROUP.add(tile)
            elif level[y][x] == 'B':
                SKULL = Boss(x, y)
                DEADLY_TILES_GROUP.add(SKULL)
                TILES_GROUP.remove(SKULL)
    return PLAYER, x, y


# ----------------------------- Создание уровней --------------------------------------


# ----------------------------- Кнопки главного меню --------------------------------------
class Button(pygame.sprite.Sprite):
    images = [load_image('first_btn.png'),
              load_image('second_btn.png'),
              load_image('boss_btn.png'),
              load_image('save_menu_btn.png'),
              load_image('save_btn.png'),
              load_image('load_btn.png')]
    c_images = [load_image('first_btn_clicked.png'),
                load_image('second_btn_clicked.png'),
                load_image('boss_btn_clicked.png'),
                load_image('save_menu_btn_clicked.png'),
                load_image('save_btn_clicked.png'),
                load_image('load_btn_clicked.png')]

    def __init__(self, n):
        super().__init__(BTN_SPRITES)
        self.image = Button.images[n]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        if n < 3:
            self.rect.topleft = (100, 200 + 120 * n)
        elif n == 3:
            self.rect.topleft = (700, 475)
        else:
            self.rect.topleft = (575, 125 + 100 * (n - 4))

    def update(self, pos, button=3, cur=None):
        global LEVEL, FIRST_SCORE, FIRST_COMPLETE, SECOND_SCORE, SECOND_COMPLETE, SCREEN, ERROR_TEXT
        x, y = pos
        if self.rect.x <= x <= self.rect.x + self.rect.w and self.rect.y <= y <= self.rect.y + self.rect.h:
            if self.image in Button.images:
                self.image = Button.c_images[Button.images.index(self.image)]
            if button == 1 and self.rect.topleft == (100, 200):
                SOUND.play('click')
                LEVEL = 'first'
                generate_level(load_level('_just_run_level.txt'))
                rules_of_first(SCREEN, CLOCK)
            elif button == 1 and self.rect.topleft == (100, 320):
                SOUND.play('click')
                LEVEL = 'second'
                generate_level(load_level('_platformer_level.txt'))
                rules_of_second(SCREEN, CLOCK)
            elif button == 1 and self.rect.topleft == (100, 440) and (FIRST_COMPLETE and SECOND_COMPLETE):
                SOUND.play('click')
                LEVEL = 'boss_but'
                generate_level(load_level('_boss_button.txt'))
                rules_of_boss(SCREEN, CLOCK)
            elif button == 1 and self.rect.topleft == (700, 475):
                SOUND.play('click')
                LEVEL = 'save'
            elif button == 1 and self.rect.topleft == (575, 125):
                SOUND.play('click')
                if cur:
                    try:
                        ERROR_TEXT = False
                        if FIRST_COMPLETE:
                            SAVES[cur - 1][0] = FIRST_SCORE
                        else:
                            SAVES[cur - 1][0] = '???'
                        if SECOND_COMPLETE:
                            SAVES[cur - 1][1] = f'{SECOND_SCORE} \n'
                        else:
                            SAVES[cur - 1][1] = f'??? \n'
                        result = [';'.join([str(x) for x in line]) for line in SAVES]
                        table = open('game_data/saves.txt', 'w', encoding="utf8")
                        for line in result:
                            table.write(line)
                        table.close()
                        LEVEL = 'menu'
                    except ValueError:
                        ERROR_TEXT = 'ERROR: smth broke'
            elif button == 1 and self.rect.topleft == (575, 225):
                SOUND.play('click')
                if cur:
                    try:
                        ERROR_TEXT = False
                        FIRST_SCORE = int(SAVES[cur - 1][0])
                        if FIRST_SCORE is not None:
                            FIRST_COMPLETE = True
                        SECOND_SCORE = int(SAVES[cur - 1][1])
                        if SECOND_SCORE is not None:
                            SECOND_COMPLETE = True
                        LEVEL = 'menu'
                    except ValueError:
                        ERROR_TEXT = 'ERROR: broken save'
        else:
            if self.image in Button.c_images:
                self.image = Button.images[Button.c_images.index(self.image)]


# ----------------------------- Кнопки главного меню --------------------------------------


class ReturnBtn(pygame.sprite.Sprite):
    def __init__(self):
        global PLAYER
        super().__init__(RETURN_SPRITE)
        self.image = load_image('return_btn.png')
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.topleft = 5, 5

    def update(self, pos, button=3):
        global LEVEL, KEY, ERROR_TEXT
        x, y = pos
        if self.rect.x <= x <= self.rect.x + 50 and self.rect.y <= y <= self.rect.y + 50:
            self.image = load_image('return_btn_clicked.png')
            if button == 1:
                SOUND.play('click')
                LEVEL = 'menu'
                ERROR_TEXT = False
                for elem in ALL_SPRITES:
                    elem.kill()
                KEY = None
        else:
            self.image = load_image('return_btn.png')


# ----------------------------- Анимация внизу окна ---------------------------------------


class Point:
    points = []

    def __init__(self):
        self.h = 600
        self.w = random.randint(0, 800)
        self.color = (4, 242, 255)

    def update(self):
        Point.points.clear()
        if self.h > 500:
            self.h -= 2
        else:
            POINTS.remove(self)
            Point.points.append(self)


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
                    generate_level(load_level('_platformer_level.txt'))
                    CAMERA = Camera()
                    SECOND_SCORE -= 1
                    pygame.mixer.music.unpause()
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


def ending_credits(screen, clock):
    global LEVEL, CAMERA, SECOND_COMPLETE, FIRST_COMPLETE
    fon = load_image('end.png')
    y = 300
    check = False
    while True:
        screen.fill((0, 0, 0))
        screen.blit(fon, (0, y))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    LEVEL = 'menu'
                    SECOND_COMPLETE, FIRST_COMPLETE = False, False
                    CAMERA = None
                    return
        if y > (-1 * 2400) and not check:
            y -= 0.5
        else:
            fon = load_image('end_end.png')
            check = True
            y = 0
        animation()
        pygame.display.flip()
        clock.tick(FPS)


def rules_of_first(screen, clock):
    global LEVEL, CAMERA, FIRST_SCORE, FIRST_COMPLETE
    while True:
        SCREEN.fill(pygame.Color('black'))
        fon = pygame.transform.scale(load_image('first_rules.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                FIRST_COMPLETE = False
                FIRST_SCORE = 0
                CAMERA = Camera()
                LEVEL = 'first'
                return
        animation()
        pygame.display.flip()
        clock.tick(FPS)


def rules_of_second(screen, clock):
    global LEVEL, CAMERA, SECOND_SCORE, SECOND_COMPLETE
    while True:
        SCREEN.fill(pygame.Color('black'))
        fon = pygame.transform.scale(load_image('second_rules.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                SECOND_COMPLETE = False
                SECOND_SCORE = 30
                CAMERA = Camera()
                return
        animation()
        pygame.display.flip()
        clock.tick(FPS)


def rules_of_boss(screen, clock):
    global LEVEL, CAMERA, SECOND_SCORE, FIRST_SCORE, HEALTH, DIFF
    while True:
        SCREEN.fill(pygame.Color('black'))
        fon = pygame.transform.scale(load_image('boss_rules.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                if FIRST_SCORE > 1:
                    DIFF = 'easy'
                elif FIRST_SCORE < -1:
                    DIFF = 'hard'
                else:
                    DIFF = 'normal'
                if SECOND_SCORE > 15:
                    HEALTH = 3
                elif SECOND_SCORE < 0:
                    HEALTH = 1
                else:
                    HEALTH = 2
                CAMERA = Camera()
                return
        animation()
        pygame.display.flip()
        clock.tick(FPS)


# ----------------------------- Заставка, экран смерти и окна правил --------------------------------------


# ----------------------------- Вспомогательные вещи ------------------------------------------------------
class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(CURSOR)
        self.image = load_image('cursor.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 60, 135
        self.pos = 0

    def update(self, n):
        if -1 < self.pos + n < 12:
            self.pos += n
        self.rect.y = (125 + self.pos * 25) + 10 + self.pos * 5


def save_list_visual(screen):
    global SAVES
    pygame.draw.rect(screen, (4, 242, 255), [(50, 125), (425, 375)], 5)
    font = pygame.font.Font('font/orbitron-bold.otf', 12)
    for n, line in enumerate(SAVES):
        text = font.render(f"Result 1st: {line[0]}, Result 2nd: {line[1]}", True, pygame.Color('cyan'))
        screen.blit(text, (170, (125 + n * 25) + 17 + n * 5))
        pygame.draw.rect(screen, pygame.Color('cyan'), [(85, (125 + n * 25) + 10 + n * 5), (380, 25)], 1)


def save_list_init():
    global SAVES
    table = open('game_data/saves.txt', encoding="utf8")
    reader = [line.split(';') for line in table]
    for line in reader:
        t = [line[0], line[1]]
        SAVES.append(t)
    table.close()


# ----------------------------- Штуки для сейвов ------------------------------------------------------


# ----------------------------- Музлишко ------------------------------------------------------
class Sound_Control:
    def __init__(self, channels):
        self.check = False
        self.dict = {'coin': pygame.mixer.Sound('game_data/sound/coin.wav'),
                     'click': pygame.mixer.Sound('game_data/sound/click.wav'),
                     'death': pygame.mixer.Sound('game_data/sound/death.wav'),
                     'boom': pygame.mixer.Sound('game_data/sound/zap.wav'),
                     'bug_death': pygame.mixer.Sound('game_data/sound/bug_death.wav'),
                     'shoot': pygame.mixer.Sound('game_data/sound/hero_shot.wav'),
                     'bug_shoot': pygame.mixer.Sound('game_data/sound/bug_shot.wav'),
                     'boss_awoken': pygame.mixer.Sound('game_data/sound/awakening.wav'),
                     'pre_attack': pygame.mixer.Sound('game_data/sound/pre_attack.wav'),
                     'saw_attack': pygame.mixer.Sound('game_data/sound/saw.wav'),
                     'bolt_attack': pygame.mixer.Sound('game_data/sound/thunder.wav'),
                     'damage': pygame.mixer.Sound('game_data/sound/damage.wav')
                     }
        self.channels = channels
        self.prev = 'menu'
        self.now = 'menu'
        self.dict['bug_shoot'].set_volume(0.4)
        self.dict['click'].set_volume(0.3)
        self.dict['shoot'].set_volume(0.6)
        self.dict['boom'].set_volume(0.3)
        self.dict['boss_awoken'].set_volume(0.6)
        self.dict['saw_attack'].set_volume(1.2)
        self.dict['damage'].set_volume(2)

    def music_control(self, final=False):
        global LEVEL
        pygame.mixer.init()
        if LEVEL == 'menu' and pygame.mixer.music.get_busy() and self.check:
            pygame.mixer.music.fadeout(210)
            self.prev = 'menu'
            self.check = False
        elif (LEVEL == 'first' or LEVEL == 'second') and pygame.mixer.music.get_busy() and (not self.check):
            pygame.mixer.music.fadeout(210)
            self.prev = 'levels'
            self.check = True
        elif 'boss' in LEVEL and pygame.mixer.music.get_busy() and (not self.check):
            pygame.mixer.music.fadeout(210)
            self.prev = 'boss'
            self.check = True
        elif LEVEL == 'menu' and (not pygame.mixer.music.get_busy()):
            self.now = 'menu'
            pygame.mixer.music.load('game_data/music/main_menu.mp3')
            pygame.mixer.music.set_volume(0.65)
            pygame.mixer.music.play()
        elif (LEVEL == 'first' or LEVEL == 'second') and (not pygame.mixer.music.get_busy()):
            self.now = 'levels'
            pygame.mixer.music.load('game_data/music/level.mp3')
            pygame.mixer.music.set_volume(0.65)
            pygame.mixer.music.play(10)
        elif 'boss' in LEVEL and (not pygame.mixer.music.get_busy()):
            self.now = 'boss'
            pygame.mixer.music.load('game_data/music/boss.mp3')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play()
        elif final:
            self.prev = 'final'
            self.now = 'final'
            pygame.mixer.music.fadeout(210)
            pygame.mixer.music.load('game_data/music/final.mp3')
            pygame.mixer.music.play()
        if self.prev != self.now:
            for chan in self.channels:
                chan.fadeout(140)

    def play(self, sound):
        global CHANNEL, BOOM_CHANNEL, BUG_CHANNEL, ATTACK_CHANNEL
        pygame.mixer.init()
        if sound == 'boom':
            BOOM_CHANNEL.play(self.dict[sound])
        elif sound == 'bug_shoot' or sound == 'boss_awoken' or sound == 'damage':
            BUG_CHANNEL.play(self.dict[sound])
        elif sound in ['saw_attack', 'bolt_attack']:
            ATTACK_CHANNEL.play(self.dict[sound])
        else:
            CHANNEL.play(self.dict[sound])


# ----------------------------- Музлишко ------------------------------------------------------


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


def scores(screen):
    global FIRST_COMPLETE, FIRST_SCORE, SECOND_COMPLETE, SECOND_SCORE, LEVEL
    if LEVEL == 'menu':
        if FIRST_COMPLETE:
            if FIRST_SCORE > 1:
                color = (57, 255, 20)
                text = 'GOOD'
            elif FIRST_SCORE < -1:
                text = 'BAD'
                color = (255, 7, 58)
            else:
                text = 'NOT BAD'
                color = (255, 255, 255)
            font = pygame.font.Font('font/orbitron-bold.otf', 30)
            text = font.render(f"Result: {text}", True, color)
            screen.blit(text, (350, 230))
        if SECOND_COMPLETE:
            if SECOND_SCORE > 15:
                text = 'GOOD'
                color = (57, 255, 20)
            elif SECOND_SCORE < 0:
                text = 'BAD'
                color = (255, 7, 58)
            else:
                text = 'NOT BAD'
                color = (255, 255, 255)
            font = pygame.font.Font('font/orbitron-bold.otf', 30)
            text = font.render(f"Result: {text}", True, color)
            screen.blit(text, (350, 350))
    elif LEVEL == 'second':
        if SECOND_SCORE > 15:
            color = (57, 255, 20)
        elif SECOND_SCORE < 0:
            color = (255, 7, 58)
        else:
            color = (255, 255, 255)
        font = pygame.font.Font('font/orbitron-bold.otf', 30)
        text = font.render(f"{SECOND_SCORE}", True, color)
        screen.blit(text, (700, 50))


def interface(health):
    for h in INTERFACE:
        h.kill()
    for i in range(health):
        hp = pygame.sprite.Sprite()
        hp.image = load_image('heart.png')
        hp.rect = hp.image.get_rect()
        hp.rect.x, hp.rect.y = 5 + (55 * i), 70
        hp.add(INTERFACE)
# ----------------------------- Вспомогательные вещи ------------------------------------------------------


def main():
    global FPS, LEVEL, PLAYER, KEY, FIRST_SCORE, left, right, up, \
        CHANNEL, SOUND, BOOM_CHANNEL, BUG_CHANNEL, ATTACK_CHANNEL
    pygame.init()
    pygame.display.set_caption('I wanna be a CODER')

    pygame.mixer.set_num_channels(4)
    CHANNEL = pygame.mixer.Channel(0)
    BOOM_CHANNEL = pygame.mixer.Channel(1)
    BUG_CHANNEL = pygame.mixer.Channel(2)
    ATTACK_CHANNEL = pygame.mixer.Channel(3)
    channels = [CHANNEL, BOOM_CHANNEL, BUG_CHANNEL, ATTACK_CHANNEL]

    SOUND = Sound_Control(channels)
    SOUND.music_control()

    start_screen(SCREEN, CLOCK)
    extras()
    cur = Cursor()
    save_list_init()
    btns = []
    save_btns = []
    btn = ReturnBtn()
    for n in range(4):
        btns.append(Button(n))
    for n in range(4, 6):
        b = Button(n)
        BTN_SPRITES.remove(b)
        SAVE_BTN_SPRITES.add(b)
        save_btns.append(b)
    running = True
    while running:
        SCREEN.fill(pygame.Color('black'))
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.quit()

            if LEVEL == 'menu':
                if event.type == pygame.MOUSEMOTION:
                    for b in btns:
                        b.update(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for b in btns:
                        b.update(event.pos, event.button)

            elif LEVEL == 'save':
                if event.type == pygame.MOUSEMOTION:
                    btn.update(event.pos)
                    for b in save_btns:
                        b.update(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    btn.update(event.pos, event.button)
                    for b in save_btns:
                        b.update(event.pos, event.button, (cur.pos + 1))
                if event.type == pygame.MOUSEWHEEL:
                    cur.update(event.y)

            elif LEVEL == 'first':
                if event.type == pygame.KEYDOWN:
                    KEY = event.key
                if event.type == pygame.KEYUP:
                    KEY = None
                if event.type == pygame.MOUSEMOTION:
                    btn.update(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    btn.update(event.pos, event.button)

            elif (LEVEL == 'second') or ('boss' in LEVEL):
                if LEVEL == 'boss_but':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        PLAYER.update(True)
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
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    PLAYER.shoot()
                    btn.update(event.pos, event.button)
                if event.type == pygame.MOUSEMOTION:
                    btn.update(event.pos)

        if LEVEL == 'menu':
            SOUND.music_control()
            animation()
            BTN_SPRITES.draw(SCREEN)
            scores(SCREEN)
            if not FIRST_COMPLETE or not SECOND_COMPLETE:
                LOCK_GROUP.draw(SCREEN)
        elif LEVEL == 'save':
            animation()
            RETURN_SPRITE.draw(SCREEN)
            SAVE_BTN_SPRITES.draw(SCREEN)
            save_list_visual(SCREEN)
            CURSOR.draw(SCREEN)
            if ERROR_TEXT:
                font = pygame.font.Font('font/orbitron-bold.otf', 20)
                text = font.render(f"{ERROR_TEXT}", True, pygame.Color('red'))
                SCREEN.blit(text, (500, 470))
        else:
            if 'boss' not in LEVEL:
                SOUND.music_control()
            ALL_SPRITES.draw(SCREEN)
            RETURN_SPRITE.draw(SCREEN)
            INTERFACE.draw(SCREEN)
            if LEVEL == 'second' or ('boss' in LEVEL):
                if 'boss' in LEVEL:
                    for a in ATTACK:
                        a.update()
                    for b in But:
                        b.update()
                    for b in BOSS:
                        b.update()
                for m in BONUS_SPRITES:
                    m.update()
                for e in EFFECTS:
                    e.update()
                for s in DEADLY_TILES_GROUP:
                    s.update()
                for bug in ENEMY_GROUP:
                    bug.update()
                for shoot in SHOOT_GROUP:
                    shoot.update()
                for shoot in PLAYER_SHOOT_GROUP:
                    shoot.update()
                scores(SCREEN)
            PLAYER.update()
            if CAMERA:
                CAMERA.update(PLAYER)
                for sprite in ALL_SPRITES:
                    CAMERA.apply(sprite)
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
