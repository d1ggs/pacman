from arena import *
from pacman_map import *
import random
import pygame
pygame.init() # Si utilizza pygame per la riproduzione dei suoni

## Costanti
FRAME_RATE = 30

class PacmanArena(Arena):

    def __init__(self, width: int, height: int):
        self._w, self._h = width, height
        self._lifes = 2 # Vite; si perde a -1
        self._actors = []
        ## Inizializzazione dei personaggi del gioco
        for x, y, w, h in walls_pos: Wall(self, x, y, w, h)
        for x, y in cookies_pos: Cookie(self, x, y)
        for x, y in powers_pos: Power(self, x, y)
        Ghost(self, 108, 88, 0)
        Ghost(self, 108, 112, 1)
        Ghost(self, 124, 112, 2)
        Ghost(self, 92, 112, 3)
        Bonus(self)
        Gate(self)
        ## Suoni
        self._sounds = [pygame.mixer.Sound('sound/OpeningSong.wav'),
                        pygame.mixer.Sound('sound/Dies.wav'),
                        pygame.mixer.Sound('sound/WakaWaka.wav'),
                        pygame.mixer.Sound('sound/Siren.wav'),
                        pygame.mixer.Sound('sound/EatingCherry.wav'),
                        pygame.mixer.Sound('sound/EatingGhost.wav'),
                        pygame.mixer.Sound('sound/ExtraLive.wav')]
        self.sound(0).play()

    def playing(self) -> bool:
        result = 1
        ## condizione di vittoria
        for a in self._actors:
            if isinstance(a, Cookie) or isinstance(a, Power):
                result = 0
        ## condizione di sconfitta
        if self._lifes == -1: result = 2
        return result # 0 -> continua a giocare, 1 -> hai vinto, 2 -> hai perso

    def sound(self, i:int):
        return self._sounds[i]

    def rect_in_wall(self, actor: Actor, rect: (int, int, int, int)) -> bool:
        for other in self._actors:
            if isinstance(other, Wall) or (isinstance(other, Gate) and not actor.getGate()):
                x1, y1, w1, h1 = rect
                x2, y2, w2, h2 = other.rect()
                if (y2 < y1 + h1 and y1 < y2 + h2 and x2 < x1 + w1 and x1 < x2 + w2):
                    return True
        return False

    def going_to_wall(self, actor: Actor, dx: int, dy: int) -> bool:
        x, y, w, h = actor.rect()
        return self.rect_in_wall(actor, (x + dx, y + dy, w, h))


class Wall(Actor):

    def __init__(self, arena, x:int, y:int, w:int, h:int):
        self._x, self._y = x, y
        self._w, self._h = w, h
        arena.add(self)

    def rect(self) -> tuple:
        return self._x, self._y, self._w, self._h

class Bonus(Actor):

    def __init__(self, arena):
        self._arena = arena
        self._symbol = -1
        self._w = 16
        self._h = 16
        self._status = 1
        self._counter = 0
        self.set_pos()
        self._arena.add(self)
        
    def set_pos(self):
    ## Genera la posizione del bonus
        self._x = random.randint(1,14)*8
        self._y = random.randint(1,14)*8
        while self._arena.rect_in_wall(self, self.rect()) or (92 <= self._x <= 139 and 108 <= self._y <= 131):
            self._x = random.randint(1,14)*16
            self._y = random.randint(1,14)*16

    def status(self,status):
    ## STATI
    ## 0 -> visibile
    ## 1 -> mangiato da PacMan
    ## 2 -> tutti i bonus già mangiati, non visibile
        if status == 1: self._symbol = -1
        elif status == 0:
            if self._symbol < 7: self._symbol += 1
            elif self._symbol == 7: status = 2
        self._counter = 0
        self.set_pos()
        self._status = status

    def symbol(self) -> tuple:
        if self._status == 1:
            self._counter += 1 
            if self._counter == FRAME_RATE*10: self.status(0)
            return (48, 192)
        elif self._status == 0: return (32 + (16 * self._symbol), 48)
        else: return (48, 192)

    def getNumber(self) -> int:
        return self._symbol
    
    def getGate(self)-> bool:
        return False

    def getStatus(self) -> int:
        return self._status
        
    def rect(self) -> tuple:
        return self._x, self._y, self._w, self._h
    

