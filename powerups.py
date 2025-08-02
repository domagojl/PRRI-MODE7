import pygame as pg
import numpy as np
import time 
from settings import SHOTGUN

class Drop:
    def __init__(self, pos):
        self.pos = np.array(pos, dtype=np.float32)
        self.collected = False
        self.texture = pg.Surface((20, 20))  

    def update(self, character_pos):
        if np.linalg.norm(self.pos - character_pos) < 0.6:
            self.on_pickup()
            self.collected = True

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            scaled_texture = pg.transform.scale(self.texture, (scale, scale))
            screen.blit(scaled_texture, (int(screen_x) - scale // 2, int(screen_y) - scale // 2))

    def on_pickup(self):
        pass


class HealthDrop(Drop):
    def __init__(self, pos, player, app):
        super().__init__(pos)
        self.texture = pg.image.load("textures/health.png").convert_alpha()
        self.player = player
        self.app = app  

    def on_pickup(self):
        print("Medical supplies found!")
        if self.player.health < self.player.max_health:
            self.player.health += 5
            self.player.health = max(0, min(self.player.health, self.player.max_health))
            self.app.health_sound.play()  


class ShotgunDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("textures/uzi.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("Shotgun acquired!")
        self.app.apply_powerup(SHOTGUN)
        self.app.equipment_timer = time.time() + 8






class SpeedUpDrop(Drop):
    def __init__(self, pos, app):
        super().__init__(pos)
        self.texture = pg.image.load("textures/speed.png").convert_alpha()
        self.app = app

    def on_pickup(self):
        print("Adrenaline rush activated!")
        self.app.apply_speed_boost(1.6, duration=6) 