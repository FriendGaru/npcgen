from typing import Dict

NUM2WORD = {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}

STATS_ATTRIBUTES = ('str', 'dex', 'con', 'int', 'wis', 'cha', )
DEFAULT_ATTRIBUTE_VALUE = 8
ATTRIBUTES_FULL: Dict[str, str] = {
    'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution',
    'int': 'Intelligence', 'wis': 'Wisdom', 'cha': ' Charisma',
}

STATS_BASE = {
    'hitDiceNum': 1, 'hitDiceSize': 8, 'hitPointsExtra': 0, 'proficiencyExtra': 0,
    'speedWalk': 30, 'speedFly': 0, 'speedBurrow': 0, 'speedSwim': 0,
    'randomStatPoints': 0,
    'size': 'medium',
    # Armor AC Bonus is granted to some fighters
    'armorACBonus': 0,
}
STATS_DERIVED = (
    'hitPoints', 'proficiency',
    'moveWalkFinal', 'moveFlyFinal', 'moveBurrowFinal', 'moveSwimFinal'
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
ARMORS_FILENAME = 'armors.csv'
WEAPONS_FILENAME = 'weapons.csv'
TRAITS_FILENAME = 'traits.csv'
SPELLS_FILENAME = 'spells.csv'
SPELLLISTS_FILENAME = 'spelllists.csv'
LOADOUTPOOLS_FILENAME = 'loadoutpools.csv'
RACETEMPLATES_FILENAME = 'racetemplates.csv'
CLASSTEMPLATES_FILENAME = 'classtemplates.csv'

TRAIT_TYPES = (
    'passive', 'hidden', 'action', 'reaction',
)

# TRAITS = {
#     'breathWeapon': {
#         'displayName': 'Breath Weapon', 'traitType': 'action',
#         'traitText': 'Does {proficiency}d6 damage with DC{conDC}'
#     },
#
#     'naturalArmor': {
#         'displayName': 'Natural Armor', 'traitType': 'passive',
#         'traitText': 'Has natural AC 13 + Dex modifier',
#         'tags': {'giveArmor': 'natural_armor'}
#     },
#
#     'lucky': {
#         'displayName': 'Lucky', 'traitType': 'passive',
#         'traitText': 'Reroll 1s.'
#     },
#
#
# }
VALID_SIZES = (
    'small', 'medium', 'large',
)
DEFAULT_SIZE = 'medium'


# TEMPLATES_RACE = {
#     'humanoid': {
#         'displayName': 'Humanoid (Any)',
#     },
#
#     'aaracocra': {
#         'displayName': 'Aaracocra',
#         'attributeBonuses': {'dex': 2, 'wis': 2},
#         'baseStats': {'speedWalk': 20, 'speedFly': 50},
#         'traits': ['lucky']
#     },
#
#     'halflingLightfoot': {
#         'displayName': 'Halfling (Lightfoot)',
#         'attributeBonuses': {'dex': 2, 'wis': 1},
#         'baseStats': {'speedWalk': 25, 'size': 'small'},
#         'traits': ['lucky']
#     },
#
#     'lizardFolk': {
#         'displayName': 'Lizardfolk',
#         'attributeBonuses': {'con': 2, 'wis': 1},
#         'traits': ['naturalArmor']
#     },
# }
DEFAULT_RACE = 'humanoid'

# TEMPLATES_CLASS = {
#     # internalName: (DisplayName, statPriorities, skills, saves, traits, armors, weapons)
#     'soldier': {
#         'displayName': 'Soldier', 'priorityAttributes': ('str', 'con'),
#         'saves': ('con', ),
#         'skillsFixed': ('athletics', ),
#         'skillsRandom': (2, 'acrobatics', 'stealth', 'survival', 'intimidation', ),
#         'armorLoadoutSet': 'soldier',
#         'weaponLoadoutSet': 'soldier',
#         'tags': (),
#     },
#
#     'magicker': {
#         'displayName': 'Magicker', 'priorityAttributes': ('int', 'con'),
#         'saves': ('int', 'wis', ),
#         'skillsFixed': ('arcana', 'investigation'),
#         'skillsRandom': (2, 'religion', 'insight', 'nature', 'history'),
#         'armorLoadoutSet': 'mage',
#         'weaponLoadoutSet': 'mage',
#         'tags': (),
#         'spellCastingProfile': 'evoker',
#     },
# }
DEFAULT_CLASS = 'soldier'

ARMORS = {
    # internalName: (base armor, armorType,
    #               minStr(-1 for none)), StealthDisadvantage, displayName), extraFlags)
    # Tags:
    # preferred : If there's a tie for AC, choose this armor. No sense wearing leather armor if natural armor would be
    # just as good, after all
    # notArmor : Doesn't count as wearing armor, in case another ability is dependent on that
    # extra : This armor is unreliable, so the character should have a 'base' armor as well. Mainly just for Mage Armor.
    # noShield : Shields provide no bonus when used with this armor.
    'none': (
        'Unarmored', 10, 'light', -1, False, {'notArmor'}),
    'padded': (
        'Padded Armor', 11, 'light', -1, True, {}),
    'leather': (
        'Leather Armor', 11, 'light', -1, False, {}),
    'studdedLeather': (
        'Studded Leather Armor', 12, 'light', -1, False, {}),

    'hide': (
        'Hide Armor', 12, 'medium', -1, False, {}),
    'chainShirt': (
        'Chain Shirt', 13, 'medium', -1, False, {}),
    'scaleMail': (
        'Scale Mail', 14, 'medium', -1, True, {}),

    'ringMail': (
        'Ring Mail', 14, 'heavy', -1, True, {}),
    'chainMail': (
        'Chain Mail', 16, 'heavy', 13, True, {}),

    'unarmoredDefenseBarbarian': (
        'Unarmored', 14, 'light', -1, False, {'notArmor', 'preferred'}),
    'unarmoredDefenseMonk': (
        'Unarmored', 14, 'light', -1, False, {'notArmor', 'noShield', 'preferred'}),

    'naturalArmor': (
        'Natural Armor', 13, 'light', -1, False, {'preferred'}),

    'mageArmor': (
        'Mage Armor', 14, 'light', -1, False, {'extra', })

}

DEFAULT_WEAPON_REACH = 'reach 5 ft.'
WEAPON_REACH_W_BONUS = 'reach 10 ft.'
DEFAULT_NUM_TARGETS = 1
# WEAPONS = {
#     # internalName : (displayName, dmgDiceNum, dmgDiceSize, damageType,
#     #                   type (melee:'m', ranged:'r', both:'b'), shortRange, longRange,
#     #                   tags,)
#
#     # simple melee
#     'unarmed': (
#         'Unarmed', 1, 1, 'bludgeoning',
#         'm', 0, 0,
#         {}
#     ),
#     'club': (
#         'Club', 1, 4, 'bludgeoning',
#         'm', 0, 0,
#         {'light'}
#     ),
#     'dagger': (
#         'Dagger', 1, 4, 'piercing',
#         'm', 20, 60,
#         {'finesse', 'light', 'thrown'}),
#     'greatclub': (
#         'Greatclub', 1, 8, 'bludgeoning',
#         'm', 0, 0,
#         {'2h'}
#     ),
#     'handaxe': (
#         'Handaxe', 1, 6, 'slashing',
#         'm', 20, 60,
#         {'light', 'thrown'}
#     ),
#     ##
#     'quarterstaff': (
#         'Quarterstaff', 1, 6, 'bludgeoning',
#         'm', 0, 0,
#         {'versatile': (1, 8)}
#     ),
#
#     # simple ranged
#     'crossbowLight': (
#         'Crossbow, Light', 1, 8, 'piercing',
#         'r', 80, 320,
#         {'ammunition', 'loading', '2h'}
#     ),
#     'dart': (
#         'Dart', 1, 4, 'piercing',
#         'r', 20, 60,
#         {'finesse', 'thrown'}
#     ),
#
#     # martial melee
#     'battleaxe': (
#         'Battleaxe', 1, 8, 'slashing',
#         'm', 0, 0,
#         {'versatile': (1, 10)}
#     ),
#
#     'flail': (
#         'Flail', 1, 8, 'bludgeoning',
#         'm', 0, 0,
#         {}
#     ),
#
#     'glaive': (
#         'Glaive', 1, 10, 'slashing',
#         'm', 0, 0,
#         {'heavy', 'reach', '2h'}
#     ),
# }

DEFAULT_LOADOUT_POOL_WEIGHT = 10

DEFAULT_LOADOUTSET_WEIGHT = 10
WEAPON_LOADOUT_SETS = {
    # internalName : (
    #   [guaranteed items],
    #   *[(optional weight), *items],
    # ),
    'soldier':  (
        [],
        ['battleaxe'],
        ['flail', 'shield'],
        ['handaxe', 'shield', 'crossbow_light'],
    ),
    'mage': (
        [],
        [1, 'club'],
        [1, 'quarterstaff'],
        [1, 'club', 'shield'],
        [100, 'club', 'dagger', 'quarterstaff', 'crossbow_light'],
    ),
}

ARMOR_LOADOUT_SETS = {
    # Like weapons, but since characters choose best armor later it's okay to give them more guaranteed armor
    'soldier': (
        ['leather', 'hide'],
        [10, ],
        [10, 'chain_shirt'],
        [10, 'ring_mail'],
        [10, 'chain_mail'],
    ),
    'mage': (
        ['mage_armor'],
        [10, 'padded'],
        [10, 'unarmored'],
    ),
}

CASTER_SPELL_SLOTS = {
    # Index zeroes are dummied out so the index can nicely correspond to ccharacter/spell level
    'full': (
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
    ),
    'half': (
        (),
        #1
        (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 2, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
        #6
        (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
        #11
        (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 2, 0, 0, 0, 0, 0,),
        #16
        (-1, 4, 3, 3, 2, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 3, 1, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 3, 1, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 3, 2, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 3, 2, 0, 0, 0, 0,),
    ),
    'third': (
        (),
        #1
        (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 2, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
        #6
        (-1, 3, 0, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 2, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
        #11
        (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 0, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 2, 0, 0, 0, 0, 0, 0,),
        #16
        (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 0, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
        (-1, 4, 3, 3, 1, 0, 0, 0, 0, 0,),
    ),
}

CASTER_SPELLS_KNOWN = {
    'full': (-1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15),
    'half': (-1, 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11),
    'third': (-1, 0, 0, 3, 4, 4, 4, 5, 6, 6, 7, 8, 8, 9, 10, 10, 11, 11, 11, 12, 13),
}

CASTER_CANTRIPS_KNOWN = {
    'wizard': (-1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, ),
    'sorcerer': (-1, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, ),
}

# SPELLS_FILE = 'spells.txt'

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

# SPELL_LISTS_AUTO = {
#     'evoker': {
#         'class': 'sorcerer',
#         'school': 'evocation',
#     },
#     'conjurer': {
#         'class': 'cleric',
#         'school': 'conjuration',
#     },
#     'wizard': {
#         'class': 'wizard',
#     },
#     'cleric': {
#         'class': 'cleric'
#     },
# }
#
# SPELL_LISTS_FIXED = {
#     'healer': (
#         'cure wounds', 'healing word', 'mass cure wounds', 'heal',
#     ),
# }

DEFAULT_SPELL_WEIGHT = 10
SPELLCASTER_PROFILES = {
    'wizard': {
        'castStat': 'int',
        'readyStyle': 'prepared',
        'slots': 'full',
        'spellsKnown': None,
        'cantrips': 'wizard',
        'spellLists': ('wizard',),
    },

    'evoker': {
        'castStat': 'int',
        'readyStyle': 'prepared',
        'slots': 'full',
        'spellsKnown': None,
        'cantrips': 'wizard',
        'spellLists': ((50, 'evoker'), 'wizard',),
    },

    'priest': {
        'castStat': 'wis',
        'readyStyle': 'known',
        'slots': 'half',
        'spellsKnown': None,
        'cantrips': 'sorcerer',
        'spellLists': ((200, 'healer'), 'cleric',),
    }
}