class Gate(Actor):

    def __init__(self, arena):
        self._x, self._y = 108, 104
        self._w, self._h = 16, 8
        arena.add(self)

    def rect(self) -> tuple:
        return self._x, self._y, self._w, self._h


class Cookie(Actor):
    W, H = 4, 4

    def __init__(self, arena, x:int, y:int):
        self._x, self._y = x, y
        self._arena = arena
        self._arena.add(self)

    def symbol(self):
        return 166, 54
    
    def collide(self, other):
        if isinstance(other, PacMan):
            x, y, w, h = other.rect()
            if (self._y == y + 6 and y == self._y - 6 and self._x == x + 6 and x == self._x - 6):
                other.scores += 10
                self._arena.sound(2).stop()
                self._arena.sound(2).play()
                self._arena.remove(self)


class Power(Actor):
    W, H = 8, 8

    def __init__(self, arena, x:int, y:int):
        self._x, self._y = x, y
        self._arena = arena
        self._arena.add(self)
        self._counter = 0

    def symbol(self):
        if self._counter < 5:
            self._counter += 1
            return 180, 52
        elif 5 <= self._counter <= 9:
            self._counter += 1
            if self._counter == 10: self._counter = 0
            return 180, 16
    
    def collide(self, other):
        if isinstance(other, PacMan):
            x, y, w, h = other.rect()
            if (self._y == y + 4 and y == self._y - 4 and self._x == x + 4 and x == self._x - 4):
                other.scores += 50
                self._arena.sound(6).play()
                self._arena.remove(self)
                for a in self._arena.actors():
                    if isinstance(a, Ghost) and a.getStatus() != 4 and a.getStatus() != 5:
                        a.status(2)          

