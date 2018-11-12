import collections
import random
import csv
import toml
import json
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

SPELLCASTER_PROFILES_FILE = \
    pkg.resource_filename(__name__, 'data/spellcasterprofiles.csv')
ARMORS_LOADOUT_POOLS_FILE = \
    pkg.resource_filename(__name__, 'data/loadoutpools_armors.csv')
WEAPONS_LOADOUT_POOLS_FILE = \
    pkg.resource_filename(__name__, 'data/loadoutpools_weapons.csv')

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

        self.trait_templates = {}
        self.load_traits_from_toml(traits_toml_loc)

        self.race_templates = collections.OrderedDict()
        self.race_categories = collections.OrderedDict()
        self.load_races_from_toml(races_toml_loc)

        self.class_templates = collections.OrderedDict()
        self.class_categories = collections.OrderedDict()
        self.load_classes_from_toml(classes_toml_loc)

        self.build_options_dict = self.get_build_options_dict()

        self.content_type_map = {
            ContentType.ARMOR: self.armor_templates,
            ContentType.WEAPON: self.weapon_templates,
            ContentType.ARMOR_LOADOUT_POOL: self.armor_loadout_pools,
            ContentType.WEAPON_LOADOUT_POOL: self.weapon_loadout_pools,
            ContentType.RACE: self.race_templates,
            ContentType.CLASS: self.class_templates,
            ContentType.SPELL: self.spells,
            ContentType.TRAIT: self.trait_templates,
        }

        self.build_options_dict = self.get_build_options_dict()
        
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
            set_obj_attr_from_dict(new_race_template, race_dict, 'subrace_label')
            if 'subrace_label' not in race_dict and 'subraces' in race_dict:
                new_race_template.subrace_label = 'Subrace'

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
        content_name = content_name.lower()

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

    # This builds a dictionary with all the info needed for building menus, etc. for selecting build options
    # Should be jsonifiable for javascript
    def get_build_options_dict(self):
        options_dict = collections.OrderedDict()

        # Race stuff
        # Options is for all the individual options
        options_dict['race_options'] = collections.OrderedDict()
        # Categories is sorted by categories, for building menus
        options_dict['race_categories'] = list(self.race_categories.keys())
        options_dict['race_options']['random_race'] = {'display': 'Random Race', 'categories': ['Races', ]}
        for category, races_list in self.race_categories.items():
            options_dict['race_options']['random_' + category] = \
                {'display': 'Random ' + category, 'categories': [category, ]}
        for race_template in self.race_templates.values():
            assert isinstance(race_template, RaceTemplate)
            options_dict['race_options'][race_template.int_name] = \
                {'display': race_template.display_name, 'categories': race_template.categories}
            if race_template.subraces:
                options_dict['race_options'][race_template.int_name]['subrace_label'] = race_template.subrace_label
                options_dict['race_options'][race_template.int_name]['subraces'] = collections.OrderedDict()
                for subrace_template in race_template.subraces.values():
                    assert isinstance(subrace_template, SubraceTemplate)
                    if subrace_template.display_name:
                        display = subrace_template.display_name
                    else:
                        display = subrace_template.int_name.title()
                    options_dict['race_options'][race_template.int_name]['subraces'][subrace_template.int_name] = \
                        {'display': display}
                    
        # Class stuff
        options_dict['class_options'] = collections.OrderedDict()
        options_dict['class_categories'] = list(self.class_categories.keys())
        options_dict['class_options']['random_class'] = {'display': 'Random Class', 'categories': ['Classes', ]}
        for category, classes_list in self.class_categories.items():
            options_dict['class_options']['random_' + category] = \
                {'display': 'Random ' + category, 'categories': [category, ]}
        for class_template in self.class_templates.values():
            assert isinstance(class_template, ClassTemplate)
            options_dict['class_options'][class_template.int_name] = \
                {'display': class_template.display_name, 'categories': class_template.categories}
            if class_template.subclasses_primary:
                options_dict['class_options'][class_template.int_name]['subclass_primary_label'] = \
                    class_template.subclass_primary_label
                options_dict['class_options'][class_template.int_name]['subclasses_primary'] = collections.OrderedDict()
                for subclass_template in class_template.subclasses_primary.values():
                    assert isinstance(subclass_template, SubclassTemplate)
                    if subclass_template.display_name:
                        display = subclass_template.display_name
                    else:
                        display = subclass_template.int_name.title()
                    options_dict['class_options'][class_template.int_name]['subclasses_primary'][subclass_template.int_name] = \
                        {'display': display}
            if class_template.subclasses_secondary:
                options_dict['class_options'][class_template.int_name]['subclass_secondary_label'] = \
                    class_template.subclass_secondary_label
                options_dict['class_options'][class_template.int_name]['subclasses_secondary'] = collections.OrderedDict()
                for subclass_template in class_template.subclasses_secondary.values():
                    assert isinstance(subclass_template, SubclassTemplate)
                    if subclass_template.display_name:
                        display = subclass_template.display_name
                    else:
                        display = subclass_template.int_name.title()
                    options_dict['class_options'][class_template.int_name]['subclasses_secondary'][subclass_template.int_name] = \
                        {'display': display}

        # Roll methods
        options_dict['roll_method_options'] = collections.OrderedDict()
        categories_list = []
        for roll_option_name, option_tup in ROLL_METHODS.items():
            options_dict['roll_method_options'][roll_option_name] = {'display': option_tup[0], 'categories': [option_tup[3], ]}
            if option_tup[3] not in categories_list:
                categories_list.append(option_tup[3])
        options_dict['roll_method_categories'] = categories_list

        # HD sizes
        options_dict['hd_size_options'] = collections.OrderedDict()
        options_dict['hd_size_options']['default'] = {'display': 'Default'}
        for hd_size in VALID_HD_SIZES:
            hd_size_str = str(hd_size)
            options_dict['hd_size_options'][hd_size_str] = {'display': 'd' + hd_size_str}

        # HD num
        options_dict['hd_num_options'] = collections.OrderedDict()
        for hd_num in range(1, 21):
            hd_num_str = str(hd_num)
            options_dict['hd_num_options'][hd_num_str] = {'display': hd_num_str}

        return options_dict


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

        self.subrace_label = None
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
    def __init__(self, weight=DEFAULT_SPELL_LIST_WEIGHT):
        self.weight = weight
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
