import pygame
import constants

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("arial", 72, bold=True)
        self.font_button = pygame.font.SysFont("arial", 36)
        
        # Define buttons
        button_width = 300
        button_height = 60
        center_x = constants.WINDOW_SIZE[0] // 2
        
        self.play_button = pygame.Rect(
            center_x - button_width // 2,
            250,
            button_width,
            button_height
        )

        self.options_button = pygame.Rect(
            center_x - button_width // 2,
            360,
            button_width,
            button_height
        )
        
        self.quit_button = pygame.Rect(
            center_x - button_width // 2,
            460,
            button_width,
            button_height
        )
        
        self.hovered_button = None
    
    def draw(self):
        self.screen.fill((20, 20, 40))  # Dark blue background
        
        # Draw title
        title = self.font_title.render("PLATFORMER NAME", True, (255, 255, 255))
        title_rect = title.get_rect(center=(constants.WINDOW_SIZE[0] // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Play button
        play_color = (100, 200, 100) if self.play_button.collidepoint(mouse_pos) else (50, 150, 50)
        pygame.draw.rect(self.screen, play_color, self.play_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.play_button, 3)
        play_text = self.font_button.render("LOAD WORLD", True, (255, 255, 255))
        play_button_x, play_button_y = self.play_button.center
        play_text_rect = play_text.get_rect(center=(play_button_x + 15, play_button_y))
        self.screen.blit(play_text, play_text_rect)

        # Options button
        options_color = (100, 100, 200) if self.options_button.collidepoint(mouse_pos) else (50, 50, 150)
        pygame.draw.rect(self.screen, options_color, self.options_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.options_button, 3)
        options_text = self.font_button.render("OPTIONS", True, (255, 255, 255))
        options_button_x, options_button_y = self.options_button.center
        options_text_rect = play_text.get_rect(center=(options_button_x + 30, options_button_y))
        self.screen.blit(options_text, options_text_rect)
        
        # Quit button
        quit_color = (200, 100, 100) if self.quit_button.collidepoint(mouse_pos) else (150, 50, 50)
        pygame.draw.rect(self.screen, quit_color, self.quit_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.quit_button, 3)
        quit_text = self.font_button.render("QUIT", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)
    
    def handle_click(self, pos):
        if self.play_button.collidepoint(pos):
            return "world_select"
        elif self.options_button.collidepoint(pos):
            return "options"  # Add this
        elif self.quit_button.collidepoint(pos):
            return "quit"
        return None

class WorldSelectMenu:
    def __init__(self, screen, save_system):
        self.screen = screen
        self.save_system = save_system
        self.font_title = pygame.font.SysFont("arial", 60, bold=True)
        self.font_button = pygame.font.SysFont("arial", 32)
        self.font_description = pygame.font.SysFont("arial", 20)
        self.font_small = pygame.font.SysFont("arial", 16)
        
        # World data: (name, seed, description)
        self.worlds = [
            ("World 1", 68, ""),
            ("World 2", 420, ""),
            ("World 3", 999, ""),
            ("World 4", 1337, "")
        ]
        
        # Create buttons for each world
        self.world_buttons = []
        self.load_buttons = []
        self.delete_buttons = []
        
        button_width = 400
        button_height = 100
        load_button_width = 100
        delete_button_width = 80
        center_x = constants.WINDOW_SIZE[0] // 2
        start_y = 150
        spacing = 120
        
        for i in range(4):
            # Main world button
            button = pygame.Rect(
                center_x - button_width // 2 - 100,
                start_y + i * spacing,
                button_width,
                button_height
            )
            self.world_buttons.append(button)
            
            # Load button (to the right of main button)
            load_button = pygame.Rect(
                button.right + 10,
                button.top,
                load_button_width,
                button_height // 2 - 5
            )
            self.load_buttons.append(load_button)
            
            # Delete button (below load button)
            delete_button = pygame.Rect(
                button.right + 10,
                button.top + button_height // 2 + 5,
                delete_button_width,
                button_height // 2 - 5
            )
            self.delete_buttons.append(delete_button)
        
        # Back button
        self.back_button = pygame.Rect(50, 50, 120, 50)
    
    def draw(self):
        self.screen.fill((30, 30, 50))
        
        # Draw title
        title = self.font_title.render("SELECT A WORLD", True, (255, 255, 255))
        title_rect = title.get_rect(center=(constants.WINDOW_SIZE[0] // 2, 80))
        self.screen.blit(title, title_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw world buttons
        for i, (button, world_data) in enumerate(zip(self.world_buttons, self.worlds)):
            world_name, seed, description = world_data
            has_save = self.save_system.save_exists(seed)
            
            # Button color based on hover
            if button.collidepoint(mouse_pos):
                color = (80, 120, 200)
            else:
                color = (50, 80, 150)
            
            # Draw main button background
            pygame.draw.rect(self.screen, color, button)
            pygame.draw.rect(self.screen, (255, 255, 255), button, 3)
            
            # Draw world name
            name_text = self.font_button.render(world_name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(button.centerx, button.top + 25))
            self.screen.blit(name_text, name_rect)
            
            # Draw description
            desc_text = self.font_description.render(description, True, (200, 200, 200))
            desc_rect = desc_text.get_rect(center=(button.centerx, button.top + 55))
            self.screen.blit(desc_text, desc_rect)
            
            # Draw seed info and save status
            if has_save:
                # Load save data to show time played
                save_data = self.save_system.load_game(seed)
                if save_data:
                    time_str = self.save_system.format_time(save_data['time_played'])
                    status_text = f"Seed: {seed} | Saved: {time_str}"
                else:
                    status_text = f"Seed: {seed} | Save exists"
            else:
                status_text = f"Seed: {seed} | New Game"
            
            seed_text = self.font_small.render(status_text, True, (150, 150, 150))
            seed_rect = seed_text.get_rect(center=(button.centerx, button.top + 80))
            self.screen.blit(seed_text, seed_rect)
            
            # Draw Load button if save exists
            if has_save:
                load_button = self.load_buttons[i]
                load_color = (100, 200, 100) if load_button.collidepoint(mouse_pos) else (50, 150, 50)
                pygame.draw.rect(self.screen, load_color, load_button)
                pygame.draw.rect(self.screen, (255, 255, 255), load_button, 2)
                load_text = self.font_description.render("LOAD", True, (255, 255, 255))
                load_rect = load_text.get_rect(center=load_button.center)
                self.screen.blit(load_text, load_rect)
                
                # Draw Delete button
                delete_button = self.delete_buttons[i]
                delete_color = (200, 100, 100) if delete_button.collidepoint(mouse_pos) else (150, 50, 50)
                pygame.draw.rect(self.screen, delete_color, delete_button)
                pygame.draw.rect(self.screen, (255, 255, 255), delete_button, 2)
                delete_text = self.font_small.render("DEL", True, (255, 255, 255))
                delete_rect = delete_text.get_rect(center=delete_button.center)
                self.screen.blit(delete_text, delete_rect)
        
        # Draw back button
        back_color = (100, 100, 100) if self.back_button.collidepoint(mouse_pos) else (60, 60, 60)
        pygame.draw.rect(self.screen, back_color, self.back_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.back_button, 2)
        back_text = self.font_description.render("BACK", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
    
    def handle_click(self, pos):
        # Check back button
        if self.back_button.collidepoint(pos):
            return "back"
        
        # Check delete buttons first
        for i, delete_button in enumerate(self.delete_buttons):
            if delete_button.collidepoint(pos):
                seed = self.worlds[i][1]
                if self.save_system.save_exists(seed):
                    self.save_system.delete_save(seed)
                    return "refresh"
        
        # Check load buttons
        for i, load_button in enumerate(self.load_buttons):
            if load_button.collidepoint(pos):
                seed = self.worlds[i][1]
                if self.save_system.save_exists(seed):
                    return ("load_game", seed)
        
        # Check world buttons (new game)
        for i, button in enumerate(self.world_buttons):
            if button.collidepoint(pos):
                if self.save_system.save_exists(self.worlds[i][1]):
                    return ("load_game", self.worlds[i][1])
                return ("new_game", self.worlds[i][1])
        
        return None
    
class OptionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("arial", 60, bold=True)
        self.font_option = pygame.font.SysFont("arial", 32)
        self.font_value = pygame.font.SysFont("arial", 28)
        
        # Options that will be implemented later
        self.options = {
            "master_volume": 100,
            "music_volume": 80,
            "sfx_volume": 100,
            "show_fps": False,
            "fullscreen": False,
        }
        
        # Current selection
        self.selected_option = 0
        self.option_names = list(self.options.keys())
        
        # Back button
        self.back_button = pygame.Rect(50, 50, 120, 50)
    
    def draw(self):
        self.screen.fill((30, 30, 50))
        
        # Draw title
        title = self.font_title.render("OPTIONS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(constants.WINDOW_SIZE[0] // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Draw notice that options are not functional yet
        notice_font = pygame.font.SysFont("arial", 20)
        notice = notice_font.render("(Settings currently for display only)", True, (150, 150, 150))
        notice_rect = notice.get_rect(center=(constants.WINDOW_SIZE[0] // 2, 130))
        self.screen.blit(notice, notice_rect)
        
        # Draw options
        start_y = 200
        spacing = 80
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option_name in enumerate(self.option_names):
            y = start_y + i * spacing
            
            # Option name
            display_name = option_name.replace("_", " ").title()
            
            # Highlight if selected
            if i == self.selected_option:
                color = (100, 150, 255)
            else:
                color = (255, 255, 255)
            
            name_text = self.font_option.render(display_name, True, color)
            name_rect = name_text.get_rect(midleft=(100, y))
            self.screen.blit(name_text, name_rect)
            
            # Option value
            value = self.options[option_name]
            if isinstance(value, bool):
                value_str = "ON" if value else "OFF"
                value_color = (100, 255, 100) if value else (255, 100, 100)
            else:
                value_str = str(value)
                value_color = (200, 200, 200)
            
            value_text = self.font_value.render(value_str, True, value_color)
            value_rect = value_text.get_rect(midright=(constants.WINDOW_SIZE[0] - 100, y))
            self.screen.blit(value_text, value_rect)
            
            # Draw slider for volume options
            if "volume" in option_name:
                slider_x = constants.WINDOW_SIZE[0] - 300
                slider_y = y + 5
                slider_width = 150
                slider_height = 10
                
                # Background
                pygame.draw.rect(self.screen, (60, 60, 60), 
                               (slider_x, slider_y, slider_width, slider_height))
                
                # Fill
                fill_width = int((value / 100) * slider_width)
                pygame.draw.rect(self.screen, (100, 150, 255),
                               (slider_x, slider_y, fill_width, slider_height))
        
        # Draw back button
        back_color = (100, 100, 100) if self.back_button.collidepoint(mouse_pos) else (60, 60, 60)
        pygame.draw.rect(self.screen, back_color, self.back_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.back_button, 2)
        back_text = self.font_option.render("BACK", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # Draw controls at bottom
        controls_font = pygame.font.SysFont("arial", 18)
        controls = controls_font.render("Use UP/DOWN arrows to navigate | Enter to toggle", 
                                       True, (150, 150, 150))
        controls_rect = controls.get_rect(center=(constants.WINDOW_SIZE[0] // 2, 
                                                  constants.WINDOW_SIZE[1] - 50))
        self.screen.blit(controls, controls_rect)
    
    def handle_click(self, pos):
        if self.back_button.collidepoint(pos):
            return "back"
        return None
    
    def navigate(self, direction):
        self.selected_option = (self.selected_option + direction) % len(self.option_names)
    
    def toggle_selected(self):
        option_name = self.option_names[self.selected_option]
        value = self.options[option_name]
        if isinstance(value, bool):
            self.options[option_name] = not value
