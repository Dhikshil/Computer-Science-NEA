import pygame
import constants
import math
from character import Character

class Friendly(Character):
    def __init__(self, animations, spawn_pos):#
        # hitbox and position
        hitbox_height = constants.TILE_SIZE // constants.TILE_SCALE
        hitbox_width = constants.TILE_SIZE // constants.TILE_SCALE
        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.rect.midbottom = spawn_pos
        
        # image control
        self.animations = animations
        self.action = 0  # 0 idle
        self.in_range = False
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        self.image_rect = self.image.get_rect(midbottom = self.rect.midbottom)
        
        # direction
        self.flip = False
        self.update_time = pygame.time.get_ticks()

        # AI tuning variables
        self.detection_range = 40

        self.dialogue = "Hello, Traveller"

        self.health = 10000

    def updateAi(self, player, surface):
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = math.hypot(dx, dy)

        if distance <= self.detection_range:
            self.draw_dialogue_box(surface, self.dialogue)

        self.update()

    def draw_dialogue_box(self, surface, dialogue):
        box_rect = pygame.Rect(50, constants.WINDOW_SIZE[1] - 150,
                           constants.WINDOW_SIZE[0] - 100, 100)

        pygame.draw.rect(surface, (0, 0, 0), box_rect)
        pygame.draw.rect(surface, (255, 255, 255), box_rect, 3)

        font = pygame.font.SysFont("arial", 22)
        rendered = font.render(dialogue, True, (255, 255, 255))
        surface.blit(rendered, (box_rect.x + 20, box_rect.y + 20))