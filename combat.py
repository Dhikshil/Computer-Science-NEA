import constants
import pygame
import math
import random

class CombatSystem():
    def __init__(self):
        self.attack_cooldowns = {}
        self.crit_chance = 0.15  # 15% chance for critical hit

    def can_attack(self, attacker, cooldown_ms):
        now = pygame.time.get_ticks()
        last = self.attack_cooldowns.get(attacker, 0)
        if now - last >= cooldown_ms:
            self.attack_cooldowns[attacker] = now
            return True
        return False

    def in_attack_range(self, attacker, target, range_px):
        distance = math.hypot(
            attacker.rect.centerx - target.rect.centerx,
            attacker.rect.centery - target.rect.centery
        )
        return distance <= range_px

    def apply_damage(self, attacker, target, weapon = None):
        base_damage = attacker.damage_calculator(weapon)
        
        # Check for critical hit
        is_critical = random.random() < self.crit_chance
        if is_critical:
            damage = base_damage * 1.5  # Crits do 50% more damage
        else:
            damage = base_damage
        
        target.take_damage(damage)
        return damage, is_critical