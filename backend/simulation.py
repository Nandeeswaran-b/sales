import random
import datetime
from typing import List, Dict
from models import Shelf, Item, ShelfStatus

# Predefined datasets for different environments
ENV_DATA = {
    "Supermarket": [
        {"id": "I001", "name": "Cereal Box", "count": 10},
        {"id": "I002", "name": "Milk Carton", "count": 20},
        {"id": "I003", "name": "Soda Can", "count": 15},
        {"id": "I004", "name": "Bread Loaf", "count": 8},
        {"id": "I005", "name": "Apple Bag", "count": 12},
    ],
    "Museum": [
        {"id": "M001", "name": "Ancient Vase", "count": 1},
        {"id": "M002", "name": "Gold Coin", "count": 5},
        {"id": "M003", "name": "Dino Bone", "count": 2},
        {"id": "M004", "name": "Old Sword", "count": 1},
        {"id": "M005", "name": "Painting", "count": 1},
    ],
    "Library": [
        {"id": "L001", "name": "History Book", "count": 5},
        {"id": "L002", "name": "Science Journal", "count": 10},
        {"id": "L003", "name": "Novel", "count": 7},
        {"id": "L004", "name": "Encyclopedia", "count": 3},
        {"id": "L005", "name": "Magazine", "count": 15},
    ]
}

class SimulationManager:
    def __init__(self):
        self.shelves: List[Shelf] = []
        self.current_env = "Supermarket"
        self.initialize_environment(self.current_env)

    def initialize_environment(self, env_name: str):
        if env_name not in ENV_DATA:
            env_name = "Supermarket" # Fallback
        
        self.current_env = env_name
        self.shelves = []
        items_pool = ENV_DATA[env_name]
        
        # Create a grid of shelves, e.g., 3 rows x 4 cols
        rows = 3
        cols = 4
        
        count = 0
        for r in range(rows):
            for c in range(cols):
                count += 1
                # Randomly assign an item from the pool
                raw_item = random.choice(items_pool)
                
                # Create Item Instance
                item = Item(
                    id=f"{raw_item['id']}-{count}",
                    name=raw_item['name'],
                    expected_count=raw_item['count'],
                    detected_count=raw_item['count'], # Initially perfect
                    expected_position_x=0.5,
                    expected_position_y=0.5,
                    detected_position_x=0.5,
                    detected_position_y=0.5
                )
                
                shelf = Shelf(
                    id=f"S-{r}-{c}",
                    row=r,
                    col=c,
                    item=item,
                    status=ShelfStatus.NORMAL,
                    last_scanned=datetime.datetime.now().isoformat()
                )
                self.shelves.append(shelf)

    def perform_scan(self):
        """Simulate a robot scan that finds discrepancies."""
        timestamp = datetime.datetime.now().isoformat()
        
        for shelf in self.shelves:
            shelf.last_scanned = timestamp
            
            # Reset temporarily to normal before applying random defects
            # In a real system, we'd keep state, but here we want to demonstrate change
            if shelf.item:
                shelf.item.detected_count = shelf.item.expected_count
                shelf.item.detected_position_x = shelf.item.expected_position_x
                shelf.status = ShelfStatus.NORMAL
            
            # Random chance of issue
            choice = random.random()
            
            if choice < 0.10: # 10% chance missing
                shelf.status = ShelfStatus.MISSING
                if shelf.item:
                    shelf.item.detected_count = 0
            
            elif choice < 0.25: # 15% chance misaligned
                shelf.status = ShelfStatus.MISALIGNED
                if shelf.item:
                    # Perturb position
                    shelf.item.detected_position_x += random.uniform(-0.3, 0.3)
            
            elif choice < 0.35: # 10% chance low stock
                shelf.status = ShelfStatus.LOW_STOCK
                if shelf.item:
                    shelf.item.detected_count = max(0, shelf.item.expected_count - random.randint(3, 8))
            
            else:
                shelf.status = ShelfStatus.NORMAL

        return self.get_state()

    def get_state(self):
        return [s.to_dict() for s in self.shelves]
