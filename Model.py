import pygame
import os
import math
import random

BASE = 1.11842691472    # fifth root of 1.75 AKA 5 points equates to 75% improvement (assuming 1.0 scaling)

# helper functions
def getObject(dict, name):
    if name in dict.keys():
        return dict[name]
    return None

class Ability():

    def __init__(self, file):
        # initialize all the things
        self.name = "default"
        self.targetingMode = "self"
        self.travelIcon = "none"

        # scalings, need one for each attribute (set to 0 for no relevance)
        # scaling values are to adjust effectiveness of each attribute on a given ability
        # intended mostly to distinguish abilities which want scaling or are fine with less investment
        # also having 0.0 scale implies this attribute has no influence, can be useful info
        # defense scalings, could be fun for some cases, usually not used
        self.scaleLife = 1.0
        self.scaleToughness = 1.0
        self.scaleEvasion = 1.0
        self.scaleMovement = 1.0
        self.scaleMana = 1.0
        # ability attributes
        self.scalePotency = 1.0
        self.scaleDuration = 1.0
        self.scaleApplication = 1.0
        self.scaleSpeed = 1.0
        self.scaleEfficiency = 1.0
        self.scaleRecovery = 1.0
        self.scaleSubtlety = 1.0

        # ability effect values
        self.baseDamage = 0.0  # can switch to negative for healing effects
        # duration beyond 0.5, for lingering effects. Leave at 0 for standard damage dealers
        self.baseDuration = 0.0  # should probably standardize the tick rate of DoT effects, so no tick rate value needed
        # ideally all effects have a half-second delay between arriving at their destination and activating
        # so we'll need animation frames to blend between projectile and full effect TODO LATER, could just have start of landed animation look like the travel icon
        self.baseRadius = 1.0
        self.baseSpeed = 0.1
        self.baseCost = 0.0
        self.baseCooldown = 0.0
        self.baseSoundRadiusMultiplier = 5.0  # multiply by final radius to get noise range

        self.evasionEffect = 1.0
        self.armorEffect = 1.0
        # TODO going to need slightly more complicated values for buffs and debuffs, can add as they come up

        self.shape = "circle"  # circle and line only for now
        self.team = "friendly"  # friendly (buffs), enemy (damage), all (environment changers)
        self.volatile = False

        self.animation = "none"
        self.draws = []
        self.maxRange = 0.0


        # read file with ability name for other values
        infile = open(file, "r")
        for line in infile:
            mySplit = line.split("=")
            if len(mySplit) == 2:
                # valid line
                var = mySplit[0]
                val = str(mySplit[1]).strip()
                # a lot of if's
                if var == "name":
                    self.name = val
                if var == "targetingMode":
                    self.targetingMode = val
                if var == "travelIcon":
                    self.travelIcon = val
                if var == "scaleLife":
                    self.scaleLife = float(val)
                if var == "scaleToughness":
                    self.scaleToughness = float(val)
                if var == "scaleEvasion":
                    self.scaleEvasion = float(val)
                if var == "scaleMovement":
                    self.scaleMovement = float(val)
                if var == "scaleMana":
                    self.scaleMana = float(val)
                if var == "scalePotency":
                    self.scalePotency = float(val)
                if var == "scaleDuration":
                    self.scaleDuration = float(val)
                if var == "scaleApplication":
                    self.scaleApplication = float(val)
                if var == "scaleSpeed":
                    self.scaleSpeed = float(val)
                if var == "scaleEfficiency":
                    self.scaleEfficiency = float(val)
                if var == "scaleRecovery":
                    self.scaleRecovery = float(val)
                if var == "scaleSubtlety":
                    self.scaleSubtlety = float(val)
                if var == "baseDamage":
                    self.baseDamage = float(val)
                if var == "baseDuration":
                    self.baseDuration = float(val)
                if var == "baseRadius":
                    self.baseRadius = float(val)
                if var == "baseSpeed":
                    self.baseSpeed = float(val)
                if var == "baseCost":
                    self.baseCost = float(val)
                if var == "baseCooldown":
                    self.baseCooldown = float(val)
                if var == "baseSoundRadiusMultiplier":
                    self.baseSoundRadiusMultiplier = float(val)
                if var == "shape":
                    self.shape = val
                if var == "team":
                    self.team = val
                if var == "animation":
                    self.animation = val
                if var == "volatile":
                    self.animation = bool(val)
                if var == "maxRange":
                    self.maxRange = float(val)
                if var == "evasionEffect":
                    self.evasionEffect = float(val)
                if var == "armorEffect":
                    self.armorEffect = float(val)

        infile.close()
        if self.animation != "none":
            # load images from animation folder into draws
            for img in os.listdir("Assets/Animations/"+self.animation):
                self.addDraw("Assets/Animations/"+self.animation+"/"+img)
                #print("Loading", img, "from", self.animation, "for ability", self.name)
        #print("Initalized ability", self.name)

    def addDraw(self, draw):
        #print("Adding", draw, "for", self.name)
        self.draws.append(draw)
        #print("Total", self.draws)

    def cast(self, caster, targetX, targetY):
        # actually cast the ability
        if not caster.alive:
            return False
        #print(caster.name, "cast", self.name)
        # TODO cost mana and activate cooldown on caster
        manaCost = self.baseCost/(BASE**(caster.efficiency*self.scaleEfficiency))
        if caster.currentMana < manaCost:
            return False
        caster.currentMana -= manaCost
        # TOOD implement
        # need to create a drawable which contains all needed info (link to caster for dynamic attributes)
        # target coords always given, not always needed (mouse coords at time of cast)
        if self.targetingMode == "self":
            targetX = caster.locX
            targetY = caster.locY
        if self.maxRange != 0.0:
            # check if target pos is in range
            dist = math.sqrt((caster.locX-targetX)**2+(caster.locY-targetY)**2)
            if dist > self.maxRange:
                return False
        payload = self.name
        return Projectile(self.travelIcon, caster.locX, caster.locY, caster, targetX, targetY, self.baseSpeed, self.scaleSpeed, self.volatile, payload)

    def trigger(self, caster, targetX, targetY, map):
        # actually trigger the effects of the ability at target location
        # this part can vary wildly based on the flags in the ability settings
        #validTargets = []
        # find all targets within spell radius (or whatever shape its using) who are characters not on the team of the caster
        # with these targets, apply damage and other effects according to number scalings
        #print("Triggered", self.name)
        # regardless of the other effects above, we need to draw the spell going off
        actualSize = int(self.baseRadius * BASE ** (caster.application * self.scaleApplication))
        if self.baseDuration == 0.0:
            # for now just return a drawable with the first thing in the animation, scale based on caster radius
            #baseDraw = pygame.image.load("Assets/Animations/"+self.animation+"/"+self.draws[0])
            #scaledDraw = pygame.transform.scale(baseDraw, (actualSize, actualSize))
            #print("Draws", self.draws)
            searchRadius = self.baseRadius * BASE ** (caster.application * self.scaleApplication)
            validTargets = map.findValidTargets(targetX, targetY, searchRadius, self.team, caster.team)
            for target in validTargets:
                target.damage(self.baseDamage * BASE ** (caster.potency * self.scalePotency), self.evasionEffect, self.armorEffect)
            # draw it!
            triggerDraw = Drawable(self.draws[0], targetX, targetY)
            triggerDraw.setScale(actualSize)
            triggerDraw.setLimit(0.3)   # use default 0.3 second animation time
            return triggerDraw
        else:
            # need to make a special kind of drawable subclass, which contains a reference to caster and ability data, something which inherits from both ability and drawable?
            triggerDraw = Effect(str(self.draws[0]), targetX, targetY, caster, self, map)
            return triggerDraw

