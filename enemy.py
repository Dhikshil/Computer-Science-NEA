import pygame
import constants
import math
from character import Character

class Enemy(Character):
    def __init__(self, animations, spawn_pos):#
        # hitbox and position
        hitbox_height = constants.TILE_SIZE // constants.TILE_SCALE
        hitbox_width = constants.TILE_SIZE // constants.TILE_SCALE
        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.rect.midbottom = spawn_pos
        
        # image control
        self.animations = animations
        self.action = 0  # 0 idle, 1 hit, 2 run
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        self.image_rect = self.image.get_rect(midbottom = self.rect.midbottom)
        
        # direction
        self.flip = False
        self.update_time = pygame.time.get_ticks()

        # AI tuning variables
        self.detection_range = 300
        self.attack_range = 40
        self.vel_x = 0
        self.vel_y = 0
        self.jumping = False
        self.ai_controlled = True

    def update_action(self):
        # update action
        if self.vel_x != 0:
            self.action = 2  # running
        else:
            self.action = 0  # idle

    def updateAi(self, obstacles, player):
        self.vel_x = 0
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = math.hypot(dx, dy)

        if distance <= self.detection_range:
            self.action = 2  # run

            if dx > 5:
                self.vel_x = -constants.PLAYER_SPEED * 0.6
            elif dx < -5:
                self.vel_x = constants.PLAYER_SPEED * 0.6

            if constants.TILE_SIZE <= dy <= constants.TILE_SIZE * 2:
                self.jump()
        else:
            self.action = 0  # idle

        
        self.move(obstacles)
        self.update()
