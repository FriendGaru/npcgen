import itertools
import string
from npcgen.npcgen_content import *

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


# There are a bunch of times where you use hd/level to get a simple value
# Most attack cantrips, for example, do a single die of damage at level one and add a die at levels 5, 11, and 17
# Since it's very common and takes up an annoying amount of space, this is just a helper function
# starting_val: the val at level 1
# increase_points: the levels at which the value goes up
# character_hd: how many hd the character we're check has
# increment: how much to increase at each point
# For example, that cantrip progression for a level 10 character would look like
# increment_from_hd(1, (5, 11, 17), 10) and would return 2
def increment_from_hd(starting_val, increase_points, character_hd, increment=1):
    out_val = starting_val
    for point in increase_points:
        if character_hd >= point:
            out_val += increment
    return out_val


class NPCGenerator:
    """
    NPC Generator builds all of the necessary data from external files, stores them, and builds instances of the
    Character class based on given parameters.
    """

    def __init__(self):

        self.content_source = ContentSource()

        self.roll_options = ROLL_METHODS_OPTIONS
        self.roll_keys = list(ROLL_METHODS.keys())

        self.hd_size_options = tuple(itertools.chain(['Default'], ['d' + str(x) for x in VALID_HD_SIZES]))

    def build_trait(self, character: 'Character', trait_name):
        trait_template = self.content_source.get_trait_template(trait_name)
        trait_feature_instance = FeatureTrait(character, trait_template)
        return trait_feature_instance

    # Applies everything EXCEPT features/traits
    @staticmethod
    def apply_race_template(character: 'Character', race_template: 'RaceTemplate'):

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
    def apply_class_template(self, character: 'Character', class_template: 'ClassTemplate', seed):

        character.class_name = class_template.display_name
        character.priority_attributes = class_template.priority_attributes

        rnd_instance = random.Random(seed + 'skills')
        fixed_skills = class_template.skills_fixed
        # we want to avoid random.sample() here because it won't guarantee the same choices by seed
        randomized_skills = rnd_instance.sample(class_template.skills_random, class_template.num_random_skills)
        skills_to_add = itertools.chain(fixed_skills, randomized_skills)
        for skill in skills_to_add:
            character.add_skill(skill)

        for save in class_template.saves:
            character.saves.add(save)

        for language in class_template.languages:
            character.add_language(language)

        if class_template.multiattack_type:
            character.multiattack = class_template.multiattack_type

        if class_template.armors_loadout_pool:
            armors_pool_name = class_template.armors_loadout_pool
            assert self.content_source.is_valid_content(
                ContentType.ARMOR_LOADOUT_POOL, armors_pool_name), \
                "apply_class_template('{}'): {} is invalid armors pool"\
                .format(class_template.int_name, armors_pool_name)
            loadout_pool = self.content_source.get_armor_loadout_pool(armors_pool_name)
            loadout = loadout_pool.get_random_loadout(seed=seed)
            if loadout.armors:
                for armor in loadout.armors:
                    character.give_armor(armor)

        if class_template.weapons_loadout_pool:
            weapons_pool_name = class_template.weapons_loadout_pool
            assert self.content_source.is_valid_content(
                ContentType.WEAPON_LOADOUT_POOL, weapons_pool_name), \
                "apply_class_template('{}'): {} is invalid weapons pool"\
                .format(class_template.int_name, weapons_pool_name)
            loadout_pool = self.content_source.get_weapon_loadout_pool(weapons_pool_name)
            loadout = loadout_pool.get_random_loadout(seed=seed)
            if loadout.weapons:
                for weapon in loadout.weapons:
                    character.give_weapon(weapon)

    def get_options(self, options_type):
        """
        Returns a list of tuples for potential race options: [(internal_name, display_name),...]
        """
        if options_type == 'race_choice':
            return self.content_source.get_race_user_options()
        elif options_type == 'class_choice':
            return self.content_source.get_class_user_options()
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
        options_dict = {}  # No, PyCharm, lots of stuff in the flask app breaks if I rewrite it as a dict literal
        options_dict['race_options'] = self.get_options('race_choice')
        options_dict['class_options'] = self.get_options('class_choice')
        options_dict['attribute_roll_options'] = self.get_options('attribute_roll_method')
        options_dict['hit_dice_num_options'] = self.get_options('hit_dice_num')
        options_dict['hit_dice_bonus_options'] = self.get_options('hit_dice_bonus')
        options_dict['hit_dice_size_options'] = self.get_options('hit_dice_size')
        return options_dict

    def get_random_option(self, option_type):
        if option_type == 'race':
            return random.choice(self.content_source.get_race_choices())
        elif option_type == 'class':
            return random.choice(self.content_source.get_class_choices())
        elif option_type == 'roll':
            return random.choice(self.roll_keys)
        else:
            raise ValueError("Invalid value type '{}' requested for random option.".format(option_type))

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

        if 'race_choice' in request_dict.keys() \
                and request_dict['race_choice'] in self.content_source.valid_user_race_choices():
            clean_dict['race_choice'] = request_dict['race_choice']
        else:
            is_valid = False
            clean_dict['race_choice'] = self.get_random_option('race')

        if 'class_choice' in request_dict.keys() \
                and request_dict['class_choice'] in self.content_source.valid_user_class_choices():
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

        # This is for the super random option, which is anything at all
        if race_choice == 'random_race':
            rnd_instance = random.Random(seed + 'random_race')
            race_choice = rnd_instance.choice(self.content_source.get_race_choices())
        if class_choice == 'random_class':
            rnd_instance = random.Random(seed + 'random_class')
            class_choice = rnd_instance.choice(self.content_source.get_class_choices())

        # This is for the category specific random options
        if 'random_' in race_choice:
            category = race_choice.replace('random_', '')
            rnd_instance = random.Random(seed + 'random_race_from_category')
            race_choice = rnd_instance.choice(self.content_source.race_categories[category])
        if 'random_' in class_choice:
            category = class_choice.replace('random_', '')
            rnd_instance = random.Random(seed + 'random_class_from_category')
            class_choice = rnd_instance.choice(self.content_source.class_categories[category])

        # Sanity checks
        assert 1 <= hit_dice_num <= 20, 'Invalid HD_NUM received: {}'.format(hit_dice_num)
        # assert class_choice in self.class_keys, 'Invalid class_template: {}'.format(class_choice)
        # assert race_choice in self.race_keys, 'Invalid race_template: {}'.format(race_choice)

        new_character = Character(seed, self.content_source)

        if name:
            new_character.name = name

        new_character.set_stat('hit_dice_num', hit_dice_num)
        new_character.set_stat('hit_dice_extra', bonus_hd)

        race_template = self.content_source.get_race_template(race_choice)
        assert isinstance(race_template, RaceTemplate)
        self.apply_race_template(new_character, race_template)

        class_template = self.content_source.get_class_template(class_choice)
        assert isinstance(class_template, ClassTemplate)
        self.apply_class_template(new_character, class_template, seed=seed)

        # Get all the traits and features from the templates, have the factories instantiate them,
        # then give them to the new character
        for trait_name in itertools.chain(race_template.traits, class_template.traits):
            debug_print('Trait: {}'.format(trait_name))
            trait_feature = self.build_trait(new_character, trait_name)
            trait_feature.give_to_owner()
        for feature_name, feature_args in itertools.chain((
                race_template.features.items()), class_template.features.items()):
            debug_print('Feature: {} args: {}'.format(feature_name, str(feature_args)), 3)
            feature_instance = build_character_feature(new_character, feature_name, feature_args)
            feature_instance.give_to_owner()
            # It's possible for features to give themselves sub features during instantiation
            # So, we need this step, too
            # Right now, this will ignore subfeatures of subfeatures, could change this if a need arises
            feature_instance.give_sub_features_to_owner()

        # Do the pre-attribute rolling first pass of features
        debug_print('Begin features first_pass', 2)
        for feature in new_character.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature.first_pass()

        # Note, for floating attributes bonuses like half-elves to apply, race traits need to be applied before
        # Rolling attributes
        attribute_roll_params = ROLL_METHODS[attribute_roll_method][1]
        attribute_roll_fixed_vals = ROLL_METHODS[attribute_roll_method][2]
        new_character.roll_attributes(*attribute_roll_params,
                                      rerolls_allowed=rerolls_allowed,
                                      min_total=min_total,
                                      no_attribute_swapping=no_attribute_swapping,
                                      force_optimize=force_optimize,
                                      fixed_rolls=attribute_roll_fixed_vals,)

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

        if not no_asi:
            new_character.generate_asi_progression()
            new_character.apply_asi_progression()

        new_character.update_derived_stats()

        # Second and third passes for CharacterFeatures
        debug_print('Begin features second_pass', 2)
        for feature in new_character.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature.second_pass()
        debug_print('Begin features third_pass', 2)
        for feature in new_character.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature.third_pass()

        # Update again, just to be sure
        new_character.update_derived_stats()

        # All characters get unarmored 'armor'
        new_character.give_armor('unarmored')
        # Remember, speeds have to come after armor selection
        new_character.choose_armors()

        new_character.update_speeds()

        # Fourth pass
        debug_print('Begin features fourth_pass', 2)
        for feature in new_character.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature.fourth_pass()

        # cr factor and stat block build time
        debug_print('Begin features cr/statblock build pass', 2)
        for feature in new_character.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature.build_cr_factors_and_stat_block_entries()

        debug_print('Build success!', 1)
        return new_character