class Drawable():
    def __init__(self, dat, x, y, mode="img"):
        if mode == "img":      # TODO reconfigure img based constructor, specifically the scale and size fields
            self.scale = 40
            self.age = 0.0
            self.limit = None
            #img = "Assets/testChar.png"
            #print("Loading image from", os.getcwd(), "its", img)
            self.alpha = False  # TODO store loaded images from animation folder as specific vars (no loading after initialization, could inherit loaded images from Loadable)
            # TODO reconfigure drawable use cases to always use a loadable which has preloaded and converted images
            self.image = pygame.image.load(dat).convert()
            self.locX = x
            self.locY = y
            self.boundX, self.boundY = self.image.get_size()
            self.oldX = 0
            self.oldY = 0

            # things that need to be set for consistency since this is a shared constructor  TODO standardize usage (having multiple constructors is a pain to maintain, at least in this form)
            self.roof = False
            self.vulnerable = False
            self.collidable = False
            self.team = "None"
            self.animation = "None"
            self.baseLife = 1.0
            self.baseMana = 0.0
            self.baseToughness = 1.0
            self.baseEvasion = 1.0
            self.baseMovement = 0.0
        elif mode == "load":
            # use a loadable to fill values instead
            assert isinstance(dat, Loadable), "Drawable given non-loadable data"
            self.scale = 1.0
            self.age = 0.0
            self.limit = None
            self.locX = x
            self.locY = y
            self.oldX = x
            self.oldY = y

            # fields from loadable that are definitely here
            self.baseLife = dat.baseLife
            self.baseMana = dat.baseMana
            self.baseToughness = dat.baseToughness
            self.baseEvasion = dat.baseEvasion
            self.baseMovement = dat.baseMovement
            self.animation = dat.animation
            self.vulnerable = dat.vulnerable
            self.team = dat.team
            self.collidable = dat.collidable
            self.roof = dat.roof
            self.alpha = dat.alpha
            imgLocation = "None"
            if self.animation != "None":
                self.image = "Assets/Animations/"+self.animation+"/Base.png"
            else:
                self.image = dat.image
            if self.alpha:
                self.image = pygame.image.load(imgLocation).convert_alpha()
            else:
                self.image = pygame.image.load(imgLocation).convert()
            self.boundX, self.boundY = self.image.get_size()

    def setScale(self, scal):
        scal = int(scal)
        self.scale = scal
        self.image = pygame.transform.scale(self.image, (scal*2, scal*2))
        self.boundX, self.boundY = self.image.get_size()
    def setLimit(self, limit):
        self.limit = limit
        self.age = 0.0

    def setImage(self, filename):
        # given filename, load image and set scale
        if self.alpha:
            self.image = pygame.image.load(filename).convert_alpha()
        else:
            self.image = pygame.image.load(filename).convert()
        self.setScale(self.scale)

    def move(self, newX, newY):
        self.oldX = self.locX
        self.oldY = self.locY
        self.locX = int(newX)
        self.locY = int(newY)    # TODO success states?

