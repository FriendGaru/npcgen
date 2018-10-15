import random
import csv
import itertools
import math
import string
import collections
from typing import Dict
import pkg_resources as pkg

# -1 - Nothing at all
# 0 - Errors only
# 1 - Basic operations
# 2 - Minor operations
# 3 - Painfully Verbose
DEBUG_LEVEL = 1

DATA_PATH = pkg.resource_filename('npcgen', 'data/')

ARMORS_FILE = \
    pkg.resource_filename(__name__, 'data/armors.csv')
WEAPONS_FILE = \
    pkg.resource_filename(__name__, 'data/weapons.csv')
TRAITS_FILE = \
    pkg.resource_filename(__name__, 'data/traits.csv')
SPELLS_FILE = \
    pkg.resource_filename(__name__, 'data/spells.csv')
SPELLLISTS_FILE = \
    pkg.resource_filename(__name__, 'data/spelllists.csv')
SPELLCASTER_PROFILES_FILE = \
    pkg.resource_filename(__name__, 'data/spellcasterprofiles.csv')
ARMORS_LOADOUT_POOLS_FILE = \
    pkg.resource_filename(__name__, 'data/loadoutpools_armors.csv')
WEAPONS_LOADOUT_POOLS_FILE = \
    pkg.resource_filename(__name__, 'data/loadoutpools_weapons.csv')
RACE_TEMPLATES_FILE = \
    pkg.resource_filename(__name__, 'data/racetemplates.csv')
CLASS_TEMPLATES_FILE = \
    pkg.resource_filename(__name__, 'data/classtemplates.csv')

STATS_ATTRIBUTES = ('str', 'dex', 'con', 'int', 'wis', 'cha',)
DEFAULT_ATTRIBUTE_VALUE = 8
ATTRIBUTES_ABBREVIATION_TO_FULL_WORD: Dict[str, str] = {
    'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution',
    'int': 'Intelligence', 'wis': 'Wisdom', 'cha': ' Charisma',
}

STATS_BASE = {
    'hit_dice_num': 1, 'hit_dice_size': 8,
    # extra hit dice are used ONLY for hp calculations
    'hit_dice_extra': 0, 'hit_points_extra': 0,
    'proficiency_extra': 0,
    'speed_walk': 30, 'speed_fly': 0, 'speed_burrow': 0, 'speed_swim': 0,
    # These are used for various trait implementations
    'bonus_hp_per_level': 0,  # Dwarf toughness
    'speed_bonus_universal': 0,
    'floating_attribute_points': 0,
    'breath_weapon_dice': 2,  # For dragonborn breath weapons
}

SKILLS = {
    'athletics': 'str',
    'acrobatics': 'dex',
    'sleight of hand': 'dex',
    'stealth': 'dex',
    'arcana': 'int',
    'history': 'int',
    'investigation': 'int',
    'nature': 'int',
    'religion': 'int',
    'animal handling': 'wis',
    'insight': 'wis',
    'medicine': 'wis',
    'perception': 'wis',
    'survival': 'wis',
    'deception': 'cha',
    'intimidation': 'cha',
    'performance': 'cha',
    'persuasion': 'cha',
}

ROLL_METHODS = {
    # 'internal_name': (
    #   'display_name',
    #   (roll_dice params),
    #   (fixed roll vals)
    #  )
    # Technically, don't really need the display name here, but might be useful later
    '3d6': (
        'Roll 3d6',
        (6, 3, 0, 0),
        ()
    ),
    '4d6dl': (
        'Roll 4d6, drop the lowest',
        (6, 3, 1, 0),
        ()
    ),
    '4d6dh': (
        'Roll 4d6, drop the highest',
        (6, 3, 0, 1),
        ()
    ),
    '5d6dldh': (
        'Roll 5d6, drop the lowest and highest',
        (6, 3, 1, 1),
        ()
    ),
    '5d6dl2': (
        'Roll 5d6, drop the two lowest',
        (6, 3, 2, 0),
        ()
    ),
    '5d6dh2': (
        'Roll 5d6, drop the two highest',
        (6, 3, 0, 2),
        ()
    ),
    '7d6dl2dh2': (
        'Roll 7d6, drop the two lowest and the two highest',
        (6, 3, 2, 2,),
        ()
    ),
    'array_standard': (
        'Standard Array (15, 14, 13, 12, 10, 8)',
        (6, 3, 0, 0,),
        (15, 14, 13, 12, 10, 8),
    ),
}

# Roll methods should be manually sorted for display
# Uses the same sorting style as race and class options
ROLL_METHODS_OPTIONS = (
    ('@CATEGORY', 'Random'),
    ('3d6', 'Roll 3d6'),
    ('4d6dl', 'Roll 4d6, drop lowest'),
    ('4d6dh', 'Roll 4d6, drop highest'),
    ('5d6dldh', 'Roll 5d6, drop lowest and highest',),
    ('5d6dl2', 'Roll 5d6, drop two lowest',),
    ('5d6dh2', 'Roll 5d6, drop two highest',),
    ('7d6dl2dh2', 'Roll 7d6, drop two lowest and highest',),
    ('@CATEGORY', 'Fixed Arrays'),
    ('array_standard', 'Standard Array (15, 14, 13, 12, 10, 8)',),
)

DEFAULT_ROLL_METHOD = '3d6'
# Max times a stat reroll is allowed, to prevent overflowing
REROLLS_CAP = 99
DEFAULT_HIT_DICE_NUM = 5
DEFAULT_HIT_DICE_SIZE = 8
# Max hit dice a character can have for generating stats
# Characters may still have bonus hd, which give extra hp but are not used for stat calculations
HIT_DICE_NUM_CAP = 20

VALID_HD_SIZES = (
    4, 6, 8, 10, 12
)

TRAIT_TYPES = (
    'hidden', 'passive', 'multiattack', 'action', 'reaction',
)

VALID_SIZES = (
    'small', 'medium', 'large',
)
DEFAULT_SIZE = 'medium'

DEFAULT_CREATURE_TYPE = 'humanoid'

DEFAULT_RACE = 'humanoid'
DEFAULT_CLASS = 'soldier'

LANGUAGES = (
    'common', 'dwarvish', 'elvish', 'giant', 'gnomish', 'goblin', 'halfling', 'orc',
    'abyssal', 'celestial', 'draconic', 'deep speech', 'infernal', 'primordial', 'sylvan', 'undercommon',
)

HEAVY_ARMOR_MOVE_PENALTY = -10

WEAPON_REACH_NORMAL = 5
WEAPON_REACH_W_BONUS = 10
DEFAULT_NUM_TARGETS = 1

# When building a loadout pool this is the weight applied to loadouts that have no specified weight
DEFAULT_LOADOUT_WEIGHT = 1

# Ability score increases, how often and how many points per increase
ASI_HD_PER_INCREASE = 4
ASI_POINTS_PER_INCREASE = 2
# How likely a character is to pick their priority stats vs a random one
ASI_PROGRESSION_PRIORITY_WEIGHT = 3
ASI_PROGRESSION_OTHER_WEIGHT = 1
# If enabled, this scale will be used to give decreasing weight to lesser priority attributes
# For example, with a priority weight of 3, other weight of 1, and a subsequent scale:
# If a character has str, dex, and con as priority attributes she would have the following weights when choosing an ASI
# str: 3, dex: 2.25, con: 1.6875, int: 1, wis: 1, cha: 1
ASI_PROGRESSION_PRIORITY_SUBSEQUENT_SCALE = 0.75
# A character will never go above this value when choosing ASIs
ASI_DEFAULT_ATTRIBUTE_CAP = 20

MAX_SPELL_CHOICES_PER_LEVEL = 10
DEFAULT_SPELLS_READIED_PROGRESSION = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 1,
    2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 1, 2, 3,
)

