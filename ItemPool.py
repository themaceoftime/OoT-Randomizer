from collections import namedtuple
import logging
import random
from itertools import chain
from Utils import random_choices
from Item import ItemFactory
from ItemList import item_table
from LocationList import location_groups
from decimal import Decimal, ROUND_HALF_UP


# Generates itempools and places fixed items based on settings.

overworld_always_items = ([
    'Biggoron Sword',
    'Goron Tunic',
    'Zora Tunic',
    'Stone of Agony',
    'Fire Arrows',
    'Light Arrows',
    'Dins Fire',
    'Farores Wind',
    'Nayrus Love',
    'Rupee (1)']
    + ['Progressive Hookshot']
    + ['Hylian Shield']
    + ['Progressive Strength Upgrade']
    + ['Progressive Scale'] * 2
    + ['Recovery Heart']
    + ['Bow'] * 2
    + ['Slingshot'] * 2
    + ['Bomb Bag'] * 2
    + ['Bombs (5)']
    + ['Bombs (20)']
    + ['Progressive Wallet'] * 2
    + ['Magic Meter'] * 2
    + ['Double Defense']
    + ['Deku Stick Capacity']
    + ['Deku Nut Capacity']
    + ['Piece of Heart (Treasure Chest Game)'])


easy_items = ([
    'Biggoron Sword',
    'Kokiri Sword',
    'Boomerang',
    'Lens of Truth',
    'Megaton Hammer',
    'Iron Boots',
    'Goron Tunic',
    'Zora Tunic',
    'Hover Boots',
    'Mirror Shield',
    'Fire Arrows',
    'Light Arrows',
    'Dins Fire',
    'Progressive Hookshot',
    'Progressive Strength Upgrade',
    'Progressive Scale',
    'Progressive Wallet',
    'Magic Meter',
    'Deku Stick Capacity', 
    'Deku Nut Capacity', 
    'Bow', 
    'Slingshot', 
    'Bomb Bag',
    'Double Defense'] +
    ['Heart Container'] * 8 +
    ['Piece of Heart'])

normal_items = (['Piece of Heart'] * 33)


item_difficulty_max = {
    'plentiful': {},
    'balanced': {},
    'scarce': {
        'Bombchus': 3,
        'Bombchus (5)': 1,
        'Bombchus (10)': 2,
        'Bombchus (20)': 0,
        'Magic Meter': 1, 
        'Double Defense': 0, 
        'Deku Stick Capacity': 1, 
        'Deku Nut Capacity': 1, 
        'Bow': 2, 
        'Slingshot': 2, 
        'Bomb Bag': 2,
        'Heart Container': 0,
    },
    'minimal': {
        'Bombchus': 1,
        'Bombchus (5)': 1,
        'Bombchus (10)': 0,
        'Bombchus (20)': 0,
        'Magic Meter': 1, 
        'Nayrus Love': 1,
        'Double Defense': 0, 
        'Deku Stick Capacity': 0, 
        'Deku Nut Capacity': 0, 
        'Bow': 1, 
        'Slingshot': 1, 
        'Bomb Bag': 1,
        'Heart Container': 0,
        'Piece of Heart': 0,
    },
}

TriforceCounts = {
    'plentiful': Decimal(2.00),
    'balanced':  Decimal(1.50),
    'scarce':    Decimal(1.25),
    'minimal':   Decimal(1.00),
}

normal_bottles = [
    'Bottle',
    'Bottle with Milk',
    'Bottle with Red Potion',
    'Bottle with Green Potion',
    'Bottle with Blue Potion',
    'Bottle with Fairy',
    'Bottle with Fish',
    'Bottle with Bugs',
    'Bottle with Poe',
    'Bottle with Big Poe',
    'Bottle with Blue Fire']

bottle_count = 4


dungeon_rewards = [
    'Kokiri Emerald',
    'Goron Ruby',
    'Zora Sapphire',
    'Forest Medallion',
    'Fire Medallion',
    'Water Medallion',
    'Shadow Medallion',
    'Spirit Medallion',
    'Light Medallion'
]


normal_rupees = (
    ['Rupees (5)'] * 5 +
    ['Rupees (20)'] * 4 +
    ['Rupees (50)'] * 6 +
    ['Rupees (200)'] * 3)