class Effect(Drawable):
    def __init__(self, img, x, y, caster, ability, map):
        super().__init__(img, x, y)
        self.setScale(ability.baseRadius*BASE**(caster.application*ability.scaleApplication))
        self.caster = caster
        self.ability = ability
        self.setLimit(ability.baseDuration*BASE**(caster.duration*ability.scaleDuration))
        self.map = map
        self.time = 0.0
    def tick(self, frameTime):
        # given an amount of time, deal damage to relevant characters within ability radius accordingly
        validTargets = self.map.findValidTargets(self.locX, self.locY, self.scale, self.ability.team, self.caster.team)
        for target in validTargets:
            target.damage(frameTime*self.ability.baseDamage*BASE**(self.caster.potency*self.ability.scalePotency))
        # also apply slow, speed, whatever other continuous effects here    TODO

        # also a good time to switch images
        self.time += frameTime  # TODO animation speed modifier, 2.0 means animation cycle will play two times per second
        # use time % len(draws) to determine which image to use
        drawNum = int(self.time % len(self.ability.draws))
        self.setImage(self.ability.draws[drawNum])


class Projectile(Drawable):
    def __init__(self, img, x, y, caster, targetX, targetY, speed, scaleSpeed, volatile, payload):
        self.targetX = -1
        self.targetY = -1
        self.speed = 0.1
        self.scaleSpeed = 0.0
        self.caster = "Jeff"
        self.volatile = False
        self.payload = "default"  # ability to be activated on landing
        super().__init__(img, x, y)
        self.targetX = targetX
        self.targetY = targetY
        self.speed = speed
        self.scaleSpeed = scaleSpeed
        self.payload = payload
        self.caster = caster
        self.volatile = volatile

    def moveProj(self, time):
        # return false if proj keeps moving, true if detonating
        actualSpeed = self.speed * time * BASE ** (self.caster.speed * self.scaleSpeed)
        #print("Proj",self.caster.speed)
        deltaX = self.targetX - self.locX
        deltaY = self.targetY - self.locY
        targetDist = math.sqrt(deltaX**2+deltaY**2)
        # check if at destination this frame
        if targetDist <= actualSpeed:
            # you have arrived at your destination
            self.move(self.targetX, self.targetY)
            #self.locX = self.targetX
            #self.locY = self.targetY
            # trigger ability effects at target location
            return True
        else:
            # split actualSpeed up into X and Y components, add to locX and locY accordingly
            self.locX += deltaX/targetDist * actualSpeed
            self.locY += deltaY/targetDist * actualSpeed

        # check if colliding this frame (only for volatile)
        if self.volatile:
            # collision check time! TODO implement
            pass
        return False



