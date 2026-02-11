import pygame
from pygame.locals import *
import constants
from character import Character
from combat import CombatSystem
from world import World
from menus import MainMenu, WorldSelectMenu
from save_system import SaveSystem
from enemy import Enemy
from freindly import Friendly
from damage_display import DamageNumberManager
from items import get_item_info
from inventory_ui import InventoryUI


pygame.init()
clock = pygame.time.Clock()

# Create Screen
pygame.display.set_caption("Computer Science NEA - Platformer")
screen = pygame.display.set_mode(constants.WINDOW_SIZE)

# ... [all your existing image loading code] ...

# Scale image function
def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, ((w * scale), (h * scale)))

def map_structure(structure):
    structure_data = []
    with open(structure + ".txt", "r") as structure_raw:
        for line in structure_raw.readlines():
            row = []
            for element in line.split(","):
                row.append(int(element.strip()))
            structure_data.append(row)
    return structure_data

# Load all your sprites (same as before - keeping your existing code)
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
            image = pygame.image.load(f"C:/Users/quick/OneDrive/Documents/Computer-Science-NEA/Assets/sprites/enemy1/{animation_type}/enemy1_{x}.png").convert_alpha()
            frames.append(scale_img(image, constants.PLAYER_SCALE))
        except FileNotFoundError:
            continue
    enemy_animations.append(frames)

friendly_animations = []
friendly_animation_types = ["idle"]
for animation_type in friendly_animation_types:
    frames = []
    for x in range(1, 9):
        try: 
            image = pygame.image.load(f"C:/Users/quick/OneDrive/Documents/Computer-Science-NEA/Assets/sprites/friendly/{animation_type}/friendly_{x}.png").convert_alpha()
            frames.append(scale_img(image, constants.PLAYER_SCALE))
        except FileNotFoundError:
            continue
    friendly_animations.append(frames)

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

structures = ["house1", "house2"]
structures_map = {}
for structure in structures:
    structures_map[structure] = map_structure(structure)

# Initialize save system and menus
save_system = SaveSystem()
game_state = "main_menu"
main_menu = MainMenu(screen)
world_select_menu = WorldSelectMenu(screen, save_system)

# Initialize game objects as None
world = None
knight = None
combat = None
damage_number_manager = None
camera_x = 0
camera_y = 0
moving_left = False
moving_right = False
current_seed = None
game_start_time = 0
total_time_played = 0
# Initialize inventory UI after other initializations
inventory_ui = None
show_full_inventory = False


def start_new_game(seed):
    global world, knight, combat, camera_x, camera_y, moving_left, moving_right
    global current_seed, game_start_time, total_time_played, damage_number_manager
    global inventory_ui, show_full_inventory

    current_seed = seed
    game_start_time = pygame.time.get_ticks()
    total_time_played = 0
    
    # Create new world with selected seed
    world = World(ground_sprites, vegetation_sprites, wood_sprites, 
                  enemy_animations, friendly_animations, structures_map, seed=seed)
    knight = Character(knight_animations)
    combat = CombatSystem()
    damage_number_manager = DamageNumberManager()
    
    surface_y = world.get_surface_y_at_pixel(400)
    knight.rect.midbottom = (400, (surface_y) * constants.TILE_SIZE)
    
    # Reset camera
    camera_x = knight.rect.centerx - constants.WINDOW_SIZE[0] // 2
    camera_y = knight.rect.centery - constants.WINDOW_SIZE[1] // 2
    
    # Reset movement
    moving_left = False
    moving_right = False

    inventory_ui = InventoryUI()
    show_full_inventory = False

def load_saved_game(seed):
    global world, knight, combat, camera_x, camera_y, moving_left, moving_right
    global current_seed, game_start_time, total_time_played, damage_number_manager
    global inventory_ui, show_full_inventory  # Add this line
    
    save_data = save_system.load_game(seed)
    if not save_data:
        print("Failed to load game, starting new game instead")
        start_new_game(seed)
        return
    
    current_seed = seed
    total_time_played = save_data['time_played']
    game_start_time = pygame.time.get_ticks()
    
    # Create world and restore saved world data
    world = World(ground_sprites, vegetation_sprites, wood_sprites, 
                  enemy_animations, friendly_animations, structures_map, seed=seed)
    world.world = save_data['world']
    
    # Create knight and restore position/state
    knight = Character(knight_animations)
    knight.rect.x, knight.rect.y = save_data['player_pos']
    knight.health = save_data['player_health']
    knight.flip = save_data['player_flip']
    
    if 'player_inventory' in save_data:
        knight.load_inventory_data(save_data['player_inventory'])
    
    # Recreate enemies from saved data
    world.enemies_spawned = []
    for enemy_data in save_data['enemies']:
        enemy = Enemy(enemy_animations, spawn_pos=(0, 0))
        enemy.rect.x, enemy.rect.y = enemy_data['pos']
        enemy.health = enemy_data['health']
        enemy.flip = enemy_data['flip']
        enemy.action = enemy_data['action']
        world.enemies_spawned.append(enemy)
    
    # In load_saved_game function, update the friendlies section:
    # Recreate friendlies from saved data
    world.friendlies_spawned = []
    for friendly_data in save_data['friendlies']:
        shop_type = friendly_data.get('shop_type', 'general_store')
        friendly = Friendly(friendly_animations, spawn_pos=(0, 0), shop_type=shop_type)
        friendly.rect.x, friendly.rect.y = friendly_data['pos']
        friendly.flip = friendly_data['flip']
        friendly.action = friendly_data['action']
        world.friendlies_spawned.append(friendly)
    
    combat = CombatSystem()
    damage_number_manager = DamageNumberManager()
    
    inventory_ui = InventoryUI()
    show_full_inventory = False
    
    # Set camera to player position
    camera_x = knight.rect.centerx - constants.WINDOW_SIZE[0] // 2
    camera_y = knight.rect.centery - constants.WINDOW_SIZE[1] // 2
    
    # Reset movement
    moving_left = False
    moving_right = False
    
    print(f"Game loaded! Time played: {save_system.format_time(total_time_played)}")

