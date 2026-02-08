import pygame
import constants
import math
from character import Character
from items import get_item_info, get_shop_inventory

class Friendly(Character):
    def __init__(self, animations, spawn_pos, shop_type="general_store"):
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
        
        # Shop variables
        self.shop_type = shop_type
        self.shop_open = False
        self.selected_item_index = 0
        
        # Shop type to dialogue and name mapping
        shop_info = {
            "general_store": ("General Store", "Welcome! I sell building materials."),
            "weapon_shop": ("Weapon Shop", "Need weapons? I've got the best!"),
            "mixed_shop": ("Trading Post", "I sell a bit of everything!")
        }
        
        self.shop_name, self.greeting = shop_info.get(shop_type, ("Shop", "Welcome, traveler!"))
        self.shop_items = get_shop_inventory(shop_type)

        self.health = 10000

    def updateAi(self, player, surface):
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = math.hypot(dx, dy)

        if distance <= self.detection_range:
            self.in_range = True
            if self.shop_open:
                self.draw_shop_dialogue(surface, player)
            else:
                self.draw_greeting_dialogue(surface)
        else:
            self.in_range = False
            self.shop_open = False

        self.update()
    
    def toggle_shop(self):
        """Open or close the shop"""
        if self.in_range:
            self.shop_open = not self.shop_open
            if self.shop_open:
                self.selected_item_index = 0
    
    def navigate_shop(self, direction):
        """Navigate through shop items (direction: 1 for down, -1 for up)"""
        if self.shop_open:
            self.selected_item_index = (self.selected_item_index + direction) % len(self.shop_items)
    
    def buy_selected_item(self, player):
        """Attempt to buy the currently selected item"""
        if not self.shop_open or not self.shop_items:
            return False
        
        item_id, stock_quantity = self.shop_items[self.selected_item_index]
        item_info = get_item_info(item_id)
        price = item_info.get("price", 0)
        player_coins = player.get_item_count("coin")
        
        if player_coins < price:
            print(f"Not enough coins! Need {price}, have {player_coins}")
            return False
        
        # Remove coins
        if player.remove_item("coin", price):
            # Add item
            player.add_item(item_id, 1)
            print(f"Purchased {item_info['name']} for {price} coins!")
            return True
        
        return False

    def draw_greeting_dialogue(self, surface):
        """Draw the initial greeting dialogue"""
        box_rect = pygame.Rect(50, constants.WINDOW_SIZE[1] - 150,
                           constants.WINDOW_SIZE[0] - 100, 100)

        pygame.draw.rect(surface, (0, 0, 0), box_rect)
        pygame.draw.rect(surface, (255, 255, 255), box_rect, 3)

        # Shop name
        font_title = pygame.font.SysFont("arial", 24, bold=True)
        title = font_title.render(self.shop_name, True, (255, 215, 0))
        surface.blit(title, (box_rect.x + 20, box_rect.y + 15))
        
        # Greeting
        font = pygame.font.SysFont("arial", 18)
        greeting = font.render(self.greeting, True, (255, 255, 255))
        surface.blit(greeting, (box_rect.x + 20, box_rect.y + 45))
        
        # Instruction
        instruction_font = pygame.font.SysFont("arial", 16)
        instruction = instruction_font.render("Press F to browse shop", True, (200, 200, 200))
        surface.blit(instruction, (box_rect.x + 20, box_rect.y + 70))
    
    def draw_shop_dialogue(self, surface, player):
        """Draw the shop dialogue with items"""
        box_rect = pygame.Rect(50, constants.WINDOW_SIZE[1] - 200,
                           constants.WINDOW_SIZE[0] - 100, 180)

        pygame.draw.rect(surface, (0, 0, 0), box_rect)
        pygame.draw.rect(surface, (255, 215, 0), box_rect, 4)

        font_title = pygame.font.SysFont("arial", 20, bold=True)
        font = pygame.font.SysFont("arial", 16)
        font_small = pygame.font.SysFont("arial", 14)
        
        # Shop name and player coins
        title = font_title.render(f"{self.shop_name}", True, (255, 215, 0))
        surface.blit(title, (box_rect.x + 20, box_rect.y + 10))
        
        player_coins = player.get_item_count("coin")
        coins_text = font.render(f"Your Coins: {player_coins}", True, (255, 215, 0))
        coins_rect = coins_text.get_rect(right=box_rect.right - 20, top=box_rect.y + 10)
        surface.blit(coins_text, coins_rect)
        
        # Draw shop items (3 items visible at a time)
        y_offset = box_rect.y + 45
        items_to_show = 3
        start_index = max(0, self.selected_item_index - 1)
        
        for i in range(start_index, min(start_index + items_to_show, len(self.shop_items))):
            item_id, stock_quantity = self.shop_items[i]
            item_info = get_item_info(item_id)
            price = item_info.get("price", 0)
            
            # Highlight selected item
            is_selected = (i == self.selected_item_index)
            
            # Item background
            item_bg_rect = pygame.Rect(box_rect.x + 15, y_offset - 2, box_rect.width - 30, 35)
            if is_selected:
                pygame.draw.rect(surface, (60, 60, 80), item_bg_rect)
                pygame.draw.rect(surface, (255, 215, 0), item_bg_rect, 2)
            
            # Selection arrow
            if is_selected:
                arrow = font.render(">", True, (255, 215, 0))
                surface.blit(arrow, (box_rect.x + 20, y_offset))
            
            # Item name and price
            item_text = f"{item_info['name']} - {price} coins"
            color = (255, 255, 255) if is_selected else (200, 200, 200)
            text = font.render(item_text, True, color)
            surface.blit(text, (box_rect.x + 40, y_offset))
            
            # Can't afford indicator
            if player_coins < price:
                cant_afford = font_small.render("(Can't afford)", True, (255, 100, 100))
                surface.blit(cant_afford, (box_rect.x + 350, y_offset + 2))
            
            # Item description
            if is_selected:
                desc = font_small.render(item_info['description'], True, (180, 180, 180))
                surface.blit(desc, (box_rect.x + 40, y_offset + 18))
            
            y_offset += 40
        
        # Instructions at bottom
        instructions = "UP/DOWN: Navigate | ENTER: Buy | F: Close"
        inst_text = font_small.render(instructions, True, (200, 200, 200))
        inst_rect = inst_text.get_rect(center=(box_rect.centerx, box_rect.bottom - 15))
        surface.blit(inst_text, inst_rect)
        
        # Scroll indicators
        if self.selected_item_index > 0:
            up_arrow = font_small.render("▲ More above", True, (150, 150, 150))
            surface.blit(up_arrow, (box_rect.x + 20, box_rect.y + 35))
        
        if self.selected_item_index < len(self.shop_items) - 1:
            down_arrow = font_small.render("▼ More below", True, (150, 150, 150))
            down_rect = down_arrow.get_rect(right=box_rect.right - 20, top=box_rect.y + 35)
            surface.blit(down_arrow, down_rect)