class Character(Drawable):

    def __init__(self, loaded, x, y):
        # loaded is a Loadable, with all data needed to fill in a character's data minus specific position (hence x y args)
        assert isinstance(loaded, Loadable), "Character creation failed, loaded wrong type"

        self.animation = loaded.animation

        if self.animation == "None":
            img = loaded.image
            self.baseImage = img
            self.evadeImage = img
            self.leftImage = img
            self.rightImage = img
            self.deadImage = img
        else:   # TODO cleanup hardcoded directories
            self.baseImage = "Assets/Animations/"+self.animation+"/Base.png"
            img = self.baseImage
            self.evadeImage = "Assets/Animations/"+self.animation+"/Evaded.png"
            self.leftImage = "Assets/Animations/"+self.animation+"/Left.png"
            self.rightImage = "Assets/Animations/"+self.animation+"/Right.png"
            self.deadImage = "Assets/Animations/"+self.animation+"/Dead.png"
        self.evadeReset = 0.2   # how long to show evade image before switching back
        self.recentEvade = self.evadeReset  # how long has it been since the last evade, defaults to max render time

        super().__init__(img, x, y)

        self.name = loaded.name
        self.team = loaded.team
        # items
        # need both equipped and owned
        self.inventory = []  # item list, item objects store which slot they go to
        self.equipped = {}  # dict keyed by gear slot

        # abilities
        self.abilities = {}  # dict keyed by casting slot   # TODO implement loadout options in loadable file

        # base stats
        self.baseLife = loaded.baseLife
        self.baseMana = loaded.baseMana
        self.baseMove = loaded.baseMovement
        # note: toughness and evasion are saved as % damage taken and % chance to be hit, respectively
        self.baseToughness = loaded.baseToughness
        self.baseEvasion = loaded.baseEvasion

        # attributes, number is points invested
        # passive   # TODO load from file?? probably
        self.life = 0
        self.toughness = 0
        self.evasion = 0
        self.movement = 0
        self.mana = 0
        # active
        self.potency = 0
        self.duration = 0
        self.application = 0
        self.speed = 0
        self.efficiency = 0
        self.recovery = 0
        self.subtlety = 0

        self.alive = True
        self.vulnerable = loaded.vulnerable

        self.collisionRadius = 20.0  # TODO calibrate, switch to rectangle check? Need rectangles AND circles
        self.sizeX = loaded.sizeX
        self.sizeY = loaded.sizeY

        # current health and mana
        self.currentLife = self.getMaxLife()
        self.currentMana = self.getMaxMana()

    def addItem(self, ite):
        self.inventory.append(ite)
    def addEquip(self, ite):
        if ite.equipSlot in self.equipped.keys():
            self.remEquip(ite.equipSlot)
        self.equipped[ite.equipSlot] = ite
        # increase attributes by amounts on item
        # TODO
    def remEquip(self, slot):
        if slot in self.equipped.keys():
            if self.equipped[slot] is not None:
                self.addItem(self.equipped[slot])
                # reduce attributes by amounts on item
                # TODO
            self.equipped.pop(slot)
    def terminate(self):
        self.alive = False
        #self.image = pygame.image.load("Assets/DefaultCorpse.png")
        self.setLimit(5.0)
        #print(self.name,"was killed. New limit", self.limit)

    def getMaxMana(self):
        return self.baseMana * BASE ** self.mana

    def getMaxLife(self):
        return self.baseLife * BASE ** self.life

    def getMoveSpeed(self):
        return self.baseMove * BASE ** self.movement

    def damage(self, amount, evasionEffect=1.0, armorEffect=1.0):
        if self.alive:
            damageDealt = amount
            if amount >= 0.0:   # negative damage means a healing effect, which should not be mitigated by toughness or evasion
                hit = (random.uniform(0.0,1.0) <= self.baseEvasion/(BASE**(self.evasion*evasionEffect)))
                if hit:
                    damageDealt = amount * self.baseToughness/(BASE**(self.toughness*armorEffect))
                else:
                    damageDealt = 0.0
                    #print(self.name, "evaded damage!")
                    self.recentEvade = 0.0
            self.currentLife -= damageDealt
            if self.currentLife <= 0.0:
                self.currentLife = 0.0
                self.terminate()
            #print("Dealt", damageDealt, "to", self.name, "Would have been", amount)
        else:
            # already dead
            pass

    def animate(self, frameTime):
        # decide which image to use for this character this frame, based on frameTime, recent evades, current life, etc
        if self.alive:
            # for now this will just switch between normal and evaded images
            if self.recentEvade < self.evadeReset:
                self.recentEvade += frameTime
                self.setImage(self.evadeImage)
            else:
                # not drawing the evade image, can check movement instead
                diffX = self.oldX - self.locX
                diffY = self.oldY - self.locY
                #print(diffX, "base", self.getMoveSpeed()*frameTime, "right", self.getMoveSpeed() * -1.2 * frameTime)
                if diffX < self.getMoveSpeed() * -1.2 * frameTime:  # percent movement threshold is above 1 courtesy of player movespeed bonus TODO reorganize
                    self.setImage(self.rightImage)
                elif diffX > self.getMoveSpeed() * 1.2 * frameTime:
                    self.setImage(self.leftImage)
                else:
                    self.setImage(self.baseImage)
        else:
            # alive is False
            #print(self.name,"is dead with limit", self.limit, "and age", self.age)
            self.setImage(self.deadImage)


