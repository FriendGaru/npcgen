import random, re
from npcgendata import *

# -1 - Nothing at all
# 0 - Errors only
# 1 - Basic operations completed
# 2 - The nitty gritty
DEBUG_LEVEL = 1

def rollDie(dieSize):
    return random.randint(1, dieSize)


# numDice is the total AFTER dropping lowest and highest
def rollDice(dieSize, numDice, dropLowest=0, dropHighest=0):
    diceToRoll = numDice + dropLowest + dropHighest
    dicePool = []
    for i in range(diceToRoll):
        dicePool.append(rollDie(dieSize))
    dicePool.sort()
    if dropHighest > 0:
        dicePool = dicePool[dropLowest:-dropHighest]
    else:
        dicePool = dicePool[dropLowest:]
    return sum(dicePool)


def dprint(message, requiredLevel=2):
    if DEBUG_LEVEL >= requiredLevel:
        print(message)

def numPlusser(num):
    if num >=0:
        return '+' + str(num)
    else:
        return str(num)


class NPCGenerator:
    def __init__(self, traitsDict=TRAITS, templatesClassDict=TEMPLATES_CLASS, templatesRaceDict=TEMPLATES_RACE,
                 armorsDict=ARMORS, weaponsDict=WEAPONS, weaponsLoadoutSetsDict=WEAPON_LOADOUT_SETS, armorLoadoutsSetsDict=ARMOR_LOADOUT_SETS,
                 spellsFile=SPELLS_FILE, autoSpellListsDict=SPELL_LISTS_AUTO, spellListsFixedDict=SPELL_LISTS_FIXED,
                 spellCasterProfilesDict=SPELLCASTER_PROFILES):

        self.templates = {}
        self.traits = {}
        self.weapons = {}
        self.armors = {}
        self.weaponLoadoutSets = {}
        self.armorLoadoutSets = {}

        self.buildTraits(traitsDict)
        self.buildTemplates(templatesClassDict, 'Class')
        self.buildTemplates(templatesRaceDict, 'Race')
        self.buildArmors(armorsDict)
        self.buildWeapons(weaponsDict)
        self.weaponLoadoutSets = self.buildLoadoutSetsDict(weaponsLoadoutSetsDict)
        self.armorLoadoutSets = self.buildLoadoutSetsDict(armorLoadoutsSetsDict)

        self.spells = {}
        self.spellLists = {}
        self.buildSpellsFromFile(spellsFile)
        self.buildAutoSpellLists(autoSpellListsDict)
        self.buildFixedSpellLists(spellListsFixedDict)
        self.spellcasterProfiles = {}
        self.buildSpellcasterProfiles(spellCasterProfilesDict)

    def buildTraits(self, traitsDict):
        for traitName, traitDict in traitsDict.items():
            newTrait = Trait(traitName, traitDict['displayName'], traitDict['traitType'], traitDict['traitText'],
                             traitDict.get('tags', {}))
            self.traits[traitName] = newTrait

    def giveTrait(self, character: 'Character', traitName):
        trait = self.traits[traitName]
        character.traits[traitName] = trait

        if 'giveArmor' in trait.tags:
            self.giveArmor(character, trait.tags['giveArmor'])

    def giveArmor(self, character, armorName):
        armor = self.armors[armorName]
        character.armors[armorName] = armor

    def giveWeapon(self, character, weaponName):
        weapon = self.weapons[weaponName]
        character.loadout.append(weapon)

    def buildTemplates(self, templatesDict, templateType=None):
        for templateName in templatesDict:
            templateDict = templatesDict[templateName]
            newTemplate = Template(templateName, templateDict.get('displayName'))

            newTemplate.priorityAttributes = templateDict.get('priorityAttributes')
            newTemplate.attributeBonuses = templateDict.get('attributeBonuses')
            newTemplate.baseStats = templateDict.get('baseStats')
            newTemplate.statBonuses = templateDict.get('statBonuses')
            newTemplate.skillsFixed = templateDict.get('skillsFixed')
            newTemplate.skillsRandom = templateDict.get('skillsRandom')
            newTemplate.saves = templateDict.get('saves')
            newTemplate.traits = templateDict.get('traits')
            newTemplate.armors = templateDict.get('armors')
            newTemplate.weapons = templateDict.get('weapons')
            newTemplate.weaponLoadoutSet = templateDict.get('weaponLoadoutSet')
            newTemplate.armorLoadoutSet = templateDict.get('armorLoadoutSet')
            newTemplate.spellCastingProfile = templateDict.get('spellCastingProfile')

            newTemplate.templateType = templateType

            self.templates[templateName] = newTemplate
            
    def buildArmors(self, armorsDict: dict):
        for armorName, armorParams in armorsDict.items():
            newArmor = Armor(armorName, *armorParams)
            self.armors[armorName] = newArmor
            
    def buildWeapons(self, weaponsDict: dict):
        for weaponName, weaponParams in weaponsDict.items():
            newWeapon = Weapon(weaponName, *weaponParams)
            self.weapons[weaponName] = newWeapon

    def buildLoadoutSetsDict(self, rawLoadoutSetsDict: dict):
        loadoutsSetsDict = {}
        for loadoutSetName, loadouts in rawLoadoutSetsDict.items():
            newLoadoutSet = LoadoutSet(loadoutSetName)
            newLoadoutSet.guaranteedLoadoutItems = loadouts[0]
            for loadout in loadouts[1:]:
                if type(loadout[0]) == int:
                    weight = loadout.pop(0)
                else:
                    weight = DEFAULT_LOADOUTSET_WEIGHT
                newLoadoutSet.addLoadout(loadout, weight)
            loadoutsSetsDict[loadoutSetName] = newLoadoutSet
        return loadoutsSetsDict

    def applyTemplate(self, character: 'Character', templateName, templateType=None):
        template = self.templates[templateName]

        if templateType == 'race':
            character.raceName = template.displayName
        elif templateType == 'class':
            character.className = template.displayName

        if template.priorityAttributes:
            character.priorityAttributes = template.priorityAttributes

        if template.attributeBonuses:
            for k, v in template.attributeBonuses.items():
                character.attributeBonuses[k] = v

        if template.traits:
            for trait in template.traits:
                self.giveTrait(character, trait)

        if template.armors:
            for armor in template.armors:
                self.giveArmor(character, armor)

        if template.skillsFixed:
            for skill in template.skillsFixed:
                character.skills[skill] = False

        if template.skillsRandom:
            chosenSkills = random.choices(template.skillsRandom[1:], k=template.skillsRandom[0])
            for skill in chosenSkills:
                character.skills[skill] = False

        if template.saves:
            for save in template.saves:
                character.saves.add(save)

        if template.weaponLoadoutSet:
            try:
                loadoutSet = self.weaponLoadoutSets[template.weaponLoadoutSet]
            except ValueError:
                dprint("Error! Couldn't find loadout " + template.weaponLoadoutSet, 0)
                return

            loadout = loadoutSet.getRandomLoadout()
            if 'shield' in loadout:
                character.hasShield = True
                loadout.remove('shield')
            else:
                character.hasShield = False

            for item in loadout:
                self.giveWeapon(character, item)
                
        if template.armorLoadoutSet:
            try:
                loadoutSet = self.armorLoadoutSets[template.armorLoadoutSet]
            except ValueError:
                dprint("Error! Couldn't find loadout " + template.armorLoadoutSet, 0)
                return

            loadout = loadoutSet.getRandomLoadout()
            if 'shield' in loadout:
                character.hasShield = True
                loadout.remove('shield')
            else:
                character.hasShield = False

            for item in loadout:
                self.giveArmor(character, item)

        if template.baseStats:
            for baseStatName, statVal in template.baseStats.items():
                character.stats[baseStatName] = statVal

        if template.spellCastingProfile:
            character.spellCastingProfile = self.spellcasterProfiles.get(template.spellCastingProfile)

    # Magic Stuff
    def addSpell(self, name, level, school, source, classes):
        self.spells[name] = (level, school, source, classes)

    @staticmethod
    def buildSpellFromLine(line):
        # example: "Wall of Fire","PHB","4th","Evocation","Druid, Sorcerer, Wizard"
        line = line.lower()
        # elements = re.search(r'^"([\w\d\s\'\-]*)","([\w\d\s]*)","([\w\d\s]*)","([\w\d\s]*)","([\w\d\s\,]*)"', line)
        elements = re.match(r'^"(.*?)","(.*?)","(.*?)","(.*?)","(.*?)"', line)
        name = str(elements.group(1))
        source = str(elements.group(2))
        level = SPELL_LEVEL_ORDINAL_TO_NUM.get(str(elements.group(3)))
        school = str(elements.group(4))
        classes = str(elements.group(5)).strip().split(',')
        for i in range(len(classes)):
            classes[i] = classes[i].strip()
        return name, level, school, source, classes

    def buildSpellsFromFile(self, fileName):
        file = open(fileName, 'r')
        for line in file:
            try:
                elements = self.buildSpellFromLine(line)
                self.addSpell(*elements)
            except:
                dprint('Error! Line: "' + line + '" is an invalid spell line.', 0)

    def buildAutoSpellLists(self, autoSpellListsDict):
        for spellListName, dictVals in autoSpellListsDict.items():
            spellList = []
            for spellName, spellVals in self.spells.items():
                reqClass = dictVals.get('class')
                if reqClass and reqClass not in spellVals[3]:
                    continue
                reqSchool = dictVals.get('school')
                if reqSchool and reqSchool != spellVals[1]:
                    continue
                spellList.append(spellName)
            self.spellLists[spellListName] = spellList

    def buildFixedSpellLists(self, fixedSpellListsDict):
        for spellListName, spellsSet in fixedSpellListsDict.items():
            newSpellsSet = set()
            for spell in spellsSet:
                if spell in self.spells:
                    newSpellsSet.add(spell)
                else:
                    dprint("Error! Spell: " + spell + " not in master spell list!")
            self.spellLists[spellListName] = newSpellsSet

    def buildSpellcasterProfiles(self, spellCasterProfilesDict):
        for profileName, vals in spellCasterProfilesDict.items():
            newProfile = SpellCasterProfile()
            slotsType = vals.get('slots')
            slots = CASTER_SPELL_SLOTS.get(slotsType)
            newProfile.slots = slots
            newProfile.cantrips = vals.get('cantrips')
            newProfile.readyStyle = vals.get('readyStyle')
            newProfile.castingStat = vals.get('castStat')

            # Val of spellLists dict is the weight
            spellListsDict = {}
            for entry in vals.get('spellLists'):
                if type(entry) == tuple or type(entry) == list:
                    spellListsDict[entry[1]] = entry[0]
                else:
                    spellListsDict[entry] = DEFAULT_SPELL_WEIGHT

            # Now, go through each list and give each spell its highest weight
            spellsDict = {}
            for spellListName, weight in spellListsDict.items():
                spellList = self.spellLists.get(spellListName)
                for spell in spellList:
                    if spell in spellsDict:
                        spellsDict[spell] = max(spellsDict[spell], weight)
                    else:
                        spellsDict[spell] = weight

            # Now we've got spells each with their profile specific weights
            # Organize them by level, we'll do [spell, weight] and use zip later
            spellsByLevel = [[], [], [], [], [], [], [], [], [], [], ]
            for spellName, weight in spellsDict.items():
                spellLevel = self.spells.get(spellName)[0]
                spellsByLevel[spellLevel].append([spellName, weight])

            newProfile.spells = spellsByLevel
            self.spellcasterProfiles[profileName] = newProfile


    def newCharacter(self, attributeRollMethod=DEFAULT_ROLL_METHOD, rerollsAllowed=0, minTotal=0,
                     allowSwapping=True, forceOptimize=False,
                     fixedRolls=[],
                     classTemplate=DEFAULT_CLASS, raceTemplate=DEFAULT_RACE,
                     hitDiceNum=DEFAULT_HITDICE_NUM, hitDiceSize=DEFAULT_HITDICE_SIZE,):
        newCharacter = Character()
        self.applyTemplate(newCharacter, raceTemplate, 'race')
        self.applyTemplate(newCharacter, classTemplate, 'class')
        newCharacter.rollAttributes(*ROLL_METHODS[attributeRollMethod],
                                    rerollsAllowed=rerollsAllowed, minTotal=minTotal,
                                    allowSwapping=allowSwapping, forceOptimize=forceOptimize,
                                    fixedRolls=fixedRolls)
        newCharacter.stats['hitDiceSize'] = hitDiceSize
        newCharacter.stats['hitDiceNum'] = hitDiceNum
        newCharacter.updateDerivedStats()
        newCharacter.chooseArmors()
        return newCharacter