class Character:
    def __init__(self, seed, content_source):

        # Character Features get their seed from here, so even if Character doesn't use it it should be present
        self.seed = seed
        # Characters are allowed to look at the content source
        self.content_source = content_source

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

        self.damage_vulnerabilities = []
        self.damage_resistances = []
        self.damage_immunities = []
        self.condition_immunities = []
        self.vulnerabilities = []

        self.languages = []
        self.senses = {}

    def roll_attributes(self, die_size=6, num_dice=3, drop_lowest=0, drop_highest=0,
                        rerolls_allowed=0, min_total=0, fixed_rolls=(),
                        no_attribute_swapping=False,
                        force_optimize=False,
                        no_racial_bonus=False,):

        rnd_instance = random.Random(self.seed + 'attribute rolling')

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
                                 asi_attribute_cap=ASI_DEFAULT_ATTRIBUTE_CAP,):

        rnd_instance = random.Random(self.seed + 'generateasiprogression')

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

        asi_points_remaining = (self.get_hd() // hd_per_increase) * points_per_increase

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

    # Speed is partially dependent on armor, which is determined separately from derived stats
    def update_speeds(self):
        # Python lets us multiply bools by ints, so yay
        # This val should only be nonzero if a character is wearing heavy armor, doesn't have enough strength,
        # and hasn't has their penalty reduced, such as by the heavy_armor_training_trait
        armor_move_penalty = self.chosen_armor.speed_penalty()

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

    # Used so often might as well give it its own method
    def get_hd(self):
        return self.get_stat('hit_dice_num')

    def set_stat(self, stat, value):
        self.stats[stat] = value

    def give_armor(self, armor_name, extra=False):
        armor_template = self.content_source.get_armor(armor_name)
        equipped_armor = EquippedArmor(armor_template, self)
        if extra:
            self.extra_armors[armor_name] = equipped_armor
        else:
            self.armors[armor_name] = equipped_armor

    def give_weapon(self, weapon_name):
        weapon_template = self.content_source.get_weapon(weapon_name)
        equipped_weapon = EquippedWeapon(weapon_template, self)
        self.weapons[weapon_name] = equipped_weapon

    def get_best_weapon_hit_dmg(self):
        best_to_hit = 0
        best_avg_dmg = 0
        for weapon in self.weapons.values():
            if weapon.get_to_hit() > best_to_hit:
                best_to_hit = weapon.get_to_hit()
                best_avg_dmg = weapon.get_damage(use_versatile=True)[0]
            elif weapon.get_to_hit() == best_to_hit:
                best_avg_dmg = max(best_avg_dmg, weapon.get_damage(use_versatile=True)[0])
        return best_to_hit, best_avg_dmg

    def get_best_ac(self):
        assert type(self.chosen_armor) == EquippedArmor, "Can't get AC before setting armor!"
        best_ac = self.chosen_armor.get_ac()
        if self.extra_armors:
            for extra_armor in self.extra_armors.values():
                best_ac = max(best_ac, extra_armor.get_ac())
        return best_ac

    def get_cr(self):

        cr_factors_all = []
        # From weapons
        for weapon in self.weapons.values():
            for weapon_cr_factor in weapon.get_cr_factors():
                cr_factors_all.append(weapon_cr_factor)
        # From features
        for character_feature in self.character_features.values():
            for feature_cr_factor in character_feature.get_cr_factors():
                cr_factors_all.append(feature_cr_factor)

        best_attack_damage = -1
        best_attack_to_hit = -1
        best_ability_level = -1
        best_ability_dc = -1
        effective_damage_bonus = 0
        effective_ac_bonus = 0
        effective_hp_bonus = 0

        for cr_factor in cr_factors_all:
            assert isinstance(cr_factor, CRFactor), str(cr_factor)
            if cr_factor.cr_type == CRFactor.ATTACK:
                if cr_factor.damage > best_attack_damage:
                    best_attack_damage = cr_factor.damage
                    best_attack_to_hit = cr_factor.to_hit
            elif cr_factor.cr_type == CRFactor.ABILITY:
                if cr_factor.ability_level > best_ability_dc:
                    best_ability_level = cr_factor.ability_level
                    best_ability_dc = cr_factor.dc
            elif cr_factor.cr_type == CRFactor.EFFECTIVE_DAMAGE_MOD:
                effective_damage_bonus += cr_factor.extra_damage
            elif cr_factor.cr_type == CRFactor.EFFECTIVE_AC_MOD:
                effective_ac_bonus += cr_factor.extra_ac
            elif cr_factor.cr_type == CRFactor.EFFECTIVE_HP_MOD:
                effective_hp_bonus += cr_factor.extra_ac
            else:
                debug_print('!!!ERROR!!! Invalid cr_factory type {} received'.format(cr_factor.cr_type), 0)

        effective_hp = self.stats['hit_points_total'] + effective_hp_bonus
        effective_ac = self.get_best_ac() + effective_ac_bonus

        starting_defensive_rating = 33
        for i in range(0, len(CHALLENGE_RATING_CHART)):
            if CHALLENGE_RATING_CHART[i][3] > effective_hp:
                starting_defensive_rating = i
                break
        expected_ac = CHALLENGE_RATING_CHART[starting_defensive_rating][2]
        def_rating_shift = int(float(effective_ac - expected_ac) / 2)
        defensive_rating = starting_defensive_rating + def_rating_shift

        offensive_attack_rating = -1
        effective_best_damage = -1
        effective_best_to_hit = -1
        if best_attack_damage > 0:
            effective_best_damage = best_attack_damage + effective_damage_bonus
            effective_best_to_hit = best_attack_to_hit  # Might have other influences later
            starting_offensive_attack_rating = 33
            for i in range(0, len(CHALLENGE_RATING_CHART)):
                if CHALLENGE_RATING_CHART[i][5] > effective_best_damage:
                    starting_offensive_attack_rating = i
                    break
            expected_to_hit = CHALLENGE_RATING_CHART[starting_offensive_attack_rating][4]
            off_attack_rating_shift = int(float(effective_best_to_hit - expected_to_hit) / 2)
            offensive_attack_rating = starting_offensive_attack_rating + off_attack_rating_shift

        offensive_ability_rating = -1
        effective_best_ability_level = -1
        effective_best_ability_dc = -1
        if best_ability_level > 0:
            effective_best_ability_level = best_ability_level
            effective_best_ability_dc = best_ability_dc
            starting_offensive_ability_rating = max(effective_best_ability_level, 0)
            expected_dc = CHALLENGE_RATING_CHART[starting_offensive_ability_rating][6]
            off_ability_rating_shift = int(float(effective_best_ability_dc - expected_dc) / 2)
            offensive_ability_rating = starting_offensive_ability_rating + off_ability_rating_shift

        # if offensive_attack_rating >= 0 and offensive_ability_rating >= 0:
        #     combined_attack_rating = offensive_attack_rating + offensive_ability_rating
        #     offensive_rating = combined_attack_rating // 2 + combined_attack_rating % 2
        # else:
        #     offensive_rating = max(offensive_attack_rating, offensive_ability_rating)

        # Take the better of attack and ability ratings
        # If the difference between the two is within 2, add one more to the rating because that means it well rounded
        offensive_rating = max(offensive_attack_rating, offensive_ability_rating)
        if abs(offensive_attack_rating - offensive_ability_rating) <= 2:
            offensive_rating += 1

        combined_cr_rating = (defensive_rating + offensive_rating) // 2

        expected_proficiency = CHALLENGE_RATING_CHART[combined_cr_rating][1]

        actual_proficiency = self.get_stat('proficiency')
        if actual_proficiency > expected_proficiency:
            combined_cr_rating += 1
        elif actual_proficiency < expected_proficiency:
            combined_cr_rating -= 1

        debug_print('CR Calc: hp{} ac{} dmg{} hit{} caster{} dc{}'
                    .format(effective_hp, effective_ac, effective_best_damage, effective_best_to_hit,
                            effective_best_ability_level, effective_best_ability_dc), 2)
        debug_print('CR Calc: def{} off{} combined{}'.format(defensive_rating, offensive_rating, combined_cr_rating), 2)

        return CHALLENGE_RATING_CHART[combined_cr_rating][0]

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
    # I don't have a good way to get replacement tools, so only skills will get a free replacement if the character
    # already has it
    # Replacement skills are completely random. Not ideal, but it's fine.
    # Should always give add_skill an rnd_instance, because you never know when it might need it for a replacement skill
    def add_skill(self, skill, expertise=False, allow_replacement=True):
        debug_print("add skill: {} expertise={}".format(skill, str(expertise)), 3)
        rnd_instance = random.Random(self.seed + skill + str(expertise) + str(allow_replacement) + 'addskill')
        # Tools can have spaces in them, so they use underscores in the csv file
        # Make sure underscores have become spaces, first
        skill = skill.replace('_', ' ')
        if skill in SKILLS:
            if skill not in self.skills:
                self.skills.add(skill)
                if expertise:
                    self.skills_expertise.add(skill)
            elif skill in self.skills and not expertise:
                replacement_skill = rnd_instance.choice(self.get_non_proficient_skills())
                self.add_skill(replacement_skill)
            elif expertise and skill not in self.skills_expertise:
                self.skills_expertise.add(skill)
                if allow_replacement:
                    if not rnd_instance:
                        rnd_instance = random.Random()
                    replacement_skill = rnd_instance.choice(self.get_non_proficient_skills())
                    self.add_skill(replacement_skill)
            elif expertise and skill in self.skills_expertise:
                if allow_replacement:
                    if not rnd_instance:
                        rnd_instance = random.Random()
                    replacement_skill = rnd_instance.choice(self.get_non_expertise_skills())
                    self.add_skill(replacement_skill, expertise=True)
            else:
                debug_print("!!!ERROR!!! add_skill method screwed up and could not add skill {} expertise={}"
                            .format(skill, str(expertise)))
        else:
            self.tool_proficiencies.add(skill)
            if expertise:
                self.tools_expertise.add(skill)

    def get_non_proficient_skills(self):
        out_skills = set(SKILLS.keys())
        for prof_skill in self.skills:
            out_skills.remove(prof_skill)
        return list(out_skills)

    def get_non_expertise_skills(self):
        out_skills = set(SKILLS.keys())
        for prof_skill in self.skills_expertise:
            out_skills.remove(prof_skill)
        return list(out_skills)

    def add_tag(self, tag, tag_val=None):
        if not tag_val:
            tag_val = []
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

    def choose_armors(self):

        rnd_instance = random.Random(self.seed + 'choosearmor')

        best_ac_armors = []
        # First check for AC
        best_ac = 0
        for armor_obj in self.armors.values():
            armor_ac = armor_obj.get_ac()
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

    def get_all_stat_block_entries(self):
        all_entries = []
        for feature in self.character_features.values():
            assert isinstance(feature, CharacterFeature)
            feature_entries = feature.get_stat_block_entries()
            for stat_block_entry in feature_entries:
                all_entries.append(stat_block_entry)
        return all_entries

    def build_stat_block(self, trait_visibility=1):
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

        all_block_entries = self.get_all_stat_block_entries()
        # Add weapons as entries, too
        for weapon in self.weapons.values():
            all_block_entries.append(weapon.get_stat_block_entry())
        passive_entries = []
        multiattack_entries = []
        action_entries = []
        spellcasting_entries = []
        hidden_entries = []
        attack_entries = []
        reaction_entries = []
        for entry in all_block_entries:
            assert isinstance(entry, StatBlockEntry)
            if entry.get_visibility() <= trait_visibility:
                if entry.get_category() == 'passive':
                    passive_entries.append((entry.get_title(), entry.get_entry()))
                elif entry.get_category() == 'multiattack':
                    multiattack_entries.append((entry.get_title(), entry.get_entry()))
                elif entry.get_category() == 'spellcasting':
                    spellcasting_entries.append((entry.get_title(), entry.get_entry()))
                elif entry.get_category() == 'action':
                    action_entries.append((entry.get_title(), entry.get_entry()))
                elif entry.get_category() == 'attack':
                    attack_entries.append((entry.get_title(), entry.get_entry()))
                elif entry.get_category() == 'reaction':
                    reaction_entries.append((entry.get_title(), entry.get_entry()))
            else:
                hidden_entries.append(entry.get_title())

        sb.attacks = attack_entries
        sb.passive_traits = passive_entries
        sb.multiattack = multiattack_entries
        sb.actions = action_entries
        sb.spellcasting_traits = spellcasting_entries
        sb.reactions = reaction_entries
        sb.hidden_traits = nice_list(hidden_entries)

        return sb


# Everything that can appear as an entry in a stat block musty implement this functionality
# These blocks are "ready to go" for the renderer
# The only logic done here is separating things into logical chunks for the renderer
class StatBlockEntry:
    def __init__(self, title, category, visibility, text, subtitles=None):
        self.title = title
        self.subtitles = subtitles
        if not self.subtitles:
            self.subtitles = []
        self.text = text
        self.category = category
        self.visibility = visibility

    def __str__(self):
        return "{}. {}".format(self.title, self.text)

    def __repr__(self):
        return "<StatBlockEntry:{}>".format(self.title)

    def add_subtitle(self, subtitle):
        self.subtitles.append(subtitle)

    def get_subtitles(self):
        return ', '.join(self.subtitles)

    # The part that is typically in bold with a period at the end.
    def get_title(self, include_subtitles=True):
        if include_subtitles and self.subtitles:
            return '{} ({})'.format(self.title, ', '.join(self.subtitles))
        else:
            return self.title

    # The normal text stuff
    def get_entry(self):
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
    def get_visibility(self):
        return self.visibility


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
        if self.multiattack or self.attacks or self.actions:
            disp += 'ACTIONS\n'
            for multiattack in self.multiattack:
                disp += multiattack[0] + '. ' + multiattack[1] + '\n'
            for attack in self.attacks:
                disp += attack[0] + '. ' + attack[1] + '\n'
            for action in self.actions:
                disp += action[0] + '. ' + action[1] + '\n'
        if self.reactions:
            disp += 'REACTIONS\n'
            for reaction in self.reactions:
                disp += reaction[0] + '. ' + reaction[1] + '\n'

        return disp

    def get_dict(self):
        return self.__dict__


def build_character_feature(character: 'Character', feature_string, args_tup=()):
    feature_class = FEATURE_CLASS_REFERENCE[feature_string]
    feature_instance = feature_class(character, args_tup=args_tup)
    return feature_instance


# When it comes time to give a character a feature, you must instantiate that feature
# Since character features are kinda meaningless without being attached to a character,
# they MUST have an owner specified as part of instantiation
# Character features can access the reference to its owner's seed for randomization
# THey can also use the owners reference to NPCGenerator if they needs to access the generator's data
class CharacterFeature:
    # Randomization and initialization stuff that is not dependent on character stats should happen duing the features's
    # __init__ method.
    # At this point, the only reliable piece of info about the character is how many hd it will have
    # If a character feature has associated subfeatures, they MUST be generated during __init__
    # This ensures that sub features will get the chance to do everything they want to do
    def __init__(self, owner: 'Character'):
        self.int_name = 'dummy'
        self.owner = owner
        self.content_source = self.owner.content_source
        assert isinstance(self.content_source, ContentSource), \
            "Character Feature:{} couldn't find NPCGenerator on owner!".format(self.__class__)
        self.seed = self.owner.seed
        self.stat_block_entries = []
        self.cr_factors = []
        self.sub_features = []

    def __repr__(self):
        return '<Character Feature: {}>'.format(self.int_name)

    def add_sub_feature(self, sub_feature_string, args_tup=()):
        sub_feature = build_character_feature(self.owner, sub_feature_string, args_tup=args_tup)
        self.sub_features.append(sub_feature)

    def add_sub_trait(self, trait_name):
        trait_template = self.content_source.get_trait_template(trait_name)
        trait_feature = FeatureTrait(self.owner, trait_template)
        self.sub_features.append(trait_feature)

    # This method is called after initialization, when it's time to assign the feature to the character
    # This should only be overriden if the function wants to do some sort of merging with other similar features
    # Some kind of innate magic, for example, might want to check if there's already an innate magic feature
    # and if so merge with it, rather than having two
    # This could definitely be moved into the __init__ function, but I figured making it explicit would be more
    # easily understood
    def give_to_owner(self):
        self.owner.add_character_feature(self)

    def give_sub_features_to_owner(self):
        for sub_feature in self.sub_features:
            sub_feature.give_to_owner()

    # first_pass() is called just after race/class templates have been applied,
    # before attributes are rolled or ASI applied
    # At this point, hit dice are known but no attributes or derived stats have been set
    # A feature should call this method if wants to affect how a character rolls for attributes or generates basic stats
    # or if it can figure out everything it wants using ONLY hit dice
    def first_pass(self):
        pass

    # second_pass() is called after attributes have been rolled and stats derived
    # At this point, the bulk of stats have been set
    # Features that want to modify other features but need to take into account character stats should act here
    def second_pass(self):
        pass

    # third_pass() is the 'main' pass
    # This is where most action should happen
    # At this point features that want to modify other features have already done their thing
    # However, a CharacterFeature cannot rely on other features to have gotten their shit together by this point
    def third_pass(self):
        pass

    # fourth_pass() is called right before the character is finished building
    # At this point, a CharacterFeature can expect other CharacterFeatures to have their shit together
    # Character features that depend on other features or modify other features can do their stuff here
    # Mainly, this should be used for things that want to make last minute decisions about CR or stat blocks
    # By this point armor and speeds have already been set
    def fourth_pass(self):
        pass

    # get_cr_factors() and get_stat_block_entries() should NOT be overriden
    # Instead, when a stat block entry or cr factor is finalized, the add_stat_block_entry or add_cr_factor
    # methods should be called and handed the item
    # Then, when the time comes they will be handed off as appropriate
    def add_stat_block_entry(self, stat_block_entry):
        assert isinstance(stat_block_entry, StatBlockEntry)
        self.stat_block_entries.append(stat_block_entry)

    def add_cr_factor(self, cr_factor):
        assert isinstance(cr_factor, CRFactor)
        self.cr_factors.append(cr_factor)

    # This is called at the very end, giving each feature a chance to build and add
    # cr factors and stat block entries if they haven't already
    def build_cr_factors_and_stat_block_entries(self):
        pass

    # This will provide all CRFactors to the CR calculator
    # It should NOT be overriden, instead the specific feature implementations should call add_cr_factor()
    # when the CRFactor is finalized
    def get_cr_factors(self):
        return self.cr_factors

    # When it comes time to build a statblock, every feature will have this function called
    # and the results will be pooled together
    # The StatBlock will then get to decide how to organize and format the results
    # Visibility and which entries should be hidden is handled by the StatBlock
    # It should NOT be overriden, instead the specific feature implementations should call add_stat_block_entry()
    # when the CRFactor is finalized
    def get_stat_block_entries(self):
        return self.stat_block_entries


# Traits are the most common and simplest form of CharacterFeature
# Traits are allowed to make simple changes to a character based on the tags they've been given and will always
# generate only a single StatBlock entry
# The stat block entry text may insert values from the character's stats dictionary, but is otherwise static
# Anything requiring additional functionality must be implemented as a custom CharacterFeature
# FeatureTraits MUST be built from a TraitTemplate and cannot take any additional arguments
# Other than that, they can be treated like a regular CharacterFeature after instantiation
class FeatureTrait(CharacterFeature):
    def __init__(self, owner, trait_template: 'TraitTemplate'):
        super().__init__(owner)
        self.int_name = trait_template.int_name
        self.title = trait_template.display_name
        self.subtitle = trait_template.subtitle
        self.trait_type = trait_template.trait_type
        self.text = trait_template.text
        self.visibility = trait_template.visibility
        self.tags = trait_template.tags

    def first_pass(self):

        rnd_instance = random.Random(self.owner.seed + self.int_name + 'first')

        if 'give_armor' in self.tags:
            for armor in self.tags['give_armor']:
                self.owner.give_armor(armor)

        if 'give_weapon' in self.tags:
            for weapon in self.tags['give_weapon']:
                self.owner.give_weapon(weapon)

        if 'give_tag' in self.tags:
            for character_tag in self.tags['give_tag']:
                self.owner.add_tag(character_tag)

        # Tools and skills are considered the same, anything not in SKILLS is considered a tool
        if 'skill_proficiency' in self.tags:
            for skill in self.tags['skill_proficiency']:
                skill = skill.replace('_', ' ')
                self.owner.add_skill(skill)

        if 'skill_random' in self.tags:
            num_random_skills = int(self.tags['skill_random'][0])
            for i in range(num_random_skills):
                if len(self.owner.get_non_proficient_skills()) > 0:
                    random_skill = rnd_instance.choice(sorted(list(SKILLS.keys())))
                    self.owner.add_skill(random_skill)

        if 'expertise_random' in self.tags:
            num_expertise = int(self.tags['expertise_random'][0])
            expertise_choices = rnd_instance.sample(self.owner.skills, num_expertise)
            for choice in expertise_choices:
                self.owner.add_skill(choice, expertise=True)

        if 'expertise_fixed' in self.tags:
            expertise_choices = self.tags['expertise_random']
            for choice in expertise_choices:
                self.owner.add_skill(choice, expertise=True)

        if 'damage_immunity' in self.tags:
            for entry in self.tags['damage_immunity']:
                self.owner.add_damage_immunity(entry)

        if 'damage_vulnerability' in self.tags:
            for entry in self.tags['damage_vulnerability']:
                self.owner.add_damage_vulnerability(entry)

        if 'damage_resistance' in self.tags:
            for entry in self.tags['damage_resistance']:
                self.owner.add_damage_resistance(entry)

        if 'condition_immunity' in self.tags:
            for entry in self.tags['condition_immunity']:
                self.owner.add_condition_immunity(entry)

        if 'save_advantage' in self.tags:
            for advantage in self.tags['save_advantage']:
                self.owner.add_save_advantage(advantage)

        if 'save_disadvantage' in self.tags:
            for disadvantage in self.tags['save_disadvantage']:
                self.owner.add_save_disadvantage(disadvantage)

        if 'sense_darkvision' in self.tags:
            val = int(self.tags['sense_darkvision'][0])
            self.owner.senses['darkvision'] = max(self.owner.senses.get('darkvision', 0), val)

        if 'bonus_hp_per_level' in self.tags:
            val = int(self.tags['bonus_hp_per_level'][0])
            self.owner.stats['bonus_hp_per_level'] += val

        if 'floating_attribute_bonus' in self.tags:
            val = int(self.tags['floating_attribute_bonus'][0])
            self.owner.stats['floating_attribute_points'] += val

        if 'random_language' in self.tags:
            num_extra_languages = self.tags['random_language'][0]
            language_options = set(LANGUAGES)
            for language in self.owner.languages:
                language_options.remove(language)
            language_choices = rnd_instance.sample(language_options, num_extra_languages)
            for language in language_choices:
                self.owner.add_language(language)

    # Traits shouldn't need to do anything on the second pass
    def third_pass(self):
        pass

    def get_cr_factors(self):
        factors_list = []
        if 'cr_damage_shift' in self.tags:
            shift_val = int(self.tags['cr_damage_shift'][0])
            cr_factor = CRFactor(CRFactor.EFFECTIVE_DAMAGE_MOD, extra_damage=shift_val)
            factors_list.append(cr_factor)
        if 'cr_ac_shift' in self.tags:
            shift_val = int(self.tags['cr_ac_shift'][0])
            cr_factor = CRFactor(CRFactor.EFFECTIVE_AC_MOD, extra_ac=shift_val)
            factors_list.append(cr_factor)
        if 'cr_hp_shift' in self.tags:
            shift_val = int(self.tags['cr_hp_shift'][0])
            cr_factor = CRFactor(CRFactor.EFFECTIVE_HP_MOD, extra_hp=shift_val)
            factors_list.append(cr_factor)
        return factors_list

    def get_stat_block_entries(self):
        text = self.text.format(**self.owner.stats)
        sb_entry = StatBlockEntry(
            title=self.title, text=text, category=self.trait_type, visibility=self.visibility, )
        return [sb_entry, ]


# When it comes time for the CR calculation, each ClassFeature may choose to provide one or more CRFactor instances
# The method for calculating CR will collect them and figure out how to use them
class CRFactor:
    ATTACK = 'attack'
    ABILITY = 'ability'
    EFFECTIVE_DAMAGE_MOD = 'effective_damage_mod'
    EFFECTIVE_AC_MOD = 'effective_ac_mod'
    EFFECTIVE_HP_MOD = 'effective_hp_mod'

    def __init__(self, cr_type, importance=-1, damage=-1.0, ability_level=-1, to_hit=-1,
                 dc=-1, extra_damage=-1, extra_ac=-1, extra_hp=-1):
        # Valid types: attack, ability, effective_damage_mod, effective_ac_mod
        self.cr_type = cr_type
        self.importance = importance
        self.damage = damage
        self.ability_level = ability_level
        self.to_hit = to_hit
        self.dc = dc
        self.extra_damage = extra_damage
        self.extra_ac = extra_ac
        self.extra_hp = extra_hp


class EquippedArmor:
    def __init__(self, armor_template: 'ArmorTemplate', owner: 'Character'):
        self.int_name = armor_template.int_name
        self.display_name = armor_template.display_name
        self.base_ac = armor_template.base_ac
        self.armor_type = armor_template.armor_type
        self.min_str = armor_template.min_str
        self.stealth_disadvantage = armor_template.stealth_disadvantage
        self.tags = armor_template.tags.copy()

        # Owner can be assigned to make references easier
        self.owner = owner

        # This stuff is usually default, but can be overriden by character features
        self.enchantment = 0

    def __repr__(self):
        return "<EquippedArmor:{}, owner:{}>".format(self.int_name, self.owner.name)

    def is_extra(self):
        return 'extra' in self.tags

    def get_ac(self,):

        owner = self.owner
        assert isinstance(owner, Character), 'Armor obj {} has no owner!'.format(self.int_name)

        base_ac = self.base_ac + self.enchantment
        total_ac = 0
        if self.armor_type == 'light' or self.armor_type == 'none':
            total_ac = base_ac + owner.get_stat('dex_mod')
        elif self.armor_type == 'medium':
            max_dex_bonus = 2
            if 'medium_armor_master' in owner.character_tags:
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
    def speed_penalty(self):

        owner = self.owner
        assert isinstance(owner, Character), 'Armor obj {} has no owner!'.format(self.int_name)

        if 'heavy_armor_penalty' in owner.character_tags:
            return 0

        if self.armor_type == 'heavy' and self.min_str > owner.get_stat('str'):
            return HEAVY_ARMOR_MOVE_PENALTY
        else:
            return 0

    def stealth_penalty(self):

        owner = self.owner
        assert isinstance(owner, Character), 'Armor obj {} has no owner!'.format(self.int_name)

        # Special case for medium armor master
        if self.armor_type == 'medium' and 'medium_armor_master' in owner.character_tags:
            return False

        return self.stealth_disadvantage

    def sheet_display(self, owner):

        if not owner:
            owner = self.owner
        assert isinstance(owner, Character), 'Armor obj {} has no owner!'.format(self.int_name)

        armor_name = self.display_name
        if self.enchantment:
            armor_name = '{} {}'.format(self.display_name, num_plusser(self.enchantment))
        outstring = str(self.get_ac()) + ' (' + armor_name
        if owner.has_shield:
            outstring += ', with shield'
        outstring += ')'
        return outstring


class EquippedWeapon:
    def __init__(self, weapon_template: 'WeaponTemplate', owner: 'Character'):
        self.int_name = weapon_template.int_name
        self.display_name = weapon_template.display_name
        self.dmg_dice_num = weapon_template.dmg_dice_num
        self.dmg_dice_size = weapon_template.dmg_dice_size
        self.damage_type = weapon_template.damage_type
        self.attack_type = weapon_template.attack_type
        self.range_short = weapon_template.range_short
        self.range_long = weapon_template.range_long
        self.tags = weapon_template.tags.copy()
        self.num_targets = weapon_template.num_targets

        # Can be assigned as owner, making referencing easier
        self.owner = owner

        # Typically not used, but can be modified by other things
        self.subtitles = []
        self.enchantment = 0
        self.extra_damages = []
        self.extra_effects = []

    def __repr__(self):
        return "<EquippedWeapon:{} owner:{}>".format(self.int_name, self.owner.name)

    def __str__(self):
        outstring = '[{},{},{},{},{},{},{},{},{},{},' \
            .format(self.int_name, self.display_name, self.dmg_dice_num, self.dmg_dice_size, self.damage_type,
                    self.attack_type, str(self.range_short), str(self.range_long), str(self.tags),
                    str(self.num_targets))
        return outstring

    def get_to_hit(self):

        owner = self.owner
        assert isinstance(owner, Character), 'Weapon obj {} has no owner!'.format(self.int_name)

        owner_str = owner.get_stat('str_mod')
        owner_dex = owner.get_stat('dex_mod')
        owner_prof = owner.get_stat('proficiency')
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
        return attack_stat + owner_prof

    def get_damage(self, use_versatile=False):

        owner = self.owner
        assert isinstance(owner, Character), 'Weapon obj {} has no owner!'.format(self.int_name)

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

        avg_dmg = dmg_dice_size / 2 * dmg_dice_num + attack_stat

        return int(avg_dmg), dmg_dice_num, dmg_dice_size, attack_stat, self.damage_type, avg_dmg

    def get_avg_dmg(self):

        owner = self.owner
        assert isinstance(owner, Character), 'Weapon obj {} has no owner!'.format(self.int_name)

        return self.get_damage(use_versatile=True)[5]

    def get_cr_factors(self):

        owner = self.owner
        assert isinstance(owner, Character), 'Weapon obj {} has no owner!'.format(self.int_name)

        to_hit = self.get_to_hit()
        avg_dmg = self.get_avg_dmg()
        cr_factor = CRFactor(CRFactor.ATTACK, to_hit=to_hit, damage=avg_dmg)
        return [cr_factor, ]

    def get_stat_block_entry(self):

        owner = self.owner
        assert isinstance(owner, Character), 'Weapon obj {} has no owner!'.format(self.int_name)

        text = ''
        is_melee = self.attack_type == 'melee'
        is_ranged = (self.attack_type == 'ranged' or 'thrown' in self.tags)
        if is_melee and is_ranged:
            text += 'Melee or ranged weapon attack: '
        elif is_melee:
            text += 'Melee weapon attack: '
        elif is_ranged:
            text += 'Ranged weapon attack: '

        text += '{} to hit, '.format(num_plusser(self.get_to_hit()))

        if is_melee and 'reach' in self.tags:
            weapon_reach = WEAPON_REACH_W_BONUS
        else:
            weapon_reach = WEAPON_REACH_NORMAL

        if is_melee and is_ranged:
            text += 'reach {} ft. or range {}/{} ft., '.format(weapon_reach, self.range_short, self.range_long)
        elif is_melee:
            text += 'reach {} ft, '.format(weapon_reach)
        elif is_ranged:
            text += 'range {}/{} ft., '.format(self.range_short, self.range_long)

        if self.num_targets == 1:
            text += 'one target. '
        else:
            text += NUM_TO_TEXT.get(self.num_targets) + ' targets. '
        ##
        avg_dmg_int, num_dmg_dice, dmg_dice_size, attack_mod, dmg_type, avg_dmg_float = self.get_damage()
        text += 'Hit: {}({}d{} {}) {} damage' \
            .format(avg_dmg_int, num_dmg_dice, dmg_dice_size, num_plusser(attack_mod, add_space=True), dmg_type)

        # Check for versatile, which increases damage with two hands.
        if is_melee and 'versatile' in self.tags:
            avg_dmg_int, num_dmg_dice, dmg_dice_size, attack_mod, dmg_type, avg_dmg_float = \
                self.get_damage(use_versatile=True)
            text += ' or {}({}d{} {}) {} damage if used with two hands' \
                .format(avg_dmg_int, num_dmg_dice, dmg_dice_size, num_plusser(attack_mod, add_space=True), dmg_type)
        text += '.'

        title = self.display_name
        if self.enchantment:
            title = '{} {}'.format(title, num_plusser(self.enchantment))
        stat_block_entry = StatBlockEntry(title, 'attack', 0, text, subtitles=self.subtitles)

        return stat_block_entry

    def add_tag(self, tag):
        self.tags.add(tag)


class FeatureMultiattack(CharacterFeature):
    def __init__(self, owner, args_tup=()):
        super().__init__(owner)
        self.int_name = 'multiattack'

        self.multiattack_type = args_tup[0]
        self.attacks = 1
        char_hd = owner.get_hd()
        if self.multiattack_type == 'fighter':
            self.attacks = increment_from_hd(1, (5, 11, 20), char_hd)
        elif self.multiattack_type == 'single':
            if char_hd >= 5:
                self.attacks = 2

        # In the future, it would be nice to have the multiattack specifically say which weapons can be used
        # self.melee_attacks = []
        # self.offhand_weapons = []
        # self.best_melee_dmg = 0
        # self.best_offhand_damage = 0
        # self.ranged_weapons = []
        # self.best_ranged_damage = 0

    def get_cr_factors(self):
        best_weapon_to_hit, best_weapon_dmg = self.owner.get_best_weapon_hit_dmg()
        damage_per_round = best_weapon_dmg * self.attacks
        cr_factor = CRFactor(CRFactor.ATTACK, to_hit=best_weapon_to_hit, damage=damage_per_round)
        return [cr_factor, ]

    def get_stat_block_entries(self):
        entries = []
        if self.attacks > 1:
            main_entry = StatBlockEntry(
                'Multiattack', 'multiattack', 0,
                "You may make {} attacks when using the attack action.".format(NUM_TO_TEXT[self.attacks]))
            entries.append(main_entry)
        return entries


HIGHEST_SPELL_LEVEL_BY_CASTER_LEVEL = (
        1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 9, 9,
)

# Although different classes have different progressions, you can actually get any of them from this table
# You just need their 'caster level', which isn't technically recognized by the rules,
# but can be derived from HD depending on whether the character is a full, half, or third caster
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
    'warlock': (-1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15),
    'half': (-1, 0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11),
    'third': (-1, 0, 0, 3, 4, 4, 4, 5, 6, 6, 7, 8, 8, 9, 10, 10, 11, 11, 11, 12, 13),
}

