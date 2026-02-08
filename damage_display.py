import pygame
import random

class DamageNumber:
    def __init__(self, x, y, damage, is_critical=False):
        self.x = x
        self.y = y
        self.damage = int(damage)
        self.is_critical = is_critical
        
        # Visual properties
        self.alpha = 255  # Opacity
        self.lifetime = 60  # Frames to live (1 second at 60 FPS)
        self.age = 0
        
        # Movement properties
        self.vel_y = -2  # Float upward
        self.vel_x = random.uniform(-0.5, 0.5)  # Slight random horizontal drift
        
        # Font and color
        if is_critical:
            self.font = pygame.font.SysFont("arial", 32, bold=True)
            self.color = (155, 50, 50)  # Bright red for crits
        else:
            self.font = pygame.font.SysFont("arial", 24, bold=True)
            self.color = (255, 50, 50)  # Yellow-orange for normal damage
        
        # Create the text surface
        self.text = self.font.render(str(self.damage), True, self.color)
        
    def update(self):
        self.age += 1
        
        # Move upward and drift
        self.y += self.vel_y
        self.x += self.vel_x
        
        # Slow down over time
        self.vel_y *= 0.95
        
        # Fade out in the last third of lifetime
        fade_start = self.lifetime * 0.66
        if self.age > fade_start:
            fade_progress = (self.age - fade_start) / (self.lifetime - fade_start)
            self.alpha = int(255 * (1 - fade_progress))
        
        return self.age < self.lifetime  # Return False when dead
    
    def draw(self, surface, camera_x, camera_y):
        # Create a copy of the text with alpha
        text_surface = self.text.copy()
        text_surface.set_alpha(self.alpha)
        
        # Calculate screen position
        screen_x = self.x - camera_x - text_surface.get_width() // 2
        screen_y = self.y - camera_y
        
        # Draw outline for better visibility
        outline_color = (0, 0, 0)
        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                if offset_x != 0 or offset_y != 0:
                    outline_text = self.font.render(str(self.damage), True, outline_color)
                    outline_text.set_alpha(self.alpha)
                    surface.blit(outline_text, (screen_x + offset_x, screen_y + offset_y))
        
        # Draw main text
        surface.blit(text_surface, (screen_x, screen_y))


class DamageNumberManager:
    def __init__(self):
        self.damage_numbers = []
    
    def add_damage_number(self, x, y, damage, is_critical=False):
        damage_number = DamageNumber(x, y, damage, is_critical)
        self.damage_numbers.append(damage_number)
    
    def update(self):
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.update()]
    
    def draw(self, surface, camera_x, camera_y):
        for damage_number in self.damage_numbers:
            damage_number.draw(surface, camera_x, camera_y)
    
    def clear(self):
        self.damage_numbers.clear()