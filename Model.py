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
        self.preview = "none"
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
                    # which folder to use for triggered ability TODO make this work for non-dot skills
                    self.animation = val
                if var == "volatile":
                    self.volatile = bool(val)
                if var == "maxRange":
                    self.maxRange = float(val)
                if var == "evasionEffect":
                    self.evasionEffect = float(val)
                if var == "armorEffect":
                    self.armorEffect = float(val)
                if var == "preview":
                    # which animation folder to use for ability preview
                    self.preview = val

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

    def trigger(self, caster, targetX, targetY, map, frameTime):
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
            validTargets = map.findValidTargets(targetX, targetY, searchRadius, self.team, caster.team, frameTime)
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
            self.imageDict = {}
            self.imageDict['base'] = pygame.image.load(dat).convert()
            self.image = self.imageDict['base']
            self.locX = float(x)
            self.locY = float(y)
            self.boundX, self.boundY = self.image.get_size()
            self.oldX = 0
            self.oldY = 0
            self.shape = "rect"
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
            self.locX = float(x)
            self.locY = float(y)
            self.oldX = x
            self.oldY = y
            # fields from loadable that are definitely here
            self.shape = dat.shape
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
            self.imageDict = dat.imageDict
            self.image = self.imageDict['base']
            self.boundX, self.boundY = self.image.get_size()
            self.setBounds(dat.sizeX, dat.sizeY)
        # starting velocities should always be zero at this stage, projectile and character classes can change this after super is called
        self.velX = 0.0
        self.velY = 0.0

    def setScale(self, scal):
        scal = int(scal)
        self.scale = scal
        self.image = pygame.transform.scale(self.image, (scal*2, scal*2))
        self.boundX, self.boundY = self.image.get_size()
    def setBounds(self, newX, newY):
        self.image = pygame.transform.scale(self.image, (int(newX), int(newY)))
        self.boundX, self.boundY = self.image.get_size()
    def setLimit(self, limit):
        self.limit = limit
        self.age = 0.0

    def setImage(self, imageKey):
        # given filename, load image and set scale
        if imageKey in self.imageDict.keys():
            self.image = self.imageDict[imageKey]
        else:
            print ("setImage failed: key not found.", imageKey, "not among", self.imageDict.keys())
        #self.setScale(self.scale)
        self.setBounds(self.boundX, self.boundY)    # set bounds to match previous image

    def move(self, frameTime):
        self.oldX = self.locX
        self.oldY = self.locY
        self.locX += frameTime * self.velX
        self.locY += frameTime * self.velY

    def forceMove(self, newX, newY):
        self.oldX = self.locX
        self.oldY = self.locY
        self.locX = newX
        self.locY = newY

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
        validTargets = self.map.findValidTargets(self.locX, self.locY, self.scale, self.ability.team, self.caster.team, frameTime)
        for target in validTargets:
            target.damage(frameTime*self.ability.baseDamage*BASE**(self.caster.potency*self.ability.scalePotency))
        # also apply slow, speed, whatever other continuous effects here    TODO

        # also a good time to switch images
        self.time += frameTime  # TODO animation speed modifier, 2.0 means animation cycle will play two times per second
        # use time % len(draws) to determine which image to use
        drawNum = int(self.time % len(self.imageDict.keys()))
        self.setImage(list(self.imageDict.keys())[drawNum])