CASTER_CANTRIPS_KNOWN = {
    'none': (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,),
    'cleric_wizard': (-1, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,),
    'sorcerer': (-1, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,),
    'bard_druid': (-1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,),
}

# Warlocks have their own thing going on, but it's close enough to use the standard spellcasting system
# It can be fitted it with just a few special case conditions and these references
WARLOCK_SLOTS = (
    -1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4
)

WARLOCK_SLOT_LEVEL = (
    -1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5
)


# Spellcasting is super messy and confusing. Not the least because of all the VERY similar sounding terms used.
# For our spellcasting feature to be robust, it needs to be able to take into account quite a lot of things.
class FeatureSpellcasting(CharacterFeature):
    def __init__(self, owner, args_tup=()):
        super().__init__(owner)
        sp_profile_name = args_tup[0]
        self.int_name = 'spellcasting_' + sp_profile_name

        sp_profile = self.content_source.get_spellcaster_profile(sp_profile_name)
        assert isinstance(sp_profile, SpellCasterProfile)

        # Characters generally either have spells 'prepared' or 'known'
        self.ready_style = sp_profile.ready_style
        # Which stat is used for casting
        self.casting_stat = sp_profile.casting_stat
        self.hd_per_casting_level = sp_profile.hd_per_casting_level
        self.cantrips_progression = CASTER_CANTRIPS_KNOWN[sp_profile.cantrips_per_level]
        self.fixed_spells_known_by_level = CASTER_FIXED_SPELLS_KNOWN.get(sp_profile.fixed_spells_known_by_level, None)
        # Currently no support for alternative spell slots tables
        self.spell_slots_table = SPELL_SLOTS_TABLE
        self.spells_known_modifier = sp_profile.spells_known_modifier

        # These values are alterable, so we need COPIES from the profile
        self.spell_lists = {}
        for spell_list_name, weight in sp_profile.spell_lists.items():
            self.add_spell_list(spell_list_name, weight)
        self.tags = sp_profile.get_tags()

        self.bonus_cantrips = 0

        # We need a set of free spells so we know to discard those picks when it comes time to choose spells
        self.free_spells = set()
        for spell_list in sp_profile.free_spell_lists:
            self.add_free_spell_list(spell_list)

        # A list of lists, index corresponds to the list of spells know for each level, 0 for cantrips
        self.spell_choices = None
        self.spell_choices = [[], [], [], [], [], [], [], [], [], [], ]
        self.spell_slots = []
        self.cantrips_readied = 0
        self.spells_readied = [[], [], [], [], [], [], [], [], [], [], ]
        self.spells_readied_set = set()
        self.spellbook = None

        # Many spells can be treated as an attack, if such a spell is readied, here it goes!
        self.spell_attacks = []

    # Hypothetically, other feature can add spell_lists to a spellcasting feature
    # For example, you could have a base cleric and have the domain be a feature that modifies the spellcasting feature
    def add_free_spell_list(self, spell_list_name):
        assert spell_list_name in self.content_source.spell_lists, \
            'Invalid list {} for adding free spells!'.format(spell_list_name)
        spell_list = self.content_source.get_spell_list(spell_list_name)
        for spell in spell_list.spells:
            self.free_spells.add(spell)

    def add_free_spell(self, spell_name):
        self.free_spells.add(spell_name)

    def add_free_spells(self, spells):
        for spell in spells:
            self.add_free_spell(spell)

    def add_random_free_spells_from_spell_list(self, num_spells, spell_list_name):
        rnd_instance = random.Random(self.seed + spell_list_name + 'addfreespellsfromlist')
        spell_list = self.content_source.get_spell_list(spell_list_name)
        spell_options = list(spell_list.spells.keys())
        rnd_instance.shuffle(spell_options)
        while num_spells > 0 and len(spell_options) > 0:
            self.add_free_spell(spell_options.pop(0))
            num_spells -= 1

    def add_spell_list(self, spell_list, weight=DEFAULT_SPELL_LIST_WEIGHT):
        if spell_list in self.spell_lists.keys():
            debug_print('Adding spell list "{}" to spellcasting feature, but already present. Overwriting weight.')
        self.spell_lists[spell_list] = weight

    def get_free_spells(self):
        return self.free_spells

    # This function will go ahead and pre-select all of the spells this character might end up knowing
    # When it comes time to get a character's spells known, they'll just grab a selection from those lists
    # Selections are weighted by spelllist as specified in the spellcaster profile
    # Will not select spells that the caster will automatically end up getting
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

    def get_spell_dc(self):
        return self.owner.get_stat(self.casting_stat + '_dc')

    def get_spell_to_hit(self):
        return self.owner.get_stat(self.casting_stat + '_attack')

    # Caster level is actually a bit weird for half and third casters like paladins and eldritch knights
    # They only get their first casting level at 2 or 3 hd, respectively
    # BUT, the next hd they gets bumps them up to the next spellcaster level regardless
    # From then on, they need 2 or 3 hd to get additional spellcasting levels
    # So, that's why this function looks weird
    def get_caster_level(self):
        hit_dice = self.owner.get_hd()
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

    # Right now it's a simple thing, but there's possibility other things may want to mess with this
    def set_spell_slots(self):
        self.spell_slots = self.spell_slots_table[self.get_caster_level()]
        self.cantrips_readied = int(self.cantrips_progression[self.owner.get_hd()]) + self.bonus_cantrips

    def get_max_spell_level(self):
        if 'warlock' in self.tags:
            return WARLOCK_SLOT_LEVEL[self.get_caster_level()]
        else:
            max_spell_level = 9
            for spell_level in range(1, 10):
                if self.spell_slots[spell_level] <= 0:
                    max_spell_level = spell_level - 1
                    break
        return max_spell_level

    def get_spell_level(self, spell_name):
        return self.content_source.get_spell(spell_name).level

    # At this point, we already have our possible spell choices made
    # Now, we're basically going to figure out how which of those spells to have readied
    # First, we figure out how many spells the character is allowed to have readied
    # Typically, this is caster level + casting stat mod
    # Some classes, however, used a fixed progression dependent on hd rather than casting stat
    # Additionally, cantrips have their own chart and are kinda separate
    # So, once we know how many spells in total we want to pick we need to decide how many of each level
    # We guarantee one for each spell level up to the maximum spell level the caster can cast
    # after that, we go through and one by one pick spell levels one by one until we run out of picks
    # For each pick, each spell level is weighted by how many spell slots the character could use to cast that level
    # That weight is also divided by the number of picks already made
    # Thus characters are biased toward making more low level picks and picks of levels they have fewer of
    # Note that any free spells the character gets will NOT be reflected in these picks
    def select_readied_spells(self):
        rnd_instance = random.Random(self.seed + self.int_name + 'spellpicking')
        char_hd = self.owner.get_hd()
        caster_level = self.get_caster_level()

        if self.fixed_spells_known_by_level:
            spells_readied_remaining = self.fixed_spells_known_by_level[char_hd]
        else:
            spells_readied_remaining = caster_level + self.owner.get_stat(
                self.casting_stat + '_mod') + self.spells_known_modifier

        max_spell_level = self.get_max_spell_level()

        # Add free spells to spells readied
        for spell_name in self.free_spells:
            self.spells_readied[self.get_spell_level(spell_name)].append(spell_name)

        # Cantrips are straightforward, simply pop them from our choices list until we have enough
        cantrips_remaining = self.cantrips_readied
        while cantrips_remaining > 0:
            self.spells_readied[0].append(self.spell_choices[0].pop(0))
            cantrips_remaining -= 1

        # Now, we have to decide which levels of spells to ready
        # When we make a pick, we're just going to pop it from spell_choices, since we shouldn't need that after this
        # First, go through and make sure the caster has at least one spell from each level she can cast
        for spell_level in range(1, max_spell_level + 1):
            if spells_readied_remaining > 0:  # Technically, a super dumb guy may not have enough picks for all levels
                self.spells_readied[spell_level].append(self.spell_choices[spell_level].pop(0))
                spells_readied_remaining -= 1

        # Now, we make the picks
        # We have to rebuild the weights after each level pick
        while spells_readied_remaining > 0:
            weights = [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, ]
            for spell_level in range(1, max_spell_level + 1):
                weights[spell_level] = sum(self.spell_slots[spell_level:])
                weights[spell_level] /= len(self.spells_readied[spell_level])
            spell_level_choice = rnd_instance.choices(range(1, max_spell_level + 1), weights[1:max_spell_level + 1])[0]
            self.spells_readied[spell_level_choice].append(self.spell_choices[spell_level_choice].pop(0))
            spells_readied_remaining -= 1

        # Finally, we add EVERY spell to a set, which we can use for easy referencing, like mage armor or shield
        for spell_level in range(0, 10):
            for spell_name in self.spells_readied[spell_level]:
                self.spells_readied_set.add(spell_name)
        # It's wacky and confusing and I don't understand it, but now self.spells_readied should have an appropriate
        # set of randomly generated spells know by level and self.spells_readied_set should have a set of all spells

    # Wizards also have a spellbook
    # Typically, it contains 6 1st level spells + 2 for every level after that.
    # Users don't need to see spells already in the prepared sopell list, so this method produces a list of
    # spells that are in a character's spellbook, but NOT currently prepared
    # Characters are assumed to spend their spell picks on the highest level spell they can
    # Every level they get chance to get an extra spell pick, for variety's sake,
    # bonus_spell_chance is percentage cvahnce of getting that extra spell
    def set_spellbook(self, starting_spells=4, spells_per_level=2, bonus_spell_chance=10):
        rnd_instance = random.Random(self.seed + self.int_name + 'spellbook')
        spellbook = []
        total_spells = [-1, starting_spells, 0, 0, 0, 0, 0, 0, 0, 0, ]
        for character_level in range(0, self.owner.get_hd()):
            spells_for_this_level = spells_per_level
            if rnd_instance.randrange(100) < bonus_spell_chance:
                spells_for_this_level += 1
            highest_spell_level = HIGHEST_SPELL_LEVEL_BY_CASTER_LEVEL[character_level]
            total_spells[highest_spell_level] += spells_for_this_level

        for spell_level in range(1, 10):
            spellbook_spells = total_spells[spell_level] - len(self.spells_readied[spell_level])
            while spellbook_spells > 0:
                if len(self.spell_choices[spell_level]):  # Make sure we still haven't already exhausted our choices
                    spellbook.append(self.spell_choices[spell_level].pop(0))
                spellbook_spells -= 1
        debug_print('Spellbook built, contains: {}'.format(str(spellbook)), 2)
        self.spellbook = spellbook

    # Hypothetically, other features might want to do something that affects spellcasting in the first pass,
    # so we do all the big stuff in the second pass
    def third_pass(self):
        self.set_spell_choices()
        self.set_spell_slots()
        self.select_readied_spells()

        if 'spellbook' in self.tags:
            self.set_spellbook()

        # Now, we can do some of those special case things
        if 'mage armor' in self.spells_readied_set:
            self.owner.give_armor('mage_armor', extra=True)

        if 'chill touch' in self.spells_readied_set:
            self.spell_attacks.append(SpellAttackChillTouch(self))
        if 'eldritch blast' in self.spells_readied_set:
            self.spell_attacks.append(SpellAttackEldritchBlast(self))

    def get_main_stat_block_entry(self):
        caster_level = self.get_caster_level()
        if caster_level == 0:
            return None

        text = "This character is a {}-level spellcaster. " \
               "Its spellcasting ability is {} (spell save DC {}, {} to hit with spell attacks). " \
               "It has the following spells {}:" \
               .format(NUM_TO_ORDINAL[caster_level],
                       ATTRIBUTES_ABBREVIATION_TO_FULL_WORD[self.casting_stat],
                       self.owner.get_stat(self.casting_stat + '_dc'),
                       num_plusser(self.owner.get_stat(self.casting_stat + '_attack')), self.ready_style) + '\n'
        # Cantrips
        if len(self.spells_readied[0]) > 0:
            text += 'Cantrips (at-will): ' + ', '.join(self.spells_readied[0])
        for i in range(1, 10):
            if len(self.spells_readied[i]) > 0 and self.spell_slots_table[caster_level][i] > 0:
                # Pluralize 'slot' or not
                if self.spell_slots_table[caster_level][i] == 1:
                    text += '\n{} level ({} slot): ' \
                        .format(NUM_TO_ORDINAL[i], self.spell_slots_table[caster_level][i])
                else:
                    text += '\n{} level ({} slots): ' \
                        .format(NUM_TO_ORDINAL[i], self.spell_slots_table[caster_level][i])
                text += ', '.join(self.spells_readied[i])
        return StatBlockEntry('Spellcasting', 'spellcasting', 0, text)

    def get_warlock_stat_block_entry(self):
        caster_level = self.get_caster_level()
        if caster_level == 0:
            return None

        text = "This character is a {}-level spellcaster. " \
               "Its spellcasting ability is {} (spell save DC {}, {} to hit with spell attacks). " \
               "This character has {} level {} spell slots which are regained after a short rest. " \
               "It has the following spells {}:" \
               .format(NUM_TO_ORDINAL[caster_level],
                       ATTRIBUTES_ABBREVIATION_TO_FULL_WORD[self.casting_stat],
                       self.owner.get_stat(self.casting_stat + '_dc'),
                       num_plusser(self.owner.get_stat(self.casting_stat + '_attack')),
                       self.get_max_spell_level(), WARLOCK_SLOTS[self.get_caster_level()],
                       self.ready_style) + '\n'
        # Cantrips
        if len(self.spells_readied[0]) > 0:
            text += 'Cantrips (at-will): ' + ', '.join(self.spells_readied[0])
        for i in range(1, 10):
            if len(self.spells_readied[i]) > 0 and self.spell_slots_table[caster_level][i] > 0:
                # Pluralize 'slot' or not
                if self.spell_slots_table[caster_level][i] == 1:
                    text += '\n{} level: ' \
                        .format(NUM_TO_ORDINAL[i], self.spell_slots_table[caster_level][i])
                else:
                    text += '\n{} level: ' \
                        .format(NUM_TO_ORDINAL[i], self.spell_slots_table[caster_level][i])
                text += ', '.join(self.spells_readied[i])
        return StatBlockEntry('Spellcasting', 'spellcasting', 0, text)

    def get_spellbook_entry(self):
        if len(self.spellbook) > 0:
            text = "You have a spellbook containing your readied spells and the following additional spells: {}"\
                .format(nice_list(self.spellbook))
        else:
            text = "You have a spellbook containing your readied spells."
        return StatBlockEntry('Spellbook', 'spellcasting', 0, text)

    @staticmethod
    def get_shield_entry():
        text = "When you are hit by an attack or targeted by the magic missile spell, " \
               "an invisible barrier of magical force appears and protects you. " \
               "Until the start of your next turn, you have a +5 bonus to AC, " \
               "including against the triggering attack, and you take no damage from magic missile."
        return StatBlockEntry('Shield', 'reaction', 0, text, subtitles=['spell'])

    def build_cr_factors_and_stat_block_entries(self):
        # CR
        caster_level = self.get_caster_level()
        dc = self.get_spell_dc()
        self.add_cr_factor(CRFactor(CRFactor.ABILITY, ability_level=caster_level, dc=dc))

        # Special case spells
        if 'shield' in self.spells_readied_set:
            self.add_cr_factor(CRFactor(CRFactor.EFFECTIVE_AC_MOD, extra_ac=1))

        for spell_attack in self.spell_attacks:
            self.add_cr_factor(spell_attack.get_cr_factor())

        # Stat block entries
        if 'warlock' in self.tags:
            self.add_stat_block_entry(self.get_warlock_stat_block_entry())
        else:
            self.add_stat_block_entry(self.get_main_stat_block_entry())
        if 'spellbook' in self.tags:
            self.add_stat_block_entry(self.get_spellbook_entry())

        # Per spell special entries
        if 'shield' in self.spells_readied_set:
            self.add_stat_block_entry(self.get_shield_entry())

        # All the spells set up as attacks
        for spell_attack in self.spell_attacks:
            self.add_stat_block_entry(spell_attack.get_stat_block_entry())


