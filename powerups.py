import pygame as pg
import numpy as np

class Drop:
    def __init__(self, pos):
        self.pos = np.array(pos, dtype=np.float32)
        self.collected = False
        self.texture = pg.Surface((20, 20))

    def update(self, player_pos):
        if np.linalg.norm(self.pos - player_pos) < 0.6:
            self.on_pickup()
            self.collected = True

    def draw(self, screen, mode7):
        x, y, scale = mode7.project(self.pos)
        if scale > 0:
            tex = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(tex, (int(x) - scale//2, int(y) - scale//2))

    def on_pickup(self):
        pass

class HealthDrop(Drop):
    def __init__(self, pos, player):
        super().__init__(pos)
        self.texture = pg.image.load("textures/Heal_powerup.png").convert_alpha()
        self.player = player

    def on_pickup(self):
        if self.player.health < self.player.max_health:
            self.player.health = min(self.player.max_health, self.player.health + 5)
