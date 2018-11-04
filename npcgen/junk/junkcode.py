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