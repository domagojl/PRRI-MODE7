import time
import pygame as pg


class ResultsScreen:
    def __init__(self, screen, time_survived, zombies_killed, waves_survived):
        self.screen = screen
        self.bg_image = pg.image.load("textures/background_game_over.png").convert()
        self.bg_image = pg.transform.scale(self.bg_image, self.screen.get_size())
        self.time_survived = time_survived
        self.zombies_killed = zombies_killed
        self.waves_survived = waves_survived
        self.font = pg.font.Font("fonts/menu_font.ttf", 110)
        self.small_font = pg.font.SysFont("Roboto", 50)
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.red = (255, 0, 0)
        self.fade_in_duration = 60
        self.elapsed_time = 0
        self.y_position = self.screen.get_height() // 2
        self.game_over_text = self.font.render("YOU DIED", True, self.white)
        self.results_fade_in_alpha = 0
        self.result_texts = [
            self.small_font.render(f"Time Survived: {self.format_time(self.time_survived)}", True, self.white),
            self.small_font.render(f"Zombies Killed: {self.zombies_killed}", True, self.white),
            self.small_font.render(f"Days Survived: {self.waves_survived}", True, self.white)
        ]

    def format_time(self, time_in_seconds):
        minutes = time_in_seconds // 60
        seconds = time_in_seconds % 60
        return f"{int(minutes):02}:{int(seconds):02}"

    def update(self):
        self.elapsed_time += 1
        if self.elapsed_time < 60:
            self.y_position -= 1
        if self.elapsed_time > 60:
            if self.results_fade_in_alpha < 255:
                self.results_fade_in_alpha += 5

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        self.screen.blit(self.game_over_text, (self.screen.get_width() // 2 - self.game_over_text.get_width() // 2, self.screen.get_height() // 5))
        alpha_surface = pg.Surface((self.screen.get_width(), self.screen.get_height()), pg.SRCALPHA)
        alpha_surface.fill((0, 0, 0, 255 - self.results_fade_in_alpha))
        self.screen.blit(alpha_surface, (0, 0))
        if self.elapsed_time > 60:
            for i, result_text in enumerate(self.result_texts):
                self.screen.blit(result_text, (self.screen.get_width() // 2 - result_text.get_width() // 2, self.screen.get_height() // 2 + i * 80))
        pg.display.flip()

    def is_done(self):
        return self.results_fade_in_alpha >= 255 