import collections
import random
import csv
import toml
from enum import Enum
from .npcgen_constants import *
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
CLASS_TEMPLATES_FILE = \
    pkg.resource_filename(__name__, 'data/classtemplates.csv')

TRAITS_TOML = \
    pkg.resource_filename(__name__, 'data/traits.toml')
ARMORS_TOML = \
    pkg.resource_filename(__name__, 'data/armors.toml')
WEAPONS_TOML = \
    pkg.resource_filename(__name__, 'data/weapons.toml')

RACE_TEMPLATES_TOML = \
    pkg.resource_filename(__name__, 'data/races.toml')
CLASS_TEMPLATES_TOML = \
    pkg.resource_filename(__name__, 'data/classes.toml')


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


# Checks to see if the origin dictionary has a key and if it does sets the corresponding attribute of the
# destination object to that value
# A helper function for building templates from toml dicts
def set_obj_attr_from_dict(destination_object, origin_dict: Dict, key, attribute_name=None):
    if key in origin_dict:
        if attribute_name:
            setattr(destination_object, attribute_name, origin_dict[key])
        else:
            setattr(destination_object, key, origin_dict[key])


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
                 weapons_toml_loc=WEAPONS_TOML,
                 armors_toml_loc=ARMORS_TOML,
                 spells_file_loc=SPELLS_FILE,
                 # spell_lists_file_loc=SPELLLISTS_FILE,
                 # spellcaster_profiles_file_loc=SPELLCASTER_PROFILES_FILE,
                 armors_loadout_pools_file_loc=ARMORS_LOADOUT_POOLS_FILE,
                 weapons_loadout_pools_file_loc=WEAPONS_LOADOUT_POOLS_FILE,
                 traits_toml_loc=TRAITS_TOML,
                 races_toml_loc=RACE_TEMPLATES_TOML,
                 classes_toml_loc=CLASS_TEMPLATES_TOML,
                 ):

        self.weapon_templates = {}
        self.load_weapons_from_toml(weapons_toml_loc)

        self.weapon_loadout_pools = {}
        self.load_weapons_loadout_pools_from_csv(weapons_loadout_pools_file_loc)

        self.armor_templates = {}
        self.load_armors_from_toml(armors_toml_loc)

        self.armor_loadout_pools = {}
        self.load_armors_loadout_pools_from_csv(armors_loadout_pools_file_loc)

        self.spells = {}
        self.load_spells_from_csv(spells_file_loc)
        #
        # self.spell_lists = {}
        # self.load_spell_lists_from_csv(spell_lists_file_loc)
        #
        # self.spellcaster_profiles = {}
        # self.load_spellcaster_profiles_from_csv(spellcaster_profiles_file_loc)

        self.trait_templates = {}
        self.load_traits_from_toml(traits_toml_loc)

        self.race_templates = collections.OrderedDict()
        self.race_categories = collections.OrderedDict()
        self.load_races_from_toml(races_toml_loc)

        self.class_templates = collections.OrderedDict()
        self.class_categories = collections.OrderedDict()
        self.load_classes_from_toml(classes_toml_loc)

        self.content_type_map = {
            ContentType.ARMOR: self.armor_templates,
            ContentType.WEAPON: self.weapon_templates,
            ContentType.ARMOR_LOADOUT_POOL: self.armor_loadout_pools,
            ContentType.WEAPON_LOADOUT_POOL: self.weapon_loadout_pools,
            ContentType.RACE: self.race_templates,
            ContentType.CLASS: self.class_templates,
            ContentType.SPELL: self.spells,
            # ContentType.SPELL_LIST: self.spell_lists,
            # ContentType.SPELLCASTER_PROFILE: self.spellcaster_profiles,
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

    def load_armors_from_toml(self, armors_toml_loc):
        toml_dict = toml.load(armors_toml_loc)
        for armor_name, armor_dict in toml_dict.items():
            new_armor_template = ArmorTemplate()

            new_armor_template.int_name = armor_name

            if 'display_name' in armor_dict:
                new_armor_template.display_name = armor_dict['display_name']
            else:
                new_armor_template.display_name = armor_name.replace('_', ' ').capitalize()

            new_armor_template.armor_type = armor_dict['armor_type']
            new_armor_template.base_ac = int(armor_dict['base_ac'])

            if 'stealth_disadvantage' in armor_dict:
                new_armor_template.stealth_disadvantage = armor_dict['stealth_disadvantage']

            if 'tags' in armor_dict:
                new_armor_template.tags = armor_dict['tags']

            self.armor_templates[armor_name] = new_armor_template

    def load_weapons_from_toml(self, weapons_toml_loc):
        toml_dict = toml.load(weapons_toml_loc)
        for weapon_name, weapon_dict in toml_dict.items():
            new_weapon_template = WeaponTemplate()

            new_weapon_template.int_name = weapon_name

            if 'display_name' in weapon_dict:
                new_weapon_template.display_name = weapon_dict['display_name']
            else:
                new_weapon_template.display_name = weapon_name.replace("_", " ").title()

            dmg_dice_num, dmg_dice_size = weapon_dict['damage'].split('d')
            new_weapon_template.dmg_dice_num = int(dmg_dice_num)
            new_weapon_template.dmg_dice_size = int(dmg_dice_size)

            new_weapon_template.damage_type = weapon_dict['damage_type']

            if 'range' in weapon_dict:
                range_short, range_long = weapon_dict['range'].split('/')
                new_weapon_template.range_short = int(range_short)
                new_weapon_template.range_long = int(range_long)

            if 'tags' in weapon_dict:
                new_weapon_template.tags = weapon_dict['tags']

            self.weapon_templates[weapon_name] = new_weapon_template

    def load_traits_from_toml(self, traits_toml_loc):
        toml_dict = toml.load(traits_toml_loc)
        for trait_name, trait_dict in toml_dict.items():
            new_trait_template = TraitTemplate()

            new_trait_template.int_name = trait_name

            if 'display_name' in trait_dict:
                new_trait_template.display_name = trait_dict['display_name']
            else:
                new_trait_template.display_name = trait_dict['internal_name'].replace('_', ' ').title()

            set_obj_attr_from_dict(new_trait_template, trait_dict, 'subtitle')
            set_obj_attr_from_dict(new_trait_template, trait_dict, 'text')
            set_obj_attr_from_dict(new_trait_template, trait_dict, 'trait_type')
            set_obj_attr_from_dict(new_trait_template, trait_dict, 'visibility')
            set_obj_attr_from_dict(new_trait_template, trait_dict, 'tags')

            self.trait_templates[new_trait_template.int_name] = new_trait_template

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

    # def load_spell_lists_from_csv(self, spell_lists_file_loc):
    #     with open(spell_lists_file_loc, newline='', encoding="utf-8") as spellListsFile:
    #         spell_lists_file_reader = csv.DictReader(spellListsFile)
    #         for line in spell_lists_file_reader:
    #
    #             # Ignore blank lines or comments using hastags
    #             if line['name'] == '' or '#' in line['name']:
    #                 continue
    #
    #             new_spell_list = SpellList()
    #             new_spell_list.name = line['name']
    #
    #             # Check for if it's an autolist
    #             # If all these fields are blank, it's not an autolist
    #             if len(line['req_classes']) > 0 or len(line['req_schools']) > 0 \
    #                     or len(line['req_levels']) > 0 or len(line['req_sources']) > 0:
    #                 req_classes = None
    #                 if line['req_classes']:
    #                     req_classes = line['req_classes'].replace(" ", "").split(",")
    #                 req_schools = None
    #                 if line['req_schools']:
    #                     req_schools = set(line['req_schools'].replace(" ", "").split(","))
    #                 req_levels = None
    #                 if line['req_levels']:
    #                     req_levels = line['req_levels'].replace(" ", "").split(",")
    #                 req_sources = None
    #                 if line['req_sources']:
    #                     req_sources = line['req_sources'].replace(" ", "").split(",")
    #
    #                 for spell_name, spell in self.spells.items():
    #                     if req_classes and spell.classes.isdisjoint(req_classes):
    #                         continue
    #                     if req_schools and spell.school not in req_schools:
    #                         continue
    #                     if req_levels and spell.level not in req_levels:
    #                         continue
    #                     if req_sources and spell.source not in req_sources:
    #                         continue
    #                     new_spell_list.add_spell(spell)
    #
    #             if line['fixed_include']:
    #                 fixed_include_spells = line['fixed_include'].split(',')
    #                 for spell_name in fixed_include_spells:
    #                     spell_name = spell_name.strip()
    #                     if spell_name not in self.spells:
    #                         debug_print("Error! spell: '{}' from spelllist '{}' not in master spelllist!"
    #                                     .format(spell_name, new_spell_list.name), 0)
    #                     else:
    #                         new_spell_list.add_spell(self.spells[spell_name])
    #
    #             if line['fixed_exclude']:
    #                 fixed_exclude_spells = line['fixed_exclude'].split(',')
    #                 for spell_name in fixed_exclude_spells:
    #                     spell_name = spell_name.strip()
    #                     if spell_name not in self.spells:
    #                         debug_print("Error! spell: '{}' from spelllist '{}' not in master spelllist!"
    #                                     .format(spell_name, new_spell_list.name), 0)
    #                     else:
    #                         new_spell_list.remove_spell(spell_name)
    #
    #             if line['spelllists_include']:
    #                 spell_lists_to_include = line['spelllists_include'].replace(" ", "").split(',')
    #                 for spellListToInclude in spell_lists_to_include:
    #                     for spell_name, spell in spellListToInclude.spells.items():
    #                         new_spell_list.add_spell(spell)
    #
    #             if line['spelllists_exclude']:
    #                 spell_lists_to_exclude = line['spelllists_exclude'].replace(" ", "").split(',')
    #                 for spellListToExclude in spell_lists_to_exclude:
    #                     spell_list = self.spell_lists[spellListToExclude]
    #                     for spell_name, spell in spell_list.spells.items():
    #                         new_spell_list.remove_spell(spell)
    #
    #             self.spell_lists[new_spell_list.name] = new_spell_list

    # def load_spellcaster_profiles_from_csv(self, spellcaster_profiles_file_loc):
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
    #                 new_spellcaster_profile.int_name = line['internal_name']
    #                 new_spellcaster_profile.casting_stat = line['casting_stat']
    #                 new_spellcaster_profile.ready_style = line['ready_style']
    #
    #                 if line["hd_per_casting_level"]:
    #                     new_spellcaster_profile.hd_per_casting_level = int(line['hd_per_casting_level'])
    #                 else:
    #                     new_spellcaster_profile.hd_per_casting_level = 1
    #
    #                 if line['cantrips_per_level']:
    #                     new_spellcaster_profile.cantrips_per_level = line['cantrips_per_level']
    #                 else:
    #                     new_spellcaster_profile.cantrips_per_level = None
    #
    #                 if line['fixed_spells_known_by_level']:
    #                     new_spellcaster_profile.fixed_spells_known_by_level = line['fixed_spells_known_by_level']
    #                 else:
    #                     new_spellcaster_profile.fixed_spells_known_by_level = None
    #
    #                 if line['spells_known_modifier']:
    #                     new_spellcaster_profile.spells_known_modifier = int(line['spells_known_modifier'])
    #                 else:
    #                     new_spellcaster_profile.spells_known_modifier = 0
    #
    #                 if line['free_spell_lists']:
    #                     new_spellcaster_profile.free_spell_lists = line['free_spell_lists'].replace(" ", "").split(',')
    #                 else:
    #                     new_spellcaster_profile.free_spell_lists = []
    #
    #                 new_spell_lists_dict = {}
    #                 for rawEntry in line['spell_lists'].replace(" ", "").split(','):
    #                     if ':' in rawEntry:
    #                         spell_list_name, weight = rawEntry.split(':')
    #                         new_spell_lists_dict[spell_list_name] = weight
    #                     else:
    #                         new_spell_lists_dict[rawEntry] = DEFAULT_SPELL_LIST_WEIGHT
    #                 new_spellcaster_profile.spell_lists = new_spell_lists_dict
    #
    #                 new_spellcaster_profile.tags = csv_tag_reader(line['tags'])
    #
    #                 # For now, only standard slots progression
    #                 # In the future, may add support for nonstandard slot progressions, like warlock
    #                 new_spellcaster_profile.spell_slots_table = None
    #
    #                 self.spellcaster_profiles[new_spellcaster_profile.int_name] = new_spellcaster_profile
    #
    #             except (ValueError, TypeError):
    #                 debug_print("Failed to build spellcaster profile: {}".format(line['internal_name']), 0)

    def load_races_from_toml(self, races_toml_loc):
        toml_dict = toml.load(races_toml_loc)
        for race_name, race_dict in toml_dict.items():
            new_race_template = RaceTemplate()
            new_race_template.int_name = race_name

            if 'display_name' in race_dict:
                new_race_template.display_name = race_dict['display_name']
            else:
                new_race_template.display_name = race_name.replace('_', ' ').title()

            set_obj_attr_from_dict(new_race_template, race_dict, 'categories')
            set_obj_attr_from_dict(new_race_template, race_dict, 'creature_type')
            set_obj_attr_from_dict(new_race_template, race_dict, 'size')
            set_obj_attr_from_dict(new_race_template, race_dict, 'attribute_bonuses')
            set_obj_attr_from_dict(new_race_template, race_dict, 'speeds')
            set_obj_attr_from_dict(new_race_template, race_dict, 'senses')
            set_obj_attr_from_dict(new_race_template, race_dict, 'languages')
            set_obj_attr_from_dict(new_race_template, race_dict, 'traits')
            set_obj_attr_from_dict(new_race_template, race_dict, 'features')
            set_obj_attr_from_dict(new_race_template, race_dict, 'subraces_label')
            if 'subraces_label' not in race_dict and 'subraces' in race_dict:
                new_race_template.subraces_label = 'Subrace'

            if 'subraces' in race_dict:
                subraces_dict = collections.OrderedDict()
                for subrace_name, subrace_dict in race_dict['subraces'].items():
                    new_subrace_template = SubraceTemplate()
                    new_subrace_template.int_name = subrace_name

                    if 'display_name' in subrace_dict:
                        new_subrace_template.display_name = subrace_dict['display_name']
                    else:
                        display_name = subrace_name.title() + ' ' + new_race_template.display_name
                        new_subrace_template.display_name = display_name

                    set_obj_attr_from_dict(new_subrace_template, subrace_dict, 'size')
                    set_obj_attr_from_dict(new_subrace_template, subrace_dict, 'attribute_bonuses')
                    set_obj_attr_from_dict(new_subrace_template, subrace_dict, 'speeds')
                    set_obj_attr_from_dict(new_subrace_template, subrace_dict, 'senses')
                    set_obj_attr_from_dict(new_subrace_template, subrace_dict, 'languages')
                    set_obj_attr_from_dict(new_subrace_template, subrace_dict, 'traits')
                    set_obj_attr_from_dict(new_subrace_template, subrace_dict, 'features')

                    subraces_dict[subrace_name] = new_subrace_template
                new_race_template.subraces = subraces_dict

            self.race_templates[race_name] = new_race_template

            for category in new_race_template.categories:
                self.add_race_to_category(race_name, category)

    def load_classes_from_toml(self, classes_toml_loc):
        toml_dict = toml.load(classes_toml_loc)
        for class_name, class_dict in toml_dict.items():
            new_class_template = ClassTemplate()
            new_class_template.int_name = class_name
            if 'display_name' in class_dict:
                new_class_template.display_name = class_dict['display_name']
            else:
                new_class_template.display_name = class_name.replace('_', ' ').title()

            set_obj_attr_from_dict(new_class_template, class_dict, 'categories')
            set_obj_attr_from_dict(new_class_template, class_dict, 'priority_attributes')
            set_obj_attr_from_dict(new_class_template, class_dict, 'hd_size')
            set_obj_attr_from_dict(new_class_template, class_dict, 'skills_fixed')
            set_obj_attr_from_dict(new_class_template, class_dict, 'skills_random')
            set_obj_attr_from_dict(new_class_template, class_dict, 'num_random_skills')
            set_obj_attr_from_dict(new_class_template, class_dict, 'weapons_loadout_pool')
            set_obj_attr_from_dict(new_class_template, class_dict, 'armors_loadout_pool')
            set_obj_attr_from_dict(new_class_template, class_dict, 'cr_calc')
            set_obj_attr_from_dict(new_class_template, class_dict, 'traits')
            set_obj_attr_from_dict(new_class_template, class_dict, 'features')

            if 'spell_casting_profile' in class_dict:
                casting_dict = class_dict['spell_casting_profile']
                new_spell_casting_profile = SpellCasterProfile()
                new_spell_casting_profile.casting_stat = casting_dict['casting_stat']
                new_spell_casting_profile.ready_style = casting_dict['ready_style']
                set_obj_attr_from_dict(new_spell_casting_profile, casting_dict, 'tags')
                set_obj_attr_from_dict(new_spell_casting_profile, casting_dict, 'hd_per_casting_level')
                if 'cantrips_per_level' in casting_dict:
                    new_spell_casting_profile.cantrips_per_level = casting_dict['cantrips_per_level']
                for spell_list_dict in casting_dict['spell_lists']:
                    new_spell_list = self.build_spell_list(**spell_list_dict)
                    new_spell_casting_profile.spell_lists[new_spell_list] = new_spell_list.weight
                new_class_template.spell_casting_profile = new_spell_casting_profile
                
            if 'subclass_primary_label' in class_dict:
                new_class_template.subclass_primary_label = class_dict['subclass_primary_label']
            elif 'subclasses_primary' in class_dict:
                new_class_template.subclass_primary_label = 'Subclass'
                
            if 'subclasses_primary' in class_dict:
                for subclass_name, subclass_dict in class_dict['subclasses_primary'].items():
                    new_subclass_template = SubclassTemplate()
                    new_subclass_template.int_name = subclass_name

                    # Basically, if NOTHING is given for display name stuff,
                    # just make the internal name a prefix for the class
                    if 'display_name' not in subclass_dict and 'display_name_prefix' not in subclass_dict \
                            and 'display_name_suffix' not in subclass_dict:
                        new_subclass_template.display_name_prefix = subclass_name.replace('_', ' ').title()

                    set_obj_attr_from_dict(new_subclass_template, subclass_dict, 'display_name')
                    set_obj_attr_from_dict(new_subclass_template, subclass_dict, 'display_name_prefix')
                    set_obj_attr_from_dict(new_subclass_template, subclass_dict, 'display_name_suffix')
                    set_obj_attr_from_dict(new_subclass_template, subclass_dict, 'traits')
                    set_obj_attr_from_dict(new_subclass_template, subclass_dict, 'features')

                    new_class_template.subclasses_primary[subclass_name] = new_subclass_template
            
            if 'subclass_secondary_label' in class_dict:
                new_class_template.subclass_secondary_label = class_dict['subclass_secondary_label']
            elif 'subclasses_secondary' in class_dict:
                new_class_template.subclass_secondary_label = 'Secondary Subclass'
                
            if 'subclasses_secondary' in class_dict:
                for subclass_name, subclass_dict in class_dict['subclasses_secondary'].items():
                    new_subclass_template = SubclassTemplate()
                    new_subclass_template.int_name = subclass_name

                    set_obj_attr_from_dict(new_subclass_template, subclass_dict, 'display_name')
                    set_obj_attr_from_dict(new_subclass_template, subclass_dict, 'traits')
                    set_obj_attr_from_dict(new_subclass_template, subclass_dict, 'features')

                    new_class_template.subclasses_secondary[subclass_name] = new_subclass_template

            self.class_templates[class_name] = new_class_template
            for category in new_class_template.categories:
                self.add_class_to_category(class_name, category)


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

    def build_spell_list(self, req_classes=None, req_schools=None, req_levels=None, req_sources=None,
                         fixed_include=None, fixed_exclude=None,
                         weight=None):

        new_spell_list = SpellList()

        if req_classes or req_schools or req_levels or req_sources:
            for spell_name, spell in self.spells.items():
                if req_classes and spell.classes.isdisjoint(set(req_classes)):
                    continue
                if req_schools and spell.school not in req_schools:
                    continue
                if req_levels and spell.level not in req_levels:
                    continue
                if req_sources and spell.source not in req_sources:
                    continue
                new_spell_list.add_spell(spell)

        if fixed_include:
            for spell_name in fixed_include:
                spell_name = spell_name.strip()
                if spell_name not in self.spells:
                    debug_print("Error! spell: '{}' from spelllist '{}' not in master spelllist!"
                                .format(spell_name, new_spell_list.name), 0)
                else:
                    new_spell_list.add_spell(self.spells[spell_name])

        if fixed_exclude:
            for spell_name in fixed_exclude:
                spell_name = spell_name.strip()
                if spell_name not in self.spells:
                    debug_print("Error! spell: '{}' from spelllist '{}' not in master spelllist!"
                                .format(spell_name, new_spell_list.name), 0)
                else:
                    new_spell_list.remove_spell(spell_name)

        if weight:
            new_spell_list.weight = weight

        return new_spell_list

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

    def get_character_build_options(self):
        options_inst = CharacterBuildOptions()
        options_inst.add_race_option('RACES', RaceClassOptionEntry('random_race', 'Random Race'))
        options_inst.add_class_option('CLASSES', RaceClassOptionEntry('random_class', 'Random Class'))

        for race_category in self.race_categories.keys():
            for race_option in self.race_categories[race_category]:
                temp = self.get_race_template(race_option)
                assert isinstance(temp, RaceTemplate)
                option_entry = RaceClassOptionEntry(race_option, temp.display_name,
                                                    temp.subraces_label, list(temp.subraces.keys()),)
                options_inst.add_race_option(race_category, option_entry)
                
        for class_category in self.class_categories.keys():
            for class_option in self.class_categories[class_category]:
                temp = self.get_class_template(class_option)
                assert isinstance(temp, ClassTemplate)
                option_entry = RaceClassOptionEntry(class_option, temp.display_name,
                                                    arg_one_label=temp.subclass_primary_label,
                                                    arg_one_options=list(temp.subclasses_primary.keys()),
                                                    arg_two_label=temp.subclass_secondary_label,
                                                    arg_two_options=list(temp.subclasses_secondary.keys()))
                options_inst.add_class_option(class_category, option_entry)

        for roll_option, roll_tup in ROLL_METHODS.items():
            category = roll_tup[3]
            display = roll_tup[0]
            roll_entry = OptionMenuEntry(roll_option, display)
            options_inst.add_roll_option(category, roll_entry)

        for i in range(1, 21):
            entry = OptionMenuEntry(str(i), str(i))
            options_inst.hd_options.append(entry)

        options_inst.hd_size_options.append(OptionMenuEntry('default', 'Default'))
        for size in VALID_HD_SIZES:
            entry = OptionMenuEntry(str(size), 'd' + str(size))
            options_inst.hd_size_options.append(entry)

        return options_inst


# This is the object that will ultimately be handed to the renderer that presents options to the user
# The keys of the ordered dicts are intended to be categories with the values as lists of entries to go into them
# For now, just race and class, will add rolld/hd after, and MUCH later support for optional parameters will go here
class CharacterBuildOptions:
    def __init__(self):
        self.race_options = collections.OrderedDict()
        self.class_options = collections.OrderedDict()

        self.roll_options = collections.OrderedDict()

        self.hd_options = []
        self.hd_size_options = []
        
    def every_race_option(self):
        race_options_list = []
        for category in self.race_options:
            for option in self.race_options[category]:
                race_options_list.append(option)
        return race_options_list

    def add_race_option(self, category, option: 'RaceClassOptionEntry'):
        category = category.title()
        if category in self.race_options:
            self.race_options[category].append(option)
        else:
            self.race_options[category] = [option, ]
            
    def every_class_option(self):
        class_options_list = []
        for category in self.class_options:
            for option in self.class_options[category]:
                class_options_list.append(option)
        return class_options_list

    def add_class_option(self, category, option: 'RaceClassOptionEntry'):
        category = category.title()
        if category in self.class_options:
            self.class_options[category].append(option)
        else:
            self.class_options[category] = [option, ]
            
    def every_roll_option(self):
        roll_options_list = []
        for category in self.roll_options:
            for option in self.roll_options[category]:
                roll_options_list.append(option)
        return roll_options_list

    def add_roll_option(self, category, option: 'OptionMenuEntry'):
        category = category.title()
        if category in self.roll_options:
            self.roll_options[category].append(option)
        else:
            self.roll_options[category] = [option, ]

    def __str__(self):
        outstring = "Races:{} Classes:{}".format(','.join(self.race_options), ','.join(self.class_options))
        return outstring

    def jsonify(self):
        out = "{"
        out += '"race_options" : {'
        for race_option in self.every_race_option():
            out += '"{}":{},'.format(race_option.int_name, race_option.jsonify())
        out = out[:-1]
        out += '},"class_options" : {'
        for class_option in self.every_class_option():
            out += '"{}":{},'.format(class_option.int_name, class_option.jsonify())
        out = out[:-1]
        out += '},"roll_options" : {'
        for roll_option in self.every_roll_option():
            out += '"{}":"{}",'.format(roll_option.int_name, roll_option.display)
        out = out[:-1]
        out += '}}'
        return out


class OptionMenuEntry:
    def __init__(self, int_name, display):
        self.int_name = int_name
        self.display = display

    def __repr__(self):
        return "<MenuEntry:{},{}>".format(self.int_name, self.display)

    def __str__(self):
        outstring = "[{},{},".format(self.int_name, self.display)
        outstring += ']'
        return outstring

    def jsonify(self):
        out = '{'
        out += '"int_name":"{}",'.format(self.int_name)
        out += '"display":"{}"'.format(self.display)
        out += '}'
        return out


class RaceClassOptionEntry(OptionMenuEntry):
    def __init__(self, int_name, display, arg_one_label=None, arg_one_options=None,
                 arg_two_label=None, arg_two_options=None):
        super().__init__(int_name, display)
        self.arg_one_label = arg_one_label
        self.arg_one_options = arg_one_options
        self.arg_one_option_displays = []
        if self.arg_one_label:
            for option in self.arg_one_options:
                self.arg_one_option_displays.append(option.title())

        self.arg_two_label = arg_two_label
        self.arg_two_options = arg_two_options
        self.arg_two_option_displays = []
        if self.arg_two_label:
            for option in self.arg_two_options:
                self.arg_one_option_displays.append(option.title())

    def __repr__(self):
        return "<RaceClassOptionEntry:{},{}>".format(self.int_name, self.display)

    def __str__(self):
        outstring = "[{},{},".format(self.int_name, self.display)
        if self.arg_one_label:
            outstring += self.arg_one_label + ',' + str(self.arg_one_options) + ','
        if self.arg_two_label:
            outstring += self.arg_two_label + ',' + str(self.arg_two_options) + ','
        outstring += ']'
        return outstring

    def jsonify(self):
        out = '{'
        out += '"int_name":"{}",'.format(self.int_name)
        out += '"display":"{}",'.format(self.display)
        if self.arg_one_label:
            out += '"arg_one_label":"{}",'.format(self.arg_one_label)
            out += '"arg_one_options":['
            for option in self.arg_one_options:
                out += '"{}",'.format(option)
            out = out[:-1] + '],'  # Json doesn't like dangling commas
        if self.arg_two_label:
            out += '"arg_two_label":"{}",'.format(self.arg_two_label)
            out += '"arg_two_options":['
            for option in self.arg_two_options:
                out = '"{}",'.format(option)
            out += out[:-1] + '],'  # Json doesn't like dangling commas
        out = out[:-1]  # Get rid of last comment or JSON breaks
        out += '}'
        return out


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

        self.languages = []

        self.traits = []
        self.features = collections.OrderedDict()

        self.subraces_label = None
        self.subraces = {}


class SubraceTemplate:
    def __init__(self):
        self.int_name = ''
        self.display_name = None

        self.size = None

        self.attribute_bonuses = None
        self.speeds = None
        self.languages = None
        self.traits = None
        self.features = None


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

        self.subclasses_primary = {}
        self.subclasses_secondary = {}

        self.subclass_primary_label = None
        self.subclass_secondary_label = None



class SubclassTemplate:
    def __init__(self):
        self.int_name = ''

        # Display name overrides the base class
        self.display_name = None

        # Prefixes and suffixes get added, primary classes going first
        self.display_name_prefix = None
        self.display_name_suffix = None
        self.traits = []
        self.features = {}


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
        self.weight = DEFAULT_SPELL_LIST_WEIGHT
        self.name = ''
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
        self.cantrips_per_level = 'none'
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
        self.tags = []

    def __repr__(self):
        return '<SpellCaster Profile: {}>'.format(self.int_name)

    # Give copies so the original profile doesn't get messed up
    def get_spell_lists(self):
        out_dict = {}
        for k, v in self.spell_lists:
            out_dict[k] = v
        return out_dict

    def get_tags(self):
        out_tags = []
        for tag in self.tags:
            out_tags.append(tag)
        return out_tags

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
        self.tags = []
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
