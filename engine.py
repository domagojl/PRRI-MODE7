import pygame as pg
import sys
import time
from settings import WIN_RES, GAME
from renderer import Renderer3D
from game import Game, Character

class GameEngine:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.mode7 = Renderer3D(self)
        self.player = Character()
        self.game = Game(self.mode7, self.player, self)
        self.state = GAME
        self.start_time = time.time()
        self.zombies_killed = 0
        pg.mixer.music.load("music/in_game_bg.mp3")
        pg.mixer.music.play(-1)

    def update(self):
        self.mode7.update()
        self.game.update(self.mode7.pos)
        self.clock.tick()
        pg.display.set_caption(f'{self.clock.get_fps():.1f}')

    def draw(self):
        self.mode7.draw()
        self.game.draw(self.screen)
        pg.display.flip()

    def check_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.game.shoot_rifle(self.mode7.pos, self.mode7.angle)

    def run(self):
        while True:
            self.check_event()
            self.update()
            self.draw()

if __name__ == "__main__":
    GameEngine().run()
