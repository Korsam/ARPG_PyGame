import pygame
import os
import math
import random

BASE = 1.11842691472    # fifth root of 1.75 AKA 5 points equates to 75% improvement (assuming 1.0 scaling)

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
                val = mySplit[1]
                # a lot of if's
                if var == "name":
                    self.name = str(val).strip()
                if var == "targetingMode":
                    self.targetingMode = str(val).strip()
                if var == "travelIcon":
                    self.travelIcon = str(val).strip()
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
                    self.shape = str(val).strip()
                if var == "team":
                    self.team = str(val).strip()
                if var == "animation":
                    self.animation = str(val).strip()
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
                print("Loading", img, "from", self.animation, "for ability", self.name)
        print("Initalized ability", self.name)

    def addDraw(self, draw):
        print("Adding", draw, "for", self.name)
        self.draws.append(draw)
        print("Total", self.draws)

    def cast(self, caster, targetX, targetY):
        # actually cast the ability
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
    def __init__(self, img, x, y):
        self.scale = 40
        self.boundX = 0
        self.boundY = 0
        self.age = 0.0
        self.limit = None
        self.collidable = False
        #img = "Assets/testChar.png"
        #print("Loading image from", os.getcwd(), "its", img)
        self.image = pygame.image.load(img)
        self.locX = x
        self.locY = y
        self.boundX, self.boundY = self.image.get_size()
        self.oldX = 0
        self.oldY = 0
        #print("Initialized drawable at pos", x, y, "with bounds", self.boundX, self.boundY, "using image at", img)
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
        self.image = pygame.image.load(filename)
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

    def __init__(self, img, x, y, nam, tea):

        self.name = "Jeff"
        self.team = "Neutral"
        # items
        # need both equipped and owned
        self.inventory = []  # item list, item objects store which slot they go to
        self.equipped = {}  # dict keyed by gear slot

        # abilities
        self.abilities = {}  # dict keyed by casting slot

        # base stats
        self.baseLife = 1000.0
        self.baseMana = 500.0
        self.baseMove = 100.0
        # note: toughness and evasion are saved as % damage taken and % chance to be hit, respectively
        self.baseToughness = 1.0
        self.baseEvasion = 1.0

        # current health and mana
        self.currentLife = self.baseLife
        self.currentMana = self.baseMana

        # attributes, number is points invested
        # passive
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

        self.collisionRadius = 20.0  # TODO calibrate

        self.animation = "testChar"

        self.baseImage = "Assets/testChar.png"
        self.evadeImage = "Assets/testCharEvaded.png"
        self.evadeReset = 0.2   # how long to show evade image before switching back
        self.recentEvade = self.evadeReset  # how long has it been since the last evade, defaults to max render time
        self.leftImage = "Assets/testCharLeft.png"  # TODO dynamic!!!!
        self.rightImage = "Assets/testCharRight.png"

        super().__init__(img, x, y)
        self.name = nam
        self.team = tea
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
        self.image = pygame.image.load("Assets/DefaultCorpse.png")
        self.setLimit(5.0)

    def getMaxMana(self):
        return self.baseMana * BASE ** self.mana

    def getMaxLife(self):
        return self.baseLife * BASE ** self.life

    def getMoveSpeed(self):
        return self.baseMove * BASE ** self.movement

    def damage(self, amount, evasionEffect=1.0, armorEffect=1.0):
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

    def animate(self, frameTime):
        # decide which image to use for this character this frame, based on frameTime, recent evades, current life, etc
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

class Collidable(Drawable):
    # drawable object which prevents movement into its space
    # coding this should lead into volatile projectile implementation
    def __init__(self, img, x, y):
        super().__init__(img, x, y)
    # could redo collision check for rectangles instead of circles
    # with everything being checked by a center position + radius, map would look more like tokens instead of actual buildings

class Map():
    def __init__(self, back):#, dataFile):

        # map dimensions
        self.width = 0
        self.height = 0
        self.loadX = 0
        self.loadY = 0
        # background image
        self.image = None
        # drawable object list
        self.draws = []

        self.image = pygame.image.load(back)
        self.width, self.height = self.image.get_size()
        # TODO implement datafile component, this will have loadX, loadY, and draws

    def addDraw(self, draw):
        self.draws.append(draw)

    # gets
    def getWidth(self):
        return self.width
    def getHeight(self):
        return self.height
    def getLoadX(self):
        return self.loadX
    def getLoadY(self):
        return self.loadY
    def getImage(self):
        return self.image
    def getDraws(self):
        return self.draws

    # sets
    # TODO maybe later

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