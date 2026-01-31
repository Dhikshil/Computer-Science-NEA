import pygame
import constants
from enemy import Enemy
from noise import pnoise2
import random

class World():
    def __init__(self, ground_sprites, vegetation_sprites, wood_sprites, enemy_animations, seed=None):
        self.ground_sprites = ground_sprites
        self.wood_sprites = wood_sprites
        self.vegetation_sprites = vegetation_sprites
        self.seed = seed if seed else random.randint(0, 1000000)
        
        # chunk system for the infinite world
        self.chunk_size = 32  # 32x32 tiles per chunk
        self.loaded_chunks = {}  # dictionary to store loaded chunks
        self.chunk_limit = 9  # can keep maximum 9 chunks loaded at once, 3x3 around player
        self.world = {}

        # perlin noise parameters
        self.noise_scale = 0.02  # how zoomed in the noise is on the image
        self.height_multiplier = 30  # how tall the terrain features can be
        self.base_height = 15  # base ground level (in tiles from the top)
        self.min_terrain_depth = 3
        self.max_terrain_depth = 8
        self.max_terrain_height = 300

        # terrain types 
        self.tile_types = {
            "air_tile" : -1,
            "surface_tile" : 0,
            "ground_tile" : 1,
            "stone_tile" : 2,
            "tree_tile" : 3,
            "bush_tile" : 4,
            "wood_tile" : 5, 
        }

        # terrain type generation thresholds
        self.cave_threshold = 0.1  # noise value above which caves appear
        self.vegetation_threshold = 0.05  # noise value above which vegetation spawns
        self.tree_vs_bush_threshold = 0.3  # if vegetation noise > this, spawn tree, else bush
        self.vegetation_density = 0.075  # how dense vegetation clusters are

        self.enemies_spawned = []
        self.enemy_animations = enemy_animations
    
    # create a gradient image of a perlin noise map given (x, y)
    def multi_octave_noise(self, x, y, octaves=4, persistence=0.2, lacunarity=2.5):
        # generates noise using noise library
        # returns a value between -1 and 1
        return pnoise2(x, y, octaves, persistence, lacunarity, repeatx=999999, repeaty=999999, base=self.seed)

    # how high shoudl the surface tile be generated
    def generate_terrain_height(self, x):
        # generates height at a given x coordinate
        noise_value = self.multi_octave_noise(x * self.noise_scale, 0)
        height = self.base_height + (noise_value * self.height_multiplier)
        return int(height)

    # the ground between the surface tile and when the stone starts generating, how should it look
    def generate_terrain_depth(self, x):
        noise_value = self.multi_octave_noise(x * self.noise_scale, 40)
        # normalise from [-1, 1] → [0, 1]
        noise_value = (noise_value + 1) / 2
        depth = self.min_terrain_depth + noise_value * (self.max_terrain_depth - self.min_terrain_depth)
        return int(depth)

    # check if the tile chosen should have vegetation
    def should_spawn_vegetation(self, x, y):
        # check if vegetation should spawn at this position
        # use different noise parameters for vegetation clustering
        vegetation_noise = self.multi_octave_noise(x * self.vegetation_density, y * self.vegetation_density, octaves=2, persistence=0.5)
        return vegetation_noise > self.vegetation_threshold
    
    # should the tile be bush or a tree
    def get_vegetation_type(self, x, y):
        # determine if vegetation should be tree or bush
        type_noise = self.multi_octave_noise(x * 0.03, y * 0.03, octaves=1)
        if type_noise > self.tree_vs_bush_threshold:
            return self.tile_types["tree_tile"]
        else:
            return self.tile_types["bush_tile"]
    
    # what image should be used for the ground or stone tile    
    def generate_tile_image_index(self, x, y, tile_type):
        # makes tile image deterministic so when reloaded, the same image will be loaded
        random.seed(self.seed + x * 1000 + y)
        texture_count = len(self.ground_sprites[tile_type])
        return random.randint(0, texture_count - 1)

    # what image should be used for the bush
    def generate_bush_image_index(self, x, y):
        random.seed(self.seed + x * 1000 + y)
        #only bushes need to be checked and we choose a random index from their list of images
        return random.randint(0, len(self.vegetation_sprites[1]) - 1)

    # what type of tile should be generated at these given tiles
    def generate_tile_type(self, x, y):
        # what heeight the terrain should be at
        terrain_height = self.generate_terrain_height(x)
        ground_height = self.generate_terrain_depth(x) + terrain_height

        # if tile is higher than surface tile, it will be air
        if y < terrain_height:
            return self.tile_types["air_tile"], 0, False
        
        # tile from one above the surface tile could be vegetation
        elif y == terrain_height:
            if self.should_spawn_vegetation(x, y):
                if self.get_vegetation_type(x, y) == self.tile_types["tree_tile"]:
                    return self.tile_types["tree_tile"], 0, False
                return self.tile_types["bush_tile"], self.generate_bush_image_index(x, y), False
            return self.tile_types["air_tile"], 0, False
        
        # this will be the surface tile
        elif y == terrain_height + 1:
            return self.tile_types["surface_tile"], 0, True
        
        # this will be the ground tile or if there is a cave, a cave will be here
        elif y > terrain_height and y <= ground_height:
            cave_noise = self.multi_octave_noise(x * 0.05, y * 0.05, octaves = 3)
            if cave_noise > self.cave_threshold:
                return self.tile_types["air_tile"], 0, False
            return self.tile_types["ground_tile"], self.generate_tile_image_index(x, y, self.tile_types["ground_tile"]), True
        
        # this will be stone tile or will be a cave
        elif y > ground_height and y <= self.max_terrain_height:
            cave_noise = self.multi_octave_noise(x * 0.03, y * 0.05, octaves = 3)
            if cave_noise > self.cave_threshold + 0.1:
                return self.tile_types["air_tile"], 0, False
            return self.tile_types["stone_tile"], self.generate_tile_image_index(x, y, self.tile_types["stone_tile"]), True
        
        # void area below the world, so the world does not go down for ever
        return self.tile_types["air_tile"], 0, False

    def generate_tile(self, x, y):
        tile_type, image_index, solid = self.generate_tile_type(x, y)
        tile = {
            "world_x" : x,
            "world_y" : y,
            "tile_type" : tile_type,
            "image_index" : image_index,
            "solid" : solid,
          }
        return tile
    
    def generate_chunk(self, chunk_x, chunk_y):
        chunk = {}
        for local_x in range(self.chunk_size):
            for local_y in range(self.chunk_size):
                world_x = chunk_x * self.chunk_size + local_x
                world_y = chunk_y * self.chunk_size + local_y
                tile = self.generate_tile(world_x, world_y)
                chunk[(local_x, local_y)] = tile
        return chunk
    
    def load_chunk(self, chunk_x, chunk_y):
        key = (chunk_x, chunk_y)
        if key not in self.world:
            self.world[key] = self.generate_chunk(chunk_x, chunk_y)
            self.spawn_enemies(chunk_x)

    def get_tile_at(self, tile_x, tile_y):
        chunk_x = tile_x // self.chunk_size
        chunk_y = tile_y // self.chunk_size

        local_x = tile_x - chunk_x * self.chunk_size
        local_y = tile_y - chunk_y * self.chunk_size

        chunk_key = (chunk_x, chunk_y)
        local_key = (local_x, local_y)

        if chunk_key not in self.world:
            self.load_chunk(chunk_x, chunk_y)

        return self.world[chunk_key][local_key]
    
    def update_chunks_around_player(self, tile_x, tile_y):
        chunk_x = tile_x // self.chunk_size
        chunk_y = tile_y // self.chunk_size

        needed_chunks = set()

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                needed_chunks.add((chunk_x + dx, chunk_y + dy))
                self.load_chunk(chunk_x + dx, chunk_y + dy)
        
        for key in needed_chunks:
            if key not in self.loaded_chunks:
                self.loaded_chunks[key] = self.world[key]

        for key in list(self.loaded_chunks):
            if key not in needed_chunks:
                del self.loaded_chunks[key]
                
    def get_surface_y_at_pixel(self, x):
        tile_x = int(x // constants.TILE_SIZE)

        # scan downward from sky to deep underground
        for tile_y in range(0, self.max_terrain_height):
            tile = self.get_tile_at(tile_x, tile_y)
            if tile["tile_type"] == self.tile_types["surface_tile"]:
                return tile["world_y"]

        return self.base_height  # fallback so it never returns None

    def get_obstacles_in_area(self, character, tiles_around_character = 3):
        obstacles = []

        character_x = character.rect.left
        character_y = character.rect.bottom

        start_x = int(character_x // constants.TILE_SIZE) - 1
        end_x = start_x + tiles_around_character + 1
        start_y = int(character_y // constants.TILE_SIZE) - 1
        end_y = start_y + tiles_around_character + 1

        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                tile = self.get_tile_at(tile_x, tile_y)
                if tile["solid"]:
                    obstacles.append(
                        pygame.Rect(tile["world_x"] * constants.TILE_SIZE, tile["world_y"] * constants.TILE_SIZE, constants.TILE_SIZE, constants.TILE_SIZE)
                    )
        return obstacles
    
    def remove_block_at(self, tile_x, tile_y, player):
        chunk_x = tile_x // self.chunk_size
        chunk_y = tile_y // self.chunk_size

        local_x = tile_x - chunk_x * self.chunk_size
        local_y = tile_y - chunk_y * self.chunk_size

        if self.world[(chunk_x, chunk_y)][(local_x, local_y)]["tile_type"] != self.tile_types["air_tile"]:
            self.world[(chunk_x, chunk_y)][(local_x, local_y)]["tile_type"] = self.tile_types["air_tile"]
            self.world[(chunk_x, chunk_y)][(local_x, local_y)]["solid"] = False
            self.world[(chunk_x, chunk_y)][(local_x, local_y)]["image_index"] = 0
            
                 

    def add_block_at(self, tile_x, tile_y, player):
        chunk_x = tile_x // self.chunk_size
        chunk_y = tile_y // self.chunk_size

        local_x = tile_x - chunk_x * self.chunk_size
        local_y = tile_y - chunk_y * self.chunk_size

        if self.world[(chunk_x, chunk_y)][(local_x, local_y)]["tile_type"] == self.tile_types["air_tile"]:
            self.world[(chunk_x, chunk_y)][(local_x, local_y)]["tile_type"] = self.tile_types["wood_tile"]
            self.world[(chunk_x, chunk_y)][(local_x, local_y)]["solid"] = True


    def spawn_enemies(self, chunk_x):
        p = 0.3 # probability of an enemy spawning

        while random.random() < p:
            tile_x = chunk_x * self.chunk_size + random.randint(0, self.chunk_size - 1)
            tile_y = self.generate_terrain_height(tile_x) - 2
            
            enemy = Enemy(self.enemy_animations, spawn_pos = (tile_x * constants.TILE_SIZE + constants.TILE_SIZE // 2, tile_y * constants.TILE_SIZE))

            self.enemies_spawned.append(enemy)

            p *= 0.6

    def draw(self, surface, camera_x, camera_y, screen_width, screen_height):

        start_x = int(camera_x // constants.TILE_SIZE) - 1
        end_x = int((camera_x + screen_width) // constants.TILE_SIZE) + 2
        start_y = int(camera_y // constants.TILE_SIZE) - 1
        end_y = int((camera_y + screen_height) // constants.TILE_SIZE) + 2

        for tile_x in range(start_x, end_x):
            for tile_y in range(start_y, end_y):
                tile = self.get_tile_at(tile_x, tile_y)

                if tile["tile_type"] != self.tile_types["air_tile"]:
                    screen_x = tile["world_x"] * constants.TILE_SIZE - camera_x
                    screen_y = tile["world_y"] * constants.TILE_SIZE  - camera_y

                    if tile["tile_type"] < len(self.ground_sprites):
                        ground_texture = self.ground_sprites[tile["tile_type"]][tile["image_index"]]
                        surface.blit(ground_texture, (screen_x, screen_y))

                    elif tile["tile_type"] == self.tile_types["tree_tile"]:
                        pointer = screen_y
                        for img in self.vegetation_sprites[0]:
                            surface.blit(img, (screen_x, pointer + 6))
                            pointer -= img.get_height()

                    elif tile["tile_type"] == self.tile_types["bush_tile"]:
                        texture = self.vegetation_sprites[tile["tile_type"] - len(self.ground_sprites)][tile["image_index"]]
                        surface.blit(texture, (screen_x, screen_y + 6))

                    elif tile["tile_type"] == self.tile_types["wood_tile"]:
                        texture = self.wood_sprites[tile["tile_type"] - len(self.ground_sprites) - len(self.vegetation_sprites) - 1][tile["image_index"]]
                        surface.blit(texture, (screen_x, screen_y))