class Player():

    def __init__(self, id):
        self.steamID = "0"
        self.characters = []
        self.steamID = id
    def addChar(self, charFile):
        # load character data from file, TODO implement
        return

class Item():

    def __init__(self, slot, ico):
        self.equipSlot = "none"  # equipSlot is a string for name of slot this item belongs to
        self.icon = "none"
        # can add a variable number of attribute bonuses, each being a tuple of (attribute, bonus)
        self.attributes = []

        self.equipSlot = slot
        self.icon = ico

    def addAttribute(self, att, bonus):
        newAtt = (att, bonus)
        self.attributes.append(newAtt)

class Loadable(): # called Loadable because Object is a terrible name
    # a Loadable contains info loaded from a config file for a drawable TYPE (something which might have multiple instances in a given map)
    # Loadable objects should only be used to create Drawables, not treated as Drawables themselves
    # TODO follow this with volatile projectile implementation
    # character's should inherit from loadable (use a loadable's data in constructor, don't inherit since loaded values are shared)
    def __init__(self, filename):
        # load data from file
        # TODO missing var detection, error catching stuff (test cases even?)
        # default values. Default to zero mitigation, zero evasion rate, zero movement, one hitpoint, no mana
        self.baseLife = 1.0
        self.baseMana = 0.0
        self.baseToughness = 1.0  # percent damage taken (0-1)
        self.baseEvasion = 1.0  # percent of hits which land (0-1)
        self.baseMovement = 0.0
        self.animation = "None"  # if left at none, just use base image for all cases
        self.vulnerable = False     # can't be damaged by default, since default case is terrain object
        self.team = "None"
        self.image = "None"
        self.collidable = False
        self.roof = False
        self.name = "BrokenFile"    # TODO error cases over here, certain fields MUST be present, name being most important
        self.alpha = False
        infile = open(filename, "r")
        for line in infile:
            mySplit = line.split("=")
            if len(mySplit) == 2:
                # valid line
                var = mySplit[0]
                val = str(mySplit[1]).strip()
                if var == "image":
                    self.image = val
                if var == "name":
                    self.name = val
                if var == "team":
                    self.team = val
                # collidable = drawable object which prevents movement into its space
                if var == "collidable":
                    self.collidable = bool(val)
                # portal = object which links to another map upon colliding (for fast travel between zones)
                if var == "portal":
                    self.portal = bool(val)   # if portal is true, collidable must be forced on. If projectiles can go through, going to need to take target data vs actual pos to find new trajectory and distance
                if var == "vulnerable":
                    self.vulnerable = bool(val)
                if var == "sizeX":
                    self.sizeX = val
                if var == "sizeY":
                    self.sizeY = val
                if var == "animation":
                    self.animation = val
                if var == "baseLife":
                    self.baseLife = float(val)
                if var == "baseToughness":
                    self.baseToughness = float(val)
                if var == "baseEvasion":
                    self.baseEvasion = float(val)
                if var == "baseMana":
                    self.baseMana = float(val)
                if var == "baseMovement":
                    self.baseMovement = float(val)
                # roof = drawable which will be hidden when player occupies the same space
                if var == "roof":
                    self.roof = bool(val)
                # alpha = image has some transparency and should use convert_alpha (costs more than convert but preserves alpha channels)
                if var == "alpha":
                    self.alpha = bool(val)


        infile.close()
    # could redo collision check for rectangles instead of circles
    # with everything being checked by a center position + radius, map would look more like tokens instead of actual buildings
    # need both rectangles and circles, maybe even rectangles which aren't axis-bound (for line based skill shapes, potentially cones)

