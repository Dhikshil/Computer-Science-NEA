import pygame
from pygame.locals import *
import constants
from character import Character
from enemy import Enemy
from world import World

pygame.init()
clock = pygame.time.Clock()

#Create Screen
pygame.display.set_caption("Computer Science NEA - Platformer")
screen = pygame.display.set_mode(constants.WINDOW_SIZE)

#Scale image function
def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, ((w * scale), (h * scale)))

#load player images
#player image array structure#
#[[idle], [hit], [run], [roll]]
knight_animations = []
knight_animation_types = ["idle", "hit", "run", "roll"]
for animation_type in knight_animation_types:
    frames = []
    for x in range(1,9):
        try:
            image = pygame.image.load(f"C:/Users/quick/OneDrive/Documents/Computer-Science-NEA/Assets/sprites/knight/{animation_type}/knight_{x}.png").convert_alpha()
            frames.append(scale_img(image, constants.PLAYER_SCALE))
        except FileNotFoundError:
            continue
    knight_animations.append(frames)

enemy_animations = []
enemy_animation_types = ["idle", "hit", "run"]
for animation_type in enemy_animation_types:
    frames = []
    for x in range(1, 9):
        try: 
            image = image = pygame.image.load(f"C:/Users/quick/OneDrive/Documents/Computer-Science-NEA/Assets/sprites/enemy1/{animation_type}/enemy1_{x}.png").convert_alpha()
            frames.append(scale_img(image, constants.PLAYER_SCALE))
        except FileNotFoundError:
            continue
    enemy_animations.append(frames)

#load ground tilesa
#ground tiles array structure
#[[green_surface], [green_dirt], [stones]]
ground_sprites = []
ground_sprite_types = ["surface", "ground", "stone"]
for ground_type in ground_sprite_types:
    frames = []
    for i in range(1,4):
        try:
            image = pygame.image.load(f"C:/Users/quick/OneDrive/Documents/Computer-Science-NEA/Assets/sprites/grounds/green_{ground_type}/{ground_type}_{i}.png").convert_alpha()
            frames.append(scale_img(image, constants.TILE_SCALE))
        except FileNotFoundError:
            continue
    ground_sprites.append(frames)

vegetation_sprites = []
vegetation_sprite_types = ["tree1", "bush"]
for vegetation_type in vegetation_sprite_types:
    frames = []
    for i in range(1,5):
        try:
            image = pygame.image.load(f"C:/Users/quick/OneDrive/Documents/Computer-Science-NEA/Assets/sprites/vegetation/{vegetation_type}/{vegetation_type}_{i}.png").convert_alpha()
            frames.append(scale_img(image, constants.TILE_SCALE))
        except FileNotFoundError:
            continue
    vegetation_sprites.append(frames)

wood_sprites = []
wood_sprite_types = ["plank"]
for wood_type in wood_sprite_types: 
    frames = []
    for i in range(1,5):
        try:
            image = pygame.image.load(f"C:/Users/quick/OneDrive/Documents/Computer-Science-NEA/Assets/sprites/wood/{wood_type}/{wood_type}_{i}.png").convert_alpha()
            frames.append(scale_img(image, constants.TILE_SCALE))
        except FileNotFoundError:
            continue
    wood_sprites.append(frames)

world = World(ground_sprites, vegetation_sprites, wood_sprites, enemy_animations, seed=1234)  #use fixed seed for consistent world
knight = Character(knight_animations)

surface_y = world.get_surface_y_at_pixel(400)

knight.rect.midbottom = (400, (surface_y) * constants.TILE_SIZE)

#movement variables
moving_left = False
moving_right = False

#camera variables
camera_x = knight.rect.centerx - constants.WINDOW_SIZE[0] // 2
camera_y = knight.rect.centery - constants.WINDOW_SIZE[1] // 2

