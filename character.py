import pygame
import constants
import math
import random
from items import get_item_info, ITEMS

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

        self.ai_controlled = False

        self.health = 100
        self.max_health = 100
        self.damage = 20
        self.cooldown = 200
        
        # Hit animation control
        self.is_hit = False
        self.hit_animation_finished = False
        
        # Inventory system
        self.inventory = {}  # {item_id: quantity}
        self.hotbar_slots = 9  # Number of hotbar slots
        self.hotbar = [None] * self.hotbar_slots  # [item_id or None, ...]
        self.selected_hotbar_slot = 0  # Currently selected slot (0-8)
        
    def add_item(self, item_id, quantity=1):
        item_info = get_item_info(item_id)
        if not item_info:
            print(f"Unknown item: {item_id}")
            return False
        
        max_stack = item_info["max_stack"]
        
        # Add to existing stack or create new entry
        if item_id in self.inventory:
            self.inventory[item_id] += quantity
        else:
            self.inventory[item_id] = quantity
            
        # Auto-add to hotbar if there's space and item not already in hotbar
        if item_id not in self.hotbar:
            for i in range(self.hotbar_slots):
                if self.hotbar[i] is None:
                    self.hotbar[i] = item_id
                    break
        
        return True
    
    def remove_item(self, item_id, quantity=1):
        if item_id not in self.inventory:
            return False
        
        if self.inventory[item_id] < quantity:
            return False
        
        self.inventory[item_id] -= quantity
        
        # Remove from inventory if quantity reaches 0
        if self.inventory[item_id] <= 0:
            del self.inventory[item_id]
            
            # Remove from hotbar if item is gone
            for i in range(self.hotbar_slots):
                if self.hotbar[i] == item_id:
                    self.hotbar[i] = None
        
        return True
    
    def get_item_count(self, item_id):
        return self.inventory.get(item_id, 0)
    
    def has_item(self, item_id, quantity=1):
        return self.get_item_count(item_id) >= quantity
    
    def use_item(self, item_id):
        if item_id not in self.inventory:
            return False
        
        item_info = get_item_info(item_id)
        if not item_info:
            return False
        
        # Handle consumables
        if item_info["type"] == "consumable":
            if "heal_amount" in item_info:
                self.health = min(self.max_health, self.health + item_info["heal_amount"])
                self.remove_item(item_id, 1)
                print(f"Used {item_info['name']}, healed {item_info['heal_amount']} HP")
                return True
        
        # Handle weapons (for future implementation)
        elif item_info["type"] == "weapon":
            # Could equip weapon here
            print(f"Equipped {item_info['name']}")
            return True
        
        return False
    
    def get_selected_item(self):
        selected_item_id = self.hotbar[self.selected_hotbar_slot]
        if selected_item_id and selected_item_id in self.inventory:
            return selected_item_id
        return None
    
    def cycle_hotbar(self, direction):
        self.selected_hotbar_slot = (self.selected_hotbar_slot + direction) % self.hotbar_slots
    
    def get_inventory_data(self):
        return {
            "inventory": self.inventory.copy(),
            "hotbar": self.hotbar.copy(),
            "selected_slot": self.selected_hotbar_slot
        }
    
    def load_inventory_data(self, inventory_data):
        self.inventory = inventory_data.get("inventory", {})
        self.hotbar = inventory_data.get("hotbar", [None] * self.hotbar_slots)
        self.selected_hotbar_slot = inventory_data.get("selected_slot", 0)

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
            return (damage + weapon["damage"]) * random.uniform(1.0, 1.2)

    def draw_at_position(self, surface, position):
        # Calculate where to draw the image based on the collision rect position
        image_pos = (position[0] + (self.rect.width - self.image.get_width()) // 2, position[1] + self.rect.height - self.image.get_height())
        surface.blit(self.image, image_pos)