class Map():
    def __init__(self, dataFile, objectDict, characterDict):

        # drawable object list
        self.draws = []

        # defaults in case of badly written level file
        self.background = "Missing"
        self.width = "Missing"
        self.height = "Missing"
        self.loadX = "Missing"
        self.loaxY = "Missing"

        infile = open(dataFile, "r")
        for line in infile:
            mySplit = line.split("=")
            if len(mySplit) == 2:
                # valid line
                var = mySplit[0]
                val = str(mySplit[1]).strip()

                # background image file name
                if var == "background":
                    self.background = val

                # width and height of physical gamespace (boundaries)
                if var == "width":
                    self.width = float(val)
                if var == "height":
                    self.height = float(val)
                # coordinates to load players into if new playthrough TODO multiple spots based on name of previous level
                if var == "loadX":
                    self.loadX = float(val)
                if var == "loadY":
                    self.loadY = float(val)

                if len(val.split(",")) == 2:
                    objectLocX, objectLocY = val.split(",")
                    objectLocX = float(objectLocX)
                    objectLocY = float(objectLocY)
                    objectName = var
                    # verify object exists in object set (global dictionary in View)
                    foundObject = getObject(objectDict, objectName)
                    foundCharacter = getObject(characterDict, objectName)
                    if foundObject is None and foundCharacter is None:
                        # object name was not found in either character or object sets
                        raise Exception("Loadable not found:", objectName)
                    if foundObject is not None and foundCharacter is not None:
                        # object name was found in both sets, cannot distinguish
                        raise Exception("Duplicate loadable found:", objectName)
                    # once we have the object data from file, spawn an instance of it at locX,locY (via addDraws)
                    # we can now assert it is exactly a standard drawable or a character
                    if foundObject is not None:
                        myDraw = Drawable(foundObject, objectLocX, objectLocY, "load")  # need to use loadable mode since python doesn't like multiple constructors
                        self.addDraw(myDraw)
                    if foundCharacter is not None:
                        myChar = Character(foundCharacter, objectLocX, objectLocY)
                        self.addDraw(myChar)

        infile.close()

        if self.background == "Missing" or self.width == "Missing" or self.height == "Missing" or self.loadX == "Missing" or self.loadY == "Missing":
            raise Exception("Missing data in level file")

        self.image = pygame.image.load("Assets/Maps/"+self.background).convert() # TODO rescale image to match width and height
        # map background image cannot have alpha
        # TODO alpha flag on other drawables, since non-alpha draws are much faster
        # TODO load and convert all images BEFORE gameplay, no loading files mid game
        self.width, self.height = self.image.get_size() # atm just overwriting width and height with image size

    def addDraw(self, draw):
        self.draws.append(draw)

    def findValidTargets(self, targetX, targetY, radius, teamType, teamMatch):
        validTargets = []
        for draw in self.draws:
            if isinstance(draw, Character):
                validTarget = False
                # distance check, just use circles for now
                dist = math.sqrt((targetX - draw.locX) ** 2 + (targetY - draw.locY) ** 2) - draw.collisionRadius
                if dist <= radius:
                    # print("Character is close enough", self.team)
                    if teamType == "all":
                        validTarget = True
                    elif teamType == "enemy":
                        if draw.team != teamMatch:
                            validTarget = True
                    elif teamType == "friendly":
                        if draw.team == teamMatch:
                            validTarget = True
                if validTarget:
                    validTargets.append(draw)
        return validTargets