class SpellAttack:
    def __init__(self, spellcasting_feature: 'FeatureSpellcasting'):
        self.spellcasting_feature = spellcasting_feature
        self.owner = self.spellcasting_feature.owner

    def get_stat_block_entry(self):
        pass

    def get_cr_factor(self):
        pass


class SpellAttackChillTouch(SpellAttack):
    TEXT = "Ranged spell attack: {} to hit, range 120 ft., one target. " \
           "Hit: {}d8 necrotic damage " \
           "and target can't regain hit points until the start of your next turn. " \
           "If you hit an undead target, it also has disadvantage on attack rolls " \
           "against you until the end of your next turn."

    def attack_dice(self):
        return increment_from_hd(1, (5, 11, 17), self.owner.get_hd())

    def get_cr_factor(self):
        return CRFactor(CRFactor.ATTACK, damage=self.attack_dice()*4.5,
                        to_hit=self.spellcasting_feature.get_spell_to_hit())

    def get_stat_block_entry(self):
        text = self.TEXT
        to_hit = num_plusser(self.spellcasting_feature.get_spell_to_hit())
        text = text.format(to_hit, self.attack_dice())
        return StatBlockEntry('Chill Touch', 'attack', 1, text, subtitles=['cantrip', 'VS'])


class SpellAttackEldritchBlast(SpellAttack):
    TEXT_SINGLE = \
        "Ranged spell attack: {} to hit, range 120 ft., one target. " \
        "Hit: 1d8 force damage.\n" \
        "A beam of crackling energy streaks toward one creature within range."

    TEXT_MULTIPLE = \
        "Ranged spell attack: {} to hit, range 120 ft., up to {} targets. " \
        "Hit: 1d8 force damage.\n" \
        "{} beams of crackling energy streak toward one or more creatures within range. " \
        "You can direct the beams at the same target or at different ones. " \
        "Make a ranged spell attack for each beam. "

    def beams(self):
        return increment_from_hd(1, (5, 11, 17), self.owner.get_hd())

    def get_cr_factor(self):
        return CRFactor(CRFactor.ATTACK, damage=self.beams()*5.5,
                        to_hit=self.spellcasting_feature.get_spell_to_hit())

    def get_stat_block_entry(self):
        beams = self.beams()
        to_hit = num_plusser(self.spellcasting_feature.get_spell_to_hit())
        if beams > 1:
            text = self.TEXT_MULTIPLE.format(to_hit, beams, NUM_TO_TEXT[beams].title())
        else:
            text = self.TEXT_SINGLE.format(to_hit)
        return StatBlockEntry('Eldritch Blast', 'attack', 1, text, subtitles=['cantrip', 'VS'])


