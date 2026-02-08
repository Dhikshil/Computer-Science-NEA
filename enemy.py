import pygame
import constants
import math
import random
from character import Character
from combat import CombatSystem

combat = CombatSystem()

class Enemy(Character):
    def __init__(self, animations, spawn_pos):
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

        self.damage = 10
        self.attack_cooldown = 1200
        self.attack_cooldown_ticks = pygame.time.get_ticks()
        self.health = 40
        
        # Hit animation control
        self.is_hit = False
        self.hit_animation_finished = False
        self.coin_drop_min = 3
        self.coin_drop_max = 8

    def update_action(self):
        # Don't change action if currently playing hit animation
        if self.is_hit and not self.hit_animation_finished:
            return
            
        # update action
        if self.vel_x != 0:
            self.action = 2  # running
        else:
            self.action = 0  # idle

    def get_coin_drops(self):
        return random.randint(self.coin_drop_min, self.coin_drop_max)

    def updateAi(self, obstacles, player, damage_number_manager=None):
        # Don't move or attack while playing hit animation
        if self.is_hit and not self.hit_animation_finished:
            self.move(obstacles)
            self.update()
            return
        
        self.vel_x = 0
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = math.hypot(dx, dy)

        if distance <= self.detection_range and distance > self.attack_range:
            self.action = 2  # run

            if dx > 5:
                self.vel_x = -constants.PLAYER_SPEED * 0.6
            elif dx < -5:
                self.vel_x = constants.PLAYER_SPEED * 0.6

            if constants.TILE_SIZE <= dy <= constants.TILE_SIZE * 2:
                self.jump() 

        elif distance <= self.attack_range:
            if combat.can_attack(self, self.attack_cooldown):
                damage, is_critical = combat.apply_damage(self, player)
                
                # Spawn damage number at player position
                if damage_number_manager:
                    damage_number_manager.add_damage_number(
                        player.rect.centerx,
                        player.rect.top - 10,  # Slightly above player
                        damage,
                        is_critical
                    )
                
                print(f"Player hit for {damage} damage! Player health: {player.health}")

        else:
            self.action = 0  # idle
        
        self.move(obstacles)
        self.update()