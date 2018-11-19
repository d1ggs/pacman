
class Actor(object):

    def rect(self) -> tuple:
        return self._x, self._y, self.W, self.H

    def getStatus(self):
        pass

    def status(self, status: int):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def move(self):
        pass

    def collide(self, other):
        pass

    def symbol(self):
        pass

class Arena(object):

    def __init__(self):
        pass

    def actors(self) -> list:
        return list(self._actors)

    def size(self) -> tuple:
        return (self._w, self._h)

    def getLifes(self) -> int:
        return self._lifes


    def add(self, a):
        if a not in self._actors: self._actors.append(a)

    def remove(self, a):
        if a in self._actors: self._actors.remove(a)

    def lose_life(self):
        self._lifes -= 1


    def move_all(self):
        for a in self.actors():
            previous_pos = a.rect()
            a.move()
            if a.rect() != previous_pos:
                for other in reversed(self.actors()):
                    if other is not a and self.check_collision(a, other):
                        a.collide(other)
                        other.collide(a)

    def check_collision(self, a1, a2) -> bool:
        x1, y1, w1, h1 = a1.rect()
        x2, y2, w2, h2 = a2.rect()
        return (y2 < y1 + h1 and y1 < y2 + h2 and x2 < x1 + w1 and x1 < x2 + w2)