SPELL_SLOTS_TABLE = (
    # SPELL_SLOTS_TABLE[caster_level][spell_level]
    (),
    # 1
    (-1, 2, 0, 0, 0, 0, 0, 0, 0, 0,),
    (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
    (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
    (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
    (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
    # 6
    (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
    (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
    (-1, 4, 3, 3, 2, 0, 0, 0, 0, 0,),
    (-1, 4, 3, 3, 3, 1, 0, 0, 0, 0,),
    (-1, 4, 3, 3, 3, 2, 0, 0, 0, 0,),
    # 11
    (-1, 4, 3, 3, 3, 2, 1, 0, 0, 0,),
    (-1, 4, 3, 3, 3, 2, 1, 0, 0, 0,),
    (-1, 4, 3, 3, 3, 2, 1, 1, 0, 0,),
    (-1, 4, 3, 3, 3, 2, 1, 1, 0, 0,),
    (-1, 4, 3, 3, 3, 2, 1, 1, 1, 0,),
    # 16
    (-1, 4, 3, 3, 3, 2, 1, 1, 1, 0,),
    (-1, 4, 3, 3, 3, 2, 1, 1, 1, 1,),
    (-1, 4, 3, 3, 3, 3, 1, 1, 1, 1,),
    (-1, 4, 3, 3, 3, 3, 2, 1, 1, 1,),
    (-1, 4, 3, 3, 3, 3, 2, 2, 1, 1,),
)

CASTER_FIXED_SPELLS_KNOWN = {
    'sorcerer': (-1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15),
    'bard': (-1, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 15, 16, 18, 19, 19, 20, 22, 22, 22),
    'half': (-1, 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11),
    'third': (-1, 0, 0, 3, 4, 4, 4, 5, 6, 6, 7, 8, 8, 9, 10, 10, 11, 11, 11, 12, 13),
}

CASTER_CANTRIPS_KNOWN = {
    'none': (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,),
    'cleric_wizard': (-1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,),
    'sorcerer': (-1, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,),
    'bard_druid': (-1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,),
}

CHALLENGE_RATING_CHART = (
    # CR,    prof,  AC, HP,   hit,dpr,  saveDC
    ('0 (0 or 10 XP)', 2, 13, 6, 3, 1, 13),
    ('1/8 (25 XP)', 2, 13, 35, 3, 3, 13),
    ('1/4 (50 XP)', 2, 13, 49, 3, 5, 13),
    ('1/2 (100 XP)', 2, 13, 70, 3, 8, 13),
    ('1 (200 XP)', 2, 13, 85, 3, 14, 13),
    ('2 (450 XP)', 2, 13, 100, 3, 20, 13),
    ('3 (700 XP)', 2, 13, 115, 4, 26, 13),
    ('4 (1,100 XP)', 2, 14, 130, 5, 32, 14),
    ('5 (1,800 XP)', 3, 15, 145, 6, 38, 15),
    ('6 (2,300 XP)', 3, 15, 160, 6, 44, 15),
    ('7 (2,900 XP)', 3, 15, 175, 6, 50, 15),
    ('8 (3,900 XP)', 3, 16, 190, 7, 56, 16),
    ('9 (5,000 XP)', 4, 16, 205, 7, 62, 16),
    ('10 (5,900 XP)', 4, 17, 220, 7, 68, 16),
    ('11 (7,200 XP)', 4, 17, 235, 8, 74, 17),
    ('12 (8,400 XP)', 4, 17, 250, 8, 80, 17),
    ('13 (10,000 XP)', 5, 18, 265, 8, 74, 18),
    ('14 (11,500 XP)', 5, 18, 280, 8, 74, 18),
    ('15 (13,000 XP)', 5, 18, 295, 8, 74, 18),
    ('16 (15,000 XP)', 5, 18, 310, 9, 74, 18),
    ('17 (18,000 XP)', 6, 19, 325, 10, 74, 19),
    ('18 (20,000 XP)', 6, 19, 340, 10, 74, 19),
    ('19 (22,000 XP)', 6, 19, 355, 10, 74, 19),
    ('20 (25,000 XP)', 6, 19, 400, 10, 74, 19),
    ('21 (33,000 XP)', 7, 19, 445, 11, 74, 20),
    ('22 (41,000 XP)', 7, 19, 490, 11, 74, 20),
    ('23 (50,000 XP)', 7, 19, 535, 11, 74, 20),
    ('24 (62,000 XP)', 7, 19, 580, 12, 74, 21),
    ('25 (75,000 XP)', 8, 19, 625, 12, 74, 21),
    ('26 (90,000 XP)', 8, 19, 670, 12, 74, 21),
    ('27 (105,000 XP)', 8, 19, 715, 13, 74, 22),
    ('28 (120,000 XP)', 8, 19, 760, 13, 74, 22),
    ('29 (135,000 XP)', 9, 19, 805, 13, 74, 22),
    ('30 (155,000 XP)', 9, 19, 850, 14, 74, 23),
)

ORDINAL_TO_NUM = {
    'cantrip': 0,
    '1st': 1,
    '2nd': 2,
    '3rd': 3,
    '4th': 4,
    '5th': 5,
    '6th': 6,
    '7th': 7,
    '8th': 8,
    '9th': 9,
}

NUM_TO_ORDINAL = {
    1: '1st',
    2: '2nd',
    3: '3rd',
    4: '4th',
    5: '5th',
    6: '6th',
    7: '7th',
    8: '8th',
    9: '9th',
    10: '10th',
    11: '11th',
    12: '12th',
    13: '13th',
    14: '14th',
    15: '15th',
    16: '16th',
    17: '17th',
    18: '18th',
    19: '19th',
    20: '20th',
}

NUM_TO_TEXT = {
    0: 'zero',
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
}

NUM_TIMES_TO_TEXT = {
    0: 'zero',
    1: 'once',
    2: 'twice',
    3: 'three times',
    4: 'four times',
    5: 'five times',
    6: 'six times',
    7: 'seven times',
    8: 'eight times',
    9: 'nine times',
    10: 'ten times',
}

DEFAULT_SPELL_WEIGHT = 1

# Data for special traits
MARTIAL_ARTS_DAMAGE = (
    (-1, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 8, 10, 10, 10, 10,)
)


# Random functions can accept an instance of random,
# If they don't get one, they default to the global random
# Should make seeding more reliable and not have to screw with global seeding
def roll_die(die_size, rnd_instance=None):
    if not rnd_instance:
        rnd_instance = random
    return rnd_instance.randint(1, die_size)


def roll_dice(die_size, num_dice, drop_lowest=0, drop_highest=0, rnd_instance=None):
    """
    Rolls a number of dice and returns the total, dropping the lowest or highest dice values as specified.
    numDice is the number of dice to add up AFTER dropping dice.
    """
    dice_to_roll = num_dice + drop_lowest + drop_highest
    dice_pool = []
    for i in range(dice_to_roll):
        dice_pool.append(roll_die(die_size, rnd_instance))
    dice_pool.sort()
    if drop_highest > 0:
        dice_pool = dice_pool[drop_lowest:-drop_highest]
    else:
        dice_pool = dice_pool[drop_lowest:]
    return sum(dice_pool)


def weighted_sample(population, weights, k, rnd_instance=None):
    """
    This function draws a random sample of length k
    from the sequence 'population' according to the
    list of weights
    """
    if not rnd_instance:
        rnd_instance = random
    sample = set()
    population = list(population)
    weights = list(weights)
    while len(sample) < k:
        choice = rnd_instance.choices(population, weights)[0]
        sample.add(choice)
        index = population.index(choice)
        weights.pop(index)
        population.remove(choice)
        weights = [x / sum(weights) for x in weights]
    return list(sample)


def debug_print(message, required_level=2):
    """
    Prints out a message for debugging purposes. Higher numbers are more verbose, uses the DEBUG_LEVEL constant.
    """
    if DEBUG_LEVEL >= required_level:
        print(message)


def num_plusser(num, add_space=False):
    """
    Takes a number, returns a str with a '+' in front of it if it's 0 or more, as is standard for modifiers in DnD.
    If add_space == true, a space is included between the sign and the number
    """
    if num >= 0:
        if add_space:
            return '+ ' + str(num)
        else:
            return '+' + str(num)
    else:
        if add_space:
            return '- ' + str(abs(num))
        else:
            return str(num)


def nice_list(data):
    """
    Takes a list of strings and joins them in a nice, grammatical fashion
    a
    a and b
    a, b, and c
    a, b, c, and d
    """
    return ", ".join(data[:-2] + [" and ".join(data[-2:])])


def random_string(length, rnd_instance=None):
    if not rnd_instance:
        rnd_instance = random
    return ''.join(rnd_instance.choice(string.ascii_letters) for _ in range(length))


# I format my csv tag entries like 'tag_name:tag_val1;tag_val2,second_tag_name'
# This will break them apart and return dictionaries like {tag_name: [tag_val1, tag_val2], second_tag_name: []}
def csv_tag_reader(item_line, tag_delimiter=',', tag_value_separator=':', tag_val_delimiter=';'):
    tags_dict = {}
    for tag_raw in item_line.replace(" ", "").split(tag_delimiter):
        if tag_value_separator in tag_raw:
            tag_name, tag_values_raw = tag_raw.split(tag_value_separator)
            tag_val_list = tag_values_raw.split(tag_val_delimiter)
        else:
            tag_name, tag_val_list = tag_raw, []
        tags_dict[tag_name] = tag_val_list
    return tags_dict


class NPCGenerator:
    """
    NPC Generator builds all of the necessary data from external files, stores them, and builds instances of the
    Character class based on given parameters.
    """

    def __init__(self,
                 weapons_file_loc=WEAPONS_FILE,
                 armors_file_loc=ARMORS_FILE,
                 spells_file_loc=SPELLS_FILE,
                 spell_lists_file_loc=SPELLLISTS_FILE,
                 spellcaster_profiles_file_loc=SPELLCASTER_PROFILES_FILE,
                 # loadout_pools_file_loc=LOADOUT_POOLS_FILE,
                 armors_loadout_pools_file_loc=ARMORS_LOADOUT_POOLS_FILE,
                 weapons_loadout_pools_file_loc=WEAPONS_LOADOUT_POOLS_FILE,
                 traits_file_loc=TRAITS_FILE,
                 race_templates_file_loc=RACE_TEMPLATES_FILE,
                 class_templates_file_loc=CLASS_TEMPLATES_FILE,
                 ):

        self.weapons = {}
        self.build_weapons_from_csv(weapons_file_loc)

        self.armors = {}
        self.build_armors_from_csv(armors_file_loc)

        self.armors_loadout_pools = {}
        self.build_armors_loadout_pools_from_csv(armors_loadout_pools_file_loc)

        self.weapons_loadout_pools = {}
        self.build_weapons_loadout_pools_from_csv(weapons_loadout_pools_file_loc)

        self.traits = {}
        self.build_traits_from_csv(traits_file_loc)

        self.spells = {}
        self.build_spells_from_csv(spells_file_loc)

        self.spell_lists = {}
        self.build_spell_lists_from_csv(spell_lists_file_loc)

        self.spellcaster_profiles = {}
        self.build_spellcaster_profiles_from_csv(spellcaster_profiles_file_loc)

        # All ???_options attributes are intended to provide easy access to valid options when it comes time to render
        # They are of the format [(option internal_name, option display_name), ... ]
        # Entries may have the internal name "@CATEGORY", which indicates it is not a valid option, but rather a sorting
        # category, such as for categories in an html drop down menu
        # ???_keys, on the other hand, contain ONLY valid options for new_character() parameters
        # and can be used for easily grabbing valid random options or for validating requests

        self.race_templates = {}
        self.race_options = []  # For the HTML drop down boxes, includes categories for sorting
        self.race_keys = []
        self.race_random_categories = {}
        self.build_race_templates_from_csv(race_templates_file_loc)

        self.class_templates = {}
        self.class_options = []  # For the HTML drop down boxes, includes categories for sorting
        self.class_keys = []
        self.class_random_categories = {}
        self.build_class_templates_from_csv(class_templates_file_loc)

        self.roll_options = ROLL_METHODS_OPTIONS
        self.roll_keys = list(ROLL_METHODS.keys())

        self.hd_size_options = tuple(itertools.chain(['Default'], ['d' + str(x) for x in VALID_HD_SIZES]))

    def build_armors_from_csv(self, armors_file_loc):
        with open(armors_file_loc, newline='', encoding="utf-8") as armors_file:
            armors_file_reader = csv.DictReader(armors_file)
            for line in armors_file_reader:

                # Ignore blank lines or comments using hashtags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue

                new_armor = Armor()
                new_armor.int_name = line['internal_name']
                if line['display_name']:
                    new_armor.display_name = line['display_name']
                else:
                    new_armor.display_name = new_armor.int_name.capitalize()
                new_armor.base_ac = int(line['base_ac'])
                new_armor.armor_type = line['armor_type']
                if line['min_str']:
                    new_armor.min_str = int(line['min_str'])
                if line['stealth_disadvantage'] == 'TRUE':
                    new_armor.stealth_disadvantage = True
                new_armor.tags = set(line['tags'].replace(" ", "").split(','))
                self.armors[new_armor.int_name] = new_armor

    def build_weapons_from_csv(self, weapons_file_loc):
        with open(weapons_file_loc, newline='', encoding="utf-8") as weaponsFile:
            weapons_file_reader = csv.DictReader(weaponsFile)
            for line in weapons_file_reader:

                # Ignore blank lines or comments using hastags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue

                new_weapon = Weapon()
                new_weapon.int_name = line['internal_name']
                if line['display_name']:
                    new_weapon.display_name = line['display_name']
                else:
                    new_weapon.display_name = line['internal_name'].capitalize()
                new_weapon.dmg_dice_num = int(line['dmg_dice_num'])
                new_weapon.dmg_dice_size = int(line['dmg_dice_size'])
                new_weapon.damage_type = line['damage_type']
                new_weapon.attack_type = line['attack_type']
                if line['short_range']:
                    new_weapon.range_short = int(line['short_range'])
                if line['long_range']:
                    new_weapon.range_long = int(line['long_range'])
                new_weapon.tags = set(line['tags'].replace(" ", "").split(','))
                self.weapons[new_weapon.int_name] = new_weapon
                debug_print("Weapon Added: " + str(new_weapon), 3)

    def build_traits_from_csv(self, traits_file_loc):
        with open(traits_file_loc, newline='', encoding="utf-8") as traitsFile:
            traits_file_reader = csv.DictReader(traitsFile)
            for line in traits_file_reader:

                # Ignore blank lines or comments using hastags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue
                try:
                    new_trait_factory = TraitFactory()
                    new_trait_factory.int_name = line['internal_name']
                    if line['display_name']:
                        new_trait_factory.display_name = line['display_name']
                    else:
                        new_trait_factory.display_name = line['internal_name'].replace('_', ' ').title()

                    if line['recharge']:
                        new_trait_factory.recharge = line['recharge']

                    new_trait_factory.trait_type = line['trait_type']

                    if line['visibility']:
                        new_trait_factory.visibility = int(line['visibility'])
                    else:
                        new_trait_factory.visibility = 0

                    new_trait_factory.text = line['text'].replace('\\n', '\n\t')
                    if line['text_short']:
                        new_trait_factory.text_short = line['text_short'].replace('\\n', '\n\t')
                    else:
                        new_trait_factory.text_short = new_trait_factory.text

                    # if line['tags']:
                    #     new_tags_dict = {}
                    #     for raw_tag in line['tags'].replace(' ', '').split(','):
                    #         if ':' in raw_tag:
                    #             tag_name, tag_value = raw_tag.split(':')
                    #             # NOTE if you want to give multiple of something like armor or resistances, you need to
                    #             # use semicolons to separate them
                    #             # Each tag for a trait will ALWAYS have a list associated with it,
                    #             # remember when doing trait logic
                    #             new_tags_dict[tag_name] = tag_value.split(';')
                    #         else:
                    #             new_tags_dict[raw_tag] = None
                    #     new_trait_factory.tags = new_tags_dict

                    if line['tags']:
                        new_trait_factory.tags = csv_tag_reader(line['tags'])

                    self.traits[new_trait_factory.int_name] = new_trait_factory
                except (ValueError, TypeError):
                    print("Error procession trait {}".format(line['internal_name']))

    def build_armors_loadout_pools_from_csv(self, loadout_pools_file_loc):
        with open(loadout_pools_file_loc, newline="", encoding="utf-8") as loadoutPoolsFile:
            loadout_pools_file_reader = csv.DictReader(loadoutPoolsFile)
            new_loadout_pool = None
            for line in loadout_pools_file_reader:

                # loadout pools are a little different, blank lines mean they get added to the previous pool
                # Hashtag comment lines are still skippable
                # Completely blank lines should also be skipped
                if '#' in line['name']:
                    continue
                elif not line['name'] and not line['armors']:
                    continue

                if line['name']:
                    # If we get a new loadout pool, as specified by something int he name column,
                    # Add the current pool and start a new one
                    if new_loadout_pool:
                        self.armors_loadout_pools[new_loadout_pool.name] = new_loadout_pool
                    new_loadout_pool = LoadoutPool()
                    new_loadout_pool.name = line['name']
                if line['weight']:
                    weight = int(line['weight'])
                else:
                    weight = DEFAULT_LOADOUT_WEIGHT

                armors = line['armors'].replace(" ", "").split(',')

                new_loadout = Loadout()
                new_loadout.armors = armors
                new_loadout_pool.add_loadout(new_loadout, weight)

            # When we get to the end, add the last pool
            self.armors_loadout_pools[new_loadout_pool.name] = new_loadout_pool

    def build_weapons_loadout_pools_from_csv(self, loadout_pools_file_loc):
        with open(loadout_pools_file_loc, newline="", encoding="utf-8") as loadoutPoolsFile:
            loadout_pools_file_reader = csv.DictReader(loadoutPoolsFile)
            new_loadout_pool = None
            for line in loadout_pools_file_reader:

                # loadout pools are a little different, blank lines mean they get added to the previous pool
                # Hashtag comment lines are still skippable
                # Completely blank lines should also be skipped
                if '#' in line['name']:
                    continue
                elif not line['name'] and not line['weapons']:
                    continue

                if line['name']:
                    # If we get a new loadout pool, as specified by something int he name column,
                    # Add the current pool and start a new one
                    if new_loadout_pool:
                        self.weapons_loadout_pools[new_loadout_pool.name] = new_loadout_pool
                    new_loadout_pool = LoadoutPool()
                    new_loadout_pool.name = line['name']
                if line['weight']:
                    weight = int(line['weight'])
                else:
                    weight = DEFAULT_LOADOUT_WEIGHT

                weapons = line['weapons'].replace(" ", "").split(',')
                if line['shield']:
                    shield = True
                else:
                    shield = False

                new_loadout = Loadout()
                new_loadout.weapons = weapons
                new_loadout.shield = shield
                new_loadout_pool.add_loadout(new_loadout, weight)

            # When we get to the end, add the last pool
            self.weapons_loadout_pools[new_loadout_pool.name] = new_loadout_pool

    def build_spells_from_csv(self, spells_file_loc):
        with open(spells_file_loc, newline='', encoding="utf-8") as spellsFile:
            spells_file_reader = csv.DictReader(spellsFile)
            for line in spells_file_reader:

                # Ignore blank lines or comments using hastags
                if line['name'] == '' or '#' in line['name']:
                    continue

                new_spell = Spell()
                new_spell.name = line['name']
                new_spell.source = line['source']
                new_spell.level = ORDINAL_TO_NUM[line['level']]
                new_spell.school = line['school']
                new_spell.classes = set(line['classes'].replace(" ", "").split(','))
                self.spells[new_spell.name] = new_spell

    def build_spell_lists_from_csv(self, spell_lists_file_loc):
        with open(spell_lists_file_loc, newline='', encoding="utf-8") as spellListsFile:
            spell_lists_file_reader = csv.DictReader(spellListsFile)
            for line in spell_lists_file_reader:

                # Ignore blank lines or comments using hastags
                if line['name'] == '' or '#' in line['name']:
                    continue

                new_spell_list = SpellList()
                new_spell_list.name = line['name']

                # Check for if it's an autolist
                # If all these fields are blank, it's not an autolist
                if len(line['req_classes']) > 0 or len(line['req_schools']) > 0 \
                        or len(line['req_levels']) > 0 or len(line['req_sources']) > 0:
                    req_classes = None
                    if line['req_classes']:
                        req_classes = line['req_classes'].replace(" ", "").split(",")
                    req_schools = None
                    if line['req_schools']:
                        req_schools = set(line['req_schools'].replace(" ", "").split(","))
                    req_levels = None
                    if line['req_levels']:
                        req_levels = line['req_levels'].replace(" ", "").split(",")
                    req_sources = None
                    if line['req_sources']:
                        req_sources = line['req_sources'].replace(" ", "").split(",")

                    for spell_name, spell in self.spells.items():
                        if req_classes and spell.classes.isdisjoint(req_classes):
                            continue
                        if req_schools and spell.school not in req_schools:
                            continue
                        if req_levels and spell.level not in req_levels:
                            continue
                        if req_sources and spell.source not in req_sources:
                            continue
                        new_spell_list.add_spell(spell)

                if line['fixed_include']:
                    fixed_include_spells = line['fixed_include'].split(',')
                    for spell_name in fixed_include_spells:
                        spell_name = spell_name.strip()
                        if spell_name not in self.spells:
                            debug_print("Error! spell: '{}' from spelllist '{}' not in master spelllist!"
                                        .format(spell_name, new_spell_list.name), 0)
                        else:
                            new_spell_list.add_spell(self.spells[spell_name])

                if line['fixed_exclude']:
                    fixed_exclude_spells = line['fixed_exclude'].split(',')
                    for spell_name in fixed_exclude_spells:
                        spell_name = spell_name.strip()
                        if spell_name not in self.spells:
                            debug_print("Error! spell: '{}' from spelllist '{}' not in master spelllist!"
                                        .format(spell_name, new_spell_list.name), 0)
                        else:
                            new_spell_list.remove_spell(spell_name)

                if line['spelllists_include']:
                    spell_lists_to_include = line['spelllists_include'].replace(" ", "").split(',')
                    for spellListToInclude in spell_lists_to_include:
                        for spell_name, spell in spellListToInclude.spells.items():
                            new_spell_list.add_spell(spell)

                if line['spelllists_exclude']:
                    spell_lists_to_exclude = line['spelllists_exclude'].replace(" ", "").split(',')
                    for spellListToExclude in spell_lists_to_exclude:
                        spell_list = self.spell_lists[spellListToExclude]
                        for spell_name, spell in spell_list.spells.items():
                            new_spell_list.remove_spell(spell)

                self.spell_lists[new_spell_list.name] = new_spell_list

    # def build_spellcaster_profiles_from_csv(self, spellcaster_profiles_file_loc):
    #     with open(spellcaster_profiles_file_loc, newline="", encoding="utf-8") as spellcaster_profiles_file:
    #         spellcaster_profiles_file_reader = csv.DictReader(spellcaster_profiles_file)
    #         for line in spellcaster_profiles_file_reader:
    #
    #             try:
    #
    #                 # Ignore blank lines or comments using hastags
    #                 if line['internal_name'] == '' or '#' in line['internal_name']:
    #                     continue
    #
    #                 new_spellcaster_profile = SpellCasterProfile()
    #                 new_spellcaster_profile.intName = line['internal_name']
    #                 new_spellcaster_profile.casting_stat = line['casting_stat']
    #                 new_spellcaster_profile.ready_style = line['ready_style']
    #
    #                 # Alternative slots progressions not implemented
    #                 # Probably not needed, since all casters currently in the game derive their slots from the standard
    #                 new_spellcaster_profile.spell_slots_table = SPELL_SLOTS_TABLE
    #
    #                 if line["hd_per_casting_level"]:
    #                     new_spellcaster_profile.hd_per_casting_level = int(line['hd_per_casting_level'])
    #                 else:
    #                     new_spellcaster_profile.hd_per_casting_level = 1
    #
    #                 new_spellcaster_profile.cantrips_per_level = CASTER_CANTRIPS_KNOWN[line['cantrips_per_level']]
    #
    #                 if line['fixed_spells_known_by_level']:
    #                     new_spellcaster_profile.fixed_spells_known_by_level = \
    #                         CASTER_FIXED_SPELLS_KNOWN[line['fixed_spells_known_by_level']]
    #                 else:
    #                     new_spellcaster_profile.fixed_spells_known_by_level = None
    #
    #                 if line['spells_known_modifier']:
    #                     new_spellcaster_profile.spells_known_modifier = int(line['spells_known_modifier'])
    #                 else:
    #                     new_spellcaster_profile.spells_known_modifier = 0
    #
    #                 if line['free_spell_lists']:
    #                     for spell_list_name in line['free_spell_lists'].replace(" ", "").split(','):
    #                         new_spellcaster_profile.free_spell_lists.append(self.spell_lists[spell_list_name])
    #                 else:
    #                     new_spellcaster_profile.free_spell_lists = None
    #
    #                 new_spell_lists_dict = {}
    #                 for rawEntry in line['spell_lists'].replace(" ", "").split(','):
    #                     if ':' in rawEntry:
    #                         spell_list_name, weight = rawEntry.split(':')
    #                         new_spell_lists_dict[self.spell_lists[spell_list_name]] = weight
    #                     else:
    #                         new_spell_lists_dict[self.spell_lists[rawEntry]] = DEFAULT_SPELL_WEIGHT
    #                 new_spellcaster_profile.spell_lists = new_spell_lists_dict
    #
    #                 # For now, only standard slots progression
    #                 # In the future, may add support for nonstandard slot progressions, like warlock
    #                 new_spellcaster_profile.spell_slots_table = SPELL_SLOTS_TABLE
    #
    #                 self.spellcaster_profiles[new_spellcaster_profile.intName] = new_spellcaster_profile
    #
    #             except (ValueError, TypeError):
    #                 debug_print("Failed to build spellcaster profile: {}".format(line['internal_name']), 0)

    def build_spellcaster_profiles_from_csv(self, spellcaster_profiles_file_loc):
        with open(spellcaster_profiles_file_loc, newline="", encoding="utf-8") as spellcaster_profiles_file:
            spellcaster_profiles_file_reader = csv.DictReader(spellcaster_profiles_file)
            for line in spellcaster_profiles_file_reader:

                try:

                    # Ignore blank lines or comments using hastags
                    if line['internal_name'] == '' or '#' in line['internal_name']:
                        continue

                    new_spellcaster_profile = SpellCasterProfile()
                    new_spellcaster_profile.intName = line['internal_name']
                    new_spellcaster_profile.casting_stat = line['casting_stat']
                    new_spellcaster_profile.ready_style = line['ready_style']

                    if line["hd_per_casting_level"]:
                        new_spellcaster_profile.hd_per_casting_level = int(line['hd_per_casting_level'])
                    else:
                        new_spellcaster_profile.hd_per_casting_level = 1

                    if line['cantrips_per_level']:
                        new_spellcaster_profile.cantrips_per_level = line['cantrips_per_level']
                    else:
                        new_spellcaster_profile.cantrips_per_level = None

                    if line['fixed_spells_known_by_level']:
                        new_spellcaster_profile.fixed_spells_known_by_level = line['fixed_spells_known_by_level']
                    else:
                        new_spellcaster_profile.fixed_spells_known_by_level = None

                    if line['spells_known_modifier']:
                        new_spellcaster_profile.spells_known_modifier = int(line['spells_known_modifier'])
                    else:
                        new_spellcaster_profile.spells_known_modifier = 0

                    if line['free_spell_lists']:
                        new_spellcaster_profile.free_spell_lists = line['free_spell_lists'].replace(" ", "").split(',')
                    else:
                        new_spellcaster_profile.free_spell_lists = None

                    new_spell_lists_dict = {}
                    for rawEntry in line['spell_lists'].replace(" ", "").split(','):
                        if ':' in rawEntry:
                            spell_list_name, weight = rawEntry.split(':')
                            new_spell_lists_dict[spell_list_name] = weight
                        else:
                            new_spell_lists_dict[rawEntry] = DEFAULT_SPELL_WEIGHT
                    new_spellcaster_profile.spell_lists = new_spell_lists_dict

                    if line['tags']:
                        new_tags_dict = {}
                        for raw_tag in line['tags'].replace(' ', '').split(','):
                            if ':' in raw_tag:
                                tag_name, tag_value = raw_tag.split(':')
                                # NOTE if you want to give multiple of something like armor or resistances, you need to
                                # use semicolons to separate them
                                # Each tag for a trait will ALWAYS have a list associated with it,
                                # remember when doing trait logic
                                new_tags_dict[tag_name] = tag_value.split(';')
                            else:
                                new_tags_dict[raw_tag] = None
                        new_spellcaster_profile.tags = new_tags_dict

                    # For now, only standard slots progression
                    # In the future, may add support for nonstandard slot progressions, like warlock
                    new_spellcaster_profile.spell_slots_table = SPELL_SLOTS_TABLE

                    self.spellcaster_profiles[new_spellcaster_profile.intName] = new_spellcaster_profile

                except (ValueError, TypeError):
                    debug_print("Failed to build spellcaster profile: {}".format(line['internal_name']), 0)

    def build_race_templates_from_csv(self, race_templates_file_loc):
        with open(race_templates_file_loc, newline='', encoding="utf-8") as race_templates_file:
            race_templates_file_reader = csv.DictReader(race_templates_file)

            current_category = ''
            add_random_entries = False
            for line in race_templates_file_reader:

                # Ignore blank lines or comments using hashtags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue

                # For building random categories automatically
                elif line['internal_name'] == '@CATEGORY':
                    self.race_options.append(('@CATEGORY', line['display_name']))
                    current_category = line['display_name'].lower().replace(' ', '_')
                    add_random_entries = False
                    continue
                elif line['internal_name'] == '@RANDOM':
                    self.race_options.append(('random_' + current_category, line['display_name']))
                    self.race_random_categories['random_' + current_category] = []
                    self.race_keys.append('random_' + current_category)
                    add_random_entries = True
                    continue
                elif add_random_entries:
                    self.race_random_categories['random_' + current_category].append(line['internal_name'])

                try:
                    new_race_template = RaceTemplate()
                    new_race_template.int_name = line["internal_name"]
                    if line["display_name"]:
                        new_race_template.display_name = line['display_name']
                    else:
                        new_race_template.display_name = line['internal_name'].capitalize()

                    new_attribute_bonuses_dict = {}
                    if line['attribute_bonuses']:
                        for raw_attribute_bonus in line['attribute_bonuses'].replace(' ', '').split(','):
                            attribute, bonus = raw_attribute_bonus.split(':')
                            bonus = int(bonus)
                            new_attribute_bonuses_dict[attribute] = bonus
                    new_race_template.attribute_bonuses = new_attribute_bonuses_dict

                    new_race_template.languages = line['languages'].replace(" ", "").split(',')

                    if line['creature_type']:
                        new_race_template.creature_type = line['creature_type']
                    else:
                        new_race_template.creature_type = DEFAULT_CREATURE_TYPE

                    if line['size']:
                        new_race_template.size = line['size']
                    else:
                        new_race_template.size = DEFAULT_SIZE

                    if line['speeds']:
                        for entry in line['speeds'].replace(' ', '').split(','):
                            speed, val = entry.split(':')
                            new_race_template.speeds[speed] = int(val)

                    if line['traits']:
                        new_race_template.traits = line['traits'].replace(" ", "").split(',')

                    if line['languages']:
                        new_race_template.languages = line['languages'].replace(" ", "").split(',')

                    if line['features']:
                        new_features_dict = {}
                        for raw_feature in line['features'].replace(' ', '').split(','):
                            if ':' in raw_feature:
                                feature_name, feature_value = raw_feature.split(':')
                                # NOTE if you want to give multiple of something like armor or resistances, you need to
                                # use semicolons to separate them
                                # Each tag for a trait will ALWAYS have a list associated with it,
                                # remember when doing trait logic
                                new_features_dict[feature_name] = feature_value.split(';')
                            else:
                                new_features_dict[raw_feature] = []
                        new_race_template.features = new_features_dict

                    self.race_options.append((new_race_template.int_name, new_race_template.display_name))
                    self.race_templates[new_race_template.int_name] = new_race_template
                    self.race_keys.append(new_race_template.int_name)

                except ValueError:
                    print("Error processing race template {}".format(line['internal_name']))

    def build_class_templates_from_csv(self, class_templates_file_loc):
        with open(class_templates_file_loc, newline='', encoding="utf-8") as class_templates_file:
            class_templates_file_reader = csv.DictReader(class_templates_file)

            current_category = ''
            add_random_entries = False
            for line in class_templates_file_reader:

                # Ignore blank lines or comments using hashtags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue

                # For building random categories automatically
                elif line['internal_name'] == '@CATEGORY':
                    self.class_options.append(('@CATEGORY', line['display_name']))
                    current_category = line['display_name'].lower().replace(' ', '_')
                    add_random_entries = False
                    continue
                elif line['internal_name'] == '@RANDOM':
                    self.class_options.append(('random_' + current_category, line['display_name']))
                    self.class_random_categories['random_' + current_category] = []
                    self.class_keys.append('random_' + current_category)
                    add_random_entries = True
                    continue
                elif add_random_entries:
                    self.class_random_categories['random_' + current_category].append(line['internal_name'])

                try:
                    new_class_template = ClassTemplate()
                    new_class_template.int_name = line['internal_name']

                    if line['display_name']:
                        new_class_template.display_name = line['display_name']
                    else:
                        new_class_template.display_name = line['internal_name'].replace('_', ' ').capitalize()

                    new_class_template.priority_attributes = line['priority_attributes'].replace(" ", "").split(',')
                    new_class_template.hd_size = int(line['hd_size'])

                    new_class_template.saves = line['saves'].replace(" ", "").split(',')
                    new_class_template.skills_fixed = line['skills_fixed'].replace(" ", "").split(',')
                    new_class_template.skills_random = line['skills_random'].replace(" ", "").split(',')
                    if line['num_random_skills']:
                        new_class_template.num_random_skills = int(line['num_random_skills'])
                    else:
                        new_class_template.num_random_skills = 0

                    # if line['loadout_pool']:
                    #     new_class_template.loadout_pool = line['loadout_pool']

                    if line['weapons_loadout']:
                        new_class_template.weapons_loadout_pool = line['weapons_loadout']

                    if line['armors_loadout']:
                        new_class_template.armors_loadout_pool = line['armors_loadout']

                    if line['multiattack_type']:
                        new_class_template.multiattack_type = line['multiattack_type']

                    if line['traits']:
                        new_class_template.traits = line['traits'].replace(" ", "").split(',')

                    if line['spellcasting_profile']:
                        new_class_template.spell_casting_profile = \
                            self.spellcaster_profiles[line['spellcasting_profile']]

                    if line['cr_calc']:
                        new_class_template.cr_calc_type = line['cr_calc']
                    else:
                        new_class_template.cr_calc_type = 'attack'

                    if line['features']:
                        new_features_dict = {}
                        for raw_feature in line['features'].replace(' ', '').split(','):
                            if ':' in raw_feature:
                                feature_name, feature_value = raw_feature.split(':')
                                # NOTE if you want to give multiple of something like armor or resistances, you need to
                                # use semicolons to separate them
                                # Each tag for a trait will ALWAYS have a list associated with it,
                                # remember when doing trait logic
                                new_features_dict[feature_name] = feature_value.split(';')
                            else:
                                new_features_dict[raw_feature] = []
                        new_class_template.features = new_features_dict

                    self.class_options.append((new_class_template.int_name, new_class_template.display_name))
                    self.class_templates[new_class_template.int_name] = new_class_template
                    self.class_keys.append(new_class_template.int_name)

                except ValueError:
                    print("Error processing class template {}.".format(line['internal_name']))

    # def give_trait(self, character: 'Character', trait_name, rnd_instance=None, process_tags=True):
    #
    #     # Process tags means the trait will execute tag stuff
    #     # This allows a handful of traits to basically give themselves to the character for the sake of ordering
    #
    #     if not rnd_instance:
    #         rnd_instance = random
    #
    #     assert trait_name in self.traits, "Trait {} not found!".format(trait_name)
    #
    #     trait = self.traits[trait_name]
    #
    #     # If a character already has the trait from another source,
    #     # and doesn't have the repeatable tag, don't give again
    #     if trait_name in character.traits and 'repeatable' not in trait.tags:
    #         return
    #
    #     # Remember,
    #     # trait.tags = {tag_name: [tag_val_1, tag_val_2, ...], ...}
    #     # each tag ALWAYS has a list associated with it even if it's for a single value
    #
    #     # Some tags might implicitly require that the trait should not be given to the character
    #     # Traits that give other traits, for example
    #     # They can set this flag to false to block the giving at the end
    #     give_trait = True
    #
    #     if process_tags:
    #         if 'give_armor' in trait.tags:
    #             for armor in trait.tags['give_armor']:
    #                 self.give_armor(character, armor)
    #
    #         if 'give_weapon' in trait.tags:
    #             for weapon in trait.tags['give_weapon']:
    #                 self.give_weapon(character, weapon)
    #
    #         if 'give_tag' in trait.tags:
    #             for character_tag in trait.tags['give_tag']:
    #                 character.add_tag(character_tag)
    #
    #         # Tools and skills are considered the same, anything not in SKILLS is considered a tool
    #         if 'skill_proficiency' in trait.tags:
    #             for skill in trait.tags['skill_proficiency']:
    #                 skill = skill.replace('_', ' ')
    #                 if skill not in character.skills:
    #                     character.add_skill(skill)
    #                 elif len(character.get_non_proficient_skills()) > 0:
    #                     random_skill = rnd_instance.choice(character.get_non_proficient_skills())
    #                     debug_print('Trait {}: {} already present, adding {} instead'
    #                                 .format(trait_name, skill, random_skill))
    #                     character.add_skill(random_skill)
    #
    #         if 'skill_random' in trait.tags:
    #             num_random_skills = int(trait.tags['skill_random'][0])
    #             for i in range(num_random_skills):
    #                 if len(character.get_non_proficient_skills()) > 0:
    #                     random_skill = rnd_instance.choice(character.get_non_proficient_skills())
    #                     debug_print('Trait {}: giving random skill {}.'
    #                                 .format(trait_name, random_skill))
    #                     character.add_skill(random_skill)
    #
    #         if 'expertise_random' in trait.tags:
    #             num_expertise = int(trait.tags['expertise_random'][0])
    #             expertise_choices = rnd_instance.sample(character.skills, num_expertise)
    #             for choice in expertise_choices:
    #                 character.add_skill(choice, expertise=True)
    #
    #         if 'expertise_fixed' in trait.tags:
    #             expertise_choices = trait.tags['expertise_random']
    #             for choice in expertise_choices:
    #                 character.add_skill(choice, expertise=True)
    #
    #         if 'damage_immunity' in trait.tags:
    #             for entry in trait.tags['damage_immunity']:
    #                 character.add_damage_immunity(entry)
    #
    #         if 'damage_vulnerability' in trait.tags:
    #             for entry in trait.tags['damage_vulnerability']:
    #                 character.add_damage_vulnerability(entry)
    #
    #         if 'damage_resistance' in trait.tags:
    #             for entry in trait.tags['damage_resistance']:
    #                 character.add_damage_resistance(entry)
    #
    #         if 'condition_immunity' in trait.tags:
    #             for entry in trait.tags['condition_immunity']:
    #                 character.add_condition_immunity(entry)
    #
    #         if 'save_advantage' in trait.tags:
    #             for advantage in trait.tags['save_advantage']:
    #                 character.add_save_advantage(advantage)
    #
    #         if 'save_disadvantage' in trait.tags:
    #             for disadvantage in trait.tags['save_disadvantage']:
    #                 character.add_save_disadvantage(disadvantage)
    #
    #         if 'sense_darkvision' in trait.tags:
    #             val = int(trait.tags['sense_darkvision'][0])
    #             character.senses['darkvision'] = max(character.senses.get('darkvision', 0), val)
    #
    #         if 'bonus_hp_per_level' in trait.tags:
    #             val = int(trait.tags['bonus_hp_per_level'][0])
    #             character.stats['bonus_hp_per_level'] += val
    #
    #         if 'floating_attribute_bonus' in trait.tags:
    #             val = int(trait.tags['floating_attribute_bonus'][0])
    #             character.stats['floating_attribute_points'] += val
    #
    #         if 'random_language' in trait.tags:
    #             num_extra_languages = trait.tags['random_language'][0]
    #             language_options = set(LANGUAGES)
    #             for language in character.languages:
    #                 language_options.remove(language)
    #             language_choices = rnd_instance.sample(language_options, num_extra_languages)
    #             for language in language_choices:
    #                 character.add_language(language)
    #
    #         if 'random_subtraits' in trait.tags:
    #             # If the first val is an int, then that's how many subtraits to give
    #             # If it's not, assume we need only one
    #             try:
    #                 num_subtraits = int(trait.tags['random_subtraits'][0])
    #                 trait_options = trait.tags['random_subtraits'][1:]
    #             except ValueError:
    #                 num_subtraits = 1
    #                 trait_options = trait.tags['random_subtraits'][:]
    #             assert num_subtraits <= len(trait_options), \
    #                 "Trait {} doesn't have enough subtrait options!!".format(trait_name)
    #             trait_choices = rnd_instance.sample(trait_options, num_subtraits)
    #             # We're going to call this function again to give this trait to the character, but without processing
    #             # the tags, hopefully ensuring things end up in the right order
    #             self.give_trait(character, trait_name, rnd_instance=rnd_instance, process_tags=False)
    #             for trait_choice in trait_choices:
    #                 self.give_trait(character, trait_choice, rnd_instance=rnd_instance, process_tags=True)
    #             give_trait = False
    #
    #     # happens at end because some traits might not actually get added
    #     # All traits get added to the character's dictionary, and non-hidden ones get added to the order attributes
    #     # Complicated, but this will maintain trait order which can be important for traits with subtraits
    #     if give_trait:
    #         character.traits[trait_name] = trait

    def give_armor(self, character, armor_name, extra=False):
        armor = self.armors[armor_name]
        if extra:
            character.extra_armors[armor_name] = armor
        else:
            character.armors[armor_name] = armor

    def give_weapon(self, character, weapon_name):
        weapon = self.weapons[weapon_name]
        character.weapons[weapon_name] = weapon

    # Applies everything EXCEPT features/traits
    def apply_race_template(self, character: 'Character', race_template):

        if type(race_template) == str:
            race_template = self.race_templates[race_template]
        assert isinstance(race_template, RaceTemplate), \
            "apply_race_template() requires either a RaceTemplate or a string indicating a valid RaceTemplate"

        character.race_name = race_template.display_name
        character.attribute_bonuses = race_template.attribute_bonuses
        for k, v in race_template.base_stats.items():
            character.set_stat(k, v)
        character.creature_type = race_template.creature_type
        character.size = race_template.size
        for k, v in race_template.speeds.items():
            character.set_stat('speed_' + k, v)
        for k, v in race_template.senses.items():
            character.set_stat('sense_' + k, v)
        for language in race_template.languages:
            character.add_language(language)

    # Applies everything EXCEPT features/traits
    def apply_class_template(self, character: 'Character', class_template, seed=None):

        if not seed:
            seed = random_string(10)

        if type(class_template) == str:
            class_template = self.class_templates[class_template]
        assert isinstance(class_template, ClassTemplate), \
            "apply_class_template() requires either a ClassTemplate or a string indicating a valid ClassTemplate"

        character.class_name = class_template.display_name
        character.priority_attributes = class_template.priority_attributes

        rnd_instance = random.Random(seed + 'skills')
        fixed_skills = class_template.skills_fixed
        randomized_skills = rnd_instance.sample(class_template.skills_random, class_template.num_random_skills)
        skills_to_add = itertools.chain(fixed_skills, randomized_skills)
        for skill in skills_to_add:
            if skill in character.skills and len(character.get_non_proficient_skills()) > 0:
                replacement_skill = rnd_instance.choice(character.get_non_proficient_skills())
                debug_print('Class {}: Already proficient in {}, adding {} instead.'
                            .format(class_template.int_name, skill, replacement_skill))
                character.add_skill(replacement_skill)
            else:
                character.add_skill(skill)

        for save in class_template.saves:
            character.saves.add(save)

        for language in class_template.languages:
            character.add_language(language)

        if class_template.multiattack_type:
            character.multiattack = class_template.multiattack_type

        if class_template.armors_loadout_pool:
            loadout_pool = self.armors_loadout_pools[class_template.armors_loadout_pool]
            loadout = loadout_pool.get_random_loadout(rnd_instance=random.Random(seed + 'armorsloadout'))
            if loadout.armors:
                for armor in loadout.armors:
                    self.give_armor(character, armor)

        if class_template.weapons_loadout_pool:
            loadout_pool = self.weapons_loadout_pools[class_template.weapons_loadout_pool]
            loadout = loadout_pool.get_random_loadout(rnd_instance=random.Random(seed + 'weaponsloadout'))
            if loadout.weapons:
                for weapon in loadout.weapons:
                    self.give_weapon(character, weapon)
            character.has_shield = loadout.shield

    # Take a string, grab the correct CharacterFeatureFactory, and get the CharacterFeature
    def build_character_feature(self, feature_string, character, seed, short, args_tup):
        if feature_string == 'multiattack':
            return FeatureMultiattack(character=character, npc_gen=self, seed=seed, short=short, args_tup=args_tup)
        elif feature_string == 'spellcasting':
            return FeatureSpellcasting(character=character, npc_gen=self, seed=seed, short=short, args_tup=args_tup)
        elif feature_string == 'tinker':
            return FeatureTinker(character=character, npc_gen=self, seed=seed, short=short, args_tup=args_tup)
        elif feature_string == 'dragonborn_feature':
            return FeatureDragonborn(character=character, npc_gen=self, seed=seed, short=short, args_tup=args_tup)
        else:
            debug_print("'{}' has not been associated with CharacterFeature class!".format(feature_string), 0)
            raise ValueError

    def new_character(self,

                      seed=None,
                      race_choice=DEFAULT_RACE,
                      class_choice=DEFAULT_CLASS,
                      hit_dice_num=DEFAULT_HIT_DICE_NUM,
                      attribute_roll_method=DEFAULT_ROLL_METHOD,

                      name='',
                      rerolls_allowed=0,
                      min_total=0,
                      no_attribute_swapping=False,
                      force_optimize=False,
                      hit_dice_size=None,
                      bonus_hd=0,
                      no_asi=False,
                      ):

        if not seed:
            seed = random_string(10)

        debug_print('Starting build: {} {} {}d{} (+{}hd) seed={} roll={}'
                    .format(race_choice, class_choice, hit_dice_num, hit_dice_size, bonus_hd,
                            seed, attribute_roll_method), 1)

        rnd_instance = random.Random(seed + 'random_race')
        if race_choice in self.race_random_categories:
            race_choice = rnd_instance.choice(self.race_random_categories[race_choice])

        rnd_instance = random.Random(seed + 'random_class')
        if class_choice in self.class_random_categories:
            class_choice = rnd_instance.choice(self.class_random_categories[class_choice])

        # Sanity checks
        assert 1 <= hit_dice_num <= 20, 'Invalid HD_NUM received: {}'.format(hit_dice_num)
        assert class_choice in self.class_keys, 'Invalid class_template: {}'.format(class_choice)
        assert race_choice in self.race_keys, 'Invalid race_template: {}'.format(race_choice)

        new_character = Character()
        new_character.seed = seed

        if name:
            new_character.name = name

        new_character.set_stat('hit_dice_num', hit_dice_num)
        new_character.set_stat('hit_dice_extra', bonus_hd)

        race_template = self.race_templates[race_choice]
        assert isinstance(race_template, RaceTemplate)
        self.apply_race_template(new_character, race_template)

        class_template = self.class_templates[class_choice]
        assert isinstance(class_template, ClassTemplate)
        self.apply_class_template(new_character, class_template)

        # Get all the traits and features from the templates, have the factories instantiate them,
        # then give them to the new character
        for trait_name in itertools.chain(race_template.traits, class_template.traits):
            trait_factory = self.traits[trait_name]
            assert isinstance(trait_factory, TraitFactory)
            trait_feature = trait_factory.get_character_feature(new_character, self, seed=seed, short=True, args_tup=())
            trait_feature.give_to_character(new_character)
        for feature_name, feature_args in race_template.features.items():
            feature_instance = self.build_character_feature(
                feature_name, new_character, seed=seed, short=True, args_tup=feature_args)
            feature_instance.give_to_character(new_character)
        for feature_name, feature_args in class_template.features.items():
            feature_instance = self.build_character_feature(
                feature_name, new_character, seed=seed, short=True, args_tup=feature_args)
            feature_instance.give_to_character(new_character)

        # Do the pre-attribute rolling first pass of features
        for feature in new_character.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature.first_pass(new_character, self, seed)

        # Note, for floating attributes bonuses like half-elves to apply, race traits need to be applied before
        # Rolling attributes
        rnd_instance = random.Random(seed + 'attributes')
        attribute_roll_params = ROLL_METHODS[attribute_roll_method][1]
        attribute_roll_fixed_vals = ROLL_METHODS[attribute_roll_method][2]
        new_character.roll_attributes(*attribute_roll_params,
                                      rerolls_allowed=rerolls_allowed,
                                      min_total=min_total,
                                      no_attribute_swapping=no_attribute_swapping,
                                      force_optimize=force_optimize,
                                      fixed_rolls=attribute_roll_fixed_vals,
                                      rnd_instance=rnd_instance, )

        if hit_dice_size:
            if hit_dice_size == 'Default' and class_template.hd_size:
                new_character.set_stat('hit_dice_size', class_template.hd_size)
            elif hit_dice_size == 'Default' and not class_template.hd_size:
                new_character.set_stat('hit_dice_size', DEFAULT_HIT_DICE_SIZE)
            else:
                try:
                    hit_dice_size = int(hit_dice_size)
                    assert hit_dice_size in VALID_HD_SIZES
                    new_character.set_stat('hit_dice_size', hit_dice_size)
                except (ValueError, AssertionError, TypeError):
                    new_character.set_stat('hit_dice_size', DEFAULT_HIT_DICE_SIZE)
        elif class_template.hd_size:
            new_character.set_stat('hit_dice_size', class_template.hd_size)
        else:
            new_character.set_stat('hit_dice_size', DEFAULT_HIT_DICE_SIZE)

        rnd_instance = random.Random(seed + 'asi')
        if not no_asi:
            new_character.generate_asi_progression(priority_attribute_weight=ASI_PROGRESSION_PRIORITY_WEIGHT,
                                                   other_attribute_weight=ASI_PROGRESSION_OTHER_WEIGHT,
                                                   rnd_instance=rnd_instance)
            new_character.apply_asi_progression(hd_per_increase=ASI_HD_PER_INCREASE,
                                                points_per_increase=ASI_POINTS_PER_INCREASE)

        new_character.update_derived_stats()

        # Second and third passes for CharacterFeatures
        for feature in new_character.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature.second_pass(new_character, self, seed)
        for feature in new_character.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature.third_pass(new_character, self, seed)

        # Update again, just to be sure
        new_character.update_derived_stats()

        rnd_instance = random.Random(seed + 'armor')
        self.give_armor(new_character, 'unarmored')
        # Remember, speeds have to come after armor selection
        new_character.choose_armors(rnd_instance=rnd_instance)

        new_character.update_speeds()

        debug_print('Build success!', 1)
        return new_character

    def get_options(self, options_type):
        """
        Returns a list of tuples for potential race options: [(internal_name, display_name),...]
        """
        if options_type == 'race_choice':
            return self.race_options
        elif options_type == 'class_choice':
            return self.class_options
        elif options_type == 'attribute_roll_method':
            return self.roll_options
        elif options_type == 'hit_dice_num':
            return [(str(x), str(x)) for x in range(1, HIT_DICE_NUM_CAP)]
        elif options_type == 'hit_dice_bonus':
            return [(str(x), str(x)) for x in range(0, HIT_DICE_NUM_CAP)]
        elif options_type == 'hit_dice_size':
            return [(str(x), str(x)) for x in itertools.chain(['Default', ], VALID_HD_SIZES)]
        else:
            raise ValueError("Invalid value type '{}' requested for options list.".format(options_type))

    def get_options_dict(self):
        options_dict = {}
        options_dict['race_options'] = self.get_options('race_choice')
        options_dict['class_options'] = self.get_options('class_choice')
        options_dict['attribute_roll_options'] = self.get_options('attribute_roll_method')
        options_dict['hit_dice_num_options'] = self.get_options('hit_dice_num')
        options_dict['hit_dice_bonus_options'] = self.get_options('hit_dice_bonus')
        options_dict['hit_dice_size_options'] = self.get_options('hit_dice_size')
        return options_dict

    def get_random_option(self, option_type):
        if option_type == 'race':
            return random.choice(self.race_keys)
        elif option_type == 'class':
            return random.choice(self.class_keys)
        elif option_type == 'roll':
            return random.choice(self.roll_keys)
        else:
            raise ValueError("Invalid value type '{}' requested for random option.".format(option_type))

    def validate_params(self, class_choice=None, race_choice=None,
                        hd=None, hd_size=None, roll_choice=None):

        if class_choice is not None:
            if class_choice not in self.class_keys:
                return False

        if race_choice is not None:
            if race_choice not in self.race_keys:
                return False

        if hd is not None:
            if int(hd) < 1 or int(hd) > 20:
                return False

        if hd_size is not None:
            if hd_size != 'Default':
                try:
                    hd_size = int(hd_size)
                    if hd_size not in self.hd_size_options:
                        return False
                except ValueError:
                    return False

        if roll_choice is not None:
            if roll_choice not in self.roll_keys:
                return False

        return True

    # This function takes in a dictionary intended for building a new npc
    # It goes through and makes sure the dictionary is ready to go
    # If there are any problems, it will return (False, {New Dictionary})
    # If the dictionary is good to go, it will return (True, {New dictionary})
    # If ANYTHING is amiss, including unneeded values, it will return false, so that the request can be made again
    # with a nice, clean, minimal dictionary
    # Can also be used to simply generate a random dictionary suitable for a new character request
    def validate_request_dict(self, request_dict=None):
        # A request NEEDS race, class, hd_num, and seed
        # Everything else can go to default values

        is_valid = True
        clean_dict = {}

        if 'race_choice' in request_dict.keys() and request_dict['race_choice'] in self.race_keys:
            clean_dict['race_choice'] = request_dict['race_choice']
        else:
            is_valid = False
            clean_dict['race_choice'] = self.get_random_option('race')

        if 'class_choice' in request_dict.keys() and request_dict['class_choice'] in self.class_keys:
            clean_dict['class_choice'] = request_dict['class_choice']
        else:
            is_valid = False
            clean_dict['class_choice'] = self.get_random_option('class')

        if 'hit_dice_num' in request_dict.keys():
            try:
                hd_num = int(request_dict['hit_dice_num'])
                assert 1 <= hd_num <= 20
                clean_dict['hit_dice_num'] = int(request_dict['hit_dice_num'])
            except (ValueError, AssertionError, TypeError):
                is_valid = False
                clean_dict['hit_dice_num'] = random.randint(1, 20)
        else:
            is_valid = False
            clean_dict['hit_dice_num'] = random.randint(1, 20)

        if 'seed' in request_dict.keys() \
                and type(request_dict['seed']) == str and len(request_dict['seed']) > 0:
            clean_dict['seed'] = request_dict['seed']
        else:
            is_valid = False
            clean_dict['seed'] = random_string(10)

        if 'hit_dice_size' in request_dict.keys():
            if request_dict['hit_dice_size'] == 'Default':
                clean_dict['hit_dice_size'] = request_dict['hit_dice_size']
            else:
                try:
                    hd_size = int(request_dict['hit_dice_size'])
                    assert hd_size in VALID_HD_SIZES
                    clean_dict['hit_dice_size'] = request_dict['hit_dice_size']
                except (ValueError, AssertionError, TypeError):
                    is_valid = False
        else:
            is_valid = False
            clean_dict['hit_dice_size'] = 'Default'

        if 'attribute_roll_method' in request_dict.keys() and request_dict['attribute_roll_method'] in self.roll_keys:
            clean_dict['attribute_roll_method'] = request_dict['attribute_roll_method']
        else:
            is_valid = False
            clean_dict['attribute_roll_method'] = DEFAULT_ROLL_METHOD

        if 'name' in request_dict.keys():
            clean_dict['name'] = request_dict['name']

        return is_valid, clean_dict


class Character:
    def __init__(self):
        self.seed = None
        self.name = ''

        self.stats = {}
        for attr in STATS_ATTRIBUTES:
            self.stats[attr] = DEFAULT_ATTRIBUTE_VALUE
        for stat in STATS_BASE:
            self.stats[stat] = STATS_BASE[stat]

        self.attribute_bonuses = {}
        self.priority_attributes = []
        self.asi_progression = []

        self.race_name = ''
        self.class_name = ''

        self.creature_type = ''
        self.size = ''

        self.multiattack = None

        # I don't like directly referencing traits, so I'm adding an intermediary step.
        # Traits can give character tags, which in turn may be referenced by character logic
        # Tags are not included in stat blocks at all
        self.character_tags = {}

        # Expertise skills should only every be a subset of skills
        self.skills = set()
        self.skills_expertise = set()
        self.tool_proficiencies = set()
        self.tools_expertise = set()

        self.saves = set()
        self.save_advantages = set()
        self.save_disadvantages = set()

        # Armors and weapons are handled as dictionaries of the form {internal_name: object, ...}
        # This way they hopefully won't get any duplicate items
        self.armors = {}
        self.chosen_armor = None
        self.extra_armors = {}
        self.weapons = {}
        self.has_shield = False

        # Using an ordered dict to maintain consistency in how traits are displayed
        self.character_features = collections.OrderedDict()
        self.traits = collections.OrderedDict()

        self.damage_vulnerabilities = []
        self.damage_resistances = []
        self.damage_immunities = []
        self.condition_immunities = []
        self.vulnerabilities = []

        self.languages = []
        self.senses = {}

        self.spell_casting_ability = None

    def roll_attributes(self, die_size=6, num_dice=3, drop_lowest=0, drop_highest=0,
                        rerolls_allowed=0, min_total=0, fixed_rolls=(),
                        no_attribute_swapping=False,
                        force_optimize=False,
                        no_racial_bonus=False,
                        rnd_instance=None, ):

        if not rnd_instance:
            rnd_instance = random

        attribute_dict = {}

        # Apply reroll cap, so wacky high numbers aren't allowed
        rerolls_allowed = min(rerolls_allowed, REROLLS_CAP)
        rolls = []

        # Make initial rolls, reroll if the total is too low
        while rerolls_allowed >= 0:
            rerolls_allowed -= 1
            rolls = list(fixed_rolls[:])
            total_rolled = sum(rolls)
            while len(rolls) < len(STATS_ATTRIBUTES):
                roll = roll_dice(die_size, num_dice, drop_lowest, drop_highest, rnd_instance=rnd_instance)
                rolls.append(roll)
                total_rolled += roll
            if total_rolled >= min_total:
                break

        rnd_instance.shuffle(rolls)
        for attribute in STATS_ATTRIBUTES:
            attribute_dict[attribute] = rolls.pop()
        debug_print('Starting attribute rolls: {}'.format(attribute_dict), 3)

        # forcedOptimize means the highest attributes will ALWAYS be the
        if not no_attribute_swapping:
            finalized_attributes = set()
            for priorityAttribute in self.priority_attributes:
                swap_options = set(STATS_ATTRIBUTES)
                swap_options.remove(priorityAttribute)
                swap_options -= finalized_attributes
                if not force_optimize:
                    swap_options -= set(self.priority_attributes)
                highest_val = max(*[attribute_dict[x] for x in swap_options], attribute_dict[priorityAttribute])
                if highest_val > attribute_dict[priorityAttribute]:
                    valid_swaps = ([k for k, v in attribute_dict.items() if k in swap_options and v == highest_val])
                    swap_choice = rnd_instance.choice(valid_swaps)
                    attribute_dict[priorityAttribute], attribute_dict[swap_choice] = \
                        attribute_dict[swap_choice], attribute_dict[priorityAttribute]
                    debug_print('Attribute swap: ' + priorityAttribute + ', ' + swap_choice, 3)
                finalized_attributes.add(priorityAttribute)

        if not no_racial_bonus:
            for attribute, bonus in self.attribute_bonuses.items():
                debug_print("Racial attribute bonus: {} {} -> {}"
                            .format(attribute, attribute_dict[attribute], attribute_dict[attribute] + bonus), 3)
                attribute_dict[attribute] += bonus

        # Floating attribute bonuses, such as half-elves
        # Fortunately, those bonuses only ever apply +1, so we can keep this on the simple side
        floating_points = self.get_stat('floating_attribute_points')
        # Can't stack them with other racial bonuses
        floating_options = set(STATS_ATTRIBUTES[:])
        floating_preference = self.priority_attributes[:]
        for attribute, bonus in self.attribute_bonuses.items():
            if bonus > 0:
                floating_options.remove(attribute)
        while floating_points > 0:
            if len(floating_preference) > 0:
                next_attribute_choice = floating_preference.pop(0)
                if next_attribute_choice in floating_options:
                    debug_print('Floating attribute bonus: {} {} -> {}'
                                .format(next_attribute_choice, attribute_dict[next_attribute_choice],
                                        attribute_dict[next_attribute_choice] + 1))
                    attribute_dict[next_attribute_choice] += 1
                    floating_points -= 1
                    floating_options.remove(next_attribute_choice)
                    continue
            elif len(floating_options) > 0:
                next_attribute_choice = rnd_instance.choice(list(floating_options))
                debug_print('Floating attribute bonus: {} {} -> {}'
                            .format(next_attribute_choice, attribute_dict[next_attribute_choice],
                                    attribute_dict[next_attribute_choice] + 1))
                attribute_dict[next_attribute_choice] += 1
                floating_points -= 1
                floating_options.remove(next_attribute_choice)
                continue
            else:
                break

        # Set stats
        for attribute, val in attribute_dict.items():
            self.stats[attribute] = val

    def generate_asi_progression(self,
                                 priority_attribute_weight=ASI_PROGRESSION_PRIORITY_WEIGHT,
                                 other_attribute_weight=ASI_PROGRESSION_OTHER_WEIGHT,
                                 priority_attribute_subsequent_scale=ASI_PROGRESSION_PRIORITY_SUBSEQUENT_SCALE,
                                 asi_attribute_cap=ASI_DEFAULT_ATTRIBUTE_CAP,
                                 rnd_instance=None):

        if not rnd_instance:
            rnd_instance = random

        asi_progression = []

        attribute_weights_dict = {}
        for attribute in STATS_ATTRIBUTES:
            attribute_weights_dict[attribute] = other_attribute_weight

        current_priority_attribute_weight = priority_attribute_weight
        for priority_attribute in self.priority_attributes:
            attribute_weights_dict[priority_attribute] = max(current_priority_attribute_weight,
                                                             attribute_weights_dict[priority_attribute])
            current_priority_attribute_weight *= priority_attribute_subsequent_scale

        attribute_choices = []
        attribute_weights = []
        for attribute, weight in attribute_weights_dict.items():
            attribute_choices.append(attribute)
            attribute_weights.append(weight)

        # In principle, we should only ever need HIT_DICE_NUM_CAP / ASI_HD_PER_INCREASE * ASI_POINTS_PER_INCREASE
        # But, if we add traits or things that increase attributes, we MIGHT rarely not have enough choices
        # So, double that to be super safe
        max_asi_selections = HIT_DICE_NUM_CAP / ASI_HD_PER_INCREASE * ASI_POINTS_PER_INCREASE * 2
        while len(asi_progression) < max_asi_selections:
            if len(attribute_choices) == 0:
                break
            choice_index = rnd_instance.choices(range(len(attribute_choices)), attribute_weights)[0]
            attribute = attribute_choices[choice_index]
            if (asi_progression.count(attribute) + self.get_stat(attribute)) > asi_attribute_cap:
                attribute_choices.pop(choice_index)
                attribute_weights.pop(choice_index)
            else:
                asi_progression.append(attribute)

        self.asi_progression = asi_progression

    def apply_asi_progression(self, asi_progression=None,
                              hd_per_increase=ASI_HD_PER_INCREASE,
                              points_per_increase=ASI_POINTS_PER_INCREASE,
                              asi_attribute_cap=ASI_DEFAULT_ATTRIBUTE_CAP):

        if not asi_progression:
            asi_progression = self.asi_progression[:]

        asi_points_remaining = (self.get_stat('hit_dice_num') // hd_per_increase) * points_per_increase

        while asi_points_remaining > 0:
            if len(asi_progression) == 0:
                break

            attribute_choice = asi_progression.pop(0)
            if self.get_stat(attribute_choice) < asi_attribute_cap:
                debug_print('ASI {}: {} -> {}'.format(attribute_choice,
                                                      str(self.get_stat(attribute_choice)),
                                                      str(self.get_stat(attribute_choice) + 1), ), 2)
                self.set_stat(attribute_choice, self.get_stat(attribute_choice) + 1)
                asi_points_remaining -= 1

    def update_derived_stats(self):
        # stat mods
        for attribute in STATS_ATTRIBUTES:
            # stat modifiers = stat // 2 - 5
            self.stats[attribute + '_mod'] = self.stats[attribute] // 2 - 5
        # Hit Points
        self.stats['effective_hit_dice'] = self.stats['hit_dice_num'] + self.stats['hit_dice_extra']
        hp_per_level = (self.stats['hit_dice_size'] // 2) + self.stats['con_mod'] + self.stats['bonus_hp_per_level']
        # Minimum 1 hp per level
        hp_per_level = max(1, hp_per_level)
        self.stats['hit_points_total'] = \
            self.stats['effective_hit_dice'] * hp_per_level
        # This is for when it comes time to display Z in "XdY + Z"
        self.stats['hit_points_from_con'] = \
            self.stats['effective_hit_dice'] * (self.stats['con_mod'] + self.stats['bonus_hp_per_level'])
        # Proficiency
        self.stats['proficiency'] = self.stats['hit_dice_num'] // 5 + 2 + self.stats['proficiency_extra']
        # DCs (all DCs are 8 + statMod + proficiency)
        for attribute in STATS_ATTRIBUTES:
            self.stats[attribute + '_dc'] = 8 + self.stats[attribute + '_mod'] + self.stats['proficiency']
        # Attack bonus
        for attribute in STATS_ATTRIBUTES:
            self.stats[attribute + '_attack'] = self.stats['proficiency'] + self.stats[attribute + '_mod']
        # Speed
        # Speed has to come after armor, so it gets its own method
        # Multiattack
        if self.multiattack:
            hd = self.stats['hit_dice_num']
            multiattack_type = self.multiattack
            attacks = 1
            if multiattack_type == 'fighter':
                if hd >= 20:
                    attacks = 4
                elif hd >= 11:
                    attacks = 3
                elif hd >= 5:
                    attacks = 2
            elif multiattack_type == 'single':
                if hd >= 5:
                    attacks = 2
            self.stats['attacks_per_round'] = attacks
        else:
            self.stats['attacks_per_round'] = 1

        # Trait specific stuff
        hit_dice_num = self.stats['hit_dice_num']
        if hit_dice_num >= 16:
            self.stats['breath_weapon_dice'] = 5
        elif hit_dice_num >= 11:
            self.stats['breath_weapon_dice'] = 4
        elif hit_dice_num >= 6:
            self.stats['breath_weapon_dice'] = 3
        else:
            self.stats['breath_weapon_dice'] = 2

    # Speed is partially dependent on armor, which is determined separately from derived stats
    def update_speeds(self):
        # Python lets us multiply bools by ints, so yay
        # This val should only be nonzero if a character is wearing heavy armor, doesn't have enough strength,
        # and hasn't has their penalty reduced, such as by the heavy_armor_training_trait
        armor_move_penalty = self.chosen_armor.speed_penalty(self)

        # If the base move for any is zero, that means they don't have that ype of movement at all
        # Technically, I guess if speed is reduced below zero they should lose that movement, so let's do that too
        if self.get_stat('speed_walk') > 0:
            self.set_stat('speed_walk_final',
                          self.get_stat('speed_walk')
                          + self.get_stat('speed_bonus_universal') + armor_move_penalty
                          )
        else:
            self.set_stat('speed_walk_final', 0)
        self.set_stat('speed_walk_final', max(0, self.get_stat('speed_walk_final')))

        if self.get_stat('speed_swim') > 0:
            self.set_stat('speed_swim_final',
                          self.get_stat('speed_swim')
                          + self.get_stat('speed_bonus_universal') + armor_move_penalty
                          )
        else:
            self.set_stat('speed_swim_final', 0)
        self.set_stat('speed_swim_final', max(0, self.get_stat('speed_swim_final')))

        if self.get_stat('speed_fly') > 0:
            self.set_stat('speed_fly_final',
                          self.get_stat('speed_fly')
                          + self.get_stat('speed_bonus_universal') + armor_move_penalty
                          )
        else:
            self.set_stat('speed_fly_final', 0)
        self.set_stat('speed_fly_final', max(0, self.get_stat('speed_fly_final')))

        if self.get_stat('speed_burrow') > 0:
            self.set_stat('speed_burrow_final',
                          self.get_stat('speed_burrow')
                          + self.get_stat('speed_bonus_universal') + armor_move_penalty
                          )
        else:
            self.set_stat('speed_burrow_final', 0)
        self.set_stat('speed_burrow_final', max(0, self.get_stat('speed_burrow_final')))

    def get_stat(self, stat):
        return self.stats[stat]

    def set_stat(self, stat, value):
        self.stats[stat] = value

    def get_best_attack(self):
        best_to_hit = 0
        best_avg_dmg = 0
        for weapon in self.weapons.values():
            if weapon.get_to_hit(self) > best_to_hit:
                best_to_hit = weapon.get_to_hit(self)
                best_avg_dmg = weapon.get_damage(self, use_versatile=True)[0]
            elif weapon.get_to_hit(self) == best_to_hit:
                best_avg_dmg = max(best_avg_dmg, weapon.get_damage(self, use_versatile=True)[0])
        return best_to_hit, best_avg_dmg

    def get_best_ac(self):
        assert type(self.chosen_armor) == Armor, "Can't get AC before setting armor!"
        best_ac = self.chosen_armor.get_ac(self)
        if self.extra_armors:
            for extra_armor in self.extra_armors.values():
                best_ac = max(best_ac, extra_armor.get_ac(self))
        return best_ac

    def get_cr(self):
        effective_to_hit, effective_attack_dmg = self.get_best_attack()
        effective_dmg_per_round = effective_attack_dmg * self.stats['attacks_per_round']
        effective_hp = self.stats['hit_points_total']
        effective_ac = self.get_best_ac()

        # For now, we'll just say that if a character's spellcasting level is greater than half its hit dice,
        # we'll treat it like a caster for CR purposes
        if self.spell_casting_ability:
            effective_caster_level = self.spell_casting_ability.get_caster_level(self)
            effective_spell_dc = self.spell_casting_ability.get_spell_dc(self)
            if self.spell_casting_ability.get_caster_level(self) > self.stats['hit_dice_num'] / 2:
                cr_focus = 'caster'
            else:
                cr_focus = 'not_caster'
        else:
            effective_caster_level = 0
            effective_spell_dc = 0
            cr_focus = 'not_caster'

        # Note, we're using row index for CR math instead of the actual number,
        # This should accommodate fractional CRs
        # Get the character's defensive challenge rating
        # Start with the max vals, in case we can't find on chart
        cr_index_def = len(CHALLENGE_RATING_CHART)
        expected_ac = 19
        for row_num in range(len(CHALLENGE_RATING_CHART)):
            row_hp = CHALLENGE_RATING_CHART[row_num][3]  # index 3 is hp
            if row_hp > effective_hp:
                cr_index_def = row_num
                expected_ac = CHALLENGE_RATING_CHART[row_num][2]
                break
        # For every two points, shift up or down one row
        cr_def_shift = int(float(effective_ac - expected_ac) / 2)
        cr_index_def += cr_def_shift

        # Get the character's offensive challenge rating
        # Start with the max vals, in case we can't find on chart
        cr_index_off = len(CHALLENGE_RATING_CHART)
        expected_to_hit = 14
        expected_dc = 23
        # So, we don't really have a good way to get avg damage for casters at the moment, so we're going to use a hack
        # For casters, we'll just start them at caster level -3 on the chart
        # Conveniently, that happens to be the row's index number
        if cr_focus == 'caster':
            cr_index_off = effective_caster_level
            expected_dc = CHALLENGE_RATING_CHART[cr_index_off][6]
            cr_off_shift = int(float(effective_spell_dc - expected_dc) / 2)
        else:
            for row_num in range(len(CHALLENGE_RATING_CHART)):
                if CHALLENGE_RATING_CHART[row_num][5] > effective_dmg_per_round:
                    cr_index_off = row_num
                    expected_to_hit = CHALLENGE_RATING_CHART[row_num][4]
                    break
            cr_off_shift = int(float(effective_to_hit - expected_to_hit) / 2)
        cr_index_off += cr_off_shift

        avg_cr_index = math.ceil((cr_index_off + cr_index_def) / 2)

        # Make sure we didn't pop out of the table somehow
        avg_cr_index = max(avg_cr_index, 0)
        avg_cr_index = min(avg_cr_index, len(CHALLENGE_RATING_CHART) - 1)

        return CHALLENGE_RATING_CHART[avg_cr_index][0]

    def get_senses(self):
        passive_perception = 10 + self.get_stat('wis_mod')
        if 'perception' in self.skills:
            passive_perception += self.get_stat('proficiency')
        senses_string = ''
        if len(self.senses.keys()) > 0:
            for k, v in self.senses.items():
                senses_string += '{} {} ft., '.format(k, v)
        senses_string += 'passive Perception {}'.format(passive_perception)
        return senses_string

    def add_character_feature(self, character_feature: 'CharacterFeature'):
        self.character_features[character_feature.int_name] = character_feature

    def add_language(self, language):
        if language not in self.languages:
            self.languages.append(language)

    def add_save_advantage(self, advantage):
        self.save_advantages.add(advantage)

    def add_save_disadvantage(self, disadvantage):
        self.save_disadvantages.add(disadvantage)

    # Can also add tools, anything that's not in the valid skills list is assumed to be a tool
    def add_skill(self, skill, expertise=False):
        # Tools can have spaces in them, so they use underscores in the csv file
        # Make sure underscores have become spaces, first
        skill = skill.replace('_', ' ')
        if skill in SKILLS:
            self.skills.add(skill)
            if expertise:
                self.skills_expertise.add(skill)
        else:
            self.tool_proficiencies.add(skill)
            if expertise:
                self.skills_expertise.add(skill)

    def get_non_proficient_skills(self):
        out_skills = set(SKILLS.keys())
        for prof_skill in self.skills:
            out_skills.remove(prof_skill)
        return list(out_skills)

    def add_tag(self, tag, tag_val=None):
        self.character_tags[tag] = tag_val

    def add_damage_resistance(self, damage_resistance):
        if damage_resistance not in self.damage_resistances:
            self.damage_resistances.append(damage_resistance)

    def add_damage_immunity(self, damage_immunity):
        if damage_immunity not in self.damage_immunities:
            self.damage_immunities.append(damage_immunity)

    def add_damage_vulnerability(self, damage_vulnerability):
        if damage_vulnerability not in self.damage_vulnerabilities:
            self.damage_vulnerabilities.append(damage_vulnerability)

    def add_condition_immunity(self, condition_immunity):
        if condition_immunity not in self.condition_immunities:
            self.condition_immunities.append(condition_immunity)

    def choose_armors(self, rnd_instance=None):

        if not rnd_instance:
            rnd_instance = random

        best_ac_armors = []
        # First check for AC
        best_ac = 0
        for armor_obj in self.armors.values():
            armor_ac = armor_obj.get_ac(self)
            if armor_ac > best_ac:
                best_ac_armors = [armor_obj, ]
                best_ac = armor_ac
            elif armor_ac == best_ac:
                best_ac_armors.append(armor_obj)
        # Next check type, 'none' > 'light' > 'medium' > 'heavy'
        best_weight = ''
        for armor_obj in best_ac_armors:
            if best_weight == 'none' or armor_obj.armor_type == 'none':
                best_weight = 'none'
            elif best_weight == 'light' or armor_obj.armor_type == 'light':
                best_weight = 'light'
            elif best_weight == 'medium' or armor_obj.armor_type == 'medium':
                best_weight = 'medium'
            elif best_weight == 'heavy' or armor_obj.armor_type == 'heavy':
                best_weight = 'heavy'
        valid_choices = []
        for armor_obj in best_ac_armors:
            if armor_obj.armor_type == best_weight:
                valid_choices.append(armor_obj)

        self.chosen_armor = rnd_instance.choice(valid_choices)

    def get_all_stat_block_entries(self, short=True):
        all_entries = []
        for feature in self.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature_entries = feature.get_stat_block_entries(self, short)
            for stat_block_entry in feature_entries:
                all_entries.append(stat_block_entry)
        return all_entries

    def build_stat_block(self, short_traits=True, trait_visibility=1):
        sb = StatBlock()

        if self.name:
            sb.name = self.name
        else:
            sb.name = '{} {}'.format(self.race_name, self.class_name)

        sb.race = self.race_name
        sb._class = self.class_name

        sb.creature_type = self.creature_type

        acstring = self.chosen_armor.sheet_display(self)
        if self.extra_armors:
            for armor in self.extra_armors.values():
                acstring += ', ' + armor.sheet_display(self)
        sb.armor = acstring

        sb.hp = '{}({}d{} {})' \
            .format(self.get_stat('hit_points_total'), self.get_stat('effective_hit_dice'),
                    self.get_stat('hit_dice_size'),
                    num_plusser(self.get_stat('hit_points_from_con'), add_space=True)
                    )
        sb.size = self.size

        speedstr = '{}ft.'.format(self.get_stat('speed_walk_final'))
        if self.get_stat('speed_fly_final') > 0:
            speedstr += ', fly {}ft.'.format(self.get_stat('speed_fly_final'))
        if self.get_stat('speed_swim_final') > 0:
            speedstr += ', swim {}ft.'.format(self.get_stat('speed_swim_final'))
        if self.get_stat('speed_burrow_final') > 0:
            speedstr += ', burrow {}ft.'.format(self.get_stat('speed_burrow_final'))
        sb.speed = speedstr

        sb.proficiency = num_plusser(self.get_stat('proficiency'))

        attributes_dict = {}
        for attribute in STATS_ATTRIBUTES:
            attribute_val = self.get_stat(attribute)
            attributes_dict[attribute] = '{} ({})' \
                .format(attribute_val, num_plusser(self.get_stat(attribute + '_mod')))
        sb.attributes_dict = attributes_dict

        all_attributes_line = ''
        for attribute in STATS_ATTRIBUTES:
            all_attributes_line += '{} {}({}) ' \
                .format(attribute.upper(), self.get_stat(attribute), num_plusser(self.get_stat(attribute + '_mod')))
        sb.attributes = all_attributes_line

        saves_line = ''
        if len(self.saves) > 0:
            saves_list = []
            for attribute in STATS_ATTRIBUTES:
                if attribute in self.saves:
                    save_val = self.stats[attribute + '_mod'] + self.stats['proficiency']
                    val_str = num_plusser(save_val)
                    saves_list.append(ATTRIBUTES_ABBREVIATION_TO_FULL_WORD[attribute] + ' ' + val_str)
            saves_line = ', '.join(saves_list)
        if len(self.save_advantages) > 0:
            saves_line += ' (advantage against {})'.format(nice_list(sorted(list(self.save_advantages))))
        if len(self.save_disadvantages) > 0:
            saves_line += ' (disadvantage against {})'.format(nice_list(sorted(list(self.save_disadvantages))))

        sb.saves = saves_line

        sb.skills = ''
        if len(self.skills) > 0:
            skills_list = []
            for skill in sorted(SKILLS):
                if skill in self.skills:
                    skill_attribute = SKILLS[skill]
                    skill_val = self.stats[skill_attribute + '_mod'] + self.stats['proficiency']
                    # check for expertise
                    if skill in self.skills_expertise:
                        skill_val += self.stats['proficiency']
                    if skill_val >= 0:
                        val_str = ' +' + str(skill_val)
                    else:
                        val_str = ' ' + str(skill_val)
                    skills_list.append(skill.capitalize() + val_str)
            sb.skills = ', '.join(skills_list)

        sb.tools = ''
        if len(self.tool_proficiencies) > 0:
            tools_list = []
            for tool in sorted(self.tool_proficiencies):
                if tool in self.tools_expertise:
                    tools_list.append(tool + '*')
                else:
                    tools_list.append(tool)
            sb.tools = ', '.join(tools_list)

        sb.cr = self.get_cr()
        sb.senses = self.get_senses()

        if self.languages and len(self.languages) > 0:
            languages = sorted(self.languages)
            if 'common' in languages:
                languages.remove('common')
                languages.insert(0, 'common')
            sb.languages = ', '.join(languages)

        if self.damage_vulnerabilities:
            sb.damage_vulnerabilities = ', '.join(sorted(self.damage_vulnerabilities))
        if self.damage_immunities:
            sb.damage_immunities = ', '.join(sorted(self.damage_immunities))
        if self.damage_resistances:
            sb.damage_resistances = ', '.join(sorted(self.damage_resistances))
        if self.condition_immunities:
            sb.condition_immunities = ', '.join(sorted(self.condition_immunities))

        all_block_entries = self.get_all_stat_block_entries(short=short_traits)
        passive_entries = []
        multiattack_entries = []
        action_entries = []
        spellcasting_entries = []
        hidden_entries = []
        for entry in all_block_entries:
            assert isinstance(entry, StatBlockEntry)
            if entry.get_visibility(self) <= trait_visibility:
                if entry.get_category() == 'passive':
                    passive_entries.append((entry.get_title(self), entry.get_entry(self)))
                elif entry.get_category() == 'multiattack':
                    multiattack_entries.append((entry.get_title(self), entry.get_entry(self)))
                elif entry.get_category() == 'spellcasting':
                    spellcasting_entries.append((entry.get_title(self), entry.get_entry(self)))
                elif entry.get_category() == 'action':
                    action_entries.append((entry.get_title(self), entry.get_entry(self)))
            else:
                hidden_entries.append(entry.get_title(self))

        attacks = []
        for weapon in self.weapons.values():
            assert isinstance(weapon, StatBlockEntry)
            attacks.append((weapon.get_title(self),
                            weapon.get_entry(self, short=short_traits)))
        sb.attacks = attacks

        sb.passive_traits = passive_entries
        sb.multiattack = multiattack_entries
        sb.actions = action_entries
        sb.spellcasting_traits = spellcasting_entries
        sb.hidden_traits = nice_list(hidden_entries)

        return sb


class StatBlock:
    """
    Stablock contains all the entries needed for displaying a stablock without any logic
    """

    def __init__(self):
        self.name = ''
        self.race = ''
        self.creature_type = ''
        self._class = ''
        self.armor = ''
        self.hp = ''
        self.size = ''
        self.speed = ''
        self.proficiency = ''
        self.attributes = ''
        self.attributes_dict = {}
        self.damage_vulnerabilities = None
        self.damage_resistances = None
        self.damage_immunities = None
        self.condition_immunities = None
        self.senses = ''
        self.saves = ''
        self.skills = ''
        self.tools = ''
        self.cr = ''
        self.languages = None
        self.hidden_traits = ''
        self.passive_traits = []
        self.spellcasting_traits = []
        self.multiattack = []
        self.attacks = []
        self.actions = []
        self.reactions = []

    def plain_text(self):
        disp = ''
        disp += self.name + '\n'
        disp += "{} {}".format(self.race, self._class) + '\n'
        # Subline
        disp += "{} {}, unaligned".format(self.size, self.creature_type) + '\n'
        disp += 'AC: ' + self.armor + '\n'
        disp += 'Hit Points: ' + self.hp + '\n'
        # disp += 'Size: ' + self.size + '\n'
        disp += 'Speed: ' + self.speed + '\n'
        disp += 'Proficiency: ' + self.proficiency + '\n'
        disp += self.attributes + '\n'
        disp += 'Saves: ' + self.saves + '\n'
        disp += 'Skills: ' + self.skills + '\n'
        if self.tools:
            disp += 'Tools: ' + self.tools + '\n'
        if self.damage_vulnerabilities:
            disp += 'Damage Vulnerabilities: ' + self.damage_vulnerabilities + '\n'
        if self.damage_resistances:
            disp += 'Damage Resistances: ' + self.damage_resistances + '\n'
        if self.damage_immunities:
            disp += 'Damage Resistances: ' + self.damage_immunities + '\n'
        if self.condition_immunities:
            disp += 'Condition Immunities: ' + self.condition_immunities + '\n'
        disp += 'Senses: ' + self.senses + '\n'
        if self.languages:
            disp += 'Languages: ' + self.languages + '\n'
        else:
            disp += 'Languages: --' + self.languages + '\n'
        if self.cr:
            disp += 'Challenge: ' + self.cr + '\n'
        for trait in self.passive_traits:
            disp += trait[0] + '. ' + trait[1] + '\n'
        if self.hidden_traits:
            disp += 'Hidden Traits: ' + self.hidden_traits + '\n'
        for spellcasting_trait in self.spellcasting_traits:
            disp += spellcasting_trait[0] + '. ' + spellcasting_trait[1] + '\n'
        for multiattack in self.multiattack:
            disp += multiattack[0] + '. ' + multiattack[1] + '\n'
        for attack in self.attacks:
            disp += attack[0] + '. ' + attack[1] + '\n'
        for action in self.actions:
            disp += action[0] + '. ' + action[1] + '\n'
        for reaction in self.reactions:
            disp += reaction[0] + '. ' + reaction[1] + '\n'

        return disp

    def get_dict(self):
        return self.__dict__


# When it comes time to give a character a feature, you must instantiate that feature
# When doing anything involving randomness, the rng should use the seed plus a method specific salt
# to instantiate random
# Character features are provided a reference to NPCGenerator, so that they can use functions that rely on its
# reference dictionaries
class CharacterFeature:
    def __init__(self, character: 'Character', npc_gen: 'NPCGenerator', seed=None, short=True, args_tup=()):
        self.int_name = 'dummy'

    # Shouldn't need to be overriden, but can be if there needs to be some kind of merginge function
    def give_to_character(self, character):
        character.add_character_feature(self)

    # first_pass() is called just after race/class templates have been applied,
    # before attributes are rolled or ASI applied
    # At this point, hit dice are known but no attributes or derived stats have been set
    # Feature should call this method if wants to affect how a character rolls for attributes or generates basic stats
    # or if it can figure out everything it wants using ONLY hit dice
    def first_pass(self, character: 'Character', npc_gen: 'NPCGenerator', seed):
        pass

    # second_pass() is called after attributes have been rolled and stats derived
    # At this point, the bulk of stats have been set
    # This is where most action should happen
    # However, a CharacterFeature cannot rely on other features to have gotten their shit together by this point
    # Basically, any feature that does stuff that relies on character stats
    #  but not other features should do their stuff here
    def second_pass(self, character: 'Character', npc_gen: 'NPCGenerator', seed):
        pass

    # third_pass() is called right after second_pass()
    # At this point, a CharacterFeature can expect other CharacterFeatures to have their shit mostly together
    # Character features that depend on other features or modify other features can do their stuff here
    def third_pass(self, character: 'Character', npc_gen: 'NPCGenerator', seed):
        pass

    # When it comes time to build a statblock, every feature will have this function called
    # and the results will be pooled together
    # The StatBlock will then get to decide how to organize and format the results
    # Note, this is where the short parameter is called,
    # which if true means shortened versions of entries should be used
    # Visibility and which entries should be hidden is handled by the StatBlock
    def get_stat_block_entries(self, character: 'Character', short=True):
        return []


# Everything that can appear as an entry in a stat block musty implement this functionality
# Features are allowed to change things based on who the owner is
class StatBlockEntry:
    def __init__(self, title, category, visibility, text, ):
        self.title = title
        self.text = text
        self.category = category
        self.visibility = visibility

    def __str__(self):
        return "{}. {}".format(self.title, self.text)

    def __repr__(self):
        return "<StatBlockEntry:{}>".format(self.title)

    # The part that is typically in bold with a period at the end.
    # When using short statblock versions, expect (1/short), etc. for abilities that recharge on a short rest
    def get_title(self, owner: Character, short=True):
        return self.title

    # The normal text stuff
    def get_entry(self, owner: Character, short=True):
        return self.text

    # Categories are used for organizing the statblock when it comes time for rendering
    # The renderer is allowed to decide on the order
    # Features with the 'hidden' category will never be shown, regardless of visibility
    def get_category(self):
        return self.category

    # When building a statblock, visibility determines what makes the cut
    # 0 - always show
    # 1 - (default) usually show, but may be hidden to save space
    # 2 - usually hide, but may be shown if a verbose version is requested
    # 3 - always hide, probably because the character can't actually use the feature,
    #     i.e. the feature has a minimum hd requirement the character doesn't meet
    # Features with the 'hidden' category will never be shown, regardless of visibility
    def get_visibility(self, owner: Character):
        return self.visibility


# Traits are the most common and simplest form of CharacterFeature
# Traits are allowed to make simple changes to a character based on the tags they've been given and will always
# generate only a single StatBlock entry
# That stat block entry text may insert values from the character's stats dictionary, but is otherwise static
# Anything requiring additional functionality must be implemented as a custom CharacterFeature
class TraitFactory:
    def __init__(self):
        self.int_name = ''
        self.display_name = ''
        self.recharge = ''
        self.trait_type = 'hidden'
        self.text_long = ''
        self.text_short = ''
        self.visibility = 0
        self.tags = {}

    def get_character_feature(self, character, npc_gen, seed=None, short=True, args_tup=()):
        if short:
            text = self.text_short
        else:
            text = self.text_long

        if short and self.recharge:
            title = "{} ({})".format(self.display_name, self.recharge)
        else:
            title = self.display_name

        return FeatureTrait(
            int_name=self.int_name,
            title=title,
            trait_type=self.trait_type,
            text=text,
            visibility=self.visibility,
            tags=self.tags,
        )


class FeatureTrait(CharacterFeature):
    def __init__(self, int_name, title, trait_type, text, visibility, tags):
        super().__init__(character=None, npc_gen=None, seed=None, short=True, args_tup=())
        self.int_name = int_name
        self.title = title
        self.trait_type = trait_type
        self.text = text
        self.visibility = visibility
        self.tags = tags

    def first_pass(self, character: 'Character', npc_gen: 'NPCGenerator', seed):

        rnd_instance = random.Random(seed + self.int_name + 'first')

        if 'give_armor' in self.tags:
            for armor in self.tags['give_armor']:
                npc_gen.give_armor(character, armor)

        if 'give_weapon' in self.tags:
            for weapon in self.tags['give_weapon']:
                npc_gen.give_weapon(character, weapon)

        if 'give_tag' in self.tags:
            for character_tag in self.tags['give_tag']:
                character.add_tag(character_tag)

        # Tools and skills are considered the same, anything not in SKILLS is considered a tool
        if 'skill_proficiency' in self.tags:
            for skill in self.tags['skill_proficiency']:
                skill = skill.replace('_', ' ')
                if skill not in character.skills:
                    character.add_skill(skill)
                elif len(character.get_non_proficient_skills()) > 0:
                    random_skill = rnd_instance.choice(character.get_non_proficient_skills())
                    debug_print('Trait {}: {} already present, adding {} instead'
                                .format(self.int_name, skill, random_skill))
                    character.add_skill(random_skill)

        if 'skill_random' in self.tags:
            num_random_skills = int(self.tags['skill_random'][0])
            for i in range(num_random_skills):
                if len(character.get_non_proficient_skills()) > 0:
                    random_skill = rnd_instance.choice(character.get_non_proficient_skills())
                    debug_print('Trait {}: giving random skill {}.'
                                .format(self.int_name, random_skill))
                    character.add_skill(random_skill)

        if 'expertise_random' in self.tags:
            num_expertise = int(self.tags['expertise_random'][0])
            expertise_choices = rnd_instance.sample(character.skills, num_expertise)
            for choice in expertise_choices:
                character.add_skill(choice, expertise=True)

        if 'expertise_fixed' in self.tags:
            expertise_choices = self.tags['expertise_random']
            for choice in expertise_choices:
                character.add_skill(choice, expertise=True)

        if 'damage_immunity' in self.tags:
            for entry in self.tags['damage_immunity']:
                character.add_damage_immunity(entry)

        if 'damage_vulnerability' in self.tags:
            for entry in self.tags['damage_vulnerability']:
                character.add_damage_vulnerability(entry)

        if 'damage_resistance' in self.tags:
            for entry in self.tags['damage_resistance']:
                character.add_damage_resistance(entry)

        if 'condition_immunity' in self.tags:
            for entry in self.tags['condition_immunity']:
                character.add_condition_immunity(entry)

        if 'save_advantage' in self.tags:
            for advantage in self.tags['save_advantage']:
                character.add_save_advantage(advantage)

        if 'save_disadvantage' in self.tags:
            for disadvantage in self.tags['save_disadvantage']:
                character.add_save_disadvantage(disadvantage)

        if 'sense_darkvision' in self.tags:
            val = int(self.tags['sense_darkvision'][0])
            character.senses['darkvision'] = max(character.senses.get('darkvision', 0), val)

        if 'bonus_hp_per_level' in self.tags:
            val = int(self.tags['bonus_hp_per_level'][0])
            character.stats['bonus_hp_per_level'] += val

        if 'floating_attribute_bonus' in self.tags:
            val = int(self.tags['floating_attribute_bonus'][0])
            character.stats['floating_attribute_points'] += val

        if 'random_language' in self.tags:
            num_extra_languages = self.tags['random_language'][0]
            language_options = set(LANGUAGES)
            for language in character.languages:
                language_options.remove(language)
            language_choices = rnd_instance.sample(language_options, num_extra_languages)
            for language in language_choices:
                character.add_language(language)

    # Traits shouldn't need to do anything on the second pass
    def second_pass(self, character: 'Character', npc_gen: 'NPCGenerator', seed):
        pass

    def get_stat_block_entries(self, character: 'Character', short=True):
        text = self.text.format(**character.stats)
        sb_entries = []
        sb_entries.append(StatBlockEntry(
            title=self.title, text=text, category=self.trait_type, visibility=self.visibility, ))
        return sb_entries


# class Trait(StatBlockEntry):
#     def __init__(self):
#         self.int_name = ''
#         self.display_name = ''
#         self.recharge = ''
#         self.trait_type = 'hidden'
#         self.text = ''
#         self.text_short = ''
#         self.visibility = 0
#         self.tags = {}
#
#     def __str__(self):
#         return '<{}:{},{},{},{}>'.format(self.int_name, self.display_name, self.trait_type, self.text, str(self.tags))
#
#     def get_title(self, owner, short=True):
#         if short and self.recharge:
#             return '{} ({})'.format(self.display_name, self.recharge)
#         return self.display_name
#
#     def get_entry(self, owner: Character, short=True):
#         if short:
#             return self.text_short.format(**owner.stats)
#         else:
#             return self.text.format(**owner.stats)
#
#     def get_category(self):
#         return self.trait_type
#
#     def get_visibility(self, owner: Character):
#         if 'min_hd' in self.tags and owner.get_stat('hit_dice_num') < int(self.tags['min_hd'][0]):
#             return 3
#         else:
#             return self.visibility
#
#     def get_character_feature(self):
#         new_feature = RevisedTrait(
#             title = self.display_name,
#             recharge = self.recharge,
#             short_text = self.text_short,
#             long_text = self.text,
#             visibility= self.visibility,
#             tags = self.tags,
#             )
#         return new_feature


class RaceTemplate:
    def __init__(self):
        self.int_name = ''
        self.display_name = ''

        self.attribute_bonuses = {}
        self.base_stats = {}

        self.creature_type = DEFAULT_CREATURE_TYPE
        self.size = DEFAULT_SIZE

        self.speeds = {}
        self.senses = {}

        self.languages = []

        self.traits = []
        self.features = collections.OrderedDict()


class ClassTemplate:
    def __init__(self):
        self.int_name = ''
        self.display_name = ''

        self.priority_attributes = []

        self.hd_size = None

        self.skills_fixed = []
        self.num_random_skills = 0
        self.skills_random = []

        self.saves = []
        self.languages = []

        self.multiattack_type = None

        self.armors_loadout_pool = None
        self.weapons_loadout_pool = None
        self.spell_casting_profile = None

        self.traits = []
        self.features = collections.OrderedDict()

        self.cr_calc_type = ''


class Armor:
    def __init__(self):
        self.int_name = ''
        self.display_name = ''
        self.base_ac = -1
        self.armor_type = ''
        self.min_str = 0
        self.stealth_disadvantage = False
        self.tags = set()

    def __repr__(self):
        return self.int_name

    def is_extra(self):
        return 'extra' in self.tags

    def get_ac(self, owner):
        base_ac = self.base_ac
        total_ac = 0
        if self.armor_type == 'light' or self.armor_type == 'none':
            total_ac = base_ac + owner.get_stat('dex_mod')
        elif self.armor_type == 'medium':
            max_dex_bonus = 2
            if 'medium_armor_master' in owner.traits:
                max_dex_bonus = 3
            # Can add case here for medium armor mastery
            total_ac = base_ac + min(max_dex_bonus, owner.get_stat('dex_mod'))
        elif self.armor_type == 'heavy':
            total_ac = base_ac
        else:
            debug_print('Armor: ' + self.int_name + ' has invalid armor type: ' + self.armor_type, 0)

        if owner.has_shield and 'noShield' not in self.tags:
            total_ac += 2

        return total_ac

    # This method returns true if a character should take a speed penalty
    # For dwarves or other characters who have heavy armor training, this will still return true,
    # but their penalty should have been reduced to zero, so it won't affect them
    def speed_penalty(self, owner: Character):

        if 'heavy_armor_penalty' in owner.character_tags:
            return 0

        if self.armor_type == 'heavy' and self.min_str > owner.get_stat('str'):
            return HEAVY_ARMOR_MOVE_PENALTY
        else:
            return 0

    def stealth_penalty(self, owner):

        # Special case for medium armor master
        if self.armor_type == 'medium' and 'medium_armor_master' in owner.traits:
            return False

        return self.stealth_disadvantage

    def sheet_display(self, owner):
        outstring = str(self.get_ac(owner)) + ' (' + self.display_name
        if owner.has_shield:
            outstring += ', with shield'
        outstring += ')'
        return outstring


# For CR calculations, an attack needs to give its to hit and average damage value
# And it needs to be able to give a stat block entry when it comes time to render
class Attack(StatBlockEntry):

    def get_to_hit(self, owner):
        pass

    def get_avg_dmg(self, owner):
        avg_dmg = 1
        return avg_dmg


class Weapon(Attack):
    def __init__(self):
        self.int_name = ''
        self.display_name = ''
        self.dmg_dice_num = 0
        self.dmg_dice_size = 0
        self.damage_type = ''
        self.attack_type = ''
        self.range_short = 0
        self.range_long = 0
        self.tags = {}
        self.num_targets = 1

    def __repr__(self):
        outstring = '[{},{},{},{},{},{},{},{},{},{},' \
            .format(self.int_name, self.display_name, self.dmg_dice_num, self.dmg_dice_size, self.damage_type,
                    self.attack_type, str(self.range_short), str(self.range_long), str(self.tags),
                    str(self.num_targets))
        return outstring

    def __str__(self):
        return self.__repr__()

    def get_to_hit(self, owner):
        owner_str = owner.get_stat('str_mod')
        owner_dex = owner.get_stat('dex_mod')
        owner_prof = owner.get_stat('proficiency')
        attack_stat = 0
        if self.attack_type == 'melee':
            if 'finesse' in self.tags:
                attack_stat = max(owner_str, owner_dex)
            # Special martial arts case
            elif 'martial_arts' in owner.character_tags and \
                    ('monk' in self.tags or
                     ('simple' in self.tags and '2h' not in self.tags and 'heavy' not in self.tags)):
                attack_stat = max(owner_str, owner_dex)
            else:
                attack_stat = owner_str
        elif self.attack_type == 'ranged':
            if 'thrown' in self.tags:
                attack_stat = max(owner_str, owner_dex)
            else:
                attack_stat = owner_dex
        return attack_stat + owner_prof

    def get_damage(self, owner, use_versatile=False):
        owner_str = owner.get_stat('str_mod')
        owner_dex = owner.get_stat('dex_mod')
        attack_stat = 0
        if self.attack_type == 'melee':
            if 'finesse' in self.tags:
                attack_stat = max(owner_str, owner_dex)
            else:
                attack_stat = owner_str
        elif self.attack_type == 'ranged':
            if 'thrown' in self.tags:
                attack_stat = max(owner_str, owner_dex)
            else:
                attack_stat = owner_dex
        # (num_dice, dice_size, dmg_bonus, dmg_type, avg_dmg)
        dmg_dice_num, dmg_dice_size = self.dmg_dice_num, self.dmg_dice_size
        if use_versatile:
            dmg_dice_size += 2

        # Check for Martial Arts special case
        if 'martial_arts' in owner.character_tags:
            if ('monk' in self.tags) or \
                    (self.attack_type == 'melee' and 'simple' in self.tags
                     and 'heavy' not in self.tags and '2h' not in self.tags):
                if dmg_dice_num == 1 and dmg_dice_size < MARTIAL_ARTS_DAMAGE[owner.get_stat('hit_dice_num')]:
                    dmg_dice_size = MARTIAL_ARTS_DAMAGE[owner.get_stat('hit_dice_num')]
                attack_stat = max(owner_str, owner_dex)

        avg_dmg = dmg_dice_size / 2 * dmg_dice_num + attack_stat

        return int(avg_dmg), dmg_dice_num, dmg_dice_size, attack_stat, self.damage_type, avg_dmg

    def get_avg_dmg(self, owner):
        return self.get_damage(owner, use_versatile=True)[5]

    def get_title(self, owner: Character, short=True):
        return self.display_name

    def get_category(self):
        return 'attack'

    def get_entry(self, owner: Character, short=True):
        entry = ''
        is_melee = self.attack_type == 'melee'
        is_ranged = (self.attack_type == 'ranged' or 'thrown' in self.tags)
        if is_melee and is_ranged:
            entry += 'Melee or ranged weapon attack: '
        elif is_melee:
            entry += 'Melee weapon attack: '
        elif is_ranged:
            entry += 'Ranged weapon attack: '

        entry += '{} to hit, '.format(num_plusser(self.get_to_hit(owner)))

        if is_melee and 'reach' in self.tags:
            weapon_reach = WEAPON_REACH_W_BONUS
        else:
            weapon_reach = WEAPON_REACH_NORMAL

        if is_melee and is_ranged:
            entry += 'reach {} ft. or range {}/{} ft., '.format(weapon_reach, self.range_short, self.range_long)
        elif is_melee:
            entry += 'reach {} ft, '.format(weapon_reach)
        elif is_ranged:
            entry += 'range {}/{} ft., '.format(self.range_short, self.range_long)

        if self.num_targets == 1:
            entry += 'one target. '
        else:
            entry += NUM_TO_TEXT.get(self.num_targets) + ' targets. '
        ##
        avg_dmg_int, num_dmg_dice, dmg_dice_size, attack_mod, dmg_type, avg_dmg_float = self.get_damage(owner)
        entry += 'Hit: {}({}d{} {}) {} damage' \
            .format(avg_dmg_int, num_dmg_dice, dmg_dice_size, num_plusser(attack_mod, add_space=True), dmg_type)

        # Check for versatile, which increases damage with two hands.
        if is_melee and 'versatile' in self.tags:
            avg_dmg_int, num_dmg_dice, dmg_dice_size, attack_mod, dmg_type, avg_dmg_float = \
                self.get_damage(owner, use_versatile=True)
            entry += ' or {}({}d{} {}) {} damage if used with two hands' \
                .format(avg_dmg_int, num_dmg_dice, dmg_dice_size, num_plusser(attack_mod, add_space=True), dmg_type)
        entry += '.'
        return entry

    def get_visibility(self, owner: Character):
        return 0


class Spell:
    def __init__(self):
        self.name = ''
        self.source = ''
        self.level = -1
        self.school = ''
        self.classes = set()

    def __repr__(self):
        return '<Spell: {}>'.format(self.name)

    def __str__(self):
        return "[{},{},{},{},{}]".format(self.name, self.source, str(self.level), self.school, str(self.classes))


class SpellList:
    def __init__(self):
        self.name = None
        self.spells = {}

    def __str__(self):
        return "[{}: {}]".format(self.name, ",".join(self.spells))

    def add_spell(self, spell_obj):
        self.spells[spell_obj.name] = spell_obj

    def remove_spell(self, spell):
        if type(spell) == Spell:
            spell = spell.name
        if spell in self.spells:
            self.spells.pop(spell)

    def get_spell_names_by_level(self):
        out_spells = [set(), set(), set(), set(), set(), set(), set(), set(), set(), set(), ]
        for spell in self.spells.values():
            out_spells[spell.level].add(spell.name)
        return out_spells

    def get_spell_set_of_level(self, level):
        outset = set()
        for spell in self.spells.values():
            if spell.level == level:
                outset.add(spell.name)
        return outset

    def num_spells_of_level(self, level):
        count = 0
        for spell in self.spells.values():
            if spell.level == level:
                count += 1
        return count


class SpellCasterProfile:
    def __init__(self):
        self.intName = ''
        self.hd_per_casting_level = 1
        self.cantrips_per_level = None
        self.spells_known_modifier = 0
        # spell_lists = {spell_list : weight}
        self.spell_lists = {}
        self.free_spell_lists = []
        self.ready_style = ''
        self.casting_stat = ''
        self.fixed_spells_known_by_level = None
        # For now, only the standard slots table is supported
        # spell_slots_table[caster_level][spell_level]
        self.spell_slots_table = None
        self.tags = {}

    def get_free_spells(self):
        free_spells = [[], [], [], [], [], [], [], [], [], [], ]
        if self.free_spell_lists:
            for free_spell_list in self.free_spell_lists:
                for spell in free_spell_list.spells.values():
                    free_spells[spell.level].append(spell.name)
        return free_spells

    def get_random_spells(self, rnd_instance=None):

        if not rnd_instance:
            rnd_instance = random

        free_spells = set()
        if self.free_spell_lists:
            for spell_list in self.free_spell_lists:
                for spell_name in spell_list.spells.keys():
                    free_spells.add(spell_name)

        spell_selections = []

        # We do this for every spell level
        for spell_level in range(0, 10):
            total_spell_count = 0
            for spell_list in self.spell_lists.keys():
                total_spell_count += spell_list.num_spells_of_level(spell_level)

            spell_options = []
            spell_weights = []

            for spell_list, weight in self.spell_lists.items():
                num_spells_of_level = spell_list.num_spells_of_level(spell_level)
                if num_spells_of_level == 0:
                    continue
                weight_per_spell = float(weight) / num_spells_of_level
                for spell_name in spell_list.get_spell_set_of_level(spell_level):
                    spell_options.append(spell_name)
                    spell_weights.append(weight_per_spell)

            spell_selections_for_level = []
            spell_selections_remaining = MAX_SPELL_CHOICES_PER_LEVEL
            while spell_selections_remaining > 0:
                # First, check that we still have options
                if len(spell_options) == 0:
                    break

                choice_by_index = rnd_instance.choices(range(len(spell_weights)), spell_weights)[0]
                spell_choice = spell_options[choice_by_index]

                spell_options.pop(choice_by_index)
                spell_weights.pop(choice_by_index)

                if spell_choice in spell_selections:
                    continue
                elif spell_choice in free_spells:
                    continue
                else:
                    spell_selections_for_level.append(spell_choice)
                    spell_selections_remaining -= 1

            spell_selections.append(spell_selections_for_level)
        return spell_selections


class Loadout:
    def __init__(self):
        self.weapons = None
        self.armors = None
        self.shield = None

    def __str__(self):
        return '<{},{},{}>'.format(str(self.weapons), str(self.armors), str(self.shield))


class LoadoutPool:
    def __init__(self):
        self.name = ''
        self.loadouts = []
        self.weights = []

    def add_loadout(self, loadout: Loadout, weight=DEFAULT_LOADOUT_WEIGHT):
        self.loadouts.append(loadout)
        self.weights.append(weight)

    def get_random_loadout(self, rnd_instance=None):
        if not rnd_instance:
            rnd_instance = random

        return rnd_instance.choices(self.loadouts, self.weights)[0]


class FeatureMultiattack(CharacterFeature):
    def __init__(self, character, npc_gen, seed, short=True, args_tup=()):
        super().__init__(character, npc_gen, seed, short=True, args_tup=())
        self.int_name = 'multiattack'

        self.multiattack_type = args_tup[0]
        self.attacks = 1
        char_hd = character.get_stat('hit_dice_num')
        if self.multiattack_type == 'fighter':
            if char_hd >= 20:
                self.attacks = 4
            elif char_hd >= 11:
                self.attacks = 3
            elif char_hd >= 5:
                self.attacks = 2
        elif self.multiattack_type == 'single':
            if char_hd >= 5:
                self.attacks = 2

    def get_stat_block_entries(self, character: 'Character', short=True):
        entries = []
        entries.append(StatBlockEntry(
            'Multiattack', 'multiattack', 0,
            "You may make {} attacks when using the attack action.".format(NUM_TO_TEXT[self.attacks])
        ))
        return entries


class FeatureSpellcasting(CharacterFeature):
    def __init__(self, character, npc_gen, seed, short=True, args_tup=()):
        super().__init__(character, npc_gen, seed, short=True, args_tup=())
        self.int_name = 'spellcasting'
        sp_profile = npc_gen.spellcaster_profiles[args_tup[0]]
        assert isinstance(sp_profile, SpellCasterProfile)

        # NPCs generally either have spells 'prepared' or 'known'
        self.ready_style = sp_profile.ready_style
        # Which stat is used for casting
        self.casting_stat = sp_profile.casting_stat
        self.hd_per_casting_level = sp_profile.hd_per_casting_level
        self.spells_readied_progression = DEFAULT_SPELLS_READIED_PROGRESSION
        self.cantrips_progression = CASTER_CANTRIPS_KNOWN[sp_profile.cantrips_per_level]
        self.fixed_spells_known_by_level = sp_profile.fixed_spells_known_by_level
        self.slots_progression = sp_profile.spell_slots_table
        self.spells_known_modifier = sp_profile.spells_known_modifier
        self.free_spell_lists = sp_profile.free_spell_lists
        self.spell_lists = sp_profile.spell_lists

        # A list of lists, index corresponds to the list of spells know for each level, 0 for cantrips
        self.spell_choices = None
        self.free_spells = self.get_free_spells(npc_gen=npc_gen)
        self.spell_choices = self.get_spell_choices(npc_gen=npc_gen, seed=seed)
        self.spells_known = [[], [], [], [], [], [], [], [], [], [], ]
        self.spells_known_set = set()

    def get_free_spells(self, npc_gen: 'NPCGenerator'):
        free_spells = [[], [], [], [], [], [], [], [], [], [], ]
        if self.free_spell_lists:
            for free_spell_list_name in self.free_spell_lists:
                spell_list = npc_gen.spell_lists[free_spell_list_name]
                for spell in spell_list.spells.values():
                    free_spells[spell.level].append(spell.name)
        return free_spells

    # We pre-select all the possible spell choices a caster can make.
    # This is where we weight the choices by spell list
    def get_spell_choices(self, npc_gen, seed):

        rnd_instance = random.Random(seed + 'spellchoices')

        free_spells = set()
        for spell_level in self.free_spells:
            for spell_name in spell_level:
                free_spells.add(spell_name)

        spell_selections = []
        # We do this for every spell level
        for spell_level in range(0, 10):
            total_spell_count = 0
            for spell_list_name in self.spell_lists.keys():
                spell_list = npc_gen.spell_lists[spell_list_name]
                total_spell_count += spell_list.num_spells_of_level(spell_level)

            spell_options = []
            spell_weights = []

            for spell_list_name, weight in self.spell_lists.items():
                spell_list = npc_gen.spell_lists[spell_list_name]
                num_spells_of_level = spell_list.num_spells_of_level(spell_level)
                if num_spells_of_level == 0:
                    continue
                weight_per_spell = float(weight) / num_spells_of_level
                for spell_name in spell_list.get_spell_set_of_level(spell_level):
                    spell_options.append(spell_name)
                    spell_weights.append(weight_per_spell)

            spell_selections_for_level = []
            spell_selections_remaining = MAX_SPELL_CHOICES_PER_LEVEL
            while spell_selections_remaining > 0:
                # First, check that we still have options
                if len(spell_options) == 0:
                    break

                choice_by_index = rnd_instance.choices(range(len(spell_weights)), spell_weights)[0]
                spell_choice = spell_options[choice_by_index]

                spell_options.pop(choice_by_index)
                spell_weights.pop(choice_by_index)

                if spell_choice in spell_selections:
                    continue
                elif spell_choice in free_spells:
                    continue
                else:
                    spell_selections_for_level.append(spell_choice)
                    spell_selections_remaining -= 1

            spell_selections.append(spell_selections_for_level)
        return spell_selections

    def get_spell_dc(self, owner):
        return owner.get_stat(self.casting_stat + '_dc')

    # Caster level is actually a bit weird for half and third casters like paladins and eldritch knights
    # They only get their first casting level at 2 or 3 hd, respectively
    # BUT, the next hd they gets bumps them up to the next spellcaster level regardless
    # So, that's why this function looks weird
    def get_caster_level(self, owner):
        hit_dice = owner.get_stat('hit_dice_num')
        if self.hd_per_casting_level == 1:
            caster_level = hit_dice
        else:
            if hit_dice < self.hd_per_casting_level:
                caster_level = 0
            elif hit_dice == self.hd_per_casting_level:
                caster_level = 1
            else:
                caster_level = (hit_dice + self.hd_per_casting_level - 1) // self.hd_per_casting_level
        return caster_level

    # Here's wehre we do all the major stuff
    def second_pass(self, character: 'Character', npc_gen: 'NPCGenerator', seed):
        rnd_instance = random.Random(seed + self.int_name + 'spellpicking')
        char_hd = character.get_stat('hit_dice_num')
        caster_level = self.get_caster_level(character)
        if self.fixed_spells_known_by_level:
            spells_readied_remaining = self.fixed_spells_known_by_level[char_hd]
        else:
            spells_readied_remaining = caster_level + character.get_stat(self.casting_stat + '_mod') + self.spells_known_modifier

        spell_slots = self.slots_progression
        max_spell_level = 9
        for spell_level in range(1, 10):
            if spell_slots[caster_level][spell_level] <= 0:
                max_spell_level = spell_level - 1
                break
            else:
                for free_spell in self.free_spells[spell_level]:
                    self.spells_known[spell_level].append(free_spell)

        cantrips_remaining = int(self.cantrips_progression[char_hd])
        while cantrips_remaining > 0:
            self.spells_known[0].append(self.spell_choices[0].pop(0))
            cantrips_remaining -= 1

        # First, go through and make sure the caster has at least one spell from each level
        for spell_level in range(1, max_spell_level + 1):
            if spells_readied_remaining > 0:
                self.spells_known[spell_level].append(self.spell_choices[spell_level].pop(0))
                spells_readied_remaining -= 1

        while spells_readied_remaining > 0:
            weights = [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]
            for spell_level in range(1, max_spell_level + 1):
                weights[spell_level] = sum(self.slots_progression[caster_level][spell_level:])
                weights[spell_level] /= len(self.spells_known[spell_level])
            spell_level_choice = rnd_instance.choices(range(1, max_spell_level + 1), weights[1:max_spell_level + 1])[0]
            self.spells_known[spell_level_choice].append(self.spell_choices[spell_level_choice].pop(0))
            spells_readied_remaining -= 1

        for spell_level in range(0, 10):
            for spell_name in self.spells_known[spell_level]:
                self.spells_known_set.add(spell_name)

        # It's wacky and confusing and I don't understand it, but now self.spells_known should have an appropriate
        # set of randomly generated spells know by level and self.spells_known_set should have a set of all spells

        # Now, we can do some of those special case things
        if 'mage armor' in self.spells_known_set:
            npc_gen.give_armor(character, 'mage_armor', extra=True)

    def get_main_stat_block_entry(self, owner, short=True):
        caster_level = self.get_caster_level(owner)
        if caster_level == 0:
            return None

        text = "This character is a {}-level spellcaster. " \
               "Its spellcasting ability is {} (spell save DC {}, {} to hit with spell attacks). " \
               "It has the following spells {}:" \
               .format(NUM_TO_ORDINAL[caster_level],
                       ATTRIBUTES_ABBREVIATION_TO_FULL_WORD[self.casting_stat],
                       owner.get_stat(self.casting_stat + '_dc'),
                       num_plusser(owner.get_stat(self.casting_stat + '_attack')), self.ready_style) + '\n'
        # Cantrips
        if len(self.spells_known[0]) > 0:
            text += 'Cantrips (at-will): ' + ', '.join(self.spells_known[0])
        for i in range(1, 10):
            if len(self.spells_known[i]) > 0 and self.slots_progression[caster_level][i] > 0:
                # Pluralize 'slot' or not
                if self.slots_progression[caster_level][i] == 1:
                    text += '\n{} level ({} slot): ' \
                        .format(NUM_TO_ORDINAL[i], self.slots_progression[caster_level][i])
                else:
                    text += '\n{} level ({} slots): ' \
                        .format(NUM_TO_ORDINAL[i], self.slots_progression[caster_level][i])
                text += ', '.join(self.spells_known[i])
        return StatBlockEntry('Spellcasting', 'spellcasting', 0, text)

    def get_stat_block_entries(self, character: 'Character', short=True):
        entries = []
        entries.append(self.get_main_stat_block_entry(character, short))
        return entries


# Below this point are classes for particular Character Features
FEATURE_TINKER_OPTIONS = {
    'clockwork toy': 'This toy is a clockwork animal, monster, or person, such as a frog, mouse, bird, dragon, or soldier. When placed on the ground, the toy moves 5 feet across the ground on each of your turns in a random direction. It makes noises as appropriate to the creature it represents.',
    'fire box': 'The device produces a miniature flame, which you can use to light a candle, torch, or campfire. Using the device requires your action.',
    'music box': "When opened, this music box plays a single song at a moderate volume. The box stops playing when it reaches the song's end or when it is closed.",
}


class FeatureTinker(CharacterFeature):
    def __init__(self, character, npc_gen, seed, short=True, args_tup=()):
        super().__init__(character, npc_gen, seed, short=True, args_tup=())
        self.int_name = 'tinker'
        rnd_instance = random.Random(seed + self.int_name + 'init')
        self.choice = rnd_instance.choice(list(FEATURE_TINKER_OPTIONS.keys()))

    def first_pass(self, character: 'Character', npc_gen: 'NPCGenerator', seed):
        character.add_skill('tinkers_tools')

    def get_stat_block_entries(self, character: 'Character', short=True):
        entries = []
        entries.append(StatBlockEntry('Tinker', 'passive', 2,
                                      "You have proficiency with artisan's tools (tinker's tools). Using those tools, "
                                      "you can spend 1 hour and 10 gp worth of materials to construct a Tiny clockwork "
                                      "device (AC 5, 1 hp). The device ceases to function after 24 hours (unless you "
                                      "spend 1 hour repairing it to keep the device functioning), or when you use your "
                                      "action to dismantle it; at that time, you can reclaim the materials used to "
                                      "create it. You can have up to three such devices active at a time."))
        entries.append(StatBlockEntry(self.choice.title(), 'passive', 0,
                                      FEATURE_TINKER_OPTIONS[self.choice]))
        return entries


FEATURE_DRAGONBORN_CHART = {
    'black': ('acid', '5 by 30 ft. line', 'dex'),
    'blue': ('lightning', '5 by 30 ft. line', 'dex'),
    'brass': ('fire', '5 by 30 ft. line', 'dex'),
    'bronze': ('lightning', '5 by 30 ft. line', 'dex'),
    'copper': ('acid', '5 by 30 ft. line', 'dex'),
    'gold': ('fire', '15 ft. cone', 'dex'),
    'green': ('poison', '15 ft. cone', 'con'),
    'red': ('fire', '15 ft. cone', 'dex'),
    'silver': ('cold', '15 ft. cone', 'con'),
    'white': ('cold', '15 ft. cone', 'con'),
}


class FeatureDragonborn(CharacterFeature):
    def __init__(self, character, npc_gen, seed, short=True, args_tup=()):
        super().__init__(character, npc_gen, seed, short=True, args_tup=())
        self.int_name = 'dragonborn_feature'
        self.lineage_type = args_tup[0]

    def first_pass(self, character: 'Character', npc_gen: 'NPCGenerator', seed):
        character.add_damage_resistance(FEATURE_DRAGONBORN_CHART[self.lineage_type][0])

    def get_stat_block_entries(self, character: 'Character', short=True):
        entries = []
        hd = character.get_stat('hit_dice_num')
        if hd >= 16:
            dmg_dice = 5
        elif hd >= 11:
            dmg_dice = 4
        elif hd >= 6:
            dmg_dice = 3
        else:
            dmg_dice = 2
        text = "When you use your breath weapon, each creature in a {} must make a DC {} {} saving throw. " \
               "A creature takes {}d6 {} damage on a failed save, and half as much damage on a successful one." \
            .format(FEATURE_DRAGONBORN_CHART[self.lineage_type][1], character.get_stat('con_dc'),
                    FEATURE_DRAGONBORN_CHART[self.lineage_type][2], dmg_dice,
                    FEATURE_DRAGONBORN_CHART[self.lineage_type][0])
        breath_weapon_entry = StatBlockEntry('Breath Weapon (1/short)', 'action', 0, text)
        entries.append(breath_weapon_entry)
        return entries