class Character:
    def __init__(self):
        self.stats = {}
        for attr in STATS_ATTRIBUTES:
            self.stats[attr] = DEFAULT_ATTRIBUTE_VALUE
        for stat in STATS_BASE:
            self.stats[stat] = STATS_BASE[stat]

        self.attributeBonuses = {}
        self.priorityAttributes = []

        self.raceName = ''
        self.className = ''

        # Skills are stored as a dictionary, if the value is true that means the character has expertise
        self.skills = {}
        self.saves = set()

        self.armors = {}
        self.chosenArmor = None
        self.extraArmors = []

        self.loadout = []
        self.hasShield = False

        self.traits = {}

        self.spellCastingProfile = None
        self.spellCastingAbility = None

        self.updateDerivedStats()

    def rollAttributes(self, dieSize=6, numDice=3, dropLowest=0, dropHighest=0,
                       rerollsAllowed=0, minTotal=0, fixedRolls=[],
                       allowSwapping=True, forceOptimize=False,
                       applyAttributeBonuses=True,):

        attributeDict = {}

        # Apply reroll cap, so wacky high numbers aren't allowed
        rerollsAllowed = min(rerollsAllowed, REROLLS_CAP)
        rolls = []

        # Make initial rolls, reroll if the total is too low
        while rerollsAllowed >= 0:
            rerollsAllowed -= 1
            rolls = fixedRolls[:]
            totalRolled = sum(rolls)
            while len(rolls) < len(STATS_ATTRIBUTES):
                roll = rollDice(dieSize, numDice, dropLowest, dropHighest)
                rolls.append(roll)
                totalRolled += roll
            if totalRolled >= minTotal:
                break

        random.shuffle(rolls)
        for attribute in STATS_ATTRIBUTES:
            attributeDict[attribute] = rolls.pop()
        dprint(attributeDict)

        # forcedOptimize means the highest attributes will ALWAYS be the
        if allowSwapping:
            finalizedAttributes = set()
            for priorityAttribute in self.priorityAttributes:
                swapOptions = set(STATS_ATTRIBUTES)
                swapOptions.remove(priorityAttribute)
                swapOptions -= finalizedAttributes
                if not forceOptimize:
                    swapOptions -= set(self.priorityAttributes)
                dprint(swapOptions, 2)
                highestVal = max(*[attributeDict[x] for x in swapOptions], attributeDict[priorityAttribute])
                if highestVal > attributeDict[priorityAttribute]:
                    validSwaps = ([k for k, v in attributeDict.items() if k in swapOptions and v == highestVal])
                    swapChoice = random.choice(validSwaps)
                    attributeDict[priorityAttribute], attributeDict[swapChoice] = attributeDict[swapChoice], attributeDict[priorityAttribute]
                    dprint('Swapped: ' + priorityAttribute + ', ' + swapChoice, 2)
                finalizedAttributes.add(priorityAttribute)

        if applyAttributeBonuses:
            for attribute, bonus in self.attributeBonuses.items():
                attributeDict[attribute] += bonus

        # Set stats
        for attribute, val in attributeDict.items():
            self.stats[attribute] = val

    def updateDerivedStats(self):
        # stat mods
        for attribute in STATS_ATTRIBUTES:
            # stat modifiers = stat // 2 - 5
            self.stats[attribute + 'Mod'] = self.stats[attribute] // 2 - 5
        # Hit Points
        self.stats['hitPoints'] = (self.stats['hitDiceNum'] * self.stats['hitDiceSize']) // 2 + self.stats[
            'hitDiceNum'] * self.stats['conMod'] + self.stats['hitPointsExtra']
        # Proficiency
        self.stats['proficiency'] = self.stats['hitDiceNum'] // 5 + 2 + self.stats['proficiencyExtra']
        # DCs (all DCs are 8 + statMod + proficiency)
        for attribute in STATS_ATTRIBUTES:
            self.stats[attribute + 'DC'] = 8 + self.stats[attribute + 'Mod'] + self.stats['proficiency']
        # Attack bonus
        for attribute in STATS_ATTRIBUTES:
            self.stats[attribute + 'Attack'] = self.stats['proficiency'] + self.stats[attribute + 'Mod']
        # SpellCasting
        if self.spellCastingProfile:
            self.spellCastingAbility = self.spellCastingProfile.generateSpellCastingAbility(self.getStat('hitDiceNum'))
        # Speed
        self.stats['speedWalkFinal'] = self.stats['speedWalk']
        self.stats['speedFlyFinal'] = self.stats['speedFly']
        self.stats['speedSwimFinal'] = self.stats['speedSwim']
        self.stats['speedBurrowFinal'] = self.stats['speedBurrow']

    def getStat(self, stat):
        return self.stats[stat]

    def chooseArmors(self):
        allArmors = list(self.armors.values())
        regularArmors = []
        extraArmors = []
        # Separate armors into regular and extras
        for armor in allArmors:
            if 'extra' in armor.tags:
                extraArmors.append(armor)
            else:
                regularArmors.append(armor)
        validChoices = []
        bestAC = 0
        for armor in regularArmors:
            armorAC = armor.getAC(self)
            if armorAC > bestAC:
                validChoices = [armor, ]
                bestAC = armorAC
            elif armorAC == bestAC:
                validChoices.append(armor)
        # Need to know the regular armor AC before determining if any extras are worthwhile
        validExtras = []
        for armor in extraArmors:
            armorAC = armor.getAC(self)
            if armorAC > bestAC:
                validExtras.append(armor)
        if len(validExtras) == 0:
            validExtras = None

        #check for preferred armor
        preferredArmorFound = False
        for armor in validChoices:
            if 'preferred' in armor.tags:
                preferredArmorFound = True
        if preferredArmorFound:
            newValidChoices = []
            for armor in validChoices:
                if 'preferred' in armor.tags:
                    newValidChoices.append(armor)
            validChoices = newValidChoices

        self.chosenArmor = random.choice(validChoices)
        self.extraArmors = validExtras

    def display(self):
        outstring = ''
        # Race and Class
        outstring += '{} {}\n'.format(self.raceName, self.className)
        # Armor
        outstring += 'AC: ' + self.chosenArmor.sheetDisplay(self)
        if self.extraArmors:
            for armor in self.extraArmors:
                outstring += ', ' + armor.sheetDisplay(self)
        outstring += '\n'

        # HP
        outstring += 'Hit Points: {}({}d{}+{})\n'.format(self.getStat('hitPoints'), self.getStat('hitDiceNum'),
                                                         self.getStat('hitDiceSize'),
                                                         self.getStat('hitDiceNum') * self.getStat('conMod'))
        # Size
        outstring += 'Size: {}\n'.format(self.getStat('size'))
        # Speed
        outstring += 'Speed: {}ft.'.format(self.getStat('speedWalkFinal'))
        if self.getStat('speedFlyFinal') > 0:
            outstring += ', fly {}ft.'.format(self.getStat('speedFlyFinal'))
        if self.getStat('speedSwimFinal') > 0:
            outstring += ', swim {}ft.'.format(self.getStat('speedSwimFinal'))
        if self.getStat('speedBurrowFinal') > 0:
            outstring += ', burrow {}ft.'.format(self.getStat('speedBurrowFinal'))
        outstring += '\n'
        # Proficiency
        outstring += 'Proficiency: +{}\n'.format(self.getStat('proficiency'))
        # Attributes
        for attr in STATS_ATTRIBUTES:
            outstring += '{} {}({}) '.format(attr.upper(), self.getStat(attr),
                                             '{0:+d}'.format(self.getStat(attr + 'Mod')))
        outstring += '\n'
        # Saves
        if len(self.saves) > 0:
            outstring += 'Saves: '
            # A little more complicated, but this will put saves in the same order as attributes
            savesList = []
            for attribute in STATS_ATTRIBUTES:
                if attribute in self.saves:
                    saveVal = self.stats[attribute + 'Mod'] + self.stats['proficiency']
                    valStr = ''
                    if saveVal >= 0:
                        valStr = ' +' + str(saveVal)
                    else:
                        valStr = ' ' + str(saveVal)
                    savesList.append(ATTRIBUTES_FULL[attribute] + valStr)
            outstring += ', '.join(savesList) + '\n'

        # Skills
        if len(self.skills) > 0:
            outstring += 'Skills: '
            skillsList = []
            for skill in SKILLS_ORDERED:
                if skill in self.skills:
                    skillAttribute = SKILLS[skill]
                    skillVal = self.stats[skillAttribute + 'Mod'] + self.stats['proficiency']
                    # check for expertise
                    if self.skills[skill]:
                        skillVal += self.stats['proficiency']
                    if skillVal >= 0:
                        valStr = ' +' + str(skillVal)
                    else:
                        valStr = ' ' + str(skillVal)
                    skillsList.append(skill.capitalize() + valStr)
            outstring += ', '.join(skillsList) + '\n'
        # CR
        # Languages
        # Traits
        for traitName in self.traits:
            trait = self.traits[traitName]
            traitstring = trait.display(self) + "\n"
            outstring += traitstring
        # Spellcasting
        if self.spellCastingAbility:
            outstring += self.spellCastingAbility.display(self) + '\n'
        # Attacks
        for item in self.loadout:
            outstring += item.sheetDisplay(self) + '\n'
        return outstring