shopsanity_rupees = (
    ['Rupees (20)'] * 6 +
    ['Rupees (50)'] * 6 +
    ['Rupees (200)'] * 5 +
    ['Progressive Wallet'])


min_shop_items = (
    ['Buy Deku Shield'] +
    ['Buy Hylian Shield'] +
    ['Buy Goron Tunic'] +
    ['Buy Zora Tunic'] +
    ['Buy Deku Nut (5)'] * 2 + ['Buy Deku Nut (10)'] +
    ['Buy Deku Stick (1)'] * 2 +
    ['Buy Deku Seeds (30)'] +
    ['Buy Arrows (10)'] * 2 + ['Buy Arrows (30)'] + ['Buy Arrows (50)'] +
    ['Buy Bombchu (5)'] + ['Buy Bombchu (10)'] * 2 + ['Buy Bombchu (20)'] +
    ['Buy Bombs (5) [25]'] + ['Buy Bombs (5) [35]'] + ['Buy Bombs (10)'] + ['Buy Bombs (20)'] +
    ['Buy Green Potion'] +
    ['Buy Red Potion [30]'] +
    ['Buy Blue Fire'] +
    ['Buy Fairy\'s Spirit'] +
    ['Buy Bottle Bug'] +
    ['Buy Fish'])


deku_scrubs_items = (
    ['Deku Nuts (5)'] * 5 +
    ['Deku Stick (1)'] +
    ['Bombs (5)'] * 5 +
    ['Recovery Heart'] * 4 +
    ['Rupees (5)'] * 4) # ['Green Potion']


songlist = [
    'Zeldas Lullaby',
    'Eponas Song',
    'Suns Song',
    'Sarias Song',
    'Song of Time',
    'Song of Storms',
    'Minuet of Forest',
    'Prelude of Light',
    'Bolero of Fire',
    'Serenade of Water',
    'Nocturne of Shadow',
    'Requiem of Spirit']


tradeitems = (
    'Pocket Egg',
    'Pocket Cucco',
    'Cojiro',
    'Odd Mushroom',
    'Poachers Saw',
    'Broken Sword',
    'Prescription',
    'Eyeball Frog',
    'Eyedrops',
    'Claim Check')

tradeitemoptions = (
    'pocket_egg',
    'pocket_cucco',
    'cojiro',
    'odd_mushroom',
    'poachers_saw',
    'broken_sword',
    'prescription',
    'eyeball_frog',
    'eyedrops',
    'claim_check')


fixedlocations = {
    'Ganon': 'Triforce',
    'Pierre': 'Scarecrow Song',
    'Deliver Rutos Letter': 'Deliver Letter',
    'Master Sword Pedestal': 'Time Travel',
    'Market Bombchu Bowling Bombchus': 'Bombchu Drop',
}

droplocations = {
    'Deku Baba Sticks': 'Deku Stick Drop',
    'Deku Baba Nuts': 'Deku Nut Drop',
    'Stick Pot': 'Deku Stick Drop',
    'Nut Pot': 'Deku Nut Drop',
    'Nut Crate': 'Deku Nut Drop',
    'Blue Fire': 'Blue Fire',
    'Lone Fish': 'Fish',
    'Fish Group': 'Fish',
    'Bug Rock': 'Bugs',
    'Bug Shrub': 'Bugs',
    'Wandering Bugs': 'Bugs',
    'Fairy Pot': 'Fairy',
    'Free Fairies': 'Fairy',
    'Wall Fairy': 'Fairy',
    'Butterfly Fairy': 'Fairy',
    'Gossip Stone Fairy': 'Fairy',
    'Bean Plant Fairy': 'Fairy',
    'Fairy Pond': 'Fairy',
    'Big Poe Kill': 'Big Poe',
}

junk_pool_base = [
    ('Bombs (5)',       8),
    ('Bombs (10)',      2),
    ('Arrows (5)',      8),
    ('Arrows (10)',     2),
    ('Deku Stick (1)',  5),
    ('Deku Nuts (5)',   5),
    ('Deku Seeds (30)', 5),
    ('Rupees (5)',      10),
    ('Rupees (20)',     4),
    ('Rupees (50)',     1),
]

