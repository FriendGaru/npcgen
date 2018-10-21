import collections
import random
import csv
from enum import Enum
from npcgen.npcgen_constants import *
import pkg_resources as pkg

# -1 - Nothing at all
# 0 - Errors only
# 1 - Basic operations
# 2 - Minor operations
# 3 - Painfully Verbose
DEBUG_VERBOSITY = 1


def debug_print(message, required_verbosity=2):
    """
    Prints out a message for debugging purposes. Higher numbers are more verbose, uses the DEBUG_VERBOSITY constant.
    """
    if DEBUG_VERBOSITY >= required_verbosity:
        print(message)


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


# I format my csv tag entries like 'tag_name:tag_val1;tag_val2,second_tag_name'
# This will break them apart and return dictionaries like {tag_name: [tag_val1, tag_val2], second_tag_name: []}
def csv_tag_reader(item_line, tag_delimiter=';', tag_value_separator=':', tag_val_delimiter=','):
    if item_line == '':
        return {}
    tags_dict = {}
    for tag_raw in item_line.replace(" ", "").split(tag_delimiter):
        if tag_value_separator in tag_raw:
            tag_name, tag_values_raw = tag_raw.split(tag_value_separator)
            tag_val_list = tag_values_raw.split(tag_val_delimiter)
        else:
            tag_name, tag_val_list = tag_raw, []
        tags_dict[tag_name] = tag_val_list
    return tags_dict


class ContentType(Enum):
    ARMOR = 1
    WEAPON = 2
    RACE = 3
    CLASS = 4
    SPELL = 5
    SPELL_LIST = 6
    SPELLCASTER_PROFILE = 7
    ARMOR_LOADOUT_POOL = 8
    WEAPON_LOADOUT_POOL = 9
    TRAIT = 10


RANDOMIZABLE_RACE_CATEGORIES = (
    'gnome',
)

RANDOMIZABLE_CLASS_CATEGORIES = (
    'warrior', 
)