# Below this point are classes for particular Character Features
# If you add a new feature, you MUST update the FEATURE_CLASS_REFERENCE constant

FEATURE_TINKER_OPTIONS = {
    'clockwork toy':
        'This toy is a clockwork animal, monster, or person, such as a frog, mouse, bird, dragon, or soldier. '
        'When placed on the ground, the toy moves 5 feet across the ground '
        'on each of your turns in a random direction. '
        'It makes noises as appropriate to the creature it represents.',
    'fire box':
        'The device produces a miniature flame, which you can use to light a candle, torch, or campfire. '
        'Using the device requires your action.',
    'music box':
        "When opened, this music box plays a single song at a moderate volume. "
        "The box stops playing when it reaches the song's end or when it is closed.",
}


class FeatureTinker(CharacterFeature):
    def __init__(self, owner, args_tup=()):
        super().__init__(owner)
        self.int_name = 'tinker'
        rnd_instance = random.Random(self.seed + self.int_name + 'init')
        self.choice = rnd_instance.choice(list(FEATURE_TINKER_OPTIONS.keys()))

    def first_pass(self):
        self.owner.add_skill('tinkers_tools')

    def build_cr_factors_and_stat_block_entries(self):
        self.add_stat_block_entry(StatBlockEntry(
            'Tinker', 'passive', 2,
            "You have proficiency with artisan's tools (tinker's tools). Using those tools, "
            "you can spend 1 hour and 10 gp worth of materials to construct a Tiny clockwork "
            "device (AC 5, 1 hp). The device ceases to function after 24 hours (unless you "
            "spend 1 hour repairing it to keep the device functioning), or when you use your "
            "action to dismantle it; at that time, you can reclaim the materials used to "
            "create it. You can have up to three such devices active at a time."))
        self.add_stat_block_entry(StatBlockEntry(
            self.choice.title(), 'passive', 0, FEATURE_TINKER_OPTIONS[self.choice]))


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
    def __init__(self, owner, args_tup=()):
        super().__init__(owner)
        self.int_name = 'dragonborn_feature'
        self.lineage_type = args_tup[0]

    def first_pass(self):
        self.owner.add_damage_resistance(FEATURE_DRAGONBORN_CHART[self.lineage_type][0])

    def build_cr_factors_and_stat_block_entries(self):
        hd = self.owner.get_hd()
        dmg_dice = increment_from_hd(2, (6, 11, 16), hd)
        text = "When you use your breath weapon, each creature in a {} must make a DC {} {} saving throw. " \
               "A creature takes {}d6 {} damage on a failed save, and half as much damage on a successful one." \
            .format(FEATURE_DRAGONBORN_CHART[self.lineage_type][1], self.owner.get_stat('con_dc'),
                    FEATURE_DRAGONBORN_CHART[self.lineage_type][2], dmg_dice,
                    FEATURE_DRAGONBORN_CHART[self.lineage_type][0])
        breath_weapon_entry = StatBlockEntry('Breath Weapon', 'action', 0, text, subtitles=['1/short', ])
        self.add_stat_block_entry(breath_weapon_entry)