def save_current_game():
    global world, knight, current_seed, game_start_time, total_time_played
    
    if world is None or knight is None:
        return
    
    # Calculate total time played
    session_time = pygame.time.get_ticks() - game_start_time
    total_time = total_time_played + session_time
    
    success = save_system.save_game(
        world, 
        world.enemies_spawned,
        world.friendlies_spawned,
        knight, 
        total_time, 
        current_seed
    )
    
    if success:
        print(f"Game saved! Total time played: {save_system.format_time(total_time)}")

# Main loop
run = True
while run:
    
    if game_state == "main_menu":
        # Main menu state
        main_menu.draw()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    action = main_menu.handle_click(pygame.mouse.get_pos())
                    if action == "world_select":
                        game_state = "world_select"
                    elif action == "quit":
                        run = False
    
    elif game_state == "world_select":
        # World selection menu
        world_select_menu.draw()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    result = world_select_menu.handle_click(pygame.mouse.get_pos())
                    if result == "back":
                        game_state = "main_menu"
                    elif result == "refresh":
                        pass
                    elif result and result[0] == "new_game":
                        seed = result[1]
                        start_new_game(seed)
                        game_state = "playing"
                    elif result and result[0] == "load_game":
                        seed = result[1]
                        load_saved_game(seed)
                        game_state = "playing"
    
    elif game_state == "playing":
        # Game state
        screen.fill(constants.BG)
        
        # Update world chunks around player
        player_tile_x = knight.rect.centerx // constants.TILE_SIZE
        player_tile_y = knight.rect.centery // constants.TILE_SIZE
        world.update_chunks_around_player(player_tile_x, player_tile_y)
        
        # Calculate target camera position
        target_camera_x = knight.rect.centerx - constants.WINDOW_SIZE[0] // 2
        target_camera_y = knight.rect.centery - constants.WINDOW_SIZE[1] // 2
        
        # Smooth camera movement
        camera_speed = 1
        camera_x += (target_camera_x - camera_x) * camera_speed
        camera_y += (target_camera_y - camera_y) * camera_speed
        
        # Draw world
        world.draw(screen, camera_x, camera_y, constants.WINDOW_SIZE[0], constants.WINDOW_SIZE[1])
        
        # Get obstacles for collision detection
        knight_obstacles = world.get_obstacles_in_area(knight)
        
        # Handle input
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
        
        # Update and draw enemies
        for enemy in world.enemies_spawned:
            if enemy.action == 0:
                tiles_around_enemy = 1
                enemy_obstacles = world.get_obstacles_in_area(enemy, tiles_around_enemy)
            else: 
                enemy_obstacles = world.get_obstacles_in_area(enemy)
            
            enemy_screen_x = enemy.rect.x - camera_x 
            enemy_screen_y = enemy.rect.y - camera_y
            
            enemy.updateAi(enemy_obstacles, knight, damage_number_manager)
            enemy.draw_at_position(screen, (enemy_screen_x, enemy_screen_y))
        
        for friendly in world.friendlies_spawned:
            friendly_screen_x = friendly.rect.x - camera_x 
            friendly_screen_y = friendly.rect.y - camera_y
            
            friendly.updateAi(knight, screen)  # Removed shop_ui parameter
            friendly.draw_at_position(screen, (friendly_screen_x, friendly_screen_y))

        inventory_ui.draw_hotbar(screen, knight, constants.WINDOW_SIZE[0], constants.WINDOW_SIZE[1])
        
        knight.draw_at_position(screen, (player_screen_x, player_screen_y))
        
        # Update and draw damage numbers
        damage_number_manager.update()
        damage_number_manager.draw(screen, camera_x, camera_y)
        
        # Display time played in top-right corner
        current_session_time = pygame.time.get_ticks() - game_start_time
        total_time = total_time_played + current_session_time
        time_font = pygame.font.SysFont("arial", 20)
        time_text = time_font.render(f"Time: {save_system.format_time(total_time)}", True, (255, 255, 255))
        screen.blit(time_text, (constants.WINDOW_SIZE[0] - 150, 10))
        
        # Display player health
        health_text = time_font.render(f"Health: {int(knight.health)}", True, (255, 50, 50))
        screen.blit(health_text, (10, 10))
        
        if show_full_inventory:
            inventory_ui.draw_full_inventory(screen, knight, constants.WINDOW_SIZE[0], constants.WINDOW_SIZE[1])


        # Event handler
        for event in pygame.event.get():
            if event.type == QUIT:
                save_current_game()
                run = False
            
            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = mouse_x + camera_x
                world_y = mouse_y + camera_y
                tile_x = world_x // constants.TILE_SIZE
                tile_y = world_y // constants.TILE_SIZE
                knight_tile_obstacles = world.get_obstacles_in_area(knight, tiles_around_character = constants.PLAYER_HIT_RANGE // constants.TILE_SIZE)
                
                if event.button == 1:
                    # Attack enemies
                    attacked_any_enemy = False
                    for enemy in world.enemies_spawned[:]:
                        if combat.in_attack_range(knight, enemy, constants.PLAYER_HIT_RANGE):
                            if combat.can_attack(knight, constants.PLAYER_HIT_RANGE):
                                weapon = None
                                if get_item_info(knight.get_selected_item())["type"] == "weapon":
                                    weapon = get_item_info(knight.get_selected_item())
                                damage, is_critical = combat.apply_damage(knight, enemy, weapon)
                                knight.action = 1
                                knight.frame_index = 0
                                
                                # Spawn damage number at enemy position
                                damage_number_manager.add_damage_number(
                                    enemy.rect.centerx,
                                    enemy.rect.top - 10,
                                    damage,
                                    is_critical
                                )
                                
                                print(f"Enemy hit for {damage} damage! Enemy health: {enemy.health}")
                                
                                if enemy.health <= 0:
                                    # Drop coins when enemy dies
                                    coins_dropped = enemy.get_coin_drops()
                                    knight.add_item("coin", coins_dropped)
                                    print(f"Enemy defeated! Dropped {coins_dropped} coins!")
                                    
                                    world.enemies_spawned.remove(enemy)
                                
                                attacked_any_enemy = True
                                break
                    
                    # Only mine blocks if we didn't attack an enemy
                    if not attacked_any_enemy:
                        if knight.is_tile_in_range(tile_x, tile_y, knight_tile_obstacles, 0):
                            world.remove_block_at(tile_x, tile_y, knight)
                
                if event.button == 3:
                    tile_rect = knight.rect.inflate(80,80)
                    if knight.is_tile_in_range(tile_x, tile_y, knight_obstacles, 1) and not tile_rect.collidepoint((world_x, world_y)):
                        world.add_block_at(tile_x, tile_y, knight)
            
            if event.type == KEYDOWN:
                if event.key == K_a:
                    moving_left = True
                if event.key == K_d:
                    moving_right = True
                if event.key in (K_w, K_SPACE):
                    knight.jump()
                if event.key == K_ESCAPE:
                    save_current_game()
                    damage_number_manager.clear()  # Clear damage numbers when leaving
                    game_state = "main_menu"
                if event.key == K_F5:
                    save_current_game()
                if event.key == K_TAB:
                    show_full_inventory = not show_full_inventory
                
                # Number keys 1-9 to select hotbar slots
                if event.key in (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9):
                    knight.selected_hotbar_slot = event.key - K_1
                
                # E key to use selected item
                if event.key == K_e:
                    selected_item = knight.get_selected_item()
                    if selected_item:
                        knight.use_item(selected_item)
                
                # Q key to drop selected item (optional)
                if event.key == K_q:
                    selected_item = knight.get_selected_item()
                    if selected_item:
                        knight.remove_item(selected_item, 1)
                        print(f"Dropped 1x {selected_item}")

                            # F key to interact with friendly NPCs (toggle shop)
                if event.key == K_f:
                    for friendly in world.friendlies_spawned:
                        if friendly.in_range:
                            friendly.toggle_shop()
                            break
                
                # UP/DOWN arrows for shop navigation
                if event.key == K_UP:
                    for friendly in world.friendlies_spawned:
                        if friendly.in_range and friendly.shop_open:
                            friendly.navigate_shop(-1)
                            break
                
                if event.key == K_DOWN:
                    for friendly in world.friendlies_spawned:
                        if friendly.in_range and friendly.shop_open:
                            friendly.navigate_shop(1)
                            break
                
                # ENTER to buy item
                if event.key == K_RETURN:
                    for friendly in world.friendlies_spawned:
                        if friendly.in_range and friendly.shop_open:
                            friendly.buy_selected_item(knight)
                            break
            
            if event.type == KEYUP:
                if event.key == K_a:
                    moving_left = False
                if event.key == K_d:
                    moving_right = False
            
            if event.type == pygame.MOUSEWHEEL:
                knight.cycle_hotbar(-event.y)  # Scroll up = -1, scroll down = 1

    pygame.display.update()
    clock.tick(constants.FPS)

pygame.quit()