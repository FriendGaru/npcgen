from typing import Dict

NUM2WORD = {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}

STATS_ATTRIBUTES = ('str', 'dex', 'con', 'int', 'wis', 'cha', )
DEFAULT_ATTRIBUTE_VALUE = 8
ATTRIBUTES_FULL: Dict[str, str] = {
    'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution',
    'int': 'Intelligence', 'wis': 'Wisdom', 'cha': ' Charisma',
}

STATS_BASE = {
    'hit_dice_num': 1, 'hit_dice_size': 8, 'hit_points_extra': 0, 'proficiency_extra': 0,
    'speed_walk': 30, 'speed_fly': 0, 'speed_burrow': 0, 'speed_swim': 0,
    'random_stat_points': 0,
    'size': 'medium',
    # Armor AC Bonus is granted to some fighters
    'armorACBonus': 0,
}
STATS_DERIVED = (
    'hit_points', 'proficiency',
)

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
SKILLS_ORDERED = sorted(SKILLS.keys())

ROLL_METHODS = {
    '3d6': (6, 3, 0, 0),
    '4d6dl': (6, 3, 1, 0),
    '5d6dldh': (6, 3, 1, 1),
}
DEFAULT_ROLL_METHOD = '3d6'
# Max times a stat reroll is allowed, to prevent overflowing
REROLLS_CAP = 99
DEFAULT_HITDICE_NUM = 5
DEFAULT_HITDICE_SIZE = 8

# Data Files
DATA_FOLDER = 'data\\'
ARMORS_FILENAME = DATA_FOLDER + 'armors.csv'
WEAPONS_FILENAME = DATA_FOLDER + 'weapons.csv'
TRAITS_FILENAME = DATA_FOLDER + 'traits.csv'
SPELLS_FILENAME = DATA_FOLDER + 'spells.csv'
SPELLLISTS_FILENAME = DATA_FOLDER + 'spelllists.csv'
SPELLCASTERPROFILES_FILENAME = DATA_FOLDER + 'spellcasterprofiles.csv'
LOADOUTPOOLS_FILENAME = DATA_FOLDER + 'loadoutpools.csv'
RACETEMPLATES_FILENAME = DATA_FOLDER + 'racetemplates.csv'
CLASSTEMPLATES_FILENAME = DATA_FOLDER + 'classtemplates.csv'

TRAIT_TYPES = (
    'passive', 'hidden', 'action', 'reaction',
)

VALID_SIZES = (
    'small', 'medium', 'large',
)
DEFAULT_SIZE = 'medium'

DEFAULT_RACE = 'humanoid'
DEFAULT_CLASS = 'soldier'


DEFAULT_WEAPON_REACH = 'reach 5 ft.'
WEAPON_REACH_W_BONUS = 'reach 10 ft.'
DEFAULT_NUM_TARGETS = 1


DEFAULT_LOADOUT_POOL_WEIGHT = 10
DEFAULT_LOADOUTSET_WEIGHT = 1

ASI_HD_PER_INCREASE = 4
ASI_POINTS_PER_INCREASE = 2

ASI_PROGRESSION_PRIORITY_WEIGHT = 3
ASI_PROGRESSION_OTHER_WEIGHT = 1

MAX_SPELL_CHOICES_PER_LEVEL = 10
DEFAULT_SPELLS_READIED_PROGRESSION = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 1, 2, 3,
)

DEFAULT_SPELLCASTER_SLOTS = (
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
        #11
        (-1, 4, 3, 3, 3, 2, 1, 0, 0, 0,),
        (-1, 4, 3, 3, 3, 2, 1, 0, 0, 0,),
        (-1, 4, 3, 3, 3, 2, 1, 1, 0, 0,),
        (-1, 4, 3, 3, 3, 2, 1, 1, 0, 0,),
        (-1, 4, 3, 3, 3, 2, 1, 1, 1, 0,),
        #16
        (-1, 4, 3, 3, 3, 2, 1, 1, 1, 0,),
        (-1, 4, 3, 3, 3, 2, 1, 1, 1, 1,),
        (-1, 4, 3, 3, 3, 3, 1, 1, 1, 1,),
        (-1, 4, 3, 3, 3, 3, 2, 1, 1, 1,),
        (-1, 4, 3, 3, 3, 3, 2, 2, 1, 1,),
)

# CASTER_SPELL_SLOTS = {
#     # Index zeroes are dummied out so the index can nicely correspond to ccharacter/spell level
#     'full': (
#         (),
#         # 1
#         (-1, 2, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
#         # 6
#         (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 2, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 3, 1, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 3, 2, 0, 0, 0, 0,),
#         #11
#         (-1, 4, 3, 3, 3, 2, 1, 0, 0, 0,),
#         (-1, 4, 3, 3, 3, 2, 1, 0, 0, 0,),
#         (-1, 4, 3, 3, 3, 2, 1, 1, 0, 0,),
#         (-1, 4, 3, 3, 3, 2, 1, 1, 0, 0,),
#         (-1, 4, 3, 3, 3, 2, 1, 1, 1, 0,),
#         #16
#         (-1, 4, 3, 3, 3, 2, 1, 1, 1, 0,),
#         (-1, 4, 3, 3, 3, 2, 1, 1, 1, 1,),
#         (-1, 4, 3, 3, 3, 3, 1, 1, 1, 1,),
#         (-1, 4, 3, 3, 3, 3, 2, 1, 1, 1,),
#         (-1, 4, 3, 3, 3, 3, 2, 2, 1, 1,),
#     ),
#     'half': (
#         (),
#         #1
#         (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 2, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
#         #6
#         (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
#         #11
#         (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 2, 0, 0, 0, 0, 0,),
#         #16
#         (-1, 4, 3, 3, 2, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 3, 1, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 3, 1, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 3, 2, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 3, 2, 0, 0, 0, 0,),
#     ),
#     'third': (
#         (),
#         #1
#         (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 2, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
#         #6
#         (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
#         #11
#         (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
#         #16
#         (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
#         (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
#     ),
# }

CASTER_SPELLS_KNOWN = {
    'sorcerer': (-1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15),
    'half': (-1, 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11),
    'third': (-1, 0, 0, 3, 4, 4, 4, 5, 6, 6, 7, 8, 8, 9, 10, 10, 11, 11, 11, 12, 13),
}

CASTER_CANTRIPS_KNOWN = {
    'none': (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ),
    'wizard': (-1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, ),
    'sorcerer': (-1, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, ),
}


SPELL_LEVEL_ORDINAL_TO_NUM = {
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


DEFAULT_SPELL_WEIGHT = 10

# Data for special traits
MARTIAL_ARTS_DAMAGE = (
    (-1, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 8, 10, 10, 10, 10, )
)