MARTIAL_ARTS_DAMAGE = (
    (-1, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 8, 10, 10, 10, 10,)
)


# Martial Arts works by going through a character's weapons and checking to see if the weapon can be "upgraded" to
# a bigger die. If the weapon can be upgraded, it is, and a 'Martial Arts' subtitle is added.
# TECHNICALLY martial arts shouldn't give finesse, but it basically does, so I'm just adding that tag to valid weapons
# to allow dex to be used for attacks
# I think it would only matter for sneak attack, which I'm not going to implement precisely anyways
class FeatureMartialArts(CharacterFeature):
    def __init__(self, owner, args_tup=()):
        super().__init__(owner)
        self.upgrade_damage_die = MARTIAL_ARTS_DAMAGE[self.owner.get_hd()]

    @staticmethod
    def is_monk_weapon(weapon: 'EquippedWeapon'):
        if weapon.attack_type == 'melee':
            if 'monk' in weapon.tags:
                return True
            elif 'simple' in weapon.tags and '2h' and 'heavy' not in weapon.tags:
                return True
        return False

    def upgrade_weapon(self, weapon):
        if weapon.dmg_dice_size < self.upgrade_damage_die or 'finesse' not in weapon.tags:
            new_dmg_dice_size = max(weapon.dmg_dice_size, self.upgrade_damage_die)
            debug_print("Martial Arts applied to {}, {}->{}, finesse added".format(
                weapon.int_name, weapon.dmg_dice_size, new_dmg_dice_size))
            weapon.dmg_dice_size = new_dmg_dice_size
            weapon.add_tag('finesse')
            weapon.subtitles.append('Martial Arts')
        else:
            debug_print("Martial Arts not applied to {}".format(weapon.int_name))

    def first_pass(self):
        for weapon in self.owner.weapons.values():
            if self.is_monk_weapon(weapon):
                self.upgrade_weapon(weapon)

    def build_cr_factors_and_stat_block_entries(self):
        self.add_stat_block_entry(
            StatBlockEntry('Martial Arts', 'passive', 1,
                           'Damage scales to your level when using monk weapons.'))


