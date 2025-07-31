import numpy as np
import pygame as pg
import random
from entities import Zombie, Bullet
from powerups import HealthDrop

class Character:
    def __init__(self):
        self.health = 25
        self.max_health = 25
        self.hit_sound = pg.mixer.Sound('music/hp_up.wav')
        self.health_bar_sprite = pg.image.load('textures/bar_animated.png').convert_alpha()
        self.frame_width = 64
        self.frame_height = 64
        self.scaled_width = int(self.frame_width * 3)
        self.scaled_height = int(self.frame_height * 3)
        self.total_frames = 7
        self.health_bar_frames = []
        for i in range(self.total_frames):
            x = i * self.frame_width
            y = 0
            frame = self.health_bar_sprite.subsurface(pg.Rect(x, y, self.frame_width, self.frame_height))
            scaled_frame = pg.transform.scale(frame, (self.scaled_width, self.scaled_height))
            self.health_bar_frames.append(scaled_frame)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        self.hit_sound.play()

    def is_dead(self):
        return self.health <= 0

    def draw_health(self, screen):
        health_index = 6 - (self.health // 4)
        health_index = max(0, min(6, health_index))
        screen.blit(self.health_bar_frames[health_index], (10, 10))

class Game:
    def __init__(self, mode7, player, app):
        self.mode7 = mode7
        self.player = player
        self.app = app
        self.wave = 1
        self.bullets = []
        self.zombies = []
        self.drops = []
        self.spawn_wave()

    def spawn_wave(self):
        self.zombies.clear()
        for _ in range(3 + self.wave):
            x, y = random.uniform(-10, 10), random.uniform(-10, 10)
            self.zombies.append(Zombie((x, y)))

    def update(self, character_pos):
        for proj in self.bullets:
            proj.update()

        for proj in self.bullets:
            for enemy in self.zombies:
                if enemy.check_collision(proj):
                    proj.active = False
                    if not enemy.alive:
                        self.app.zombies_killed += 1
                        if random.random() < 0.2:
                            self.drops.append(HealthDrop(enemy.pos, self.player))

        self.bullets = [p for p in self.bullets if p.active]

        for enemy in self.zombies:
            enemy.update(character_pos)
            for bullet in enemy.bullets:
                if np.linalg.norm(np.array(character_pos) - bullet.pos) < 0.5:
                    self.player.take_damage(enemy.damage)
                    bullet.active = False

        self.zombies = [e for e in self.zombies if e.alive]
        for drop in self.drops:
            drop.update(character_pos)
        self.drops = [d for d in self.drops if not d.collected]

        if len(self.zombies) == 0:
            self.wave += 1
            self.spawn_wave()

    def draw(self, screen):
        for proj in self.bullets:
            proj.draw(screen, self.mode7)
        for enemy in self.zombies:
            enemy.draw(screen, self.mode7)
        for drop in self.drops:
            drop.draw(screen, self.mode7)
        self.player.draw_health(screen)

    def shoot_rifle(self, pos, angle):
        self.bullets.append(Bullet(pos, angle))
