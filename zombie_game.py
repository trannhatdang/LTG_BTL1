import pygame
import time
import os
import random
import gamecursor
from pygame.locals import *

ZOMBIE_PATH = os.path.join("data", "zombie")
FONT_PATH = os.path.join("data", "font")
ZOMBIE_SPAWN_IMG = os.path.join(ZOMBIE_PATH, "zombie_spawn.png")
ZOMBIE_IDLE_IMG = os.path.join(ZOMBIE_PATH, "zombie_idle.png")
ZOMBIE_DEATH_IMG = os.path.join(ZOMBIE_PATH, "zombie_death.png")
ZOMBIE_HIDE_IMG = os.path.join(ZOMBIE_PATH, "zombie_hide.png")
BACKGROUND_IMG = os.path.join("data", "background.png")
VCR_OSD_MONO_FONT = os.path.join(FONT_PATH, "VCR_OSD_MONO.ttf")
SPAWN_TIME = 1
SPAWN_LOCATIONS = [(310, 120), (760, 120), (1210, 120),
                   (310, 390), (760, 390), (1210, 390),
                   (310, 660), (760, 660), (1210, 660)]
COLLIDER_EVENT = pygame.event.custom_type()
DEFAULT_COLLIDER_OFFSET = (10, 10)

class Zombie:
    def __init__(self, position):
        self.SPAWN = 0
        self.IDLE = 1
        self.DEATH = 2
        self.HIDE = 3

        self.SPAWN_SPRITE = pygame.image.load(ZOMBIE_SPAWN_IMG)
        self.IDLE_SPRITE = pygame.image.load(ZOMBIE_IDLE_IMG)
        self.DEATH_SPRITE = pygame.image.load(ZOMBIE_DEATH_IMG)
        self.HIDE_SPRITE = pygame.image.load(ZOMBIE_HIDE_IMG)

        self._alive_time = 5

        self._anim_frame = 0
        self._default_anim_timer = 0.0833 #12 fps
        self._anim_timer = self._default_anim_timer 
        self._sprite_rect = pygame.Rect(0, 0, 64, 64)

        self._is_bonkable = False
        self._collider_offset = DEFAULT_COLLIDER_OFFSET

        self.should_be_destroyed = False
        self.status = self.SPAWN
        self.position = position

    def _animate(self, frametime):
        self._anim_timer = self._anim_timer - frametime
        if self._anim_timer <= 0:
            new_cords = self._anim_frame * 64
            self._sprite_rect = pygame.Rect(new_cords, 0, 64, 64)
            self._anim_timer = self._default_anim_timer
            self._anim_frame = (self._anim_frame + 1) % 8

    def on_loop(self, frametime):
        self._animate(frametime)
        if (self.status == self.DEATH or self.status == self.HIDE) and self._anim_frame >= 7:
            self.should_be_destroyed = True
        elif self.status == self.SPAWN and self._anim_frame >= 7:
            self.status = self.IDLE
            self._is_bonkable = True

        self._alive_time = self._alive_time - frametime
        if self._alive_time <= 0:
            self.status = self.HIDE

    def on_render(self, display_surf):
        if self.status == self.SPAWN:
            display_surf.blit(self.SPAWN_SPRITE, self.position, self._sprite_rect)
        elif self.status == self.IDLE:
            display_surf.blit(self.IDLE_SPRITE, self.position, self._sprite_rect)
        elif self.status == self.HIDE:
            display_surf.blit(self.HIDE_SPRITE, self.position, self._sprite_rect)
        else:
            display_surf.blit(self.DEATH_SPRITE, self.position, self._sprite_rect)

    def on_event(self, event):
        if not self.status == self.IDLE:
            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if not self._is_bonkable:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        min_width = self.position[0]
        max_width = self.position[0] + 64 + self._collider_offset[0]
        min_height = self.position[1]
        max_height = self.position[1] + 64 + self._collider_offset[1]
        #print(mouse_x, mouse_y)
        #print(min_width, max_width, min_height, max_height)

        if mouse_x >= min_width and mouse_x <= max_width and mouse_y >= min_height and mouse_y <= max_height:
            self.status = self.DEATH
            self._anim_frame = 0
            self._is_bonkable = True
 
class App():
    def __init__(self):
        self._display_surf = None
        self._alive_zombies = []

        self._free_spawn_locations = SPAWN_LOCATIONS
        self._occupied_spawn_locations = []

        self._background_sprite = pygame.image.load(BACKGROUND_IMG)
        self._font = None

        self._spawn_timer = SPAWN_TIME
        self._frametime = 0

        self._points = 0
        self._misses = 0
        self._hitrate = 0

        self.size = self.weight, self.height = 1584, 887
        random.seed(time.time())

    def get_random_spawn_location(self):
        if(len(self._free_spawn_locations) == 0):
            return (0, 0)

        retval = self._free_spawn_locations[random.randrange(0, len(self._free_spawn_locations))]

        return retval

    def on_init(self):
        pygame.init()
        pygame.font.init()
        self._font = pygame.font.Font(VCR_OSD_MONO_FONT, 32)
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
 
    def on_loop(self):
        for zombie in self._alive_zombies:
            zombie.on_loop(self._frametime)

            if zombie.should_be_destroyed:
                location = zombie.position
                self._free_spawn_locations.append(location)
                self._occupied_spawn_locations.remove(location)
                self._alive_zombies.remove(zombie)

                if zombie.status == zombie.DEATH:
                    self._points = self._points + 1
                else:
                    self._misses = self._misses + 1

                if(self._points + self._misses != 0):
                    self._hitrate = self._points / (self._points + self._misses)
                else:
                    self._hitrate = 0


        self._spawn_timer = self._spawn_timer - self._frametime
        if self._spawn_timer <= 0 and len(self._free_spawn_locations) > 0:
            spawn_location = self.get_random_spawn_location()
            self._occupied_spawn_locations.append(spawn_location)
            self._free_spawn_locations.remove(spawn_location)

            self._alive_zombies.append(Zombie(spawn_location))
            self._spawn_timer = SPAWN_TIME

    def on_render(self):
        self._display_surf.blit(self._background_sprite, self._background_sprite.get_rect())
        for zombie in self._alive_zombies:
            zombie.on_render(self._display_surf)

        points_surf = self._font.render("POINTS: " + str(self._points), False, (0, 0, 0))
        misses_surf = self._font.render("MISSES: " + str(self._misses), False, (0, 0, 0))
        hitrate_surf = self._font.render("HIT RATE: " + str(self._hitrate), False, (0, 0, 0))

        self._display_surf.blit(points_surf, (10, 50))
        self._display_surf.blit(misses_surf, (10, 75))
        self._display_surf.blit(hitrate_surf, (10, 100))

        pygame.display.flip()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        for zombie in self._alive_zombies:
            zombie.on_event(event)

    def on_cleanup(self):
        pygame.font.quit()
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            start_time = time.time()

            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

            self._frametime = time.time() - start_time
        self.on_cleanup()
 
if __name__ == "__main__" :
    game = App()
    game.on_execute()