# Currently, spelllists follow the convention 'domain_(name)'
CLERIC_DOMAINS = (
    'arcana', 'forge', 'grave', 'knowledge', 'life', 'light', 'nature', 'tempest', 'trickery', 'war'
)


class FeatureClericDomain(CharacterFeature):
    def __init__(self, owner, args_tup=()):
        super().__init__(owner)
        domain_name = args_tup[0]
        if not domain_name or domain_name == 'random':
            rnd_instance = random.Random(self.seed + 'chooserandomdomain')
            domain_name = rnd_instance.choice(CLERIC_DOMAINS)
        self.int_name = 'domain_' + domain_name
        self.domain_name = domain_name
        # This works because domain spell lists follow this naming convention
        # If that convention were broken, would need to re do this
        self.domain_spell_list = 'domain_' + domain_name
        if domain_name == 'war':
            self.add_sub_trait('parry')

    def first_pass(self):
        for feature in self.owner.character_features.values():
            if isinstance(feature, FeatureSpellcasting):
                feature.add_free_spell_list(self.domain_spell_list)

    def build_cr_factors_and_stat_block_entries(self):
        entry_title = '{} Domain'.format(self.domain_name.title())
        self.add_stat_block_entry(StatBlockEntry(
            entry_title, 'passive', 2,
            "Yay cleric domain."))


FEATURE_CLASS_REFERENCE = {
    'multiattack': FeatureMultiattack,
    'spellcasting': FeatureSpellcasting,
    'tinker': FeatureTinker,
    'dragonborn_feature': FeatureDragonborn,
    'martial_arts': FeatureMartialArts,
    'cleric_domain': FeatureClericDomain,
}