pending_junk_pool = []
junk_pool = []


remove_junk_items = [
    'Bombs (5)',
    'Deku Nuts (5)',
    'Deku Stick (1)',
    'Recovery Heart',
    'Arrows (5)',
    'Arrows (10)',
    'Arrows (30)',
    'Rupees (5)',
    'Rupees (20)',
    'Rupees (50)',
    'Rupees (200)',
    'Deku Nuts (10)',
    'Bombs (10)',
    'Bombs (20)',
    'Deku Seeds (30)',
    'Ice Trap',
]
remove_junk_set = set(remove_junk_items)

exclude_from_major = [ 
    'Deliver Letter',
    'Sell Big Poe',
    'Magic Bean',
    'Zeldas Letter',
    'Bombchus (5)',
    'Bombchus (10)',
    'Bombchus (20)',
    'Odd Potion',
    'Triforce Piece'
]

item_groups = {
    'Junk': remove_junk_items,
    'JunkSong': ('Prelude of Light', 'Serenade of Water'),
    'AdultTrade': tradeitems,
    'Bottle': normal_bottles,
    'Spell': ('Dins Fire', 'Farores Wind', 'Nayrus Love'),
    'Shield': ('Deku Shield', 'Hylian Shield'),
    'Song': songlist,
    'NonWarpSong': songlist[0:6],
    'WarpSong': songlist[6:],
    'HealthUpgrade': ('Heart Container', 'Piece of Heart'),
    'ProgressItem': [name for (name, data) in item_table.items() if data[0] == 'Item' and data[1]],
    'MajorItem': [name for (name, data) in item_table.items() if (data[0] == 'Item' or data[0] == 'Song') and data[1] and name not in exclude_from_major],
    'DungeonReward': dungeon_rewards,

    'ForestFireWater': ('Forest Medallion', 'Fire Medallion', 'Water Medallion'),
    'FireWater': ('Fire Medallion', 'Water Medallion'),
}


def get_junk_item(count=1, pool=None, plando_pool=None):
    if count < 1:
        raise ValueError("get_junk_item argument 'count' must be greater than 0.")

    return_pool = []
    if pending_junk_pool:
        pending_count = min(len(pending_junk_pool), count)
        return_pool = [pending_junk_pool.pop() for _ in range(pending_count)]
        count -= pending_count

    if pool and plando_pool:
        jw_list = [(junk, weight) for (junk, weight) in junk_pool
                   if junk not in plando_pool or pool.count(junk) < plando_pool[junk].count]
        try:
            junk_items, junk_weights = zip(*jw_list)
        except ValueError:
            raise RuntimeError("Not enough junk is available in the item pool to replace removed items.")
    else:
        junk_items, junk_weights = zip(*junk_pool)
    return_pool.extend(random_choices(junk_items, weights=junk_weights, k=count))

    return return_pool


def replace_max_item(items, item, max):
    count = 0
    for i,val in enumerate(items):
        if val == item:
            if count >= max:
                items[i] = get_junk_item()[0]
            count += 1


def generate_itempool(world):
    junk_pool[:] = list(junk_pool_base)
    if world.settings.junk_ice_traps == 'on':
        junk_pool.append(('Ice Trap', 10))
    elif world.settings.junk_ice_traps in ['mayhem', 'onslaught']:
        junk_pool[:] = [('Ice Trap', 1)]

    fixed_locations = list(filter(lambda loc: loc.name in fixedlocations, world.get_locations()))
    for location in fixed_locations:
        item = fixedlocations[location.name]
        world.push_item(location, ItemFactory(item, world))
        location.locked = True

    drop_locations = list(filter(lambda loc: loc.type == 'Drop', world.get_locations()))
    for drop_location in drop_locations:
        item = droplocations[drop_location.name]
        world.push_item(drop_location, ItemFactory(item, world))
        drop_location.locked = True

    # set up item pool
    (pool, placed_items) = get_pool_core(world)
    world.itempool = ItemFactory(pool, world)
    for (location, item) in placed_items.items():
        world.push_item(location, ItemFactory(item, world))
        world.get_location(location).locked = True

    world.initialize_items()
    world.distribution.set_complete_itempool(world.itempool)


