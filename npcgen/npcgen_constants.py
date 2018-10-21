from typing import Dict

STATS_ATTRIBUTES = ('str', 'dex', 'con', 'int', 'wis', 'cha',)
DEFAULT_ATTRIBUTE_VALUE = 8
ATTRIBUTES_ABBREVIATION_TO_FULL_WORD: Dict[str, str] = {
    'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution',
    'int': 'Intelligence', 'wis': 'Wisdom', 'cha': 'Charisma',
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
    4, 6, 8, 10, 12, 20
)

TRAIT_TYPES = (
    'hidden', 'passive', 'action', 'reaction',
)

VALID_SIZES = (
    'tiny', 'small', 'medium', 'large', 'huge', 'gargantuan'
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

MAX_SPELL_CHOICES_PER_LEVEL = 15
DEFAULT_SPELL_LIST_WEIGHT = 1

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