class Projectile(Drawable):
    def __init__(self, img, x, y, caster, targetX, targetY, speed, scaleSpeed, volatile, payload):
        super().__init__(img, x, y)
        self.targetX = targetX
        self.targetY = targetY
        self.speed = speed
        self.scaleSpeed = scaleSpeed
        self.payload = payload # ability to be activated on landing
        self.caster = caster
        self.volatile = volatile
        if self.volatile:
            self.collidable = True

    def targetProj(self, time):
        # return false if proj keeps moving, true if detonating. Adjusts projectile velocity to match target
        actualSpeed = self.speed * BASE ** (self.caster.speed * self.scaleSpeed)
        #print("Proj",self.caster.speed)
        # TODO option for projectile to target a draw, maybe even require such and use a telegraph icon for this
        deltaX = self.targetX - self.locX
        deltaY = self.targetY - self.locY
        targetDist = math.sqrt(deltaX**2+deltaY**2)
        # check if at destination this frame
        # split actualSpeed up into X and Y components, add to locX and locY accordingly
        if targetDist > 0.0:
            self.velX = deltaX/targetDist * actualSpeed
            self.velY = deltaY/targetDist * actualSpeed
        else:
            self.velX = 0.0
            self.velY = 0.0

        # check if colliding this frame (only for volatile)
        if self.volatile:
            # collision check time! TODO implement
            pass

        if targetDist <= actualSpeed * time:
            # you have arrived at your destination
            #self.move(self.targetX, self.targetY)
            #self.locX = self.targetX
            #self.locY = self.targetY
            # trigger ability effects at target location
            return True

        return False



class Character(Drawable):

    def __init__(self, loaded, x, y):
        # loaded is a Loadable, with all data needed to fill in a character's data minus specific position (hence x y args)
        assert isinstance(loaded, Loadable), "Character creation failed, loaded wrong type"

        super().__init__(loaded, x, y, mode="load")

        self.evadeReset = 0.2   # how long to show evade image before switching back
        self.recentEvade = self.evadeReset  # how long has it been since the last evade, defaults to max render time

        #super().__init__(img, x, y)
        self.collidable = loaded.collidable
        self.name = loaded.name
        self.team = loaded.team
        # items
        # need both equipped and owned
        self.inventory = []  # item list, item objects store which slot they go to
        self.equipped = {}  # dict keyed by gear slot

        # abilities
        self.abilities = {}  # dict keyed by casting slot   # TODO implement loadout options in loadable file
        loadAbilities = loaded.abilities.split(",")  # loadable should have either a blank, or a comma-delimited list of abilities (by name) which this character has equipped
        slot = 0
        for loadAbil in loadAbilities:
            if loadAbil != "":
                self.abilities[slot] = loadAbil
                slot += 1

        # base stats
        self.baseLife = loaded.baseLife
        self.baseMana = loaded.baseMana
        self.baseMove = loaded.baseMovement
        # note: toughness and evasion are saved as % damage taken and % chance to be hit, respectively
        self.baseToughness = loaded.baseToughness
        self.baseEvasion = loaded.baseEvasion

        # attributes, number is points invested
        # passive attribute bonuses
        self.life = loaded.life
        self.toughness = loaded.toughness
        self.evasion = loaded.evasion
        self.movement = loaded.movement
        self.mana = loaded.mana
        # active
        self.potency = loaded.potency
        self.duration = loaded.duration
        self.application = loaded.application
        self.speed = loaded.speed
        self.efficiency = loaded.efficiency
        self.recovery = loaded.recovery
        self.subtlety = loaded.subtlety

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
        self.currentLife = 0.0
        #self.image = pygame.image.load("Assets/DefaultCorpse.png")
        self.setLimit(5.0)
        self.velX = 0.0
        self.velY = 0.0
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
                self.setImage("evaded")
            else:
                # not drawing the evade image, can check movement instead
                diffX = self.oldX - self.locX
                diffY = self.oldY - self.locY
                #print(diffX, "base", self.getMoveSpeed()*frameTime, "right", self.getMoveSpeed() * -1.2 * frameTime)
                if diffX < self.getMoveSpeed() * -0.1 * frameTime:  # setting animation based on which direction is utilised the most this frame, AND if moving past a certain speed
                    self.setImage("right")
                elif diffX > self.getMoveSpeed() * 0.1 * frameTime:
                    self.setImage("left")
                else:
                    self.setImage("base")   # TODO retool image switching such that images are already loaded into pygame
        else:
            # alive is False
            #print(self.name,"is dead with limit", self.limit, "and age", self.age)
            self.setImage("dead")


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
        self.shape = "rect"

        # in case of character, need these defaults
        # passive attribute bonuses
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

        self.abilities = "" # just load as a string for now, character parser can split into list form

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
                    self.sizeX = int(val)
                if var == "sizeY":
                    self.sizeY = int(val)
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
                if var == "shape":
                    self.shape = val
                # attribute loading
                if var == "life":
                    self.life = int(val)
                if var == "toughness":
                    self.toughness = int(val)
                if var == "evasion":
                    self.evasion = int(val)
                if var == "movement":
                    self.movement = int(val)
                if var == "mana":
                    self.mana = int(val)
                if var == "potency":
                    self.potency = int(val)
                if var == "duration":
                    self.duration = int(val)
                if var == "application":
                    self.application = int(val)
                if var == "efficiency":
                    self.efficiency = int(val)
                if var == "recovery":
                    self.recovery = int(val)
                if var == "subtlety":
                    self.subtlety = int(val)
                if var == "speed":
                    self.speed = int(val)
                if var == "abilities":
                    self.abilities = val


        infile.close()

        # TODO implement image loader, probably just use animation flag and have standard file loading system
        self.imageDict = {}
        # need to do image initialization here, since loading from file and converting to faster display format is slightly expensive
        print("Loading images for", self.name)
        if self.image != "None":
            if self.alpha:
                self.imageDict['base'] = pygame.image.load(self.image).convert_alpha()
            else:
                self.imageDict['base'] = pygame.image.load(self.image).convert()
        if self.animation != "None":
            # load other images into dictionary, save transparency
            # look through animation folder, store loaded images by key of filename (strip the file extension)
            for file in os.listdir("Assets/Animations/" + self.animation):
                key = file.split(".")[0].lower()    # only want first name in file, don't use multiple .'s in name
                loadedImage = pygame.image.load("Assets/Animations/"+self.animation+"/"+file)
                if self.alpha:
                    self.imageDict[key] = loadedImage.convert_alpha()
                else:
                    self.imageDict[key] = loadedImage.convert()

    # could redo collision check for rectangles instead of circles
    # with everything being checked by a center position + radius, map would look more like tokens instead of actual buildings
    # need both rectangles and circles, maybe even rectangles which aren't axis-bound (for line based skill shapes, potentially cones)

