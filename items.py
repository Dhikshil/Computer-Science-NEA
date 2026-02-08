# Item database - easy to add new items here
ITEMS = {
    # Currency
    "coin": {
        "name": "Coin",
        "type": "currency",
        "max_stack": 999,
        "description": "Used to buy items",
        "placeable": False
    },
    
    # Resources
    "wood": {
        "name": "Wood",
        "type": "resource",
        "max_stack": 64,
        "description": "Basic building material",
        "placeable": True,
        "price": 2  # Price in coins
    },
    "apple": {
        "name": "Apple",
        "type": "consumable",
        "max_stack": 16,
        "description": "Restores 10 health",
        "heal_amount": 10,
        "placeable": False,
        "price": 5
    },
    "stone": {
        "name": "Stone",
        "type": "resource",
        "max_stack": 64,
        "description": "Hard building material",
        "placeable": True,
        "price": 3
    },
    "dirt": {
        "name": "Dirt",
        "type": "resource",
        "max_stack": 64,
        "description": "Soft earth",
        "placeable": True,
        "price": 1
    },
    
    # Weapons
    "wooden_sword": {
        "name": "Wooden Sword",
        "type": "weapon",
        "max_stack": 1,
        "description": "Basic melee weapon",
        "damage": 15,
        "durability": 50,
        "placeable": False,
        "price": 25
    },
    "stone_sword": {
        "name": "Stone Sword",
        "type": "weapon",
        "max_stack": 1,
        "description": "Stronger melee weapon",
        "damage": 25,
        "durability": 100,
        "placeable": False,
        "price": 50
    },
    "bow": {
        "name": "Bow",
        "type": "weapon",
        "max_stack": 1,
        "description": "Ranged weapon",
        "damage": 20,
        "durability": 80,
        "range": 300,
        "placeable": False,
        "price": 40
    }
}

# Tile drop tables - what items tiles drop when broken
TILE_DROPS = {
    0: [("dirt", 1)],  # surface_tile drops 1 dirt
    1: [("dirt", 1)],  # ground_tile drops 1 dirt
    2: [("stone", 1)],  # stone_tile drops 1 stone
    3: [("wood", 8), ("apple", 2)],  # tree drops 8 wood and 2 apples
    4: [("wood", 2), ("apple", 1)],  # bush drops 2 wood and 1 apple
    5: [("wood", 1)],  # wood_tile drops 1 wood
}

# Shop inventories - what each friendly NPC sells
SHOP_INVENTORIES = {
    "general_store": [
        ("wood", 10),
        ("stone", 10),
        ("dirt", 10),
        ("apple", 5)
    ],
    "weapon_shop": [
        ("wooden_sword", 1),
        ("stone_sword", 1),
        ("bow", 1)
    ],
    "mixed_shop": [
        ("wood", 5),
        ("apple", 3),
        ("wooden_sword", 1)
    ]
}

def get_item_info(item_id):
    return ITEMS.get(item_id, None)

def get_tile_drops(tile_type):
    return TILE_DROPS.get(tile_type, [])

def get_shop_inventory(shop_type):
    return SHOP_INVENTORIES.get(shop_type, [])