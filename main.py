from settings import *
from tetris import Tetris, Text
import sys
import pathlib
import pygame.mixer as mixer
import json

class App:
    def __init__(self):
        pg.init()
        mixer.init()  # Inizializza il mixer
        mixer.music.load('assets/audio/background_music.mp3')  # Carica la musica di sottofondo
        mixer.music.set_volume(0.05)  # Imposta il volume della musica al 10%
        mixer.music.play(-1)  # Riproduce la musica in loop
        pg.display.set_caption('Tetris')
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.set_timer()
        self.images = self.load_images()
        self.tetris = Tetris(self)
        self.text = Text(self)
        self.leaderboard_file = 'leaderboard.json'
        self.leaderboard = self.load_leaderboard()
        self.showing_leaderboard = False  # Per tracciare se la leaderboard è attiva

    def load_images(self):
        files = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        images = [pg.image.load(file).convert_alpha() for file in files]
        images = [pg.transform.scale(image, (TILE_SIZE, TILE_SIZE)) for image in images]
        return images

    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        self.fast_user_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        if not self.showing_leaderboard:  # Aggiorna solo se la leaderboard non è attiva
            self.tetris.update()
        self.clock.tick(FPS)

    def draw(self):
        if self.showing_leaderboard:
            self.draw_leaderboard()
        else:
            self.screen.fill(color=BG_COLOR)
            self.screen.fill(color=FIELD_COLOR, rect=(0, 0, *FIELD_RES))
            self.tetris.draw()
            self.text.draw()
        pg.display.flip()

    def check_events(self):
        self.anim_trigger = False
        self.fast_anim_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_l:  # Mostra o nasconde la leaderboard premendo 'L'
                    self.showing_leaderboard = not self.showing_leaderboard
                elif not self.showing_leaderboard:
                    self.tetris.control(pressed_key=event.key)
            elif event.type == self.user_event and not self.showing_leaderboard:
                self.anim_trigger = True
            elif event.type == self.fast_user_event and not self.showing_leaderboard:
                self.fast_anim_trigger = True

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()

    def load_leaderboard(self):
        try:
            with open(self.leaderboard_file, 'r') as file:
                return json.load(file)['scores']
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_leaderboard(self):
        with open(self.leaderboard_file, 'w') as file:
            json.dump({"scores": self.leaderboard}, file, indent=4)
    
    def update_leaderboard(self, score):
        self.leaderboard.append(score)
        self.leaderboard = sorted(self.leaderboard, reverse=True)[:10]
        self.save_leaderboard()

    def draw_leaderboard(self):
        self.screen.fill(BG_COLOR)
        self.draw_text('Leaderboard', 65, (255, 255, 255), WIN_W // 2, WIN_H // 4)
        for i, score in enumerate(self.leaderboard):
            self.draw_text(f'{i + 1}. {score}', 45, (255, 255, 255), WIN_W // 2, WIN_H // 4 + (i + 1) * 50)

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(FONT_PATH, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

if __name__ == '__main__':
    app = App()
    app.run()  