class Map():
    def __init__(self, dataFile, objectDict, characterDict):

        # drawable object list
        self.draws = []
        # current frame collisions dict (key:value is index:list where index is a draw's index in list, and list contains indices of draws the first index potentially collides with this frame)
        self.collisions = {}

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
        self.width, self.height = self.image.get_size() # atm just overwriting width and height with image size

    def addDraw(self, draw):
        self.draws.append(draw)

    def findValidTargets(self, targetX, targetY, radius, teamType, teamMatch, frameTime):
        validTargets = []
        # create a temp draw for collision check
        myTempDraw = Drawable("Assets/BlankBase.png", targetX, targetY)
        myTempDraw.setBounds(radius, radius)
        for draw in self.draws:
            if isinstance(draw, Character):
                validTarget = False
                # distance check, just use circles for now
                colTimes = checkTwoCollidableRectangles(myTempDraw, draw, frameTime)
                if colTimes[0] is not None and colTimes[1] is not None:
                #dist = math.sqrt((targetX - draw.locX) ** 2 + (targetY - draw.locY) ** 2) - draw.collisionRadius
                #if dist <= radius:
                    # print("Character is close enough", self.team)
                    if teamType == "all":
                        validTarget = True
                    elif teamType == "enemy":
                        if draw.team != teamMatch and draw.team != "map":
                            validTarget = True
                    elif teamType == "friendly":
                        if draw.team == teamMatch:
                            validTarget = True
                if validTarget:
                    validTargets.append(draw)
        return validTargets

    def screenCollisions(self, frameTime):
        # this function should be called once per frame on an active map
        # should populate a list of tuples which are the indices of draws which collide in an axis-bound rectangle check
        # consult the list from this function whenever doing further collision checks, which must take place after this is called in the frame
        # in theory this costs a little performance per frame when nothing is going on, but can save a lot when multiple collisions occur at once
        # could make list a dictionary instead, group the tuples in advance (since we'll want them based on specific draws later anyways)
        # empty old collisions dict
        self.collisions = {}
        iterA = 0
        while iterA < len(self.draws):
            colDrawA = self.draws[iterA]
            # double check this is a purposeful loop
            if colDrawA.collidable:
                # iterB = iterA + 1  # iterB starting one later than iterA is faster for catching every collision, but we don't know in advance which ones we want the keys for, so the slower loop must be used
                iterB = 0
                # regardless of actual shape, make an axis-bound rectangle which can entirely enclose colDraw
                # valid shapes atm: circle, rect
                centerXA, centerYA = colDrawA.locX, colDrawA.locY
                offsetXA, offsetYA = colDrawA.boundX/2, colDrawA.boundY/2
                velXA, velYA = colDrawA.velX, colDrawA.velY
                # with just circle and rectangle, can just use image boundaries to form rectangle TODO revisit when adding additional shapes
                while iterB < len(self.draws):
                    # get data for colDrawB
                    colDrawB = self.draws[iterB]
                    # verify this draw even concerns this loop
                    if colDrawB.collidable and iterA != iterB:
                        centerXB, centerYB = colDrawB.locX, colDrawB.locY
                        offsetXB, offsetYB = colDrawB.boundX/2, colDrawB.boundY/2
                        velXB, velYB = colDrawB.velX, colDrawB.velY

                        # actual calculation time. Goal is to find a time range for X and Y axes, then save the shared time window for later use
                        netLocX = centerXA - centerXB
                        netLocY = centerYA - centerYB
                        netVelX = velXA - velXB
                        netVelY = velYA - velYB
                        combWidth = offsetXA + offsetXB
                        combHeight = offsetYA + offsetYB

                        # calculate exact crossover time, leave at None if its not occuring in a positive time
                        # account for 0 net velocity
                        if netVelX == 0.0:
                            # relative motion on X axis is 0, are they presently overlapping?
                            if abs(netLocX) <= combWidth:
                                startTimeX = 0.0
                                endTimeX = frameTime
                            else:
                                # not moving relative to each other and not presently overlapping, therefore impossible to collide this frame
                                startTimeX = None
                                endTimeX = None
                        else:
                            colTimeX1 = (combWidth - netLocX) / netVelX
                            colTimeX2 = -(combWidth + netLocX) / netVelX
                            startTimeX = max(min(colTimeX1, colTimeX2), 0.0)
                            endTimeX = min(max(colTimeX1, colTimeX2), frameTime)

                        if netVelY == 0.0:
                            # neither is moving, are they presently overlapping?
                            if abs(netLocY) <= combHeight:
                                startTimeY = 0.0
                                endTimeY = frameTime
                            else:
                                startTimeY = None
                                endTimeY = None
                        else:
                            colTimeY1 = (combHeight - netLocY) / netVelY
                            colTimeY2 = -(combHeight + netLocY) / netVelY
                            startTimeY = max(min(colTimeY1, colTimeY2), 0.0)
                            endTimeY = min(max(colTimeY1, colTimeY2), frameTime)

                        # with start and end times found, look for overlap
                        # skip this if either range returned None
                        if startTimeX is not None and startTimeY is not None:
                            startColTime = max(startTimeX, startTimeY)
                            endColTime = min(endTimeX, endTimeY)
                            # now check frameTime constraints. We know start is less than end, but end must occur this frame or later, and start must be this frame or sooner
                            if startColTime <= endColTime and endColTime >= 0.0 and startColTime <= frameTime:
                                # collision window is valid goes from startColTime to endColTime
                                colEntryTuple = (iterB, startColTime, endColTime)#, False)    # index of object, colStart, colEnd, boolean for resolved
                                #print("Screened", iterA, "against", iterB, "and got", colEntryTuple)
                                #print("More details:\n\tPosX", centerXA, "-", centerXB, "; PosY", centerYA, "-", centerYB, ";\n\tVelX", velXA, "-", velXB, "; VelY", velYA, "-", velYB, ";\n\tWidth", offsetXA, "+", offsetXB, "; Height", offsetYA, "+", offsetYB, ";")
                                #print("\tTimeX", startTimeX, "->", endTimeX, "; TimeY", startTimeY, "->", endTimeY, "; ColTime", startColTime, "->", endColTime, ";")
                                # add entry to dictionary
                                if iterA not in self.collisions.keys():
                                    self.collisions[iterA] = []
                                self.collisions[iterA].append(colEntryTuple)
                    iterB += 1
            iterA += 1