class Trait:
    def __init__(self, intName, displayName, traitType, text, tags={}):
        self.intName = intName
        self.displayName = displayName
        self.traitType = traitType
        self.text = text
        self.tags = tags

    def toString(self):
        return self.traitType + self.displayName + self.text

    def display(self, owner):
        outstring = self.displayName + '. ' + self.text.format(**owner.stats)
        return outstring


class Template:
    def __init__(self, intName, displayName):
        self.intName = intName
        self.displayName = displayName
        self.templateType = None
        self.attributeBonuses = None
        self.statBonuses = None
        self.baseStats = None
        self.priorityAttributes = None
        self.skillsFixed = None
        self.skillsRandom = None
        self.saves = None
        self.traits = None
        # self.armors = None
        self.weaponLoadoutSet = None
        self.armorLoadoutSet = None
        self.spellCastingProfile = None


class Armor:
    def __init__(self, intName, displayName, baseAC, armorType, minStr, stealthDisadvantage, tags):
        self.intName = intName
        self.displayName = displayName
        self.baseAC = baseAC
        self.armorType = armorType
        self.minStr = minStr
        self.stealthDisadvantage = stealthDisadvantage
        self.tags = tags

    def isExtra(self):
        return 'extra' in self.tags

    def getAC(self, owner):
        baseAC = self.baseAC
        totalAC = 0
        if self.armorType == 'light':
            totalAC = baseAC + owner.getStat('dexMod')
        elif self.armorType == 'medium':
            # Can add case here for medium armor mastery
            totalAC = baseAC + min(2, owner.getStat('dexMod'))
        elif self.armorType == 'heavy':
            totalAC = baseAC
        else:
            dprint('Armor: ' + self.intName + ' has invalid armor type: ' + self.armorType, 0)

        if owner.hasShield and 'noShield' not in self.tags:
            totalAC += 2

        return totalAC

    def speedPenalty(self, owner):
        # can add case for dwarf
        if self.armorType == 'heavy' and self.minStr < owner.getStat('str'):
            return -10
        else:
            return 0

    def stealthPenalty(self, owner):
        # can add case for medium armor mastery
        return self.stealthDisadvantage

    def __repr__(self):
        return self.intName

    def sheetDisplay(self, owner):
        outstring = str(self.getAC(owner)) + ' (' + self.displayName
        if owner.hasShield:
            outstring += ', with shield'
        outstring += ')'
        return outstring