class ContentSource:
    def __init__(self,
                 weapons_file_loc=WEAPONS_FILE,
                 armors_file_loc=ARMORS_FILE,
                 spells_file_loc=SPELLS_FILE,
                 spell_lists_file_loc=SPELLLISTS_FILE,
                 spellcaster_profiles_file_loc=SPELLCASTER_PROFILES_FILE,
                 armors_loadout_pools_file_loc=ARMORS_LOADOUT_POOLS_FILE,
                 weapons_loadout_pools_file_loc=WEAPONS_LOADOUT_POOLS_FILE,
                 traits_file_loc=TRAITS_FILE,
                 race_templates_file_loc=RACE_TEMPLATES_FILE,
                 class_templates_file_loc=CLASS_TEMPLATES_FILE,
                 ):

        self.race_templates = collections.OrderedDict()
        self.race_categories = collections.OrderedDict()
        self.load_race_templates_from_csv(race_templates_file_loc)

        self.class_templates = collections.OrderedDict()
        self.class_categories = collections.OrderedDict()
        self.load_class_templates_from_csv(class_templates_file_loc)

        self.weapon_templates = {}
        self.load_weapons_from_csv(weapons_file_loc)

        self.weapon_loadout_pools = {}
        self.load_weapons_loadout_pools_from_csv(weapons_loadout_pools_file_loc)

        self.armor_templates = {}
        self.load_armors_from_csv(armors_file_loc)

        self.armor_loadout_pools = {}
        self.load_armors_loadout_pools_from_csv(armors_loadout_pools_file_loc)

        self.spells = {}
        self.load_spells_from_csv(spells_file_loc)

        self.spell_lists = {}
        self.load_spell_lists_from_csv(spell_lists_file_loc)

        self.spellcaster_profiles = {}
        self.load_spellcaster_profiles_from_csv(spellcaster_profiles_file_loc)

        self.trait_templates = {}
        self.load_traits_from_csv(traits_file_loc)

        self.content_type_map = {
            ContentType.ARMOR: self.armor_templates,
            ContentType.WEAPON: self.weapon_templates,
            ContentType.ARMOR_LOADOUT_POOL: self.armor_loadout_pools,
            ContentType.WEAPON_LOADOUT_POOL: self.weapon_loadout_pools,
            ContentType.RACE: self.race_templates,
            ContentType.CLASS: self.class_templates,
            ContentType.SPELL: self.spells,
            ContentType.SPELL_LIST: self.spell_lists,
            ContentType.SPELLCASTER_PROFILE: self.spellcaster_profiles,
            ContentType.TRAIT: self.trait_templates,
        }
        
    def add_race_to_category(self, race_name, category):
        if category in self.race_categories:
            self.race_categories[category].append(race_name)
        else:
            self.race_categories[category] = [race_name, ]
            
    def add_class_to_category(self, class_name, category):
        if category in self.class_categories:
            self.class_categories[category].append(class_name)
        else:
            self.class_categories[category] = [class_name, ]

    def load_armors_from_csv(self, armors_file_loc):
        with open(armors_file_loc, newline='', encoding="utf-8") as armors_file:
            armors_file_reader = csv.DictReader(armors_file)
            for line in armors_file_reader:

                # Ignore blank lines or comments using hashtags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue

                new_armor = ArmorTemplate()
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
                self.armor_templates[new_armor.int_name] = new_armor

    def load_weapons_from_csv(self, weapons_file_loc):
        with open(weapons_file_loc, newline='', encoding="utf-8") as weaponsFile:
            weapons_file_reader = csv.DictReader(weaponsFile)
            for line in weapons_file_reader:

                # Ignore blank lines or comments using hastags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue

                new_weapon = WeaponTemplate()
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
                self.weapon_templates[new_weapon.int_name] = new_weapon
                debug_print("Weapon Added: " + str(new_weapon), 3)

    def load_traits_from_csv(self, traits_file_loc):
        with open(traits_file_loc, newline='', encoding="utf-8") as traitsFile:
            traits_file_reader = csv.DictReader(traitsFile)
            for line in traits_file_reader:

                # Ignore blank lines or comments using hastags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue
                try:
                    new_trait_factory = TraitTemplate()
                    new_trait_factory.int_name = line['internal_name']
                    if line['display_name']:
                        new_trait_factory.display_name = line['display_name']
                    else:
                        new_trait_factory.display_name = line['internal_name'].replace('_', ' ').title()

                    if line['subtitle']:
                        new_trait_factory.recharge = line['subtitle']

                    new_trait_factory.trait_type = line['trait_type']

                    if line['visibility']:
                        new_trait_factory.visibility = int(line['visibility'])
                    else:
                        new_trait_factory.visibility = 0

                    new_trait_factory.text = line['text'].replace('\\n', '\n\t')

                    new_trait_factory.tags = csv_tag_reader(line['tags'])

                    self.trait_templates[new_trait_factory.int_name] = new_trait_factory
                except (ValueError, TypeError):
                    print("Error procession trait {}".format(line['internal_name']))

    def load_armors_loadout_pools_from_csv(self, loadout_pools_file_loc):
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
                        self.armor_loadout_pools[new_loadout_pool.name] = new_loadout_pool
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
            self.armor_loadout_pools[new_loadout_pool.name] = new_loadout_pool

    def load_weapons_loadout_pools_from_csv(self, loadout_pools_file_loc):
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
                        self.weapon_loadout_pools[new_loadout_pool.name] = new_loadout_pool
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
            self.weapon_loadout_pools[new_loadout_pool.name] = new_loadout_pool

    def load_spells_from_csv(self, spells_file_loc):
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

    def load_spell_lists_from_csv(self, spell_lists_file_loc):
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

    def load_spellcaster_profiles_from_csv(self, spellcaster_profiles_file_loc):
        with open(spellcaster_profiles_file_loc, newline="", encoding="utf-8") as spellcaster_profiles_file:
            spellcaster_profiles_file_reader = csv.DictReader(spellcaster_profiles_file)
            for line in spellcaster_profiles_file_reader:

                try:

                    # Ignore blank lines or comments using hastags
                    if line['internal_name'] == '' or '#' in line['internal_name']:
                        continue

                    new_spellcaster_profile = SpellCasterProfile()
                    new_spellcaster_profile.int_name = line['internal_name']
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
                        new_spellcaster_profile.free_spell_lists = []

                    new_spell_lists_dict = {}
                    for rawEntry in line['spell_lists'].replace(" ", "").split(','):
                        if ':' in rawEntry:
                            spell_list_name, weight = rawEntry.split(':')
                            new_spell_lists_dict[spell_list_name] = weight
                        else:
                            new_spell_lists_dict[rawEntry] = DEFAULT_SPELL_LIST_WEIGHT
                    new_spellcaster_profile.spell_lists = new_spell_lists_dict

                    new_spellcaster_profile.tags = csv_tag_reader(line['tags'])

                    # For now, only standard slots progression
                    # In the future, may add support for nonstandard slot progressions, like warlock
                    new_spellcaster_profile.spell_slots_table = None

                    self.spellcaster_profiles[new_spellcaster_profile.int_name] = new_spellcaster_profile

                except (ValueError, TypeError):
                    debug_print("Failed to build spellcaster profile: {}".format(line['internal_name']), 0)

    def load_race_templates_from_csv(self, race_templates_file_loc):
        with open(race_templates_file_loc, newline='', encoding="utf-8") as race_templates_file:
            race_templates_file_reader = csv.DictReader(race_templates_file)

            for line in race_templates_file_reader:

                # Ignore blank lines or comments using hashtags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue

                try:
                    new_race_template = RaceTemplate()
                    new_race_template.int_name = line["internal_name"]
                    if line["display_name"]:
                        new_race_template.display_name = line['display_name']
                    else:
                        # The main race name is always the start of the internal name
                        # So, for most entries a bit of finagling is called for
                        name_parts = line['internal_name'].split('_')
                        name_parts.append(name_parts.pop(0))
                        name = ' '.join(name_parts)
                        name = name.title()
                        new_race_template.display_name = name
                        
                    new_race_template.categories = line['categories'].replace(' ', '').split(',')

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

                    new_race_template.features = csv_tag_reader(line['features'])

                    self.race_templates[new_race_template.int_name] = new_race_template
                    for category in new_race_template.categories:
                        self.add_race_to_category(new_race_template.int_name, category)

                except ValueError:
                    print("Error processing race template {}".format(line['internal_name']))

    def load_class_templates_from_csv(self, class_templates_file_loc):
        with open(class_templates_file_loc, newline='', encoding="utf-8") as class_templates_file:
            class_templates_file_reader = csv.DictReader(class_templates_file)

            for line in class_templates_file_reader:

                # Ignore blank lines or comments using hashtags
                if line['internal_name'] == '' or '#' in line['internal_name']:
                    continue

                try:
                    new_class_template = ClassTemplate()
                    new_class_template.int_name = line['internal_name']

                    if line['display_name']:
                        new_class_template.display_name = line['display_name']
                    else:
                        new_class_template.display_name = line['internal_name'].replace('_', ' ').capitalize()

                    new_class_template.categories = line['categories'].replace(' ', '').split(',')

                    new_class_template.priority_attributes = line['priority_attributes'].replace(" ", "").split(',')
                    new_class_template.hd_size = int(line['hd_size'])

                    new_class_template.saves = line['saves'].replace(" ", "").split(',')
                    new_class_template.skills_fixed = line['skills_fixed'].replace(" ", "").split(',')
                    new_class_template.skills_random = line['skills_random'].replace(" ", "").split(',')
                    if line['num_random_skills']:
                        new_class_template.num_random_skills = int(line['num_random_skills'])
                    else:
                        new_class_template.num_random_skills = 0

                    if line['weapons_loadout']:
                        new_class_template.weapons_loadout_pool = line['weapons_loadout']

                    if line['armors_loadout']:
                        new_class_template.armors_loadout_pool = line['armors_loadout']

                    if line['traits']:
                        new_class_template.traits = line['traits'].replace(" ", "").split(',')

                    if line['cr_calc']:
                        new_class_template.cr_calc_type = line['cr_calc']
                    else:
                        new_class_template.cr_calc_type = 'attack'

                    new_class_template.features = csv_tag_reader(line['features'])

                    self.class_templates[new_class_template.int_name] = new_class_template
                    for category in new_class_template.categories:
                        self.add_class_to_category(new_class_template.int_name, category)

                except ValueError:
                    print("Error processing class template {}.".format(line['internal_name']))

    def is_valid_content(self, content_type: 'ContentType', content_name: str):
        content_dict = self.content_type_map[content_type]
        return content_name in content_dict

    def get_content(self, content_type: 'ContentType', content_name: str):
        content_dict = self.content_type_map[content_type]

        if content_name in content_dict:
            return content_dict[content_name]
        else:
            raise KeyError("ContentSource: Couldn't find {} - '{}'".format(content_type.name, content_name))

    def get_race_template(self, race_template_name):
        return self.get_content(ContentType.RACE, race_template_name)

    def get_class_template(self, class_template_name):
        return self.get_content(ContentType.CLASS, class_template_name)

    def get_armor(self, armor_name):
        return self.get_content(ContentType.ARMOR, armor_name)

    def get_weapon(self, weapon_name):
        return self.get_content(ContentType.WEAPON, weapon_name)

    def get_armor_loadout_pool(self, armor_loadout_pool_name):
        return self.get_content(ContentType.ARMOR_LOADOUT_POOL, armor_loadout_pool_name)

    def get_weapon_loadout_pool(self, weapon_loadout_pool_name):
        return self.get_content(ContentType.WEAPON_LOADOUT_POOL, weapon_loadout_pool_name)

    def get_spell(self, spell_name):
        return self.get_content(ContentType.SPELL, spell_name)

    def get_spell_list(self, spell_list_name):
        return self.get_content(ContentType.SPELL_LIST, spell_list_name)

    def get_spellcaster_profile(self, spellcaster_profile_name):
        return self.get_content(ContentType.SPELLCASTER_PROFILE, spellcaster_profile_name)

    def get_trait_template(self, trait_template_name):
        return self.get_content(ContentType.TRAIT, trait_template_name)

    def get_race_choices(self):
        return tuple(self.race_templates.keys())
    
    def valid_user_race_choices(self):
        valid_user_race_choices = ['random_race', ]
        for category_name in self.race_categories:
            valid_user_race_choices.append('random_' + category_name)
        for race_name in self.race_templates:
            valid_user_race_choices.append(race_name)
        return valid_user_race_choices

    def get_race_user_options(self):
        options = [('random_race', 'Random Race')]
        for item in RANDOMIZABLE_RACE_CATEGORIES:
            options.append(('random_' + item, 'Random ' + item.title()))
        for k, v in self.race_templates:
            options.append((k, v.display_name))
        return options

    def get_class_choices(self):
        return tuple(self.class_templates.keys())
    
    def valid_user_class_choices(self):
        valid_user_class_choices = ['random_class', ]
        for category_name in self.class_categories:
            valid_user_class_choices.append('random_' + category_name)
        for class_name in self.class_templates:
            valid_user_class_choices.append(class_name)
        return valid_user_class_choices
    
    def get_class_user_options(self):
        options = [('random_class', 'Random Class')]
        for item in RANDOMIZABLE_CLASS_CATEGORIES:
            options.append(('random_' + item, 'Random ' + item.title()))
        for k, v in self.class_templates:
            options.append((k, v.display_name))
        return options


