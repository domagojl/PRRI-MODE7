import pygame as pg
import sys
import time
from settings import WIN_RES, MENU, GAME
from renderer import *
from game import Game, Character
from menu import Menu
from settings import RIFLE, SHOTGUN
from endscreen import ResultsScreen

class GameEngine:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.mode7 = Renderer3D(self)
        self.player = Character()
        self.game = Game(self.mode7, self.player, self)
        self.menu = Menu(self)
        self.state = MENU
        self.speed_multiplier = 1.0
        self.speed_timer = 0
        self.equipment = RIFLE
        self.equipment_timer = 0
        self.powerup_icon = pg.image.load("textures/Steampunk_valve_and_pipe.png").convert_alpha()
        self.powerup_icon = pg.transform.scale(self.powerup_icon, (128, 128))
        self.powerup_sound = pg.mixer.Sound("music/clock.mp3")
        
        self.last_shot_time = 0
        self.firing = False
        self.fire_rates = {
            RIFLE: 200,    
            SHOTGUN: 80    
        }

        self.start_time = time.time()
        self.zombies_killed = 0
        self.results_screen = None
        self.equipment_icons = {
            RIFLE: pg.image.load("textures/glock.png").convert_alpha(),
            SHOTGUN: pg.image.load("textures/uzi.png").convert_alpha(),
        }

        self.progression_box = pg.image.load("textures/panel.png").convert_alpha()
        self.progression_box = pg.transform.scale(self.progression_box, (200, 200)) 

        original_full = pg.image.load("textures/greenbar.png").convert_alpha()
        scale_factor = 0.2
        self.bar_full = pg.transform.scale(original_full, (
        int(original_full.get_width() * scale_factor), int(original_full.get_height() * scale_factor)))

        original_speed = pg.image.load("textures/greenbar.png").convert_alpha()
        scale_factor = 0.1
        scaled_speed = pg.transform.scale(original_speed, (
            int(original_speed.get_width() * scale_factor),
            int(original_speed.get_height() * scale_factor)
        ))

        self.bar_speed = pg.transform.rotate(scaled_speed, 90) 

        for key in self.equipment_icons:
            self.equipment_icons[key] = pg.transform.scale(self.equipment_icons[key], (80, 80))
        self.equipment_frame = pg.image.load("textures/frame.png").convert_alpha()
        self.equipment_frame = pg.transform.scale(self.equipment_frame, (300, 200))
        self.firing = False
        
        self.weapon_sounds = {
            RIFLE: pg.mixer.Sound("music/desert_eagle.mp3"),    
            SHOTGUN: pg.mixer.Sound("music/machinegun.mp3")     
        }
        self.health_sound = pg.mixer.Sound("music/hp_up.wav")
        pg.mixer.music.load("music/main_menu.mp3")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)
        
    def apply_speed_boost(self, multiplier, duration=5):
        self.speed_multiplier = multiplier
        self.speed_timer = time.time() + duration
        print(f"Adrenaline surge: x{multiplier} for {duration}s")



    def show_results_screen(self):
        time_survived = int(time.time() - self.start_time)
        zombies_killed = self.zombies_killed
        waves_survived = self.game.wave

        results_screen = ResultsScreen(self.screen, time_survived, zombies_killed, waves_survived)
        results_screen.update()
        results_screen.draw()



    def wait_for_input_after_game_over(self):
        waiting_for_input = True
        while waiting_for_input:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                    self.__init__()
                    self.state = MENU
                    waiting_for_input = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.state = MENU
                    waiting_for_input = False

    def try_shoot(self):
        current_time = pg.time.get_ticks()
        if current_time - self.last_shot_time >= self.fire_rates[self.equipment]:
            self.last_shot_time = current_time
            if self.equipment == RIFLE:
                self.weapon_sounds[RIFLE].play()  
                self.game.shoot_rifle(self.mode7.pos, self.mode7.angle)
            elif self.equipment == SHOTGUN:
                self.weapon_sounds[SHOTGUN].play()  
                self.game.shoot_shotgun(self.mode7.pos, self.mode7.angle)

    def update(self):
        if self.state == MENU:
            self.menu.update()

        if self.equipment != RIFLE and time.time() > self.equipment_timer:
            self.equipment = RIFLE
            print("Equipment depleted")
        elif self.state == GAME:
            if self.player.is_dead():
                self.powerup_sound.stop()
                self.state = GAME_OVER
                self.results_screen = ResultsScreen(
                    self.screen,
                    int(time.time() - self.start_time),
                    self.zombies_killed,
                    self.game.wave
                )
                return
            character_pos = self.mode7.pos
            self.mode7.update()
            self.game.update(character_pos)
            if hasattr(self, 'equipment_timer') and time.time() > self.equipment_timer:
                self.equipment = RIFLE
                del self.equipment_timer

            
            if self.firing:
                self.try_shoot()

            self.clock.tick()
            pg.display.set_caption(f'{self.clock.get_fps():.1f}')
            if self.speed_multiplier != 1.0 and time.time() > self.speed_timer:
                self.speed_multiplier = 1.0
                print("Adrenaline faded")


        elif self.state == GAME_OVER:
            pass



    def draw_ui(self):
        box_x, box_y = self.screen.get_width() - 220, 20
        self.screen.blit(self.progression_box, (box_x, box_y))

        
        font = pg.font.Font("fonts/menu_font.ttf", 24)
        color = (255, 220, 180)

        
        wave_text = font.render(f"DAY: {self.game.wave}", True, color)
        zombies_text = font.render(f"ZOMBIES: {len(self.game.zombies)}", True, color)

        
        text_x = box_x + 30  
        
        
        wave_y = box_y + 60
        zombies_y = box_y + 100

        self.screen.blit(wave_text, (text_x, wave_y))
        self.screen.blit(zombies_text, (text_x, zombies_y)) 

        self.player.draw_health(self.screen)
   

        if self.equipment != RIFLE and time.time() < self.equipment_timer:
            x, y = 85, 600
            total = 8  
            remaining = self.equipment_timer - time.time()
            percent = max(0, min(1, remaining / total))

            full_width = int(self.bar_full.get_width() * percent)
            if full_width > 0:
                bar_clip = self.bar_full.subsurface(
                    (0, 0, full_width, self.bar_full.get_height())
                )
                self.screen.blit(bar_clip, (x, y))

        if self.speed_multiplier > 1.0 and time.time() < self.speed_timer:
            x2, y2 = 1440, 280 
            total = 6
            remaining = self.speed_timer - time.time()
            percent = max(0, min(1, remaining / total))

            full_height = int(self.bar_speed.get_height() * percent)
            if full_height > 0:

                bar_clip = self.bar_speed.subsurface(
                    (0, self.bar_speed.get_height() - full_height, self.bar_speed.get_width(), full_height)
                )
                rotated_clip = pg.transform.rotate(bar_clip, 0)
                self.screen.blit(rotated_clip, (x2, y2 + (self.bar_speed.get_height() - full_height)))

    def draw_equipment_ui(self):
        padding = 20
        frame_width, frame_height = self.equipment_frame.get_size()
        x = self.screen.get_width() - frame_width - padding
        y = self.screen.get_height() - frame_height - padding
        if x + frame_width > self.screen.get_width():
            x = self.screen.get_width() - frame_width
        if y + frame_height > self.screen.get_height():
            y = self.screen.get_height() - frame_height
        frame_rect = self.equipment_frame.get_rect()
        frame_rect.topleft = (x, y)
        self.screen.blit(self.equipment_frame, frame_rect)
        icon = self.equipment_icons[self.equipment]
        icon = pg.transform.scale(icon, (128, 128))
        icon_x = frame_rect.x + (frame_rect.width - icon.get_width()) // 2
        icon_y = frame_rect.y + (frame_rect.height - icon.get_height()) // 2
        self.screen.blit(icon, (icon_x, icon_y))

    def draw_crosshair(self):
        
        center_x, center_y = self.screen.get_width() // 2, self.screen.get_height() // 2
        crosshair_size = 8
        crosshair_color = (255, 255, 255)  
        
      
        pg.draw.line(self.screen, crosshair_color, 
                    (center_x - crosshair_size, center_y), 
                    (center_x + crosshair_size, center_y), 2)
        pg.draw.line(self.screen, crosshair_color, 
                    (center_x, center_y - crosshair_size), 
                    (center_x, center_y + crosshair_size), 2)
       
        pg.draw.circle(self.screen, crosshair_color, (center_x, center_y), 1)

    def draw(self):
        if self.state == MENU:
            self.menu.draw()
        elif self.state == GAME:
            self.mode7.draw()
            self.game.draw(self.screen)
            self.draw_ui()
            self.draw_equipment_ui()
            self.draw_crosshair()
            
            
            if self.game.wave_flash_timer > 0:
                flash_alpha = int(100 * (self.game.wave_flash_timer / 30)) 
                flash_surface = pg.Surface(self.screen.get_size())
                flash_surface.fill((255, 255, 200))  
                flash_surface.set_alpha(flash_alpha)
                self.screen.blit(flash_surface, (0, 0))
            
            pg.display.flip()
        elif self.state == GAME_OVER:
            if self.results_screen:
                self.results_screen.update()
                self.results_screen.draw()

    def check_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            if self.state == MENU and event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self.__init__()
                self.state = GAME
                self.switch_to_game()
            elif self.state == GAME_OVER:
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.__init__()
                    self.state = MENU
                    self.results_screen = None
            elif self.state == GAME and self.player.is_dead() and event.type == pg.KEYDOWN and event.key == pg.K_r:
                self.__init__()
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.firing = True
                self.try_shoot()
            elif event.type == pg.KEYUP and event.key == pg.K_SPACE:
                self.firing = False

    def switch_to_game(self):
        pg.mixer.music.stop()
        pg.mixer.music.load("music/in_game_bg.mp3")
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1, 0.0)

    def apply_powerup(self, equipment_type):
        print(f"Equipment scavenged: {equipment_type}")
        self.equipment = equipment_type
        self.equipment_timer = time.time() + 8
        self.powerup_sound.stop()
        self.powerup_sound.play()

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()
            pg.display.flip()

if __name__ == "__main__":
    app = GameEngine()
    app.run() 