class Weapon:
    def __init__(self, intName, displayName, dmgDiceNum, dmgDiceSize, damageType,
                 weaponType, shortRange, longRange, tags, numTargets=DEFAULT_NUM_TARGETS):
        self.intName = intName
        self.displayName = displayName
        self.dmgDiceNum = dmgDiceNum
        self.dmgDiceSize = dmgDiceSize
        self.damageType = damageType
        self.weaponType = weaponType
        self.rangeShort = shortRange
        self.rangeLong = longRange
        self.tags = tags
        self.numTargets = numTargets

    def getToHit(self, owner):
        ownerStr = owner.getStat('strMod')
        ownerDex = owner.getStat('dexMod')
        ownerProf = owner.getStat('proficiency')
        attackStat = 0
        if self.weaponType == 'm':
            if 'finesse' in self.tags:
                attackStat = max(ownerStr, ownerDex)
            else:
                attackStat = ownerStr
        elif self.weaponType == 'r':
            if 'thrown' in self.tags:
                attackStat = max(ownerStr, ownerDex)
            else:
                attackStat = ownerDex
        return attackStat + ownerProf

    def getDamage(self, owner, useVersatile=False):
        ownerStr = owner.getStat('strMod')
        ownerDex = owner.getStat('dexMod')
        attackStat = 0
        if self.weaponType == 'm':
            if 'finesse' in self.tags:
                attackStat = max(ownerStr, ownerDex)
            else:
                attackStat = ownerStr
        elif self.weaponType == 'r':
            if 'thrown' in self.tags:
                attackStat = max(ownerStr, ownerDex)
            else:
                attackStat = ownerDex
        # (numDice, diceSize, dmgBonus, damgType, avgDmg)
        if useVersatile:
            dmgDiceNum, dmgDiceSize = self.tags['versatile'][0], self.tags['versatile'][1]
        else:
            dmgDiceNum, dmgDiceSize = self.dmgDiceNum, self.dmgDiceSize
        avgDmg = dmgDiceSize / 2 * dmgDiceNum + attackStat
        return int(avgDmg), dmgDiceNum, dmgDiceSize, attackStat, self.damageType, avgDmg

    def sheetDisplay(self, owner):
        outstring = self.displayName + '. '
        isMelee = self.weaponType == 'm'
        isRanged = self.weaponType == 'r' or 'thrown' in self.tags
        if isMelee and isRanged:
            outstring += 'Melee or ranged weapon attack: '
        elif isMelee:
            outstring += 'Melee weapon attack: '
        elif isRanged:
            outstring += 'Ranged weapon attack: '

        toHit = self.getToHit(owner)
        if toHit >= 0 : outstring += '+'
        if toHit < 0 : outstring += '-'
        outstring += str(toHit) + ' to hit, '

        if isMelee and isRanged:
            if 'reach' in self.tags:
                outstring += '{} or range {}/{} ft., '.format(WEAPON_REACH_W_BONUS, self.rangeShort, self.rangeLong)
            else:
                outstring += '{} or range {}/{} ft., '.format(DEFAULT_WEAPON_REACH, self.rangeShort, self.rangeLong)
        elif isMelee:
            if 'reach' in self.tags:
                outstring += WEAPON_REACH_W_BONUS + ', '
            else:
                outstring += DEFAULT_WEAPON_REACH + ', '
        elif isRanged:
            outstring += 'range {}/{} ft., '.format(self.rangeShort, self.rangeLong)

        if self.numTargets == 1:
            outstring += 'one target. '
        else:
            outstring += NUM2WORD.get(self.numTargets) + ' targets. '
        ##
        dmgTup = self.getDamage(owner)
        if dmgTup[3] < 0:
            outstring += 'Hit: {}({}d{} - {}) {} damage'.format(dmgTup[0], dmgTup[1], dmgTup[2],
                                                                abs(dmgTup[3]), dmgTup[4])
        else:
            outstring += 'Hit: {}({}d{} + {}) {} damage'.format(*dmgTup)

        # Check for versatile, which increases damage with two hands.
        if isMelee and 'versatile' in self.tags:
            dmgTup = self.getDamage(owner, useVersatile=True)
            if dmgTup[3] < 0:
                outstring += ' or {}({}d{} - {}) {} damage if used with two hands'.format(dmgTup[0], dmgTup[1], dmgTup[2],
                                                                    abs(dmgTup[3]), dmgTup[4])
            else:
                outstring += ' or {}({}d{} + {}) {} damage if used with two hands'.format(*dmgTup)
        outstring += '.'
        return outstring
    

