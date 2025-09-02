import pygame
import constants
from noise import pnoise2
import random

class World():
    def __init__(self, ground_sprites, seed=None):
        self.ground_sprites = ground_sprites
        self.seed = seed if seed else random.randint(0, 1000000)

        #chunk system for the infinite world
        self.chunk_size = 32 #32x32 tiles per chunk
        self.loaded_chunks = {} #dictionary to store loaded chunks
        self.chunk_cache_limit = 9 #can keep maximum 9 chunks loaded at once, 3x3 around player

        #perlin noise parameters
        self.noise_scale = 0.035 #how zoomed in the noise is on the image
        self.height_multiplier = 50 #how tall the terrain features can be
        self.base_height = 15 #base ground level (in tiles from the top)

        #terrain generation parameters
        self.surface_tile = 0
        self.ground_tile = 1
        self.stone_tile = 2
        self.cave_threshold = 0.3 #noise value above which caves appear

    def multi_octave_noise(self, x, y, octaves=4, persistence=0.2, lacunarity = 2.5):
        #generates noise using noise library 
        #returns a value between -1 and 1
        return pnoise2(x, y, octaves, persistence, lacunarity, repeatx=999999, repeaty=999999, base=self.seed)
    
    def generate_height_at(self, x):
        #generates height at a given x coordinate
        # FIXED: Use absolute world coordinate for consistent terrain
        noise_value = self.multi_octave_noise(x * self.noise_scale, 0)
        height = self.base_height + (noise_value * self.height_multiplier)
        return int(height)

    def generate_tile_at(self, x, y):
        # DEBUG: Print terrain height calculation
        if x >= -5 and x <= 5 and y >= -5 and y <= 25:
            terrain_height = self.generate_height_at(x)
            print(f"Tile ({x}, {y}): terrain_height={terrain_height}, tile_y={y}")
        
        terrain_height = self.generate_height_at(x)
        
        if y < terrain_height:
            return -1  # Air
        elif y == terrain_height:
            return self.surface_tile  # Surface
        elif y < terrain_height + 5:
            # FIXED: Use absolute world coordinates (x, y) not relative
            cave_noise = self.multi_octave_noise(x * 0.05, y * 0.05, octaves=3)
            if cave_noise > self.cave_threshold:
                return -1  # Cave
            return self.ground_tile  # Ground/dirt
        else:
            # FIXED: Use absolute world coordinates (x, y) not relative
            cave_noise = self.multi_octave_noise(x * 0.03, y * 0.05, octaves=2)
            if cave_noise > self.cave_threshold + 0.1:
                return -1  # Deep cave
            return self.stone_tile  # Stone
    
    def get_chunk_key(self, world_x, world_y):
        chunk_x = world_x // (self.chunk_size * constants.TILE_SIZE)
        chunk_y = world_y // (self.chunk_size * constants.TILE_SIZE)
        return(chunk_x, chunk_y)
    
    def generate_chunk(self, chunk_x, chunk_y):
        chunk_data = []
        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):
                # FIXED: These are already absolute world coordinates
                world_tile_x = chunk_x * self.chunk_size + x
                world_tile_y = chunk_y * self.chunk_size + y
                
                # The generate_tile_at method now uses these absolute coordinates correctly
                tile_type = self.generate_tile_at(world_tile_x, world_tile_y)
                row.append(tile_type)
            chunk_data.append(row)
        return chunk_data

    def load_chunk(self, chunk_x, chunk_y):
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.loaded_chunks:
            self.loaded_chunks[chunk_key] = self.generate_chunk(chunk_x, chunk_y)
    
    def unload_distant_chunks(self, player_chunk_x, player_chunk_y):
        chunks_to_remove = [
            (cx, cy) for (cx, cy) in self.loaded_chunks
            if max(abs(cx - player_chunk_x), abs(cy - player_chunk_y)) > 2
        ]
        for key in chunks_to_remove:
            del self.loaded_chunks[key]

    def update_chunks_around_player(self, player_x, player_y):
        # Fix chunk coordinate calculation for negative positions
        player_chunk_x = player_x // (self.chunk_size * constants.TILE_SIZE)
        player_chunk_y = player_y // (self.chunk_size * constants.TILE_SIZE)
        
        # Handle negative coordinates properly
        if player_x < 0 and player_x % (self.chunk_size * constants.TILE_SIZE) != 0:
            player_chunk_x -= 1
        if player_y < 0 and player_y % (self.chunk_size * constants.TILE_SIZE) != 0:
            player_chunk_y -= 1
            
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.load_chunk(player_chunk_x + dx, player_chunk_y + dy)
        self.unload_distant_chunks(player_chunk_x, player_chunk_y)
    
    def get_tile_at(self, tile_x, tile_y):
        # Handle negative coordinates properly
        chunk_x = tile_x // self.chunk_size
        chunk_y = tile_y // self.chunk_size
        
        # Fix negative coordinate chunk calculation
        if tile_x < 0 and tile_x % self.chunk_size != 0:
            chunk_x -= 1
        if tile_y < 0 and tile_y % self.chunk_size != 0:
            chunk_y -= 1
            
        chunk_key = (chunk_x, chunk_y)
        
        if chunk_key not in self.loaded_chunks:
            # Generate tile directly using absolute coordinates
            return self.generate_tile_at(tile_x, tile_y)
        
        local_x = tile_x - chunk_x * self.chunk_size
        local_y = tile_y - chunk_y * self.chunk_size
        
        if local_x < 0 or local_y < 0 or local_x >= self.chunk_size or local_y >= self.chunk_size:
            # Outside chunk bounds, generate directly
            return self.generate_tile_at(tile_x, tile_y)
        
        return self.loaded_chunks[chunk_key][local_y][local_x]

    def get_obstacles_in_area(self, camera_x, camera_y, screen_width, screen_height):
        obstacles = []
        start_x = int(camera_x // constants.TILE_SIZE) - 1
        end_x = int((camera_x + screen_width) // constants.TILE_SIZE) + 2
        start_y = int(camera_y // constants.TILE_SIZE) - 1
        end_y = int((camera_y + screen_height) // constants.TILE_SIZE) + 2
        
        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                tile_type = self.get_tile_at(tile_x, tile_y)
                if tile_type != -1:  # not air
                    world_x = tile_x * constants.TILE_SIZE
                    world_y = tile_y * constants.TILE_SIZE
                    obstacles.append(
                        pygame.Rect(world_x, world_y, constants.TILE_SIZE, constants.TILE_SIZE)
                    )
        return obstacles

    def get_tile_texture_index(self, tile_x, tile_y, tile_type):
        """Get consistent texture index for a tile based on its position"""
        if tile_type >= len(self.ground_sprites) or len(self.ground_sprites[tile_type]) == 0:
            return 0
        
        # Use tile position as seed for consistent texture selection
        # This ensures the same tile always gets the same texture variant
        seed = tile_x * 374761393 + tile_y * 668265263 + self.seed
        texture_count = len(self.ground_sprites[tile_type])
        return abs(seed) % texture_count

    def draw(self, surface, camera_x, camera_y, screen_width, screen_height):
        start_x = int(camera_x // constants.TILE_SIZE) - 1
        end_x = int((camera_x + screen_width) // constants.TILE_SIZE) + 2
        start_y = int(camera_y // constants.TILE_SIZE) - 1
        end_y = int((camera_y + screen_height) // constants.TILE_SIZE) + 2

        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                tile_type = self.get_tile_at(tile_x, tile_y)
                if tile_type != -1:
                    world_x = tile_x * constants.TILE_SIZE
                    world_y = tile_y * constants.TILE_SIZE
                    screen_x = world_x - camera_x
                    screen_y = world_y - camera_y
                    
                    # FIXED: Use deterministic texture selection instead of random
                    if tile_type < len(self.ground_sprites) and len(self.ground_sprites[tile_type]) > 0:
                        texture_index = self.get_tile_texture_index(tile_x, tile_y, tile_type)
                        texture = self.ground_sprites[tile_type][texture_index]
                        surface.blit(texture, (screen_x, screen_y))