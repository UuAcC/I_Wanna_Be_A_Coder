import os
import sys
import pygame
import random


FPS = 60
WIDTH = 800
HEIGHT = 600
BTN_SPRITES = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('game_data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


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
            if button == 1:
                pass
            if self.image in Button.images:
                self.image = Button.c_images[Button.images.index(self.image)]
        else:
            if self.image in Button.c_images:
                self.image = Button.images[Button.c_images.index(self.image)]


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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen, clock):

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                rules_of_first(screen, clock)
                return
        pygame.display.flip()
        clock.tick(FPS)


def rules_of_first(screen, clock):

    fon = pygame.transform.scale(load_image('first_rules.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)



def main():
    global FPS
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    start_screen(screen, clock)

    running = True
    btns = []
    points = []
    for n in range(3):
        btns.append(Button(n))
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION:
                for b in btns:
                    b.update(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in btns:
                    b.update(event.pos, event.button)

        points.append(Point())
        for p in points:
            animate(screen, p)
            p.update()
        BTN_SPRITES.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
