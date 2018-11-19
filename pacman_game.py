'''
 Diego Piccinotti (Matricola: 264763)
 Francesco Saccani (Matricola: 265559)
'''

import pygame
from arena import *
from pacman import *
from pygame.locals import (KEYDOWN, K_RIGHT, K_d, K_LEFT, K_a, K_UP, K_w, K_DOWN, K_s, K_ESCAPE)

## Costanti
FRAME_RATE = 30
SCREEN_W, SCREEN_H = 232, 272

## Inizializzazione dell'arena e dei personaggi
arena = PacmanArena(SCREEN_W, SCREEN_H)
## Inizializzazione del personaggio Pac-Man
pacman = PacMan(arena, 108, 184)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(arena.size())
background = pygame.image.load('pacman_background.png')
sprites = pygame.image.load('pacman_sprites.png')

playing = True
pacman.direction(-2, 0)
while playing:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    ## Ciclo degli eventi esterni
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            playing = False
            esc = True
        elif e.type == pygame.KEYDOWN:
            if e.key in (K_RIGHT, K_d): pacman.direction(2, 0)
            elif e.key in (K_LEFT, K_a): pacman.direction(-2, 0)
            elif e.key in (K_UP, K_w): pacman.direction(0, -2)
            elif e.key in (K_DOWN, K_s): pacman.direction(0, 2)
            if e.key == pygame.K_ESCAPE:
                playing = False
                esc = True
    arena.move_all()
    ## Stampa a video dei personaggi
    for a in arena.actors():
        if not isinstance(a, Wall) and not isinstance(a, Gate):
            x, y, w, h = a.rect()
            xs, ys = a.symbol()
            screen.blit(sprites, (x, y), area = (xs, ys, w, h))
    ## Stampa a video del punteggio
    font = pygame.font.SysFont('Courier', 14)
    msg = font.render(str(pacman.scores), True, (255, 255, 255))
    screen.blit(msg, (6, 254))
    ## Punti dei fantasmi mangiati
    for s in reversed(pacman.scores_sprite):
        screen.blit(sprites, s[0], area = (s[1]*16, 128, 16, 16))
        if s[2] == FRAME_RATE*3: pacman.scores_sprite.remove(s)
        else: s[2] += 1
    ## Punti dei bonus mangiati
    for b in reversed(pacman.bonus_sprite):
        screen.blit(sprites, b[0], area = (b[1]*16, 144, 16, 16))
        if b[2] == FRAME_RATE*3: pacman.bonus_sprite.remove(b)
        else: b[2] += 1
    ## Stampa a video delle vite disponibili
    for l in range(arena.getLifes()):
        screen.blit(sprites, (210 - l*16, 254), area = (128, 16, 16, 16))
    ## Stampa a video della scritta READY
    if pacman.getStatus() == -1 and arena.playing() == 0:
        msg = font.render("READY!", True, (255, 255, 0))
        screen.blit(msg, (92, 136))
    ## Controlli di conclusione del gioco
    if arena.playing() != 0:
        if arena.playing() == 1:
            msg = font.render("YOU WIN", True, (255, 255, 0))
            screen.blit(msg, (88, 136))
        elif arena.playing() == 2:
            msg = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(msg, (80, 136))
        arena.sound(3).stop()
        playing = False
        esc = False
    pygame.display.flip()
    clock.tick(FRAME_RATE)
if esc: pygame.quit()
