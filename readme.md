FriendGaru's 5e NPC Generator


How to use:

import NPCGenerator from npcgen.py

call NPCGenerator.new_character() with appropriate parameters to get a Character instance.
a race choice, class choice, and hd are required.

call build_stat_block() on the Character to get a StatBlock instance

call plain_text() from the StatBlock or render the individual elements as desired


CR Calculations:

CR is really more of an art than a science, but my generator attempts to come up with reasonable values. 
My calculations are based off the guidelines in the DMG, but with some significant tweaks.
By the DMG, you basically get a creature's offensive rating by starting from the 'ideal' average damage per round
then adjusting up or down based on to hit or dc.
Behind the scenes, every character feature is basically asked if it wants to contribute a CRFactor to the final calculation.
CRFactors are mainly approximations of those offensive values.
Weapons and multiattack also contribute CRFactors.

For attacks, it's pretty straightforward, just get the damage and to hit and hand it over.
Abilities are weirder, because I don't really have a good way to get average damage from spells.
So, I cheat and just say CR is caster level - 3, then adjust up or down based on DC.
Honestly, this is probably better than the DMG method, since it takes into account non damaging spells
and healing much more reliably.
The CR Calc collects all these attack and ability factors and takes the best one to use for deciding the offensive CR rating.
If the best attack and ability ratings have a difference less than or equal to two, we bump the best up by one,
since that probably indicates we have a well rounded character.
The defensive side of the equation is much easier, since we have ready access to HP and AC.
The defensive side follows the DMG pretty closely.

Additionally, CR Factors can be offered up to boost the effective damage, hp, or ac of a character.
A 1d6 sneak attack character feature, for example, would just say 
"hey, treat this character like she does an extra 2 damage per round"
and that would be factored into the attacks.

Finally, the DMG says a creature's proficiency should be determined by CR,
but we're actually building creatures in the opposite direction.
So, my final tweak is after the combined defensive and offensive CR is grabbed,
compare it against the expected proficiency of the creature.
If it doesn't match the actual value, bump CR up or down a rank as appropriate.

The resulting value isn't perfect, of course, but it's pretty reasonable.

NOTE: HP multipliers for damage resistances has not yet been factored in.
It's on the todo list.



Character Features

