import random
from .npcgen_constants import *
from .npcgen_content import ContentSource, SpellCasterProfile
from .npcgen_main import CharacterFeature, Character, StatBlockEntry, increment_from_hd, \
    debug_print, num_plusser, CRFactor, nice_list, EquippedWeapon


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
        elif self.get_caster_level() <= 0:
            return 0
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
            main_entry = self.get_main_stat_block_entry()
            if main_entry:
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
        if args_tup[0] == 'random':
            self.lineage_type = random.Random(self.seed + 'dragonbornrandom')\
                .choice(sorted(list(FEATURE_DRAGONBORN_CHART.keys())))
        else:
            self.lineage_type = args_tup[0]

    def first_pass(self):
        self.owner.add_race_prefix(self.lineage_type)
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
        domain_arg = args_tup[0]
        if not domain_arg or domain_arg == 'random':
            self.domain_name = random.Random(self.seed + 'clericdomain').choice(CLERIC_DOMAINS)
        else:
            self.domain_name = domain_arg
        self.int_name = 'domain_' + self.domain_name
        # This works because domain spell lists follow this naming convention
        # If that convention were broken, would need to re do this
        self.domain_spell_list = 'domain_' + self.domain_name
        if self.domain_name == 'war':
            self.add_sub_trait('parry')

    def first_pass(self):
        self.owner.add_class_prefix(self.domain_name)
        for feature in self.owner.character_features.values():
            if isinstance(feature, FeatureSpellcasting):
                feature.add_free_spell_list(self.domain_spell_list)

    def build_cr_factors_and_stat_block_entries(self):
        entry_title = '{} Domain'.format(self.domain_name.title())
        self.add_stat_block_entry(StatBlockEntry(
            entry_title, 'passive', 2,
            "Yay cleric domain."))


PALADIN_OATHS = (
    'ancients', 'conquest', 'crown', 'devotion', 'redemption', 'vengeance'
)


class FeaturePaladinOath(CharacterFeature):
    def __init__(self, owner, args_tup=()):
        super().__init__(owner)
        oath_arg = args_tup[0]
        if not oath_arg or oath_arg == 'random':
            self.oath_name = random.Random(self.seed + 'paladinoath').choice(PALADIN_OATHS)
        else:
            self.oath_name = oath_arg
        self.int_name = 'oath_' + self.oath_name
        # This works because oath spell lists follow this naming convention
        # If that convention were broken, would need to re do this
        self.oath_spell_list = 'oath_' + self.oath_name

        self.oath_title = self.oath_name
        if self.oath_name in ('crown', 'ancients'):
            self.oath_title = 'of the ' + self.oath_title
        else:
            self.oath_title = 'of ' + self.oath_title

    def first_pass(self):
        self.owner.add_class_suffix(self.oath_title)
        for feature in self.owner.character_features.values():
            if isinstance(feature, FeatureSpellcasting):
                feature.add_free_spell_list(self.oath_spell_list)

    def build_cr_factors_and_stat_block_entries(self):
        entry_title = 'Oath {}'.format(self.oath_title).title()
        self.add_stat_block_entry(StatBlockEntry(
            entry_title, 'passive', 2,
            "Yay oath."))


FEATURE_CLASS_REFERENCE = {
    'multiattack': FeatureMultiattack,
    'spellcasting': FeatureSpellcasting,
    'tinker': FeatureTinker,
    'dragonborn_feature': FeatureDragonborn,
    'martial_arts': FeatureMartialArts,
    'cleric_domain': FeatureClericDomain,
    'paladin_oath': FeaturePaladinOath
}