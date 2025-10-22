import pygame
import constants
import math

class Character(pygame.sprite.Sprite): 
    def __init__(self, animations):
        super().__init__()
        self.animations = animations
        self.action = 0 #0 idle, 1 hit, 2 run, 3 roll
        self.frame_index = 0
        self.image = self.animations[self.action][self.frame_index]
        hitbox_height = 16
        hitbox_width = 16
        self.rect = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.rect.midbottom = (400, 300)
        self.image_rect = self.image.get_rect(midbottom=self.rect.midbottom)
        
        self.update_time = pygame.time.get_ticks()
        self.flip = False

        #physics
        self.vel_x = 0
        self.vel_y = 0
        self.jumping = False

        self.inventory = ["", "", ""] 
        self.inventory_pointer = 0

    def move(self, obstacles):  
        # Apply gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10

        # update action
        if self.vel_x != 0:
            self.action = 2  # running
        else:
            self.action = 0  # idle

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
        animation_cooldown = 120

        #handle animation
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        #check if animation finished
        if self.frame_index >= len(self.animations[self.action]):
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

        line_of_sight = ((self.rect.centerx, self.rect.centery) + (tile_world_x, tile_world_y))

        for obstacle in obstacles:
            if obstacle.clipline(line_of_sight):
                collisions += 1

        # Calculate distance between player center and tile center
        return math.sqrt((self.rect.centerx - tile_world_x) ** 2 + (self.rect.centery - tile_world_y) ** 2) <= constants.PLAYER_HIT_RANGE and collisions <= 1

    def draw_at_position(self, surface, position):
        # Calculate where to draw the image based on the collision rect position
        image_pos = (position[0] + (self.rect.width - self.image.get_width()) // 2, position[1] + self.rect.height - self.image.get_height())
        surface.blit(self.image, image_pos)