import pygame
import os

HAMMER_IMG = os.path.join("data", "hammer.png")

class GameCursor():
    def __init__(self):
        self.sprite = None
        self.should_be_destroyed = False
        pass
    
    def on_loop(self, frametime):
        pass

    def on_render(self, display_surf):
        cursor_surf = pg.Surface(64, 64)
        surf.blit(self._sprite, (0, 0), self._sprite_rect)
        hammer_cursor = pg.cursors.Cursor((64, 64), cursor_surf)

        pygame.cursor.set_cursor(hammer_cursor)
        pass
    
    def on_event(self, event):
        pass

class HammerCursor(GameCursor):
    def __init__(self):
        super().__init__()
        self.IDLE = 0
        self.HITTING = 1

        self._status = self.IDLE

        self._anim_frame = 0
        self._default_anim_timer = 0.02083333
        self._anim_timer = self._default_anim_timer
        self._sprite_rect = pygame.Rect(0, 0, 64, 64)

        self.sprite = pygame.image.load(HAMMER_IMG)

    def _animate(self, frametime):
        self._anim_timer = self._anim_timer - frametime
        if self._status == self.HITTING:
            new_cords = self._anim_frame * 64
            self._sprite_rect = pygame.Rect(new_cords, 0, 64, 64)
            self._anim_timer = self._default_anim_timer
            self._anim_frame = (self._anim_frame + 1) % 8
        else:
            self._anim_frame = 0

    def on_loop(self, frametime):
        super().on_loop()
        _animate(frametime)
        if self._anim_frame >= 7:
            self.should_be_destroyed = True

            event = pygame.event.Event
            event.type = COLLIDER_EVENT
            event.__dict__["data1"] = self._position

            pygame.event.post(event)
            self._status = self.IDLE

    def on_render(self, display_surf):
        super().on_render(display_surf)
        pass

    def on_event(self, event):
        super().on_event(event)
        pass
