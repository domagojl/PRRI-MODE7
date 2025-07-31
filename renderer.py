import numpy as np
import pygame as pg
from settings import WIDTH, HEIGHT, HALF_HEIGHT, HALF_WIDTH, FOCAL_LEN, SCALE, SPEED

class Renderer3D:
    def __init__(self, app):
        self.app = app
        self.floor_tex = pg.image.load('textures/floor_1.png').convert()
        self.ceil_tex = pg.image.load('textures/sky1.png').convert()
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)
        self.screen_array = pg.surfarray.array3d(pg.Surface((WIDTH, HEIGHT)))
        self.alt = 1.0
        self.angle = 0.0
        self.pos = np.array([0.0, 0.0])

    def update(self):
        self.movement()

    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    def project(self, world_pos):
        rel = world_pos - self.pos
        rx = rel[0] * np.cos(self.angle) - rel[1] * np.sin(self.angle)
        ry = rel[0] * np.sin(self.angle) + rel[1] * np.cos(self.angle)
        if ry <= 0.1:
            return -1000, -1000, 0
        x = int(WIDTH / 2 + rx / ry * WIDTH / 4)
        y = int(HEIGHT / 2 - self.alt * 50 / ry)
        scale = max(5, int(100 / ry))
        return x, y, scale

    def movement(self):
        keys = pg.key.get_pressed()
        sin_a = np.sin(self.angle)
        cos_a = np.cos(self.angle)
        speed = SPEED * 0.7
        if keys[pg.K_w]:
            self.pos[0] += speed * sin_a
            self.pos[1] += speed * cos_a
        if keys[pg.K_s]:
            self.pos[0] -= speed * sin_a
            self.pos[1] -= speed * cos_a
        if keys[pg.K_a]:
            self.pos[0] -= speed * cos_a
            self.pos[1] += speed * sin_a
        if keys[pg.K_d]:
            self.pos[0] += speed * cos_a
            self.pos[1] -= speed * sin_a
        if keys[pg.K_LEFT]:
            self.angle -= SPEED
        if keys[pg.K_RIGHT]:
            self.angle += SPEED
