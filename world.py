import pygame
import constants
from noise import pnoise2
import random

class World():
    def __init__(self, ground_sprites, vegetation_sprites, seed=None):
        self.ground_sprites = ground_sprites
        self.vegetation_sprites = vegetation_sprites
        self.seed = seed if seed else random.randint(0, 1000000)
        
        # chunk system for the infinite world
        self.chunk_size = 32  # 32x32 tiles per chunk
        self.loaded_chunks = {}  # dictionary to store loaded chunks
        self.chunk_cache_limit = 9  # can keep maximum 9 chunks loaded at once, 3x3 around player
        
        # perlin noise parameters
        self.noise_scale = 0.02  # how zoomed in the noise is on the image
        self.height_multiplier = 50  # how tall the terrain features can be
        self.base_height = 15  # base ground level (in tiles from the top)
        
        # terrain generation parameters
        self.surface_tile = 0
        self.ground_tile = 1
        self.stone_tile = 2
        self.cave_threshold = 0.5  # noise value above which caves appear
        
        # vegetation parameters
        self.tree_tile = 3
        self.bush_tile = 4
        self.vegetation_threshold = 0.05  # noise value above which vegetation spawns
        self.tree_vs_bush_threshold = 0.1  # if vegetation noise > this, spawn tree, else bush
        self.vegetation_density = 0.075  # how dense vegetation clusters are

        self.broken_blocks = set()
        self.added_blocks = set()

        self.wood_tile = 5


    def multi_octave_noise(self, x, y, octaves=4, persistence=0.1, lacunarity=2.5):
        # generates noise using noise library
        # returns a value between -1 and 1
        return pnoise2(x, y, octaves, persistence, lacunarity, repeatx=999999, repeaty=999999, base=self.seed)

    def generate_height_at(self, x):
        # generates height at a given x coordinate
        noise_value = self.multi_octave_noise(x * self.noise_scale, 0)
        height = self.base_height + (noise_value * self.height_multiplier)
        return int(height)

    def should_spawn_vegetation(self, x, y):
        # check if vegetation should spawn at this position
        # use different noise parameters for vegetation clustering
        vegetation_noise = self.multi_octave_noise(x * self.vegetation_density, y * self.vegetation_density, octaves=2, persistence=0.5)
        return vegetation_noise > self.vegetation_threshold

    def get_vegetation_type(self, x, y):
        # determine if vegetation should be tree or bush
        type_noise = self.multi_octave_noise(x * 0.03, y * 0.03, octaves=1)
        if type_noise > self.tree_vs_bush_threshold:
            return self.tree_tile
        else:
            return self.bush_tile

    def generate_tile_at(self, x, y):
        terrain_height = self.generate_height_at(x)
        
        if y < terrain_height:
            return -1  # air
        elif y == terrain_height:
            # surface level → vegetation check
            if self.should_spawn_vegetation(x, y):
                if self.get_vegetation_type(x, y) == self.tree_tile:
                    return self.tree_tile  # tree base
                else:
                    return self.bush_tile  # bush
            else:
                return self.surface_tile  # regular surface
        elif y < terrain_height + 5:
            # underground dirt layer with caves
            cave_noise = self.multi_octave_noise(x * 0.05, y * 0.05, octaves=3)
            if cave_noise > self.cave_threshold:
                return -1  # cave
            return self.ground_tile
        else:
            # deep underground stone with caves
            cave_noise = self.multi_octave_noise(x * 0.03, y * 0.05, octaves=2)
            if cave_noise > self.cave_threshold + 0.1:
                return -1  # deep cave
            return self.stone_tile

    def get_chunk_key(self, world_x, world_y):
        chunk_x = world_x // (self.chunk_size * constants.TILE_SIZE)
        chunk_y = world_y // (self.chunk_size * constants.TILE_SIZE)
        return (chunk_x, chunk_y)

    def generate_chunk(self, chunk_x, chunk_y):
        chunk_data = []
        for y in range(self.chunk_size):
            row = []
            for x in range(self.chunk_size):
                world_tile_x = chunk_x * self.chunk_size + x
                world_tile_y = chunk_y * self.chunk_size + y
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
        player_chunk_x = player_x // (self.chunk_size * constants.TILE_SIZE)
        player_chunk_y = player_y // (self.chunk_size * constants.TILE_SIZE)
        
        if player_x < 0 and player_x % (self.chunk_size * constants.TILE_SIZE) != 0:
            player_chunk_x -= 1
        if player_y < 0 and player_y % (self.chunk_size * constants.TILE_SIZE) != 0:
            player_chunk_y -= 1
            
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.load_chunk(player_chunk_x + dx, player_chunk_y + dy)
        self.unload_distant_chunks(player_chunk_x, player_chunk_y)

    def get_tile_at(self, tile_x, tile_y):
        chunk_x = tile_x // self.chunk_size
        chunk_y = tile_y // self.chunk_size
        
        if tile_x < 0 and tile_x % self.chunk_size != 0:
            chunk_x -= 1
        if tile_y < 0 and tile_y % self.chunk_size != 0:
            chunk_y -= 1
            
        chunk_key = (chunk_x, chunk_y)
        
        if chunk_key not in self.loaded_chunks:
            return self.generate_tile_at(tile_x, tile_y)
        
        local_x = tile_x - chunk_x * self.chunk_size
        local_y = tile_y - chunk_y * self.chunk_size
        
        if local_x < 0 or local_y < 0 or local_x >= self.chunk_size or local_y >= self.chunk_size:
            # outside chunk bounds, generate directly
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
                chunk_x = tile_x // self.chunk_size
                chunk_y = tile_y // self.chunk_size
                local_x = tile_x % self.chunk_size
                local_y = tile_y % self.chunk_size

                block_key = (chunk_x, chunk_y, local_x, local_y)
                is_broken = block_key in self.broken_blocks

                if tile_type != -1 and not is_broken:  # not air
                    world_x = tile_x * constants.TILE_SIZE
                    world_y = tile_y * constants.TILE_SIZE
                    obstacles.append(
                        pygame.Rect(world_x, world_y, constants.TILE_SIZE, constants.TILE_SIZE)
                    )
        return obstacles

    def remove_block_at(self, tile_x, tile_y):
        chunk_x = tile_x // self.chunk_size
        chunk_y = tile_y // self.chunk_size
        local_x = tile_x % self.chunk_size
        local_y = tile_y % self.chunk_size

        block_key = (chunk_x, chunk_y, local_x, local_y)
        self.broken_blocks.add(block_key)

    def add_block_at(self, tile_x, tile_y, obstacles):
        chunk_x = tile_x // self.chunk_size
        chunk_y = tile_y // self.chunk_size
        local_x = tile_x % self.chunk_size
        local_y = tile_y % self.chunk_size

        block_key = (chunk_x, chunk_y, local_x, local_y)
        if not(block_key in obstacles):
            if block_key in self.broken_blocks:
                self.broken_blocks.remove(block_key)
            self.added_blocks.add(block_key)
            world_x = tile_x * constants.TILE_SIZE
            world_y = tile_y * constants.TILE_SIZE
            obstacles.append(
                        pygame.Rect(world_x, world_y, constants.TILE_SIZE, constants.TILE_SIZE)
                    )
        return obstacles



    def get_tile_texture_index(self, tile_x, tile_y, tile_type):
        if tile_type >= len(self.ground_sprites) or len(self.ground_sprites[tile_type]) == 0:
            return 0
        
        # Set random seed based on tile position and world seed for consistency
        random.seed(self.seed + tile_x * 1000 + tile_y)
        texture_count = len(self.ground_sprites[tile_type])
        return random.randint(0, texture_count - 1)
    
    def get_vegetation_texture_index(self, vegetation_type):
        if vegetation_type == 1:  # bushes
            if not self.vegetation_sprites or len(self.vegetation_sprites[1]) == 0:
                return 0
            return random.randint(0, len(self.vegetation_sprites[1]) - 1)

        #trees
        return 0
    
    def draw(self, surface, camera_x, camera_y, screen_width, screen_height):
        start_x = int(camera_x // constants.TILE_SIZE) - 1
        end_x = int((camera_x + screen_width) // constants.TILE_SIZE) + 2
        start_y = int(camera_y // constants.TILE_SIZE) - 1
        end_y = int((camera_y + screen_height) // constants.TILE_SIZE) + 2

        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                tile_type = self.get_tile_at(tile_x, tile_y)

                chunk_x = tile_x // self.chunk_size
                chunk_y = tile_y // self.chunk_size
                local_x = tile_x % self.chunk_size
                local_y = tile_y % self.chunk_size

                block_key = (chunk_x, chunk_y, local_x, local_y)
                is_broken = block_key in self.broken_blocks

                if tile_type != -1:
                    world_x = tile_x * constants.TILE_SIZE
                    world_y = tile_y * constants.TILE_SIZE
                    screen_x = world_x - camera_x
                    screen_y = world_y - camera_y

                    # FIRST: Always draw the appropriate ground tile
                    ground_type_to_draw = self.surface_tile  # Default to surface
                    
                    
                    # Determine what ground tile should be here
                    terrain_height = self.generate_height_at(tile_x)
                    if tile_y == terrain_height:
                        ground_type_to_draw = self.surface_tile
                    elif tile_y > terrain_height and tile_y < terrain_height + 5:
                        ground_type_to_draw = self.ground_tile
                    elif tile_y >= terrain_height + 5:
                        ground_type_to_draw = self.stone_tile
                    
                    # Draw the ground tile
                    if ground_type_to_draw < len(self.ground_sprites) and len(self.ground_sprites[ground_type_to_draw]) > 0:
                        texture_index = self.get_tile_texture_index(tile_x, tile_y, ground_type_to_draw)
                        ground_texture = self.ground_sprites[ground_type_to_draw][texture_index]
                        original_alpha = ground_texture.get_alpha()
                        if is_broken:
                            ground_texture.set_alpha(128)
                        surface.blit(ground_texture, (screen_x, screen_y))
                        ground_texture.set_alpha(original_alpha)
                    
                    # SECOND: Draw vegetation on top if this is a vegetation tile
                    if tile_type == self.tree_tile:
                        if self.vegetation_sprites and len(self.vegetation_sprites[0]) > 0:
                            tree_images = self.vegetation_sprites[0]
                            # Draw tree starting from the top of the ground tile
                            current_y = screen_y + 6 #start at ground level
                            for img in tree_images:
                                current_y -= img.get_height()  # Move up for each tree segment
                                surface.blit(img, (screen_x, current_y))
                                
                    elif tile_type == self.bush_tile:
                        if self.vegetation_sprites and len(self.vegetation_sprites[1]) > 0:
                            bush_texture_index = self.get_vegetation_texture_index(1)
                            bush_texture = self.vegetation_sprites[1][bush_texture_index]
                            current_y = screen_y - bush_texture.get_height() + 6
                            # Draw bush sitting on top of the ground
                            surface.blit(bush_texture, (screen_x, current_y))
