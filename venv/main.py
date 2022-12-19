import pygame


fps = 60


def main():
    global fps
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    running = True
    clock = pygame.time.Clock()
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(fps)


if __name__ == "__main__":
    main()
