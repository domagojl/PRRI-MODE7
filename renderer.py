import pygame as pg
import numpy as np
from settings import *
from numba import njit, prange

class Renderer3D:
    def __init__(self, app):
        self.app = app
        self.set_textures('textures/sky1.png', 'textures/floor_1.png')
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)


        self.tex_size = self.ceil_tex.get_size()
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)

        self.screen_array = pg.surfarray.array3d(pg.Surface(WIN_RES))

        self.alt = 1.0
        self.angle = 0.0
        self.pos = np.array([0.0, 0.0])

    def set_textures(self, sky_path, ground_path):
        self.floor_tex = pg.image.load(ground_path).convert()
        self.ceil_tex = pg.image.load(sky_path).convert()
        self.tex_size = self.floor_tex.get_size()
        self.floor_array = pg.surfarray.array3d(self.floor_tex)
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)


    def update(self):
        self.movement()
        self.screen_array = self.render_frame(self.floor_array, self.ceil_array, self.screen_array,
                                              self.tex_size, self.angle, self.pos, self.alt)

    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    def project(self, world_pos):
        """Convert world coordinates (x, y) to screen coordinates (screen_x, screen_y) with size scaling"""
        relative_pos = world_pos - self.pos
        rotated_x = relative_pos[0] * np.cos(self.angle) - relative_pos[1] * np.sin(self.angle)
        rotated_y = relative_pos[0] * np.sin(self.angle) + relative_pos[1] * np.cos(self.angle)

        if rotated_y <= 0.1:  
            return -1000, -1000, 0  

        screen_x = int(WIDTH / 2 + rotated_x / rotated_y * WIDTH / 4)
        screen_y = int(HEIGHT / 2 - self.alt * 50 / rotated_y)

        
        scale = max(5, int(100 / rotated_y))  

        return screen_x, screen_y, scale

    @staticmethod
    @njit(fastmath=True, parallel=True)
    def render_frame(floor_array, ceil_array, screen_array, tex_size, angle, character_pos, alt):

        sin, cos = np.sin(angle), np.cos(angle)

       
        for i in prange(WIDTH):
            new_alt = alt
            for j in range(HALF_HEIGHT, HEIGHT):
                x = HALF_WIDTH - i
                y = j + FOCAL_LEN
                z = j - HALF_HEIGHT + new_alt

                
                px = (x * cos - y * sin)
                py = (x * sin + y * cos)

                
                floor_x = px / z - character_pos[0]
                floor_y = py / z + character_pos[1]

                
                floor_pos = int(floor_x * SCALE % tex_size[0]), int(floor_y * SCALE % tex_size[1])
                floor_col = floor_array[floor_pos]

                
                ceil_x = alt * px / z - character_pos[0] * 0.3
                ceil_y = alt * py / z + character_pos[1] * 0.3

                
                ceil_u = int(np.abs(ceil_x * SCALE) % tex_size[0])
                ceil_v = int(np.abs(ceil_y * SCALE) % tex_size[1])
                ceil_pos = (ceil_u, ceil_v)
                ceil_col = ceil_array[ceil_pos]

                
                depth = min(max(2.5 * (abs(z) / HALF_HEIGHT), 0), 1)
                fog = (1 - depth) * 25

                floor_col = (floor_col[0] * depth + fog,
                             floor_col[1] * depth + fog,
                             floor_col[2] * depth + fog)

                ceil_col = (ceil_col[0] * depth + fog,
                            ceil_col[1] * depth + fog,
                            ceil_col[2] * depth + fog)

                
                screen_array[i, j] = floor_col
                screen_array[i, -j] = ceil_col

                
                new_alt += alt

        return screen_array

    def movement(self):
        sin_a = np.sin(self.angle)
        cos_a = np.cos(self.angle)
        dx, dy = 0, 0
        player_speed = SPEED * 0.7 * self.app.speed_multiplier
        speed_sin = player_speed * sin_a
        speed_cos = player_speed * cos_a

        self.angle %= 2 * np.pi

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            dy += speed_cos
            dx += speed_sin
        if keys[pg.K_s]:
            dy += -speed_cos
            dx += -speed_sin
        if keys[pg.K_a]:
            dy += speed_sin
            dx += -speed_cos
        if keys[pg.K_d]:
            dy += -speed_sin
            dx += speed_cos
        self.pos[0] += dx
        self.pos[1] += dy

        if keys[pg.K_LEFT]:
            self.angle -= SPEED
        if keys[pg.K_RIGHT]:
            self.angle += SPEED

        if keys[pg.K_q]:
            self.alt += SPEED
        if keys[pg.K_e]:
            self.alt -= SPEED
        self.alt = min(max(self.alt, 0.3), 4.0) 