class LoadoutSet:
    def __init__(self, internalName=''):
        self.internalName = internalName
        self.guaranteedLoadoutItems = []
        self.loadouts = []
        self.weights = []

    def __repr__(self):
        return '<' + self.internalName + ', ' + str(self.loadouts) + ', ' + str(self.weights) + '>'

    def addLoadout(self, loadout, weight=DEFAULT_LOADOUTSET_WEIGHT):
        self.loadouts.append(loadout)
        self.weights.append(weight)

    def getRandomLoadout(self):
        return self.guaranteedLoadoutItems + random.choices(self.loadouts, self.weights)[0]


class SpellCasterProfile:
    def __init__(self, slots=None, cantrips=None, readyStle='prepared', castingStat='int'):
        self.slots = slots
        self.cantrips = cantrips
        self.spells = [[], [], [], [], [], [], [], [], [], [], ]
        self.readyStyle = readyStle
        self.castingStat = castingStat

    def addSpell(self, spellName, spellLevel, weight):
        if spellName in self.spells[spellLevel]:
            self.spells[spellLevel][spellName] = max(weight, self.spells[spellLevel][spellName])
        else:
            self.spells[spellLevel][spellName] = weight

    def getRandomSpells(self, spellLevel, num):
        spellsWeights = zip(*self.spells[spellLevel])
        spells = list(next(spellsWeights))
        weights = list(next(spellsWeights))
        if num > len(spells):
            return spells
        outSpells = []
        while len(outSpells) < num:
            choiceIndex = random.choices(range(len(spells)), weights)[0]
            outSpells.append(spells[choiceIndex])
            del(spells[choiceIndex])
            del(weights[choiceIndex])
        return outSpells

    def generateSpellCastingAbility(self, casterLevel, useSlotsForReadiedSpells=True):
        casterLevel = min(casterLevel, 20)
        newAbility = SpellCastingAbility(self.readyStyle, self.castingStat, casterLevel)
        newAbility.slots = self.slots[casterLevel]
        for spellLevel in range(0, 10):
            newAbility.spellsReady[spellLevel] = self.getRandomSpells(spellLevel, newAbility.slots[spellLevel])
        return newAbility


