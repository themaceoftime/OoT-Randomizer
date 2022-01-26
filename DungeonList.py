import random
import os

from Dungeon import Dungeon
from Item import ItemFactory
from Utils import data_path


dungeon_table = [
    {
        'name': 'Deku Tree',
        'id': 'deku_tree',
        'hint': 'the Deku Tree',
        'font_color': 'Green',
        'boss_key':     0, 
        'small_key':    0,
        'small_key_mq': 0,
        'dungeon_item': 1,
    },
    {
        'name': 'Dodongos Cavern',
        'id': 'dodongos_cavern',
        'hint': 'Dodongo\'s Cavern',
        'font_color': 'Red',
        'boss_key':     0, 
        'small_key':    0,
        'small_key_mq': 0,
        'dungeon_item': 1,
    },
    {
        'name': 'Jabu Jabus Belly',
        'id': 'jabu_jabus_belly',
        'hint': 'Jabu Jabu\'s Belly',
        'font_color': 'Blue',
        'boss_key':     0, 
        'small_key':    0,
        'small_key_mq': 0,
        'dungeon_item': 1,
    },
    {
        'name': 'Forest Temple',
        'id': 'forest_temple',
        'hint': 'the Forest Temple',
        'font_color': 'Green',
        'boss_key':     1, 
        'small_key':    5,
        'small_key_mq': 6,
        'dungeon_item': 1,
    },
    {
        'name': 'Bottom of the Well',
        'id': 'bottom_of_the_well',
        'hint': 'the Bottom of the Well',
        'font_color': 'Pink',
        'boss_key':     0, 
        'small_key':    3,
        'small_key_mq': 2,
        'dungeon_item': 1,
    },
    {
        'name': 'Fire Temple',
        'id': 'fire_temple',
        'hint': 'the Fire Temple',
        'font_color': 'Red',
        'boss_key':     1, 
        'small_key':    8,
        'small_key_mq': 5,
        'dungeon_item': 1,
    },
    {
        'name': 'Ice Cavern',
        'id': 'ice_cavern',
        'hint': 'the Ice Cavern',
        'font_color': 'Blue',
        'boss_key':     0, 
        'small_key':    0,
        'small_key_mq': 0,
        'dungeon_item': 1,
    },
    {
        'name': 'Water Temple',
        'id': 'water_temple',
        'hint': 'the Water Temple',
        'font_color': 'Blue',
        'boss_key':     1, 
        'small_key':    6,
        'small_key_mq': 2,
        'dungeon_item': 1,
    },
    {
        'name': 'Shadow Temple',
        'id': 'shadow_temple',
        'hint': 'the Shadow Temple',
        'font_color': 'Pink',
        'boss_key':     1, 
        'small_key':    5,
        'small_key_mq': 6,
        'dungeon_item': 1,
    },
    {
        'name': 'Gerudo Training Ground',
        'id': 'gerudo_training_ground',
        'hint': 'the Gerudo Training Ground',
        'font_color': 'Yellow',
        'boss_key':     0, 
        'small_key':    9,
        'small_key_mq': 3,
        'dungeon_item': 0,
    },
    {
        'name': 'Spirit Temple',
        'id': 'spirit_temple',
        'hint': 'the Spirit Temple',
        'font_color': 'Yellow',
        'boss_key':     1, 
        'small_key':    5,
        'small_key_mq': 7,
        'dungeon_item': 1,
    },
    {
        'name': 'Ganons Castle',
        'id': 'ganons_castle',
        'hint': 'inside Ganon\'s Castle',
        'boss_key':     1, 
        'small_key':    2,
        'small_key_mq': 3,
        'dungeon_item': 0,
    },
]


def create_dungeons(world):
    for dungeon_info in dungeon_table:
        name = dungeon_info['name']
        hint = dungeon_info['hint'] if 'hint' in dungeon_info else name
        font_color = dungeon_info['font_color'] if 'font_color' in dungeon_info else 'White'
        
        if world.settings.logic_rules == 'glitched':
            if not world.dungeon_mq[name]:
                dungeon_json = os.path.join(data_path('Glitched World'), name + '.json')
            else:
                dungeon_json = os.path.join(data_path('Glitched World'), name + ' MQ.json')
        else:
            if not world.dungeon_mq[name]:
                dungeon_json = os.path.join(data_path('World'), name + '.json')
            else:
                dungeon_json = os.path.join(data_path('World'), name + ' MQ.json')

        
        world.load_regions_from_json(dungeon_json)

        boss_keys = ItemFactory(['Boss Key (%s)' % name] * dungeon_info['boss_key'])
        if dungeon_info['id'] in world.settings.key_rings:
            small_keys = ItemFactory(['Small Key Ring (%s)' % name])
        else:
            if not world.dungeon_mq[dungeon_info['name']]:
                small_keys = ItemFactory(['Small Key (%s)' % name] * dungeon_info['small_key'])
            else:
                small_keys = ItemFactory(['Small Key (%s)' % name] * dungeon_info['small_key_mq'])
        dungeon_items = ItemFactory(['Map (%s)' % name, 
                                     'Compass (%s)' % name] * dungeon_info['dungeon_item'])
        if world.settings.shuffle_mapcompass in ['any_dungeon', 'overworld']:
            for item in dungeon_items:
                item.priority = True

        world.dungeons.append(Dungeon(world, name, hint, font_color, boss_keys, small_keys, dungeon_items))

