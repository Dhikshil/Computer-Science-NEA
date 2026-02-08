import pygame
import constants
import math
import random

class Character(pygame.sprite.Sprite): 
    def __init__(self, animations):
        super().__init__()
        self.animations = animations
        self.action = 0 #0 idle, 1 hit, 2 run, 3 roll
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        hitbox_height = constants.TILE_SIZE // constants.TILE_SCALE 
        hitbox_width = constants.TILE_SIZE // constants.TILE_SCALE
        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.rect.midbottom = (400, 300)
        self.image_rect = self.image.get_rect(midbottom=self.rect.midbottom)
        
        self.update_time = pygame.time.get_ticks()
        self.flip = False

        #physics
        self.vel_x = 0
        self.vel_y = 0
        self.jumping = False

        self.hotbar = []
        self.hotbar_pointer = 0

        self.ai_controlled = False

        self.health = 100
        self.damage = 20
        self.cooldown = 200
        
        # Hit animation control
        self.is_hit = False
        self.hit_animation_finished = False

    def update_action(self):
        # Don't change action if currently playing hit animation
        if self.is_hit and not self.hit_animation_finished:
            return
            
        # update action
        if self.vel_x != 0:
            self.action = 2  # running
        else:
            self.action = 0  # idle

    def take_damage(self, damage):
        """Called when character takes damage - triggers hit animation"""
        self.health -= damage
        self.is_hit = True
        self.hit_animation_finished = False
        self.action = 1  # Hit animation
        self.frame_index = 0  # Reset to first frame of hit animation

    def move(self, obstacles):  
        # Apply gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10

        if not self.ai_controlled:
            self.update_action()

        # Check and control player direction
        if self.vel_x < 0:
            self.flip = True
        elif self.vel_x > 0:
            self.flip = False

        # Horizontal movement
        self.rect.x += self.vel_x
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if self.vel_x > 0:  # moving right
                    self.rect.right = obstacle.left
                elif self.vel_x < 0:  # moving left
                    self.rect.left = obstacle.right

        # Vertical movement
        self.rect.y += self.vel_y
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if self.vel_y > 0:  # falling down
                    self.rect.bottom = obstacle.top
                    self.vel_y = 0
                    self.jumping = False
                elif self.vel_y < 0:  # jumping up
                    self.rect.top = obstacle.bottom
                    self.vel_y = 0

    def jump(self):
        if not self.jumping:  #can only jump if on ground
            self.vel_y = -15
            self.jumping = True

    def update(self):
        # Different animation speeds for different actions
        if self.action == 1:  # Hit animation
            animation_cooldown = 80  # Faster for hit
        else:
            animation_cooldown = 120  # Normal speed

        #handle animation
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        #check if animation finished
        if self.frame_index >= len(self.animations[self.action]):
            # If hit animation just finished
            if self.action == 1:
                self.is_hit = False
                self.hit_animation_finished = True
                self.action = 0  # Return to idle
            
            self.frame_index = 0

        #update image
        self.image = self.animations[self.action][self.frame_index]

        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

        #update image_rect to draw relative to rect (collision box)
        self.image_rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def is_tile_in_range(self, tile_x, tile_y, obstacles, collisions):

        tile_world_x = tile_x * constants.TILE_SIZE + constants.TILE_SIZE // 2
        tile_world_y = tile_y * constants.TILE_SIZE + constants.TILE_SIZE // 2

        line_of_sight = ((self.rect.centerx, self.rect.centery), (tile_world_x, tile_world_y))

        for obstacle in obstacles:
            if obstacle.clipline(line_of_sight):
                collisions += 1

        # Calculate distance between player center and tile center
        return math.sqrt((self.rect.centerx - tile_world_x) ** 2 + (self.rect.centery - tile_world_y) ** 2) <= constants.PLAYER_HIT_RANGE and collisions <= 1
    
    def damage_calculator(self, weapon):
        damage = self.damage * random.uniform(0.9,1.1)
        if weapon == None:
            return damage
        else:
            return (damage + weapon.damage) * random.uniform(1.0, 1.2)


    def draw_at_position(self, surface, position):
        # Calculate where to draw the image based on the collision rect position
        image_pos = (position[0] + (self.rect.width - self.image.get_width()) // 2, position[1] + self.rect.height - self.image.get_height())
        surface.blit(self.image, image_pos)