#main loop
run = True
while run:
    screen.fill(constants.BG)

    #update world chunks around player
    world.update_chunks_around_player(knight.rect.centerx, knight.rect.centery)

    #calculate target camera position (centered on player)
    target_camera_x = knight.rect.centerx - constants.WINDOW_SIZE[0] // 2
    target_camera_y = knight.rect.centery - constants.WINDOW_SIZE[1] // 2

    #smooth camera movement
    camera_speed = 1
    camera_x += (target_camera_x - camera_x) * camera_speed
    camera_y += (target_camera_y - camera_y) * camera_speed

    #draw world
    world.draw(screen, camera_x, camera_y, constants.WINDOW_SIZE[0], constants.WINDOW_SIZE[1])

    #get obstacles for collision detection
    knight_obstacles = world.get_obstacles_in_area(knight)

    #handle input
    knight.vel_x = 0
    if moving_right:
        knight.vel_x = constants.PLAYER_SPEED
    if moving_left:
        knight.vel_x = -constants.PLAYER_SPEED

    knight.move(knight_obstacles)
    knight.update()

    # Calculate player screen position
    player_screen_x = knight.rect.x - camera_x
    player_screen_y = knight.rect.y - camera_y


    for enemy in world.enemies_spawned:
        if enemy.action == 0:
            tiles_around_enemy = 1
            enemy_obstacles = world.get_obstacles_in_area(enemy, tiles_around_enemy)
        else: 
            enemy_obstacles = world.get_obstacles_in_area(enemy)

        enemy_screen_x = enemy.rect.x - camera_x 
        enemy_screen_y = enemy.rect.y - camera_y
        
        enemy.updateAi(enemy_obstacles, knight)

        enemy.draw_at_position(screen, (enemy_screen_x, enemy_screen_y))

    knight.draw_at_position(screen, (player_screen_x, player_screen_y))

    #event handler
    for event in pygame.event.get():
        
        if event.type == QUIT:
            run = False
        
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            #get mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            #convert screen coordinates to world coordinates using camera offset
            world_x = mouse_x + camera_x
            world_y = mouse_y + camera_y
            
            #convert world coordinates to tile coordinates
            tile_x = world_x // constants.TILE_SIZE
            tile_y = world_y // constants.TILE_SIZE
            
            #check if player is in range of this tile
            knight_tile_obstacles = world.get_obstacles_in_area(knight, tiles_around_character = constants.PLAYER_HIT_RANGE // constants.TILE_SIZE)
            if knight.is_tile_in_range(tile_x, tile_y, knight_tile_obstacles, 0):
                world.remove_block_at(tile_x, tile_y, knight)
            
            
        
        if event.type == MOUSEBUTTONDOWN and event.button == 3:  #right mouse button
            #get mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            #convert screen coordinates to world coordinates using camera offset
            world_x = mouse_x + camera_x
            world_y = mouse_y + camera_y
            
            #convert world coordinates to tile coordinates
            tile_x = world_x // constants.TILE_SIZE
            tile_y = world_y // constants.TILE_SIZE

            #inflating player's hitbox to check for mouse collision with the tile the player is in
            tile_rect = knight.rect.inflate(80,80)

            #check if player is in range of this tile
            knight_tile_obstacles = world.get_obstacles_in_area(knight, tiles_around_character = constants.PLAYER_HIT_RANGE // constants.TILE_SIZE)
            if knight.is_tile_in_range(tile_x, tile_y, knight_obstacles, 1) and not tile_rect.collidepoint((world_x, world_y)):
                world.add_block_at(tile_x, tile_y, knight)

        #key pressed
        if event.type == KEYDOWN:
            if event.key == K_a:
                moving_left = True
            if event.key == K_d:
                moving_right = True
            if event.key in (K_w, K_SPACE):
                knight.jump()

        #key released
        if event.type == KEYUP:
            if event.key == K_a:
                moving_left = False
            if event.key == K_d:
                moving_right = False

    pygame.display.update()
    clock.tick(constants.FPS)

pygame.quit()