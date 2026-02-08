import pygame
from items import get_item_info

class InventoryUI:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 16, bold=True)
        self.font_small = pygame.font.SysFont("arial", 12)
        
        # Hotbar settings
        self.slot_size = 50
        self.slot_padding = 5
        self.hotbar_y_offset = 20  # Distance from bottom of screen
        
    def draw_hotbar(self, surface, player, screen_width, screen_height):
        # Calculate hotbar position (centered at bottom)
        total_width = (self.slot_size + self.slot_padding) * player.hotbar_slots - self.slot_padding
        start_x = (screen_width - total_width) // 2
        start_y = screen_height - self.slot_size - self.hotbar_y_offset
        
        # Draw each hotbar slot
        for i in range(player.hotbar_slots):
            x = start_x + i * (self.slot_size + self.slot_padding)
            y = start_y
            
            # Determine slot color
            if i == player.selected_hotbar_slot:
                color = (100, 150, 255)  # Highlighted blue
                border_width = 4
            else:
                color = (60, 60, 60)  # Dark gray
                border_width = 2
            
            # Draw slot background
            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            pygame.draw.rect(surface, color, slot_rect)
            pygame.draw.rect(surface, (255, 255, 255), slot_rect, border_width)
            
            # Draw item if slot has one
            item_id = player.hotbar[i]
            if item_id and item_id in player.inventory:
                item_info = get_item_info(item_id)
                quantity = player.get_item_count(item_id)
                
                # Draw item name (abbreviated)
                name_text = self.font_small.render(item_info["name"][:8], True, (255, 255, 255))
                text_rect = name_text.get_rect(center=(x + self.slot_size // 2, y + 15))
                surface.blit(name_text, text_rect)
                
                # Draw quantity
                qty_text = self.font.render(str(quantity), True, (255, 255, 255))
                qty_rect = qty_text.get_rect(bottomright=(x + self.slot_size - 5, y + self.slot_size - 5))
                
                # Draw shadow for quantity
                shadow_text = self.font.render(str(quantity), True, (0, 0, 0))
                surface.blit(shadow_text, (qty_rect.x + 1, qty_rect.y + 1))
                surface.blit(qty_text, qty_rect)
            
            # Draw slot number
            num_text = self.font_small.render(str(i + 1), True, (200, 200, 200))
            num_rect = num_text.get_rect(topleft=(x + 3, y + 3))
            surface.blit(num_text, num_rect)
    
    def draw_full_inventory(self, surface, player, screen_width, screen_height):
        # Semi-transparent background
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        surface.blit(overlay, (0, 0))
        
        # Inventory panel
        panel_width = 600
        panel_height = 500
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, (40, 40, 50), panel_rect)
        pygame.draw.rect(surface, (255, 255, 255), panel_rect, 3)
        
        # Title
        title_font = pygame.font.SysFont("arial", 32, bold=True)
        title_text = title_font.render("INVENTORY", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width // 2, panel_y + 30))
        surface.blit(title_text, title_rect)
        
        # List all items in inventory
        y_offset = panel_y + 80
        item_height = 40
        
        for idx, (item_id, quantity) in enumerate(player.inventory.items()):
            item_info = get_item_info(item_id)
            
            # Item background
            item_rect = pygame.Rect(panel_x + 20, y_offset, panel_width - 40, item_height)
            pygame.draw.rect(surface, (60, 60, 70), item_rect)
            pygame.draw.rect(surface, (100, 100, 120), item_rect, 2)
            
            # Item name
            name_text = self.font.render(f"{item_info['name']}", True, (255, 255, 255))
            surface.blit(name_text, (panel_x + 30, y_offset + 5))
            
            # Item description
            desc_text = self.font_small.render(item_info['description'], True, (180, 180, 180))
            surface.blit(desc_text, (panel_x + 30, y_offset + 22))
            
            # Quantity
            qty_text = self.font.render(f"x{quantity}", True, (100, 255, 100))
            qty_rect = qty_text.get_rect(right=panel_x + panel_width - 30, centery=y_offset + item_height // 2)
            surface.blit(qty_text, qty_rect)
            
            y_offset += item_height + 5
            
            # Stop if we run out of space
            if y_offset > panel_y + panel_height - 60:
                break
        
        # Instructions
        instructions = "Press TAB to close | Use number keys 1-9 to select hotbar"
        inst_text = self.font_small.render(instructions, True, (200, 200, 200))
        inst_rect = inst_text.get_rect(center=(screen_width // 2, panel_y + panel_height - 20))
        surface.blit(inst_text, inst_rect)