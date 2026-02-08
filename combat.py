import constants
import pygame
import math

class CombatSystem():
    def __init__(self):
        self.attack_cooldowns = {}

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

    def apply_damage(self, attacker, target):
        damage = attacker.damage_calculator(None)
        target.health -= damage
        return damage
