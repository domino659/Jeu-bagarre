import pygame, sys
from pygame.constants import BLEND_MAX, DROPBEGIN

from pygame.draw import aaline, rect
from pygame.event import wait
from pygame.surfarray import pixels_green 
from settings import *
from sprites import *
from tilemap import *


class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        # Init Audio
        pygame.mixer.init()
        # Init Display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # Init name Window
        pygame.display.set_caption(TITLE)
        # Init game Clock
        self.clock = pygame.time.Clock()
        self.load_data()


    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_text_dialogue(self, text, font_name, size, color, bgcolor, x, y, align="nw"):
            font = pygame.font.Font(font_name, size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            if align == "nw":
                text_rect.topleft = (x, y)
            if align == "center":
                text_rect.center = (x, y)

            # Background
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(10, 10)

            # # Frame
            frame_rect = bg_rect.copy()
            frame_rect.inflate_ip(4, 4)

            # pygame.draw.rect(color, frame_rect)
            pygame.draw.rect(bgcolor, bg_rect)
            self.screen.blit(text_surface, text_rect)

    
    def load_data(self):
        self.player_img = pygame.image.load(PLAYER_IMG)
        self.pnj_img = pygame.image.load(PNJ_IMG)

        self.title_font = FONT

        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pygame.mixer.Sound(EFFECTS_SOUNDS[type])
    
        self.map = TiledMap(MAP)
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()    
    
        # self.map_back = TiledMap(MAP_back)
        # self.map_img_back = self.map_back.make_map()
        # self.map_rect_back = self.map_img_back.get_rect()   

    # Initialize all variable and setup for new game
    def new(self):
        # Initialize Var Sprites
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.pnj = pygame.sprite.Group()
        # #Load Game Sounds
        pygame.mixer.music.load(MUSIC)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer_music.play(loops=-1)
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'pnj':
                Pnj(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            self.draw_debug = False
        # Set Camera
        self.camera = Camera(self.map.width, self.map.height)


    def quit(self):
        pygame.quit()
        sys.exit()


    # Update portion of the game loop
    def update(self):
        self.all_sprites.update()
        # Camera Track Plater
        self.camera.update(self.player)
        # Si je massacre tt les pnj, fun du jeu
        if len(self.pnj) == 0:
            self.playing = False

        # Collision joueur pnj
        hits = pygame.sprite.spritecollide(self.player, self.pnj, False)
        for hit in hits:
            self.draw_text("Im a player", self.title_font, 18, WHITE, self.player.rect.centerx, self.player.rect.y, align="center")
            self.effects_sounds['voice'].play()
            pygame.display.flip()
            

    # Affichage Grid
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))


    def draw(self):
        # DEBUG Dessine Grid
        # self.draw_grid()

        #Map Front
        # self.screen.blit(self.map_img_back, self.camera.apply_rect(self.map_rect_back))
        # Map
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        # Place All_sprites in the camera zone
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pygame.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pygame.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
            pygame.draw.rect(self.screen, WHITE, self.camera.apply(self.player), 2)
        

        # Always Last action after drawing
        pygame.display.flip()


    def run(self):
        # Gamme LOOP
        self.playing = True
        
        while self.playing:
            # Dt -> DetlaTime (allow real time animation)
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()


    def events(self):
        # Catch all actions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                if event.key == pygame.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pygame.K_p:
                    self.playing = False


    def show_start_screen(self):
        pygame.mixer.music.load(MUSICMENU)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer_music.play(loops=-1)
        self.screen.fill(BLACK)
        pygame.time.wait(500)
        self.draw_text("WELCOME TO", self.title_font, 100, WHITE, WIDTH / 2, HEIGHT * 3 / 8, align="center")
        self.draw_text("POITIER 2077", self.title_font, 100, WHITE, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to start", self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        self.draw_text("Debug Collision: H, Game Over: P ", self.title_font, 20, WHITE, WIDTH / 2, HEIGHT * 7 / 8, align="center")
        pygame.display.flip()
        self.wait_for_keys()


    def show_game_over_screen(self):
        pygame.mixer.music.load(MUSICMENU)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer_music.play(loops=-1)
        self.screen.fill(BLACK)
        pygame.time.wait(500)
        self.draw_text("GAME OVER", self.title_font, 100, RED, WIDTH /2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to start", self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pygame.display.flip()
        self.wait_for_keys()


    def wait_for_keys(self):
        pygame.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pygame.KEYUP:
                    waiting = False


# Create the game
game = Game()
game.show_start_screen()
while True:
    game.new()
    game.run()
    game.show_game_over_screen()