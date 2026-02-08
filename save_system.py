import pickle
import os
import pygame

class SaveSystem:
    def __init__(self):
        self.save_directory = "saves"
        # Create saves directory if it doesn't exist
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_game(self, world, enemies, friendlies, knight, time_played, seed):
        """Save the game state to a file"""
        save_data = {
            'world': world.world,  # The world dictionary
            'seed': seed,
            'time_played': time_played,
            'enemies': self.serialize_entities(enemies),
            'friendlies': self.serialize_entities(friendlies),
            'player_pos': (knight.rect.x, knight.rect.y),
            'player_health': knight.health,
            'player_flip': knight.flip
        }
        
        filename = os.path.join(self.save_directory, f"world_{seed}.pkl")
        
        try:
            with open(filename, 'wb') as f:
                pickle.dump(save_data, f)
            print(f"Game saved successfully to {filename}")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, seed):
        """Load a saved game state"""
        filename = os.path.join(self.save_directory, f"world_{seed}.pkl")
        
        if not os.path.exists(filename):
            print(f"No save file found for seed {seed}")
            return None
        
        try:
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
            return save_data
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def save_exists(self, seed):
        """Check if a save file exists for this seed"""
        filename = os.path.join(self.save_directory, f"world_{seed}.pkl")
        return os.path.exists(filename)
    
    def delete_save(self, seed):
        """Delete a save file"""
        filename = os.path.join(self.save_directory, f"world_{seed}.pkl")
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"Save file deleted: {filename}")
                return True
            except Exception as e:
                print(f"Error deleting save: {e}")
                return False
        return False
    
    def serialize_entities(self, entities):
        """Convert entity objects to serializable data"""
        serialized = []
        for entity in entities:
            entity_data = {
                'pos': (entity.rect.x, entity.rect.y),
                'health': entity.health,
                'flip': entity.flip,
                'action': entity.action
            }
            serialized.append(entity_data)
        return serialized
    
    def format_time(self, milliseconds):
        """Convert milliseconds to readable time format"""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        hours = minutes // 60
        
        remaining_minutes = minutes % 60
        remaining_seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}h {remaining_minutes}m {remaining_seconds}s"
        elif minutes > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{seconds}s"