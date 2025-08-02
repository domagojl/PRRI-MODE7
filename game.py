import numpy as np
import pygame as pg
import random

from powerups import ShotgunDrop, HealthDrop, SpeedUpDrop
from entities import Zombie, RunnerZombie, BruteZombie
from settings import RIFLE, SHOTGUN

class DamageNumber:
    def __init__(self, pos, damage_amount):
        self.pos = np.array(pos, dtype=np.float32)
        self.damage = str(damage_amount)
        self.timer = 60  # Float for 60 frames (1 second at 60fps)
        self.start_timer = self.timer
        
    def update(self):
        self.pos[1] -= 0.02  # Float upward
        self.timer -= 1
        
    def draw(self, screen, mode7):
        if self.timer <= 0:
            return
            
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            # Create font if needed
            font = pg.font.Font(None, max(16, int(scale // 8)))
            
            # Fade out over time
            alpha = int(255 * (self.timer / self.start_timer))
            color = (255, 255, 255)  # White damage numbers
            
            # Render text
            text_surface = font.render(self.damage, True, color)
            text_rect = text_surface.get_rect(center=(int(screen_x), int(screen_y)))
            
            # Create surface with alpha for fading
            fade_surface = pg.Surface(text_surface.get_size())
            fade_surface.set_alpha(alpha)
            fade_surface.blit(text_surface, (0, 0))
            
            screen.blit(fade_surface, text_rect)
    
    def is_expired(self):
        return self.timer <= 0

class Character:
    def __init__(self):
        self.health = 25
        self.max_health = 25
        self.hit_sound = pg.mixer.Sound('music/hp-down.wav')
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
        print(f"Damage taken: {amount}")
        self.health = max(0, self.health - amount)
        self.hit_sound.play()

    def is_dead(self):
        return self.health <= 0

    def draw_health(self, screen):
        health_index = 6 - (self.health // 4)
        if health_index >= 30 or health_index <= 0:
            health_index = 0
        if self.health <= 4 and self.health >= 1:
            health_index = 5
        # Position in top left instead of top right
        x = 10
        y = 10
        screen.blit(self.health_bar_frames[health_index], (x, y))
        
    def update(self):
        pass

class Bullet:
    def __init__(self, character_pos, character_angle, speed=0.5, max_distance=20, offset_distance = 2.0, weapon_type=None):
        character_angle = np.radians(character_angle) if character_angle > np.pi * 2 else character_angle

        direction_x = np.cos(character_angle - np.pi/2)
        direction_y = -np.sin(character_angle - np.pi/2)
        self.direction = np.array([direction_x, direction_y], dtype=np.float32)

        rotated_offset_x = offset_distance * direction_x
        rotated_offset_y = offset_distance * direction_y

        self.pos = np.array(character_pos, dtype=np.float32) + np.array([rotated_offset_x, rotated_offset_y])
        self.speed = speed
        self.max_distance = max_distance
        self.start_pos = np.array(self.pos, dtype=np.float32)
        self.active = True
        self.weapon_type = weapon_type
        #self.app = app

    def update(self):
        self.pos += self.direction * self.speed
        if np.linalg.norm(self.pos - self.start_pos) > self.max_distance:
            self.active = False

    def draw(self, screen, mode7):
        screen_x, screen_y, scale = mode7.project(self.pos)
        if scale > 0:
            radius = max(2, scale // 15)
            # Different colors per weapon
            if self.weapon_type == RIFLE:
                color = (255, 255, 0)  # Yellow for Glock
            elif self.weapon_type == SHOTGUN:
                color = (255, 165, 0)  # Orange for Uzi
            else:
                color = (0, 0, 0)  # Default black
            pg.draw.circle(screen, color, (int(screen_x), int(screen_y)), radius)

class Game:
    def __init__(self, mode7, player, app):
        self.mode7 = mode7
        self.player = player
        self.app = app
        self.wave = 1
        self.bullets = []
        self.zombies = []
        self.drops = []
        self.wave_sound = pg.mixer.Sound("music/level_up.mp3")
        self.explosion_sound = pg.mixer.Sound("music/explosion.wav")
        
        # Muzzle flash system
        self.muzzle_flash_timer = 0
        self.muzzle_flash_pos = None
        self.muzzle_flash_weapon = None
        
        # Damage numbers system
        self.damage_numbers = []
        
        # Wave transition system
        self.wave_flash_timer = 0
        
        self.spawn_wave(self.wave)


    def spawn_wave(self, wave_num):
        self.zombies.clear()
        for _ in range(4 + wave_num * 2):
            x, y = random.uniform(-10, 10), random.uniform(-10, 10)
            if wave_num < 5:
                enemy = Zombie((x, y))
            elif wave_num < 10:
                enemy = random.choice([Zombie((x, y)), RunnerZombie((x, y))])
            elif wave_num < 15:
                enemy = random.choice([RunnerZombie((x, y)), BruteZombie((x, y))])
            else:
                enemy = random.choice([Zombie((x, y)), RunnerZombie((x, y)), BruteZombie((x, y))])
            self.zombies.append(enemy)

        match wave_num:
            case 3:
                self.mode7.set_textures('textures/cloudy_sky.png', 'textures/sand.png')
            case 6:
                self.mode7.set_textures('textures/ugly_sky.png', 'textures/volcanic_ash.png')
            case 9:
                self.mode7.set_textures('textures/ugly_sky.png', 'textures/radiation.png')
            case 12:
                self.mode7.set_textures('textures/sky1.png', 'textures/floor_1.png')
            case 15:
                self.mode7.set_textures('textures/cloudy_sky.png', 'textures/cracked_ice.png')
            case 18:
                self.mode7.set_textures('textures/cloudy_sky.png', 'textures/swamp.png')
            case 21:
                self.mode7.set_textures('textures/dark_sky.png', 'textures/factory_floor.png')
            case 24:
                self.mode7.set_textures('textures/ugly_sky.png', 'textures/pavement.png')
            case 27:
                self.mode7.set_textures('textures/ugly_sky.png', 'textures/gravel_road.png')
            case 30:
                self.mode7.set_textures('textures/sky1.png', 'textures/ground_rail_lowres.png')
            case 33:
                self.mode7.set_textures('textures/cloudy_sky.png', 'textures/ground_graveldirt_lowres.png')
            case 36:
                self.mode7.set_textures('textures/dark_sky.png', 'textures/ground_halfsnow_lowres.png')
            case 39:
                self.mode7.set_textures('textures/sky1.png', 'textures/ground_sea_lowres.png')
            case 42:
                self.mode7.set_textures('textures/cloudy_sky.png', 'textures/ground_dirt_lowres.png')
            case _:
                pass

    def update(self, character_pos):
        for proj in self.bullets:
            proj.update()

        for proj in self.bullets:
            for enemy in self.zombies:
                if enemy.check_collision(proj):
                    proj.active = False
                    # Create damage number
                    damage_pos = enemy.pos.copy()
                    damage_pos[1] -= 0.5  # Slightly above enemy
                    self.damage_numbers.append(DamageNumber(damage_pos, 50))
                    
                    if not enemy.alive:
                        self.app.zombies_killed += 1
                        if random.random() < 0.3:
                            drop_type = random.choice([HealthDrop, ShotgunDrop, SpeedUpDrop])
                            pos = enemy.pos.copy()
                            if drop_type == HealthDrop:
                                self.drops.append(HealthDrop(pos, self.player, self.app))
                            else:
                                self.drops.append(drop_type(pos, self.app))

        self.bullets = [p for p in self.bullets if p.active]

        for enemy in self.zombies:
            enemy.update(character_pos)
            for bullet in enemy.bullets:
                if np.linalg.norm(np.array(character_pos) - bullet.pos) < 0.5:
                    self.player.take_damage(enemy.damage)
                    bullet.active = False
            if isinstance(enemy, RunnerZombie):
                if np.linalg.norm(np.array(character_pos) - enemy.pos) < 0.5:
                    self.player.take_damage(enemy.damage)
                    self.explosion_sound.play()
                    enemy.alive = False

        self.zombies = [e for e in self.zombies if e.alive]

        for drop in self.drops:
            drop.update(character_pos)

        self.drops = [d for d in self.drops if not d.collected]

        # Update damage numbers
        for damage_num in self.damage_numbers:
            damage_num.update()
        self.damage_numbers = [d for d in self.damage_numbers if not d.is_expired()]

        # Update muzzle flash timer
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= 1
            
        # Update wave flash timer
        if self.wave_flash_timer > 0:
            self.wave_flash_timer -= 1

        if len(self.zombies) == 0:
            self.wave += 1
            # Trigger wave transition effect
            self.wave_flash_timer = 30  # Flash for 30 frames (0.5 seconds)
            self.wave_sound.play()
            self.spawn_wave(self.wave)

    def draw(self, screen):
        for proj in self.bullets:
            proj.draw(screen, self.mode7)
        for enemy in self.zombies:
            enemy.draw(screen, self.mode7)
        for drop in self.drops:
            drop.draw(screen, self.mode7)
        
        # Draw damage numbers
        for damage_num in self.damage_numbers:
            damage_num.draw(screen, self.mode7)
        
        # Draw muzzle flash
        if self.muzzle_flash_timer > 0 and self.muzzle_flash_pos is not None:
            screen_x, screen_y, scale = self.mode7.project(self.muzzle_flash_pos)
            if scale > 0:
                flash_size = max(10, scale // 8)
                # Different colors per weapon
                if self.muzzle_flash_weapon == RIFLE:
                    flash_color = (255, 255, 255)  # Bright white for Glock
                else:
                    flash_color = (255, 200, 100)  # Warm yellow for Uzi
                pg.draw.circle(screen, flash_color, (int(screen_x), int(screen_y)), flash_size)
                # Add smaller inner circle for more intensity
                pg.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), flash_size // 2)


    def shoot_rifle(self, pos, angle):
        # Glock: Single accurate shot, higher damage, faster bullets
        offset = 0.5 if any(np.linalg.norm(enemy.pos - pos) < 2.0 for enemy in self.zombies) else 2.0
        self.bullets.append(Bullet(pos, angle, speed=0.8, offset_distance=offset, weapon_type=RIFLE))
        
        # Trigger muzzle flash
        self.muzzle_flash_timer = 5  # Flash for 5 frames
        self.muzzle_flash_pos = pos.copy()
        self.muzzle_flash_weapon = RIFLE

    def shoot_shotgun(self, pos, angle):
        # Uzi: Single bullet, fast firing, less accurate, lower damage
        offset = 0.5 if any(np.linalg.norm(enemy.pos - pos) < 2.0 for enemy in self.zombies) else 2.0
        # Add slight random spread for less accuracy
        spread = random.uniform(-0.1, 0.1)
        self.bullets.append(Bullet(pos, angle + spread, speed=0.7, offset_distance=offset, weapon_type=SHOTGUN))
        
        # Trigger muzzle flash
        self.muzzle_flash_timer = 3  # Shorter flash for rapid fire
        self.muzzle_flash_pos = pos.copy()
        self.muzzle_flash_weapon = SHOTGUN