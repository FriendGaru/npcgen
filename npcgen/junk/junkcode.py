TRAITS_FILE = \
    pkg.resource_filename(__name__, 'data/traits.csv')
ARMORS_FILE = \
    pkg.resource_filename(__name__, 'data/armors.csv')
WEAPONS_FILE = \
    pkg.resource_filename(__name__, 'data/weapons.csv')
RACE_TEMPLATES_FILE = \
    pkg.resource_filename(__name__, 'data/racetemplates.csv')


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
                new_weapon.tags = line['tags'].replace(" ", "").split(',')
                self.weapon_templates[new_weapon.int_name] = new_weapon
                debug_print("Weapon Added: " + str(new_weapon), 3)

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

                    if line['arg_one_label']:
                        new_race_template.arg_one_label = line['arg_one_label']
                        new_race_template.arg_one_options = line['arg_one_options'].replace(' ', '').split(',')
                    else:
                        new_race_template.arg_one_label = None
                        new_race_template.arg_one_options = None

                    if line['arg_two_label']:
                        new_race_template.arg_two_label = line['arg_two_label']
                        new_race_template.arg_two_options = line['arg_two_options'].replace(' ', '').split(',')
                    else:
                        new_race_template.arg_two_label = None
                        new_race_template.arg_two_options = None

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

                    if line['arg_one_label']:
                        new_class_template.arg_one_label = line['arg_one_label']
                        new_class_template.arg_one_options = line['arg_one_options'].replace(' ', '').split(',')
                    else:
                        new_class_template.arg_one_label = None
                        new_class_template.arg_one_options = None

                    if line['arg_two_label']:
                        new_class_template.arg_two_label = line['arg_two_label']
                        new_class_template.arg_two_options = line['arg_two_options'].replace(' ', '').split(',')
                    else:
                        new_class_template.arg_two_label = None
                        new_class_template.arg_two_options = None

                    self.class_templates[new_class_template.int_name] = new_class_template
                    for category in new_class_template.categories:
                        self.add_class_to_category(new_class_template.int_name, category)

                except ValueError:
                    print("Error processing class template {}.".format(line['internal_name']))

    def set_spell_choices(self):

        rnd_instance = random.Random(self.seed + 'spellchoices')
        content_source = self.content_source

        already_chosen_spells = set()
        for spell in self.free_spells:
            already_chosen_spells.add(spell)

        spell_selections = [[], [], [], [], [], [], [], [], [], [], ]
        # We do this for every spell level
        for spell_level in range(0, 10):
            total_spells_of_this_level = 0
            for spell_list_name in self.spell_lists.keys():
                spell_list = content_source.get_spell_list(spell_list_name)
                total_spells_of_this_level += spell_list.num_spells_of_level(spell_level)

            spell_options = []
            spell_weights = []

            for spell_list_name, weight in self.spell_lists.items():
                spell_list = content_source.get_spell_list(spell_list_name)
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
                elif spell_choice in already_chosen_spells:
                    continue
                else:
                    already_chosen_spells.add(spell_choice)
                    spell_selections_for_level.append(spell_choice)
                    spell_selections_remaining -= 1

            spell_selections[spell_level] = spell_selections_for_level
        self.spell_choices = spell_selections


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



# This is the object that will ultimately be handed to the renderer that presents options to the user
# The keys of the ordered dicts are intended to be categories with the values as lists of entries to go into them
# For now, just race and class, will add rolld/hd after, and MUCH later support for optional parameters will go here
# class CharacterBuildOptions:
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

    def get_character_build_options(self):
        options_inst = CharacterBuildOptions()
        options_inst.add_race_option('RACES', RaceClassOptionEntry('random_race', 'Random Race'))
        options_inst.add_class_option('CLASSES', RaceClassOptionEntry('random_class', 'Random Class'))

        for race_category in self.race_categories.keys():
            for race_option in self.race_categories[race_category]:
                temp = self.get_race_template(race_option)
                assert isinstance(temp, RaceTemplate)
                option_entry = RaceClassOptionEntry(race_option, temp.display_name,
                                                    temp.subrace_label, list(temp.subraces.keys()), )
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

SPELLLISTS_FILE = \
    pkg.resource_filename(__name__, 'data/spelllists.csv')

if 'race_choice' in request_dict.keys() \
        and request_dict['race_choice'] in self.content_source.valid_user_race_choices():
    clean_dict['race_choice'] = request_dict['race_choice']
    race_template = self.content_source.get_race_template(request_dict['race_choice'])
    if 'subrace_choice' in request_dict.keys():
        if race_template.subraces:
            if request_dict['subrace_choice'] == 'random':
                clean_dict['subrace_choice'] = 'random'
            elif request_dict['subrace_choice'] in race_template.subraces.keys():
                clean_dict['subrace_choice'] = request_dict['subrace_choice']
            else:
                is_valid = False
        else:
            is_valid = False
else:
    is_valid = False
    clean_dict['race_choice'] = self.get_random_option('race')

if 'class_choice' in request_dict.keys() \
        and request_dict['class_choice'] in self.content_source.valid_user_class_choices():
    clean_dict['class_choice'] = request_dict['class_choice']
    class_template = self.content_source.get_class_template(request_dict['class_choice'])
    if 'subclass_primary_choice' in request_dict.keys():
        if class_template.subclasses_primary:
            if request_dict['subclass_primary_choice'] == 'random':
                clean_dict['subclass_primary_choice'] = 'random'
            elif request_dict['subclass_primary_choice'] in class_template.subclasses_primary.keys():
                clean_dict['subclass_primary_choice'] = request_dict['subclass_primary_choice']
            else:
                is_valid = False
        else:
            is_valid = False
    if 'subclass_secondary_choice' in request_dict.keys():
        if class_template.subclasses_secondary:
            if request_dict['subclass_secondary_choice'] == 'random':
                clean_dict['subclass_secondary_choice'] = 'random'
            elif request_dict['subclass_secondary_choice'] in class_template.subclasses_secondary.keys():
                clean_dict['subclass_secondary_choice'] = request_dict['subclass_secondary_choice']
            else:
                is_valid = False
        else:
            is_valid = False
else:
    is_valid = False
    clean_dict['class_choice'] = self.get_random_option('class')