# collision calculator for axis-bound rectangles. This asserts colDrawA != colDrawB and both are collidable
def checkTwoCollidableRectangles(colDrawA, colDrawB, frameTime):
    centerXA, centerYA = colDrawA.locX, colDrawA.locY
    offsetXA, offsetYA = colDrawA.boundX / 2, colDrawA.boundY / 2
    velXA, velYA = colDrawA.velX, colDrawA.velY

    centerXB, centerYB = colDrawB.locX, colDrawB.locY
    offsetXB, offsetYB = colDrawB.boundX / 2, colDrawB.boundY / 2
    velXB, velYB = colDrawB.velX, colDrawB.velY

    # actual calculation time. Goal is to find a time range for X and Y axes, then save the shared time window for later use
    netLocX = centerXA - centerXB
    netLocY = centerYA - centerYB
    netVelX = velXA - velXB
    netVelY = velYA - velYB
    combWidth = offsetXA + offsetXB
    combHeight = offsetYA + offsetYB

    # calculate exact crossover time, leave at None if its not occuring in a positive time
    # account for 0 net velocity
    if netVelX == 0.0:
        # relative motion on X axis is 0, are they presently overlapping?
        if abs(netLocX) <= combWidth:
            startTimeX = 0.0
            endTimeX = frameTime
        else:
            # not moving relative to each other and not presently overlapping, therefore impossible to collide this frame
            startTimeX = None
            endTimeX = None
    else:
        colTimeX1 = (combWidth - netLocX) / netVelX
        colTimeX2 = -(combWidth + netLocX) / netVelX
        startTimeX = max(min(colTimeX1, colTimeX2), 0.0)
        endTimeX = min(max(colTimeX1, colTimeX2), frameTime)

    if netVelY == 0.0:
        # neither is moving, are they presently overlapping?
        if abs(netLocY) <= combHeight:
            startTimeY = 0.0
            endTimeY = frameTime
        else:
            startTimeY = None
            endTimeY = None
    else:
        colTimeY1 = (combHeight - netLocY) / netVelY
        colTimeY2 = -(combHeight + netLocY) / netVelY
        startTimeY = max(min(colTimeY1, colTimeY2), 0.0)
        endTimeY = min(max(colTimeY1, colTimeY2), frameTime)

    # with start and end times found, look for overlap
    # skip this if either range returned None
    if startTimeX is not None and startTimeY is not None:
        startColTime = max(startTimeX, startTimeY)
        endColTime = min(endTimeX, endTimeY)
        # now check frameTime constraints. We know start is less than end, but end must occur this frame or later, and start must be this frame or sooner
        if startColTime <= endColTime and endColTime >= 0.0 and startColTime <= frameTime:
            # collision window is valid goes from startColTime to endColTime
            colEntryTuple = (startColTime, endColTime)
            return colEntryTuple
    noneTuple = (None, None)
    return noneTuple
