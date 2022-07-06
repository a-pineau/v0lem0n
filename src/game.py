"""Implements the game loop and handles the user's events."""

import os
import random
import pygame as pg
import math

from itertools import cycle
from player import Player
from ball import Ball
from bot import Bot
from obstacle import Obstacle
from settings import *
from os.path import join, dirname, abspath
from PyQt5.QtWidgets import (QMainWindow, QApplication, QGridLayout, QWidget, QLayout)

vec = pg.math.Vector2

# Manually places the window
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 50)

class Game:
    def __init__(self) -> None:
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode([WIDTH, HEIGHT])
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick(FPS) * 1e-3
        self.running = True  
        self.start_round = False
        self.n_frame = 0
        self.scores = {"Player": 0, "Bot": 0}
    
    def new(self):
        # Start a new game
        # Folder where the imgs are saved
        try:
            os.makedirs(SNAP_FOLDER)
        except FileExistsError:
            print(f"Folder \"{SNAP_FOLDER}\" already exists. Ignoring.")
        if os.path.isdir(SNAP_FOLDER):
            for file_name in os.listdir(SNAP_FOLDER):
                file = os.path.join(SNAP_FOLDER, file_name)
                os.remove(file)
        # Defining sprite groups
        self.balls = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        # Defining sprites
        self.player = Player(self, *PLAYER_SETTINGS) # Player
        self.ball = Ball(self, *BALL_SETTINGS) # Ball  
        self.bot = Bot(self, *BOT_SETTINGS) # Bot
        self.net = Obstacle(self, *NET_SETTINGS) # Net
        self.moving_platform = Obstacle(self, *MOVING_PLATFORM_SETTINGS) # Moving platform
        # Adding to sprite groups
        # self.balls.add(self.player, self.ball, self.bot)
        self.balls.add(self.ball, self.bot)
        self.obstacles.add(self.net)
    
    def run(self):
        # Game loop
        self.playing = True
        ball_init = cycle([BOT_INIT_X, PLAYER_INIT_X])
        while self.playing: 
            self.n_frame += 1
            self.clock.tick(FPS)
            self.events()
            self.update(ball_init) 
            self.display()
    
    def update(self, ball_init):
        # Game loop update
        if self.start_round:
            self.balls.update()
            self.obstacles.update()
            for sprite in self.balls.sprites():
                if sprite.end_round_conditions():
                    self.start_round = False
                    self.initialize_round(next(ball_init))
                    return None
                    
    def events(self):
        # Game loop - events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    if self.start_round:
                        self.player.jump()
                    else:
                        self.start_round = True
                elif event.key == pg.K_q:
                    if self.playing:
                        self.playing = False
                    self.running = False

    def initialize_round(self, ball_init_x):
        """
        TODO
        """
        # Player
        self.player.pos.x = PLAYER_INIT_X
        self.player.pos.y = PLAYER_INIT_Y
        self.player.vel = vec(0, 0)
        # Bot
        self.bot.pos.x = BOT_INIT_X
        self.bot.pos.y = BOT_INIT_Y
        self.bot.vel = vec(0, 0)
        self.bot.ball_x = None
        self.bot.direction = 0
        # Ball game
        self.ball.pos.x = ball_init_x
        self.ball.pos.y = BALL_INIT_Y
        self.ball.vel = vec(BALL_INIT_VEL_X, BALL_INIT_VEL_Y)
        self.ball.trajectory.clear()
        self.ball.drop()
                             
    def display(self):
        """
        TODO
        """
        self.screen.fill(BACKGROUND)
        self.obstacles.draw(self.screen)
        if not self.start_round:
            self.display_message(self.screen, *START_ROUND_SETTINGS)
        self.display_infos()
        # pg.draw.circle(self.screen, self.player.color, self.player.pos, self.player.r)
        pg.draw.circle(self.screen, self.ball.color, self.ball.pos, self.ball.r)
        pg.draw.circle(self.screen, self.bot.color, self.bot.pos, self.bot.r)  
        for pos in self.ball.trajectory[::7]:
            pg.draw.circle(self.screen, GREEN3, pos, 2)
        pg.display.flip()  

    def display_infos(self): 
        """
        TODO
        """
        # FPS (top-right)
        n_fps = int(self.clock.get_fps())
        font_FPS = pg.font.SysFont("Calibri", 30)
        fps_text = font_FPS.render(f"FPS: {n_fps}", True, WHITE)
        fps_text_rect = fps_text.get_rect()
        fps_text_rect.centerx = 60
        fps_text_rect.top = 5
        # Current score (top-center)
        score_player, score_bot = self.scores["Player"], self.scores["Bot"]
        font_scores = pg.font.SysFont("Calibri", 50)
        scores_text = font_scores.render(
            f"{score_player}   -   {score_bot}", 
            True, 
            WHITE)
        scores_text_rect = fps_text.get_rect()
        scores_text_rect.centerx = WIDTH * 0.5
        scores_text_rect.top = 5 
        # Drawing to screen
        self.screen.blit(fps_text, fps_text_rect)
        self.screen.blit(scores_text, scores_text_rect)

    @staticmethod
    def display_message(screen, message, font_size, color, position):
        """
        TODO
        """ 
        font = pg.font.SysFont("Calibri", font_size)
        text = font.render(message, True, color)
        text_rect = text.get_rect()
        text_rect.centerx, text_rect.top = position
        screen.blit(text, text_rect)

    def save_results(self, extension="png") -> None:
        file_name = f"snapshot_{self.n_frame}.{extension}"
        pg.image.save(self.screen, os.path.join(SNAP_FOLDER, file_name))


def main():
    g = Game()
    while g.running:
        g.new()
        g.run()
    pg.quit()

if __name__ == "__main__":
    main()