class Ghost(Actor):
    W, H = 16, 16

    def __init__(self, arena, x:int, y:int, color:int):
        self._start_x, self._start_y = x, y
        self._color = color
        self._speed = 0
        self._dir = [0, 0]
        self._status = 0
        self.status(-1)
        self._arena = arena
        self._arena.add(self)
        self._behav = random.randint(0, 1)
        self._behav_count = random.randint(0, 50)
        self._gate = False # Quando True il fantasma può attraversare il cancello del recinto iniziale

    def getStatus(self) -> int:
        return self._status

    def getGate(self) -> bool:
        return self._gate

    def status(self, status: int):
        ## STATI:
        ## -1 -> inizializzazione
        ## 0 -> normale
        ## 1 -> Pac-Man lose life
        ## 2 -> Power Pac-Man
        ## 3 -> Power Pac-Man in conclusione
        ## 4 -> mangiato da Pac-Man durante stato 2/3
        if status == -1: self.pos_init()
        elif status == 0:
            if self._status == 3: self.normal()
            else: self.start()
        elif status == 1: self.stop()
        elif status == 2: self.runaway()
        elif status == 4: self.eaten()
        self._status = status
        self._counter = 0

    def pos_init(self): # La posizione del fantasma viene ripristinata a quella iniziale
        self._x, self._y = self._start_x, self._start_y
        self._sprite = [64, 64 + self._color*16]

    def start(self): # Il fantasma inizia a muoversi
        self._speed = 2
        self._dir = [0, -2]
        self._sprite = [64, 64 + self._color*16]

    def normal(self): # Il fantasma torna a velocità normale
        self._speed = 2
        if self._y == 112 and 92 <= self._x <= 128: self._gate = True # Se è all'interno del recinto iniziale deve avere la possibilità di uscire
        if (self._dir[0] != 0 and self._x % 2 == 0) or (self._dir[1] != 0 and self._y % 2 == 0):
            self._dir = [self._dir[0]*2, self._dir[1]*2]
        else:
            self._x += self._dir[0]
            self._y += self._dir[1]
            self._dir = [self._dir[0]*2, self._dir[1]*2]
        self._sprite = [0, 64 + self._color*16]

    def stop(self): # Il fantasma si ferma
        self._speed = 0
        self._dir = [0, 0]

    def runaway(self): # Il fantasma fa retrofront, diventa blu e rallenta
        self._speed = 1
        if self._dir[0] != 0: self._dir[0] = -self._dir[0]/abs(self._dir[0])
        else: self._dir[1] = -self._dir[1]/abs(self._dir[1])
        self._sprite = [144, 64]

    def eaten(self): # Il fantasma diventa gli "occhietti" e aumenta la propria velocità
        self._speed = 4
        self._gate = True
        if (self._dir[0] != 0 and self._x % 4 == 0) or (self._dir[1] != 0 and self._y % 4 == 0):
            self._dir = [self._dir[0]*4, self._dir[1]*4]
        else:
            self._x += 4 - self._x % 4
            self._y += 4 - self._y % 4
            self._dir = [self._dir[0]*4, self._dir[1]*4]
        self._sprite = [128, 80]

    def move(self):
        Arena_W, Arena_H = self._arena.size()
        angles = ((0,0),(232,0),(0,232),(232,232))
        ## Controllo dei confini dell'arena
        if self._x < self._speed - self.W: self._x = Arena_W - self._speed
        elif self._x > Arena_W - self._speed: self._x = self._speed - self.W
        ## Creazione della lista delle sole direzioni possibili
        dirs = []
        if not self._arena.going_to_wall(self, self._dir[0], self._dir[1]): dirs.append(self._dir)
        if self._dir[0] == 0:
            if not self._arena.going_to_wall(self, self._speed, 0): dirs.append([self._speed,0])
            if not self._arena.going_to_wall(self, -self._speed, 0): dirs.append([-self._speed, 0])
        else:
            if not self._arena.going_to_wall(self, 0, self._speed): dirs.append([0, self._speed])
            if not self._arena.going_to_wall(self, 0, -self._speed): dirs.append([0, -self._speed])

        ## Il fantasma fa retrofront solo se non può fare nient'altro
        if len(dirs) == 0: self._dir = [-self._dir[0], -self._dir[1]]
        ## Modalità Frightened (movimenti a random)
        elif self._status in [2, 3]: self._dir = random.choice(dirs)
        else:
            ## Selezione dell'obiettivo (xt, yt)
            if self._gate and self._status != 4: # Il fantasma esce dal recinto iniziale per entrare in gioco
                xt, yt = 108, 88
                if self._x == xt and self._y == yt:
                    self.status(0)
                    self._gate = False
            elif self._status == 4: # Il fantasma ritorna dentro il recinto iniziale quando viene mangiato da PacMan
                xt,yt = 108, 112
                if self._x == xt and self._y == yt:
                    self.status(0)
                    self._gate = True
            elif self._behav == 0: # Modalità Scatter (pattugliamento dell'angolo)
                xt,yt = angles[self._color]
                if self._behav_count == FRAME_RATE*7:
                    self._behav_count = 0
                    self._behav = 1
                else: self._behav_count += 1
            elif self._behav == 1: # Modalità Chase (inseguimento di Pac-Man)
                for a in self._arena.actors():
                    if isinstance(a, PacMan):
                        xt, yt, w, h = a.rect()
                if self._behav_count == FRAME_RATE*7:
                    self._behav_count = 0
                    self._behav = 0
                else: self._behav_count += 1

            if len(dirs) == 1: self._dir = dirs[0]
            else: # Calcolo della distanza minore per raggiungere l'obiettivo
                x, y = self._x, self._y
                distances = []
                for i in range(len(dirs)):
                    dist = ((x + dirs[i][0]*8 - xt)**2 + (y + dirs[i][1]*8 - yt)**2)**(1/2)
                    distances.append(dist)
                dist_min = distances[0]
                dir_min = 0
                for i in range(len(dirs)):
                    if distances[i] < dist_min:
                        dist_min = distances[i]
                        dir_min = i
                self._dir = dirs[dir_min]
        ## Infine si effettua lo spostamento
        self._x += self._dir[0]
        self._y += self._dir[1]

    def symbol(self):
        # Status -1
        if self._status == -1:
            if self._counter % 3 == 0:
                if self._sprite[0] == 64: self._sprite[0] = 80
                else: self._sprite[0] = 64
            if self._counter == 5*FRAME_RATE:
                if self._color == 0: self.status(0)
                else: self.start()
            if self._counter == 5*FRAME_RATE + 90*self._color:
                if self._color != 0: self._gate = True
            self._counter += 1
        ## Status 0
        elif self._status == 0 and self._counter == 3:
            if self._dir == [self._speed,0]:
                if self._sprite[0] == 0: self._sprite[0] = 16
                else: self._sprite[0] = 0
            elif self._dir == [-self._speed,0]:
                if self._sprite[0] == 32: self._sprite[0] = 48
                else: self._sprite[0] = 32
            elif self._dir == [0,-self._speed]:
                if self._sprite[0] == 64: self._sprite[0] = 80
                else: self._sprite[0] = 64
            elif self._dir == [0,self._speed]:
                if self._sprite[0] == 96: self._sprite[0] = 112
                else: self._sprite[0] = 96
            self._counter = 0
        ## Status 1
        elif self._status == 1:
            if self._counter == FRAME_RATE: self._sprite = [96, 128]
            elif self._counter == FRAME_RATE*3:
                self.status(-1)
                return [96, 128]
            self._counter += 1
        ## Status 2
        elif self._status == 2 and self._counter % 3 == 0:
            if self._sprite[0] == 128: self._sprite[0] = 144
            elif self._sprite[0] == 144: self._sprite[0] = 128
            self._counter += 1
        elif self._status == 2 and self._counter >= FRAME_RATE*6:
            self.status(3)
        ## Status 3
        elif self._status == 3 and  self._counter % 3 == 0:
            if self._sprite[0] == 128: self._sprite[0] = 144
            elif self._sprite[0] == 144: self._sprite[0] = 160
            elif self._sprite[0] == 160: self._sprite[0] = 176
            elif self._sprite[0] == 176: self._sprite[0] = 128
            self._counter += 1
        elif self._status == 3 and self._counter >= FRAME_RATE*3:
            self.status(0)
        ## Status 4
        elif self._status == 4:
            if self._dir == [self._speed,0]: self._sprite[0] = 128
            elif self._dir == [-self._speed,0]: self._sprite[0] = 144
            elif self._dir == [0,-self._speed]:  self._sprite[0] = 160
            elif self._dir == [0,self._speed]: self._sprite[0] = 176
            self._counter = 0
        else: self._counter += 1
        return self._sprite[0], self._sprite[1]
        

