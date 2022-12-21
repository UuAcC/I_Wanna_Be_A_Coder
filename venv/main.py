import os
import sys
import pygame


FPS = 60
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
        self.rect.topleft = (100, 150 + 120 * n)
        self.rect.bottomright = (300, 200 + 120 * n)

    def update(self, pos):
        if self.rect.topleft <= pos <= self.rect.bottomright:
            if self.image in Button.images:
                self.image = Button.c_images[Button.images.index(self.image)]
        else:
            if self.image in Button.c_images:
                self.image = Button.images[Button.c_images.index(self.image)]


def main():
    global FPS
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    running = True
    clock = pygame.time.Clock()
    btns = []
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

        BTN_SPRITES.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