# class OptionsDict:
#     options_dict = collections.OrderedDict()
#
#     def add_option(self, option, category):
#         if category in self.options_dict:
#             self.options_dict[category].append(option)
#         else:
#             self.options_dict[category] = [option, ]
#
#     def get_categories(self):
#         return list(self.options_dict.keys())
#
#
# class Option:
#     def __init__(self, value, display,
#                  first_override_title=None, first_override_options=(),
#                  second_override_title=None, second_override_options=(),):
#         self.value = value
#         self.display = display
#         self.first_override_title = first_override_title
#         self.first_override_options = first_override_options
#         self.second_override_title = second_override_title
#         self.second_override_options = second_override_options

class RaceTemplate:
    def __init__(self):
        self.int_name = ''
        self.display_name = ''
        
        self.categories = []

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
        
        self.categories = []

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
        self.int_name = ''
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

    def __repr__(self):
        return '<SpellCaster Profile: {}>'.format(self.int_name)

    # Give copies so the original profile doesn't get messed up
    def get_spell_lists(self):
        out_dict = {}
        for k, v in self.spell_lists:
            out_dict[k] = v
        return out_dict

    def get_tags(self):
        out_dict = {}
        for k, v in self.tags.items():
            out_dict[k] = v
        return out_dict

    def get_free_spell_lists(self):
        return self.spell_lists[:]


class ArmorTemplate:
    def __init__(self):
        self.int_name = ''
        self.display_name = ''
        self.base_ac = -1
        self.armor_type = ''
        self.min_str = 0
        self.stealth_disadvantage = False
        self.tags = set()

    def __repr__(self):
        return '<ArmorTemplate:{}>'.format(self.int_name)


class WeaponTemplate:
    def __init__(self):
        self.int_name = ''
        self.display_name = ''
        self.dmg_dice_num = 0
        self.dmg_dice_size = 0
        self.damage_type = ''
        self.attack_type = ''
        self.range_short = 0
        self.range_long = 0
        self.tags = set()
        self.num_targets = 1

    def __repr__(self):
        return '<WeaponTemplate:{}>'.format(self.int_name)


class TraitTemplate:
    def __init__(self):
        self.int_name = ''
        self.display_name = ''
        self.subtitle = ''
        self.trait_type = 'hidden'
        self.text = ''
        self.visibility = 0
        self.tags = {}


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

    def get_random_loadout(self, seed=None):
        if not seed:
            rnd_instance = random
        else:
            rnd_instance = random.Random(seed + self.name + 'getrandomloadout')

        return rnd_instance.choices(self.loadouts, self.weights)[0]