class PacMan(Actor):
    W, H = 16, 16

    def __init__(self, arena, x:int, y:int):
        self._x, self._y = x, y
        self.status(-1)
        self._arena = arena
        self._arena.add(self)
        self.scores = 0 # Punteggio
        self.scores_sprite = []
        self.bonus_sprite = []
        self._bonus = [100, 300, 500, 700, 1000, 2000, 3000, 5000] #valori dei bonus
        self._gate = False

    def direction(self, next_dx:int, next_dy:int):
        self._next_dir = (next_dx, next_dy)

    def getStatus(self) -> int:
        return self._status

    def getGate(self) -> bool:
        return self._gate

    def status(self, status: int):
        ## STATI:
        ## -1 -> inizializzazione
        ## 0 -> normale
        ## 1 -> Pac-Man lose life
        if status == -1: self.pos_init()
        elif status == 0: self.start()
        elif status == 1: self.stop()
        self._status = status
        self._counter = 0

    def pos_init(self): # La posizione di PacMan viene ripristinata a quella iniziale
        self._x, self._y = 108, 184
        self._sprite = (16, 16)

    def start(self): # PacMan inizia a muoversi
        self.pos_init()
        self._dir = (-2, 0)
        self._next_dir = (-2, 0)

    def stop(self): # PacMan si ferma
        self._arena.sound(3).stop()
        self._dir = (0,0)
        self._next_dir = (0,0)
        self._sprite = (16, self._sprite[1])

    def collide(self, other):
        if isinstance(other, Wall):
            self._x -= self._dir[0]
            self._y -= self._dir[1]
            if self._dir == (2,0): self._sprite = (16,0)
            elif self._dir == (-2,0): self._sprite = (16,16)
            elif self._dir == (0,-2): self._sprite = (16,32)
            elif self._dir == (0,2): self._sprite = (16,48)
            self._dir = (0, 0)
        elif isinstance(other, Ghost):
            x, y, w, h = other.rect()
            if (y < self._y + self.H//2 and self._y < y + h//2 and x < self._x + self.W//2 and self._x < x + w//2):
                if other.getStatus() == 0:
                    for a in self._arena.actors(): a.status(1)
                elif other.getStatus() == 2 or other.getStatus() == 3:
                    self._arena.sound(5).play()
                    ## Calcolo punti bonus
                    num = 0 # Numero di fantasmini già mangiati
                    for a in self._arena.actors():
                        if isinstance(a, Ghost) and a.getStatus() in [0,4]: num += 1
                    if other.getStatus() == 3: num += 1
                    score = 100 * (2**(num + 1))
                    self.scores_sprite.append([(x, y), num, 0])
                    self.scores += score
                    other.status(4)
        elif isinstance(other, Bonus) and other.getStatus() == 0:
            x, y, w, h = other.rect()
            if (y < self._y + self.H//2 and self._y < y + h//2 and x < self._x + self.W//2 and self._x < x + w//2):
                other.status(-1)
                n = other.getNumber()
                self._arena.sound(4).play()
                self.bonus_sprite.append([(x, y), n, 0 ])
                self.scores += self._bonus[n]
            
    def move(self):
        Arena_W, Arena_H = self._arena.size()
        if self._status == 0:
            ## Controllo dei confini dell'arena
            if self._x < 2 - self.W: self._x = Arena_W - 2
            elif self._x > Arena_W - 2: self._x = 2 - self.W
            ## Sostituzione di dir con next_dir se possibile
            if self._dir != self._next_dir and not self._arena.going_to_wall(self, self._next_dir[0], self._next_dir[1]):
                self._dir = self._next_dir
            self._x += self._dir[0]
            self._y += self._dir[1]

    def symbol(self):
        ## Status -1
        if self._status == -1:
            if self._counter == FRAME_RATE*5:
                self._arena.sound(3).play(-1)
                self.status(0)
            self._counter += 1
        ## Status 0
        elif self._status == 0 and self._counter == 2:
            if self._dir == (2,0):
                if self._sprite == (0,0): self._sprite = (16,0)
                elif self._sprite == (16,0): self._sprite = (32,0)
                else: self._sprite = (0,0)
            elif self._dir == (-2,0):
                if self._sprite == (0,16): self._sprite = (16,16)
                elif self._sprite == (16,16): self._sprite = (32,0)
                else: self._sprite = (0,16)
            elif self._dir == (0,-2):
                if self._sprite == (0,32): self._sprite = (16,32)
                elif self._sprite == (16,32): self._sprite = (32,0)
                else: self._sprite = (0,32)
            elif self._dir == (0,2):
                if self._sprite == (0,48): self._sprite = (16,48)
                elif self._sprite == (16,48): self._sprite = (32,0)
                else: self._sprite = (0,48)
            self._counter = 0
        ## Status 1
        elif self._status == 1:
            if self._counter == FRAME_RATE:
                self._arena.sound(1).play()
                self._sprite = (48, 0)
            elif FRAME_RATE < self._counter < FRAME_RATE*3:
                if self._counter % 5 == 0: self._sprite = (self._sprite[0] + 16, 0)
            elif self._counter == FRAME_RATE*3:
                self._arena.lose_life()
                self.status(-1)
                return (180, 16)
            self._counter += 1
        else: self._counter += 1
        return self._sprite