class SpellCastingAbility:
    def __init__(self, readyStyle='known', castStat='int', casterLevel=1):
        # NPCs generally either have spells 'prepared' or 'known'
        self.readyStyle = readyStyle
        # A list with the index corresponding to the spell level, 0 is a dummy for cantrips
        self.slots = [-1, 2, 1, 0, 0, 0, 0, 0, 0, 0, ]
        # A list of lists, index corresponds to the list of spells know for each level, 0 for cantrips
        self.spellsReady = [[], [], [], [], [], [], [], [], [], [], ]
        # Which stat is used for casting
        self.castStat = castStat
        self.casterLevel = casterLevel

    def display(self, owner):
        # Header part
        outline = "Spellcasting. This character is a {}-level spellcaster. " \
                  "Its spellcasting ability is {} (spell save DC {}, {} to hit with spell attacks). " \
                  "It has the following spells {}:"\
                .format(NUM_TO_ORDINAL[self.casterLevel],
                        ATTRIBUTES_FULL[self.castStat], owner.getStat(self.castStat + 'DC'),
                        numPlusser(owner.getStat(self.castStat + "Attack")), self.readyStyle) + '\n'
        # Cantrips
        if len(self.spellsReady[0]) > 0:
            outline += 'Cantrips (at-will): ' + ', '.join(self.spellsReady[0]) + '\n'
        for i in range(1, 9):
            if len(self.spellsReady[i]) > 0:
                # Pluralize 'slot' or not
                if self.slots[i] == 1:
                    outline += '{} level ({} slot): '.format(NUM_TO_ORDINAL[i], self.slots[i])
                else:
                    outline += '{} level ({} slots): '.format(NUM_TO_ORDINAL[i], self.slots[i])
                outline += ', '.join(self.spellsReady[i]) + '\n'
        return outline