def try_collect_heart_container(world, pool):
    if 'Heart Container' in pool:
        pool.remove('Heart Container')
        pool.extend(get_junk_item())
        world.state.collect(ItemFactory('Heart Container'))
        return True
    return False


def try_collect_pieces_of_heart(world, pool):
    n = pool.count('Piece of Heart') + pool.count('Piece of Heart (Treasure Chest Game)')
    if n >= 4:
        for i in range(4):
            if 'Piece of Heart' in pool:
                pool.remove('Piece of Heart')
                world.state.collect(ItemFactory('Piece of Heart'))
            else:
                pool.remove('Piece of Heart (Treasure Chest Game)')
                world.state.collect(ItemFactory('Piece of Heart (Treasure Chest Game)'))
            pool.extend(get_junk_item())
        return True
    return False


def collect_pieces_of_heart(world, pool):
    success = try_collect_pieces_of_heart(world, pool)
    if not success:
        try_collect_heart_container(world, pool)


def collect_heart_container(world, pool):
    success = try_collect_heart_container(world, pool)
    if not success:
        try_collect_pieces_of_heart(world, pool)


def get_pool_core(world):
    pool = []
    placed_items = {
        'HC Zeldas Letter': 'Zeldas Letter',
    }

    if world.settings.shuffle_kokiri_sword:
        pool.append('Kokiri Sword')
    else:
        placed_items['KF Kokiri Sword Chest'] = 'Kokiri Sword'

    ruto_bottles = 1
    if world.settings.zora_fountain == 'open':
        ruto_bottles = 0
    elif world.settings.item_pool_value == 'plentiful':
        pending_junk_pool.append('Rutos Letter')

    if world.settings.skip_child_zelda:
        placed_items['HC Malon Egg'] = 'Recovery Heart'
    elif world.settings.shuffle_weird_egg:
        pool.append('Weird Egg')
    else:
        placed_items['HC Malon Egg'] = 'Weird Egg'

    if world.settings.shuffle_ocarinas:
        pool.extend(['Ocarina'] * 2)
        if world.settings.item_pool_value == 'plentiful':
            pending_junk_pool.append('Ocarina')
    else:
        placed_items['LW Gift from Saria'] = 'Ocarina'
        placed_items['HF Ocarina of Time Item'] = 'Ocarina'

    if world.settings.shuffle_beans:
        if world.distribution.get_starting_item('Magic Bean') < 10:
            pool.append('Magic Bean Pack')
            if world.settings.item_pool_value == 'plentiful':
                pending_junk_pool.append('Magic Bean Pack')
        else:
            pool.extend(get_junk_item())
    else:
        placed_items['ZR Magic Bean Salesman'] = 'Magic Bean'

    if world.settings.shuffle_medigoron_carpet_salesman:
        pool.append('Giants Knife')
    else:
        placed_items['GC Medigoron'] = 'Giants Knife'

    remain_shop_items = []
    # Use the vanilla items in the world's locations when appropriate.
    for location in world.get_locations():
        if location.vanilla_item is None:
            continue

        if location.type == "Shop":
            if world.settings.shopsanity == 'off':
                if world.settings.bombchus_in_logic and location.name in ['KF Shop Item 8', 'Market Bazaar Item 4', 'Kak Bazaar Item 4']:
                    placed_items[location.name] = 'Buy Bombchu (5)'
                else:
                    placed_items[location.name] = location.vanilla_item
            else:
                remain_shop_items.append(location.vanilla_item)
            continue

        if location.vanilla_item == 'Gold Skulltula Token':
            if world.settings.tokensanity == 'off' or (world.settings.tokensanity == 'dungeons' and location.dungeon) \
                    or (world.settings.tokensanity == 'overworld' and not location.dungeon):
                placed_items[location.name] = 'Gold Skulltula Token'
            else:
                pool.append('Gold Skulltula Token')
            continue

        if location.dungeon is not None:
            dungeon = location.dungeon
            if (world.settings.shuffle_bosskeys == 'vanilla' and dungeon.name != 'Ganons Castle' and location.vanilla_item == f"Boss Key ({dungeon.name})") \
                    or (world.settings.shuffle_mapcompass == 'vanilla' and location.vanilla_item in [f"Map ({dungeon.name})", f"Compass ({dungeon.name})"]) \
                    or (world.settings.shuffle_smallkeys == 'vanilla' and location.vanilla_item == f"Small Key ({dungeon.name})"):
                placed_items[location.name] = location.vanilla_item
                continue
            if location.type in ["Chest", "Collectable", "BossHeart"] \
                    and location.vanilla_item not in [f"Boss Key ({dungeon.name})", f"Map ({dungeon.name})", f"Compass ({dungeon.name})", f"Small Key ({dungeon.name})"]:
                item = location.vanilla_item
                if world.settings.bombchus_in_logic and item.startswith('Bombchus'):
                    item = 'Bombchus'
                pool.append(item)
                continue

        if location.type in ["Scrub", "GrottoNPC"]:
            if location.vanilla_item in ['Piece of Heart', 'Deku Stick Capacity', 'Deku Nut Capacity']:
                pool.append(location.vanilla_item)
            elif world.settings.shuffle_scrubs == 'off':
                placed_items[location.name] = location.vanilla_item
            continue

        if location.vanilla_item == 'Milk':
            if world.settings.shuffle_cows:
                pool.extend(get_junk_item())
            else:
                placed_items[location.name] = 'Milk'
            continue
    # End of Locations loop.

    if world.settings.bombchus_in_logic:
        pool.extend(['Bombchus'])
        if world.settings.shuffle_medigoron_carpet_salesman:
            pool.append('Bombchus')
    else:
        pool.extend(['Bombchus (10)'])
        if world.settings.shuffle_medigoron_carpet_salesman:
            pool.append('Bombchus (10)')

    if not world.settings.shuffle_medigoron_carpet_salesman:
        placed_items['Wasteland Bombchu Salesman'] = 'Bombchus (10)'

    if world.settings.gerudo_fortress == 'open':
        placed_items['Hideout Jail Guard (1 Torch)'] = 'Recovery Heart'
        placed_items['Hideout Jail Guard (2 Torches)'] = 'Recovery Heart'
        placed_items['Hideout Jail Guard (3 Torches)'] = 'Recovery Heart'
        placed_items['Hideout Jail Guard (4 Torches)'] = 'Recovery Heart'
    elif world.settings.shuffle_hideoutkeys in ['any_dungeon', 'overworld', 'keysanity']:
        if world.settings.gerudo_fortress == 'fast':
            pool.append('Small Key (Thieves Hideout)')
            placed_items['Hideout Jail Guard (2 Torches)'] = 'Recovery Heart'
            placed_items['Hideout Jail Guard (3 Torches)'] = 'Recovery Heart'
            placed_items['Hideout Jail Guard (4 Torches)'] = 'Recovery Heart'
        else:
            if 'Thieves Hideout' in world.settings.key_rings:
                pool.extend(['Small Key Ring (Thieves Hideout)'])
                pool.extend(get_junk_item(3))
            else:
                pool.extend(['Small Key (Thieves Hideout)'] * 4)
        if world.settings.item_pool_value == 'plentiful':
            if 'Thieves Hideout' in world.settings.key_rings and world.settings.gerudo_fortress != "fast":
                pending_junk_pool.extend(['Small Key Ring (Thieves Hideout)'])
            else:
                pending_junk_pool.append('Small Key (Thieves Hideout)')
    else:
        if world.settings.gerudo_fortress == 'fast':
            placed_items['Hideout Jail Guard (1 Torch)'] = 'Small Key (Thieves Hideout)'
            placed_items['Hideout Jail Guard (2 Torches)'] = 'Recovery Heart'
            placed_items['Hideout Jail Guard (3 Torches)'] = 'Recovery Heart'
            placed_items['Hideout Jail Guard (4 Torches)'] = 'Recovery Heart'
        else:
            placed_items['Hideout Jail Guard (1 Torch)'] = 'Small Key (Thieves Hideout)'
            placed_items['Hideout Jail Guard (2 Torches)'] = 'Small Key (Thieves Hideout)'
            placed_items['Hideout Jail Guard (3 Torches)'] = 'Small Key (Thieves Hideout)'
            placed_items['Hideout Jail Guard (4 Torches)'] = 'Small Key (Thieves Hideout)'

    if world.settings.shuffle_gerudo_card and world.settings.gerudo_fortress != 'open':
        pool.append('Gerudo Membership Card')
    elif world.settings.shuffle_gerudo_card:
        pending_junk_pool.append('Gerudo Membership Card')
        placed_items['Hideout Gerudo Membership Card'] = 'Ice Trap'
    else:
        placed_items['Hideout Gerudo Membership Card'] = 'Gerudo Membership Card'
    if world.settings.shuffle_gerudo_card and world.settings.item_pool_value == 'plentiful':
        pending_junk_pool.append('Gerudo Membership Card')

    if world.settings.shuffle_smallkeys != "vanilla":
        if 'Bottom of the Well' in world.settings.key_rings:
            pool.extend(get_junk_item(1 if world.dungeon_mq['Bottom of the Well'] else 2))
        if 'Forest Temple' in world.settings.key_rings:
            pool.extend(get_junk_item(5 if world.dungeon_mq['Forest Temple'] else 4))
        if 'Fire Temple' in world.settings.key_rings:
            pool.extend(get_junk_item(4 if world.dungeon_mq['Fire Temple'] else 7))
        if 'Water Temple' in world.settings.key_rings:
            pool.extend(get_junk_item(1 if world.dungeon_mq['Water Temple'] else 5))
        if 'Shadow Temple' in world.settings.key_rings:
            pool.extend(get_junk_item(5 if world.dungeon_mq['Shadow Temple'] else 4))
        if 'Spirit Temple' in world.settings.key_rings:
            pool.extend(get_junk_item(6 if world.dungeon_mq['Spirit Temple'] else 4))
        if 'Gerudo Training Ground' in world.settings.key_rings:
            pool.extend(get_junk_item(2 if world.dungeon_mq['Gerudo Training Ground'] else 8))
        if 'Ganons Castle' in world.settings.key_rings:
            pool.extend(get_junk_item(2 if world.dungeon_mq['Ganons Castle'] else 1))

    if world.settings.item_pool_value == 'plentiful' and world.settings.shuffle_smallkeys in ['any_dungeon', 'overworld', 'keysanity']:
        if 'Bottom of the Well' in world.settings.key_rings:
            pending_junk_pool.append('Small Key Ring (Bottom of the Well)')
        else:
            pending_junk_pool.append('Small Key (Bottom of the Well)')
        if 'Forest Temple' in world.settings.key_rings:
            pending_junk_pool.append('Small Key Ring (Forest Temple)')
        else:
            pending_junk_pool.append('Small Key (Forest Temple)')
        if 'Fire Temple' in world.settings.key_rings:
            pending_junk_pool.append('Small Key Ring (Fire Temple)')
        else:
            pending_junk_pool.append('Small Key (Fire Temple)')
        if 'Water Temple' in world.settings.key_rings:
            pending_junk_pool.append('Small Key Ring (Water Temple)')
        else:
            pending_junk_pool.append('Small Key (Water Temple)')
        if 'Shadow Temple' in world.settings.key_rings:
            pending_junk_pool.append('Small Key Ring (Shadow Temple)')
        else:
            pending_junk_pool.append('Small Key (Shadow Temple)')
        if 'Spirit Temple' in world.settings.key_rings:
            pending_junk_pool.append('Small Key Ring (Spirit Temple)')
        else:
            pending_junk_pool.append('Small Key (Spirit Temple)')
        if 'Gerudo Training Ground' in world.settings.key_rings:
            pending_junk_pool.append('Small Key Ring (Gerudo Training Ground)')
        else:
            pending_junk_pool.append('Small Key (Gerudo Training Ground)')
        if 'Ganons Castle' in world.settings.key_rings:
            pending_junk_pool.append('Small Key Ring (Ganons Castle)')
        else:
            pending_junk_pool.append('Small Key (Ganons Castle)')

    if world.settings.item_pool_value == 'plentiful' and world.settings.shuffle_bosskeys in ['any_dungeon', 'overworld', 'keysanity']:
        pending_junk_pool.append('Boss Key (Forest Temple)')
        pending_junk_pool.append('Boss Key (Fire Temple)')
        pending_junk_pool.append('Boss Key (Water Temple)')
        pending_junk_pool.append('Boss Key (Shadow Temple)')
        pending_junk_pool.append('Boss Key (Spirit Temple)')

    if world.settings.item_pool_value == 'plentiful' and world.settings.shuffle_ganon_bosskey in ['any_dungeon', 'overworld', 'keysanity']:
        pending_junk_pool.append('Boss Key (Ganons Castle)')

    if world.settings.shopsanity == 'off':
        pool.extend(normal_rupees)
    else:
        pool.extend(min_shop_items)
        for item in min_shop_items:
            remain_shop_items.remove(item)

        shop_slots_count = len(remain_shop_items)
        shop_nonitem_count = len(world.shop_prices)
        shop_item_count = shop_slots_count - shop_nonitem_count

        pool.extend(random.sample(remain_shop_items, shop_item_count))
        if shop_nonitem_count:
            pool.extend(get_junk_item(shop_nonitem_count))
        if world.settings.shopsanity == '0':
            pool.extend(normal_rupees)
        else:
            pool.extend(shopsanity_rupees)

    if world.settings.shuffle_scrubs != 'off':
        if world.dungeon_mq['Deku Tree']:
            pool.append('Deku Shield')
        if world.dungeon_mq['Dodongos Cavern']:
            pool.extend(['Deku Stick (1)', 'Deku Shield', 'Recovery Heart'])
        else:
            pool.extend(['Deku Nuts (5)', 'Deku Stick (1)', 'Deku Shield'])
        if not world.dungeon_mq['Jabu Jabus Belly']:
            pool.append('Deku Nuts (5)')
        if world.dungeon_mq['Ganons Castle']:
            pool.extend(['Bombs (5)', 'Recovery Heart', 'Rupees (5)', 'Deku Nuts (5)'])
        else:
            pool.extend(['Bombs (5)', 'Recovery Heart', 'Rupees (5)'])
        pool.extend(deku_scrubs_items)
        for _ in range(7):
            pool.append('Arrows (30)' if random.randint(0,3) > 0 else 'Deku Seeds (30)')

    pool.extend(overworld_always_items)

    for i in range(bottle_count):
        if i >= ruto_bottles:
            bottle = random.choice(normal_bottles)
            pool.append(bottle)
        else:
            pool.append('Rutos Letter')

    earliest_trade = tradeitemoptions.index(world.settings.logic_earliest_adult_trade)
    latest_trade = tradeitemoptions.index(world.settings.logic_latest_adult_trade)
    if earliest_trade > latest_trade:
        earliest_trade, latest_trade = latest_trade, earliest_trade
    tradeitem = random.choice(tradeitems[earliest_trade:latest_trade+1])
    world.selected_adult_trade_item = tradeitem
    pool.append(tradeitem)

    pool.extend(songlist)
    if world.settings.shuffle_song_items == 'any' and world.settings.item_pool_value == 'plentiful':
        pending_junk_pool.extend(songlist)

    if world.settings.free_scarecrow:
        world.state.collect(ItemFactory('Scarecrow Song'))
    
    if world.settings.no_epona_race:
        world.state.collect(ItemFactory('Epona', event=True))

    if world.settings.shuffle_mapcompass == 'remove' or world.settings.shuffle_mapcompass == 'startwith':
        for item in [item for dungeon in world.dungeons for item in dungeon.dungeon_items]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if world.settings.shuffle_smallkeys == 'remove':
        for item in [item for dungeon in world.dungeons for item in dungeon.small_keys]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if world.settings.shuffle_bosskeys == 'remove':
        for item in [item for dungeon in world.dungeons if dungeon.name != 'Ganons Castle' for item in dungeon.boss_key]:
            world.state.collect(item)
            pool.extend(get_junk_item())
    if world.settings.shuffle_ganon_bosskey in ['remove', 'triforce']:
        for item in [item for dungeon in world.dungeons if dungeon.name == 'Ganons Castle' for item in dungeon.boss_key]:
            world.state.collect(item)
            pool.extend(get_junk_item())

    if world.settings.shuffle_smallkeys == 'vanilla':
        # Logic cannot handle vanilla key layout in some dungeons
        # this is because vanilla expects the dungeon major item to be
        # locked behind the keys, which is not always true in rando.
        # We can resolve this by starting with some extra keys
        if world.dungeon_mq['Spirit Temple']:
            # Yes somehow you need 3 keys. This dungeon is bonkers
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
            world.state.collect(ItemFactory('Small Key (Spirit Temple)'))
        if 'shadow_temple' in world.settings.dungeon_shortcuts:
            # Reverse Shadow is broken with vanilla keys in both vanilla/MQ
            world.state.collect(ItemFactory('Small Key (Shadow Temple)'))
            world.state.collect(ItemFactory('Small Key (Shadow Temple)'))

    if not world.keysanity and not world.dungeon_mq['Fire Temple']:
        world.state.collect(ItemFactory('Small Key (Fire Temple)'))

    if world.settings.triforce_hunt:
        triforce_count = int((TriforceCounts[world.settings.item_pool_value] * world.settings.triforce_goal_per_world).to_integral_value(rounding=ROUND_HALF_UP))
        pending_junk_pool.extend(['Triforce Piece'] * triforce_count)

    if world.settings.shuffle_ganon_bosskey == 'on_lacs':
        placed_items['ToT Light Arrows Cutscene'] = 'Boss Key (Ganons Castle)'
    elif world.settings.shuffle_ganon_bosskey == 'vanilla':
        placed_items['Ganons Tower Boss Key Chest'] = 'Boss Key (Ganons Castle)'

    if world.settings.shuffle_ganon_bosskey in ['stones', 'medallions', 'dungeons', 'tokens']:
        placed_items['Gift from Sages'] = 'Boss Key (Ganons Castle)'
        pool.extend(get_junk_item())
    else:
        placed_items['Gift from Sages'] = 'Ice Trap'

    if world.settings.item_pool_value == 'plentiful':
        pool.extend(easy_items)
    else:
        pool.extend(normal_items)

    if not world.settings.shuffle_kokiri_sword:
        replace_max_item(pool, 'Kokiri Sword', 0)

    if world.settings.junk_ice_traps == 'off':
        replace_max_item(pool, 'Ice Trap', 0)
    elif world.settings.junk_ice_traps == 'onslaught':
        for item in [item for item, weight in junk_pool_base] + ['Recovery Heart', 'Bombs (20)', 'Arrows (30)']:
            replace_max_item(pool, item, 0)

    for item,max in item_difficulty_max[world.settings.item_pool_value].items():
        replace_max_item(pool, item, max)

    world.distribution.alter_pool(world, pool)

    # Make sure our pending_junk_pool is empty. If not, remove some random junk here.
    if pending_junk_pool:
        for item in set(pending_junk_pool):
            # Ensure pending_junk_pool contents don't exceed values given by distribution file
            if item in world.distribution.item_pool:
                while pending_junk_pool.count(item) > world.distribution.item_pool[item].count:
                    pending_junk_pool.remove(item)
                # Remove pending junk already added to the pool by alter_pool from the pending_junk_pool
                if item in pool:
                    count = min(pool.count(item), pending_junk_pool.count(item))
                    for _ in range(count):
                        pending_junk_pool.remove(item)

        remove_junk_pool, _ = zip(*junk_pool_base)
        # Omits Rupees (200) and Deku Nuts (10)
        remove_junk_pool = list(remove_junk_pool) + ['Recovery Heart', 'Bombs (20)', 'Arrows (30)', 'Ice Trap']

        junk_candidates = [item for item in pool if item in remove_junk_pool]
        while pending_junk_pool:
            pending_item = pending_junk_pool.pop()
            if not junk_candidates:
                raise RuntimeError("Not enough junk exists in item pool for %s to be added." % pending_item)
            junk_item = random.choice(junk_candidates)
            junk_candidates.remove(junk_item)
            pool.remove(junk_item)
            pool.append(pending_item)

    world.distribution.configure_starting_items_settings(world)
    world.distribution.collect_starters(world.state)

    return (pool, placed_items)
