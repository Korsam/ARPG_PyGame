import pygame
import pygame.freetype
import math
import random
import time
from Model import Ability, Character, Player, Item, Map, Drawable, Projectile, Effect, Loadable, checkTwoCollidableRectangles
import os

pygame.init()

display_width = 1920
display_height = 1080

gameDisplay = pygame.display.set_mode((display_width,display_height), pygame.FULLSCREEN)
pygame.display.set_caption('ARPG')

clock = pygame.time.Clock()
running = True

# dictionary of all Loadables from the objects folder
loadedObjects = {}
for objectFile in os.listdir("Assets/Objects"):
    newObject = Loadable("Assets/Objects/"+objectFile)
    newName = newObject.name
    print("Loaded object file", objectFile)#, "for ability", newName)
    loadedObjects[newName] = newObject
# dictionary of all Loadables from the characters folder
loadedCharacters = {}
for characterFile in os.listdir("Assets/Characters"):
    newCharacter = Loadable("Assets/Characters/"+characterFile)
    newName = newCharacter.name
    print("Loaded character file", characterFile, "named", newName)
    loadedCharacters[newName] = newCharacter

#testMap = Map('Assets/background.png')
level1 = Map("Assets/Maps/Level1.txt", loadedObjects, loadedCharacters)

# valid key vars
keyW = False
keyA = False
keyS = False
keyD = False

# num keys for ability selection, 1-0?
key1 = False
key2 = False
key3 = False
key4 = False
key5 = False
key6 = False
key7 = False
key8 = False
key9 = False
key0 = False

# test key for speed change
keyQ = False
keyR = False

# initialize abilities
# look through Abilities folder and create a dictionary entry for each loaded ability file found
abilityDictionary = {}
for abilityFile in os.listdir("Abilities"):
    newAbility = Ability("Abilities/"+abilityFile)
    newName = newAbility.name
    print("Loaded ability file", abilityFile)#, "for ability", newName)
    abilityDictionary[newName] = newAbility
# TODO remove hard coded ability references, rely on character loadout to determine which abilities are available (player can just cast first loaded ability until UI catches back up)
testFireBall = Ability("Abilities/Fireball")
testSword = Ability("Abilities/Sword")
acidPit = Ability("Abilities/AcidPit")

# initialize font
font = pygame.freetype.SysFont("Pygame", 12)

aliveTime = 0.0
playerSwordTime = 0.0

currentMap = level1

#print("Loaded characters:", loadedCharacters)
testChar = Character(loadedCharacters["Jeff"], currentMap.loadX, currentMap.loadY) # TODO player control should be established via team or name matching player current character field TBD
#testChar.move(80, 160)
currentMap.addDraw(testChar)

# load UI elements
manaBarBase = Drawable("Assets/UI/ManaBarBase.png", 0, 40)
lifeBarBase = Drawable("Assets/UI/LifeBarBase.png", 0, 0)
manaBarFill = Drawable("Assets/UI/ManaBarFull.png", 0, 40)
lifeBarFill = Drawable("Assets/UI/LifeBarFull.png", 0, 0)

abilityBox = pygame.image.load("Assets/UI/BaseAbilitySlot.png").convert_alpha()
highlightBox = pygame.image.load("Assets/UI/HighlightedAbilitySlot.png").convert_alpha()
highlightedAbility = 0
cooldownBox = pygame.image.load("Assets/UI/AbilityCooldown.png").convert_alpha()    # definitely want alpha on this one

# science values
#testChar.toughness += 5
#testChar.evasion += 5
#testChar.efficiency += 5
#testChar.life += 20
#testChar.mana += 20 # 20 seems like a pretty good cap for defensive stat totals, good to test extreme specialization vs distributed builds

menu=True
menuBackground = pygame.image.load("Assets/UI/MenuBackground.png").convert_alpha()
continueButton = pygame.image.load("Assets/UI/Continue.png").convert_alpha()
optionsButton = pygame.image.load("Assets/UI/Options.png").convert_alpha()
exitButton = pygame.image.load("Assets/UI/Exit.png").convert_alpha()
gameTitle = pygame.image.load("Assets/UI/GameTitle.png").convert_alpha()


badGuyTimer = 5.0

# main loop
while running:
    click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # get keyboard inputs
        # key is first pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                keyW = True
            if event.key == pygame.K_a:
                keyA = True
            if event.key == pygame.K_s:
                keyS = True
            if event.key == pygame.K_d:
                keyD = True
            if event.key == pygame.K_q:
                keyQ = True
            if event.key == pygame.K_r:
                keyR = True
            # numKeys
            if event.key == pygame.K_1:
                key1 = True
            if event.key == pygame.K_2:
                key2 = True
            if event.key == pygame.K_3:
                key3 = True
            if event.key == pygame.K_4:
                key4 = True
            if event.key == pygame.K_5:
                key5 = True
            if event.key == pygame.K_6:
                key6 = True
            if event.key == pygame.K_7:
                key7 = True
            if event.key == pygame.K_8:
                key8 = True
            if event.key == pygame.K_9:
                key9 = True
            if event.key == pygame.K_0:
                key0 = True
        # key is released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                keyW = False
            if event.key == pygame.K_a:
                keyA = False
            if event.key == pygame.K_s:
                keyS = False
            if event.key == pygame.K_d:
                keyD = False
            if event.key == pygame.K_q:
                keyQ = False
                #testChar.application -= 1
            if event.key == pygame.K_r:
                keyR = False
                #testChar.application += 1


            # numKeys
            if event.key == pygame.K_1:
                key1 = False
            if event.key == pygame.K_2:
                key2 = False
            if event.key == pygame.K_3:
                key3 = False
            if event.key == pygame.K_4:
                key4 = False
            if event.key == pygame.K_5:
                key5 = False
            if event.key == pygame.K_6:
                key6 = False
            if event.key == pygame.K_7:
                key7 = False
            if event.key == pygame.K_8:
                key8 = False
            if event.key == pygame.K_9:
                key9 = False
            if event.key == pygame.K_0:
                key0 = False

            if event.key == pygame.K_ESCAPE:
                if menu:
                    running = False
                else:
                    menu = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            # generic click detector for now
            click = True


    # put black background in first for cases where map image has been panned offscreen partly
    gameDisplay.fill((0,0,0))
    # if on menu, draw its elements
    if menu:
        gameDisplay.blit(menuBackground, (0,0))
        # draw menu elements
        gameDisplay.blit(continueButton, (300,250))
        gameDisplay.blit(optionsButton, (300,325))
        gameDisplay.blit(exitButton, (300,400))

        # draw title around 300,50
        gameDisplay.blit(gameTitle, (250,50))

        if click:
            # see if the click happened on one of the menu buttons
            leftClick = pygame.mouse.get_pressed()[0]
            if leftClick:
                # get location
                mouseX, mouseY = pygame.mouse.get_pos()
                if mouseX >= 300 and mouseX <= 500:
                    # we are within the x range TODO dynamically find this
                    if mouseY >= 250 and mouseY <= 300:
                        # continue button
                        # for now just load testMap
                        # TODO implement map loading

                        currentMap = level1
                        menu = False
                    if mouseY >= 325 and mouseY <= 375:
                        # options button
                        pass    # TODO implement options menu
                    if mouseY >= 400 and mouseY <= 450:
                        # exit button
                        running = False

    else:

    # if map is loaded, go into map code
        # can do game logic here
        frameTime = clock.tick()/1000.0  # get time since last frame, ALSO tell pygame to limit FPS at 60 TODO make configurable
        #print(frameTime)

        # PLAYER MOVEMENT STAGE
        moveX = False
        moveY = False
        playerSpeed = testChar.getMoveSpeed()  #testChar.baseMove * (1.1 ** testChar.movement)
        boost = math.sqrt(playerSpeed*playerSpeed*2)-playerSpeed
        if keyW:
            moveY = True
            testChar.velY = 0 - playerSpeed
            # bonus speed if only moving on a cardinal axis
            if not keyA and not keyD:
                testChar.velY -= boost
        if keyA:
            moveX = True
            testChar.velX = 0 - playerSpeed
            if not keyW and not keyS:
                testChar.velX -= boost
        if keyS:
            moveY = True
            testChar.velY = playerSpeed
            if not keyA and not keyD:
                testChar.velY += boost
        if keyD:
            moveX = True
            testChar.velX = playerSpeed
            if not keyW and not keyS:
                testChar.velX += boost

        if not moveX:
            testChar.velX = 0.0
        if not moveY:
            testChar.velY = 0.0

        # ability selection, just set to last one in list if available, multiple keys can be pressed but only one ability can be selected
        # so long as behavior is consistent here, shouldn't be an issue to allow multiple presses
        goodKeys = testChar.abilities.keys()
        if key1 and 0 in goodKeys:  # off by one I know, first ability loaded will be at index 0 despite being activated by key 1. I blame keyboard designers
            highlightedAbility = 0
        if key2 and 1 in goodKeys:
            highlightedAbility = 1
        if key3 and 2 in goodKeys:
            highlightedAbility = 2
        if key4 and 3 in goodKeys:
            highlightedAbility = 3
        if key5 and 4 in goodKeys:
            highlightedAbility = 4
        if key6 and 5 in goodKeys:
            highlightedAbility = 5
        if key7 and 6 in goodKeys:
            highlightedAbility = 6
        if key8 and 7 in goodKeys:
            highlightedAbility = 7
        if key9 and 8 in goodKeys:
            highlightedAbility = 8
        if key0 and 9 in goodKeys:
            highlightedAbility = 9

        # boundary enforcement
        # trigger all projectiles on reaching a map border
        for draw in currentMap.draws:
            border = False
            colRadius = 10  # TODO redo with physics engine plugin
            newX = draw.locX
            newY = draw.locY
            if isinstance(draw, Character):
                colRadius = draw.collisionRadius
            if draw.locX-colRadius < 0:
                newX = colRadius
                border = True
            if draw.locY-colRadius < 0:
                newY = colRadius
                border = True
            if draw.locX+colRadius > currentMap.width:
                newX = currentMap.width - colRadius
                border = True
            if draw.locY+colRadius > currentMap.height:
                newY = currentMap.height - colRadius
                border = True
            if border:
                draw.forceMove(newX, newY)
                if isinstance(draw, Projectile):
                    # rather than copy the trigger code, just change the target to the new location
                    draw.targetX = draw.locX
                    draw.targetY = draw.locY

        #print("Char", testChar.speed)
        # spawn some baddies occasionally
        #badGuyTimer -= frameTime   # TODO uncomment to activate endless spawning
        if badGuyTimer <= 0.0:
            # spawn a bad guy, reset timer to a random number between 5 and 20
            badGuyChar = Character(loadedCharacters["Grunt"], random.uniform(50,750), random.uniform(100,550))
            # need to check if this guy is too close to an existing character (player included)
            tooClose = False
            for draw in currentMap.draws:
                if isinstance(draw, Character):
                    dist = math.sqrt((badGuyChar.locX-draw.locX)**2+(badGuyChar.locY-draw.locY)**2)
                    if dist <= 80:
                        tooClose = True
            if not tooClose:
                currentMap.addDraw(badGuyChar)
                badGuyTimer = random.uniform(2,8)



        # need offset data from last frame for mouse targeting, will need to be updated after movement later for display phase
        offX = display_width/2 - testChar.locX
        offY = display_height/2 - testChar.locY

        # click based actions
        if click:
            targetX, targetY = pygame.mouse.get_pos()
            targetX -= offX
            targetY -= offY
            # newDraw = Drawable("Assets/FireBall.png", targetX, targetY)
            left, middle, right = pygame.mouse.get_pressed()
            if left:
                #newProjectile = acidPit.cast(testChar, targetX, targetY)
                #newProjectile = testFireBall.cast(testChar, targetX, targetY)
                newProjectile = abilityDictionary[testChar.abilities[highlightedAbility]].cast(testChar, targetX, targetY)
                if not newProjectile:
                    print("Player failed to cast", testChar.abilities[highlightedAbility])
                    # TODO put feedback into the UI when casting fails, probably by having newProjectile replaced with an error type first
                    # possible error cases: caster lacks mana, ability on cooldown, no valid targets? (maybe out of range, TODO change range limit to force casting to target within a distance)
                    #print("Not enough mana", testChar.currentMana)
                else:
                    currentMap.addDraw(newProjectile)
            '''elif right:
                newProjectile = acidPit.cast(testChar, targetX, targetY)
                #newProjectile = testSword.cast(testChar, targetX, targetY)
                if not newProjectile:
                    print("Not enough mana", testChar.currentMana)
                    #print("Target out of range")
                else:
                    if playerSwordTime > 0.0:
                        print("Attack on cooldown")
                    else:
                        currentMap.addDraw(newProjectile)
                        playerSwordTime = 1.0'''

        if playerSwordTime > 0.0:
            playerSwordTime -= frameTime

        # need to sort the draws out for figuring out draw order later. Each list should be a list of indices from currentMap.draws
        effectDraws = []
        genericDraws = []
        projectileDraws = []
        characterDraws = []    # postpone drawing characters until the very last
        iter = 0
        #print("\nNEW FRAME\n")
        # handle collisions here
        # pre-check for all easy collisions to save time if things get messy later
        currentMap.screenCollisions(frameTime)
        for draw in currentMap.draws:
            # collidable object check (stop draws from passing through each other)
            # get list of prechecked collisions for given draw, verify actions to be taken
            # if the interaction only needs one response action (ie collision resolution), remove this draw from collider's prechecked list
            manuallyMoved = 0.0
            colX = False
            colY = False
            if iter in currentMap.collisions.keys():
                myChecks = currentMap.collisions[iter]
                # sort myChecks by check[1] (collision start time), ascending order
                for check in sorted(myChecks, key=lambda x: x[1]):
                    # TODO fix corner case AKA multiple collisions at once. Inelastic only atm so this should be easy, will get more complicated later
                    #if not check[3]:    # if collision not physically resolved already
                    #print("Checking", iter, "versus", check)
                    checkDraw = currentMap.draws[check[0]]
                    colStart = check[1]
                    colEnd = check[2]
                    if draw.shape == "rect" and checkDraw.shape == "rect":
                        # double rectangle, so we already have all the info needed
                        #print(iter, "and", check[0], "are both rectangles, colliding from", colStart, "to", colEnd)
                        # as this is not a physics-focused game, going to ignore secondary collisions (collisions only visible after resolving one earlier in the frame)
                        # unless some sort of "bouncy" flag is set, use inelastic collision model
                        # TODO implement bouncy flag for elastic collisions mode
                        # for inelastic, move objects to their positions at colStart, then set velocities such that only the component running perpendicular to the collision axis is left
                        # since these are axis-bound rectangles, we can just set X or Y velocities to 0 at that position, based on which side collides (potentially both for rare corner-to-corner collision)
                        #secondary = False
                        if manuallyMoved > 0.0:
                            #continue # just skip for now
                            # some other collision has moved this, see if this collision is still valid before proceeding (at the very least can update values)
                            # need to hand valid position data to double checker, so temporarily move draw by manuallyMoved, then put it back
                            checkDraw.move(manuallyMoved)
                            newColTuple = checkTwoCollidableRectangles(draw, checkDraw, frameTime-manuallyMoved)
                            checkDraw.move(-manuallyMoved)
                            colStart = newColTuple[0]
                            colEnd = newColTuple[1]
                            if colStart is None or colEnd is None:
                                #print("Secondary collision cancelled")
                                continue    # skip this collision since it no longer occurs
                            #else:
                                #print("Secondary collision still going")
                                #secondary = True

                        draw.move(colStart)
                        if isinstance(draw, Projectile):
                            # potentially special case where volatile projectile needs triggered
                            if draw.volatile and checkDraw is not draw.caster:
                                # need to ignore in case of colliding with caster
                                draw.targetX = draw.locX
                                draw.targetY = draw.locY
                                draw.velX = 0.0
                                draw.velY = 0.0
                        manuallyMoved += colStart
                        #checkDraw.move(colStart)
                        # now check collision axis
                        diffX = abs(draw.locX - (checkDraw.locX+colStart*checkDraw.velX))
                        diffY = abs(draw.locY - (checkDraw.locY+colStart*checkDraw.velY))
                        if diffX == draw.boundX/2 + checkDraw.boundX/2 and not colX:
                            # X axis collision
                            #if secondary:
                            #    print("X Collision", draw.velX, "->", draw.velX*-0.01, ";", checkDraw.velX, "->", checkDraw.velX*-0.01)
                            draw.velX *= -0.01
                            colX = True
                            #checkDraw.velX *= -0.001
                        if diffY == draw.boundY/2 + checkDraw.boundY/2 and not colY:
                            # Y axis collision
                            #if secondary:
                            #    print("Y Collision", draw.velY, "->", draw.velY*-0.01, ";", checkDraw.velY, "->", checkDraw.velY*-0.01)
                            draw.velY *= -0.01
                            colY = True
                            #checkDraw.velY *= -0.001
                        # now move with new velocities for the rest of the frame
                        #draw.move(frameTime-colStart)
                        #checkDraw.move(frameTime-colStart)
                        #print("Frametime:", frameTime, "-", colStart, "=", frameTime-colStart)
                        #if isinstance(draw, Character):
                        #    print(draw.name, "(", iter, ") collided with", check[0])
                        #if isinstance(checkDraw, Character):
                        #    print(checkDraw.name, "(", check[0], ") collided with", iter)
                    if draw.shape == "circle" or checkDraw.shape == "circle":
                        # if either is a circle, need to check again treating BOTH as circles (circle draws will be smaller, rect temp-circles will be larger)
                        pass    # TODO implement
                    # cleanup step, remove tuples which start with iter in list keyed by check[0]
                    '''check = (check[0], check[1], check[2], True)
                    tempChecks = currentMap.collisions[check[0]]
                    tempIter = 0
                    for delCheck in tempChecks:
                        if delCheck[0] == iter:
                            #print("Cleaning up", check[0], "hits", iter)
                            # instead of deleting, just set resolved flag in case other rect vs rect checks are needed (resolved only referring to physical movement)
                            tempChecks[tempIter] = (delCheck[0], delCheck[1], delCheck[2], True)
                            #tempChecks.remove(delCheck)
                        tempIter += 1'''
            draw.move(frameTime-manuallyMoved)
            if isinstance(draw, Character):
                characterDraws.append(iter)
                #if draw.team == "Player":
                #    continue   #TODO if reimplementing players drawn last, this needs uncommented. Atm all characters are drawn last
                #print("Character is not a player", draw.currentHP, "HP")
                if draw.team != "Player" and draw.alive:
                #elif draw.alive:
                    # npc behavior here
                    # should be trying to do something
                    dist = math.sqrt((draw.locX - testChar.locX)**2+(draw.locY - testChar.locY)**2)
                    if dist <= 100:
                        if draw.age > 0:
                            newSword = testSword.cast(draw, testChar.locX, testChar.locY)
                            if not newSword:
                                # somehow failed to swing sword, on cooldown probably
                                pass
                            else:
                                currentMap.addDraw(newSword)
                                #print("Attacking with sword, age", draw.age)
                                draw.age = -1.1
                    if draw.age >= 5.0:

                        # cast a fireball at the player's current location
                        targetX = testChar.locX + random.uniform(-50, 50)
                        targetY = testChar.locY + random.uniform(-50, 50)
                        newFire = testFireBall.cast(draw, targetX, targetY)
                        if not newFire:
                            # npc not enough mana
                            # switch to melee rush!
                            speed = draw.getMoveSpeed() #draw.baseMove * 1.1**draw.movement
                            diffX = targetX - draw.locX
                            diffY = targetY - draw.locY
                            dist = math.sqrt((diffX)**2+(diffY)**2)
                            ratX = diffX/dist
                            ratY = diffY/dist
                            draw.velX = speed * ratX
                            draw.velY = speed * ratY

                        else:
                            currentMap.addDraw(newFire)
                            draw.age -= random.uniform(1, 5)
                #continue
            elif isinstance(draw, Effect):
                effectDraws.append(iter)
                draw.tick(frameTime)
            elif isinstance(draw, Projectile):
                projectileDraws.append(iter)
                if draw.targetProj(frameTime):
                    # trigger ability, get ability by name from payload, then call trigger at projectile location
                    abilityName = draw.payload
                    targetX = draw.locX
                    targetY = draw.locY
                    newTrigger = None
                    # if ability is valid (atm just in the dictionary) trigger effects
                    if abilityName in abilityDictionary.keys():
                        newTrigger = abilityDictionary[abilityName].trigger(draw.caster, targetX, targetY, currentMap, frameTime)
                    else:
                        raise Exception("Unknown ability triggered:"+abilityName)
                    # remove projectile, might not be safe to do mid-loop TODO investigate
                    if newTrigger is not None:
                        currentMap.addDraw(newTrigger)
                    #currentMap.draws.remove(draw)   # TODO current removal conditions are messy and can conflict (if projectile age limit is reached in the same frame as target)
                    draw.setLimit(-1)   # set limit to queue for removal later in frame
                    projectileDraws.pop()
            else:
                if draw.animation != "None":
                    draw.animate(frameTime)
                genericDraws.append(iter)
                #gameDisplay.blit(draw.image, (offX+int(draw.locX-draw.boundX/2), offY+int(draw.locY-draw.boundY/2)))
            #print("Draw age", draw.age)
            draw.age += frameTime
            #print("Frametime", frameTime, "total", draw.age)
            iter += 1


        # draw section
        offX = display_width/2 - testChar.locX
        offY = display_height/2 - testChar.locY
        gameDisplay.blit(currentMap.image, (offX, offY))  # draw map background

        for index in effectDraws:
            curDraw = currentMap.draws[index]
            gameDisplay.blit(curDraw.image, (offX+int(curDraw.locX - curDraw.boundX / 2), offY+int(curDraw.locY - curDraw.boundY / 2)))
        for index in genericDraws:
            curDraw = currentMap.draws[index]
            gameDisplay.blit(curDraw.image, (offX+int(curDraw.locX - curDraw.boundX / 2), offY+int(curDraw.locY - curDraw.boundY / 2)))
        for index in projectileDraws:
            curDraw = currentMap.draws[index]
            gameDisplay.blit(curDraw.image, (offX+int(curDraw.locX - curDraw.boundX / 2), offY+int(curDraw.locY - curDraw.boundY / 2)))
        for index in characterDraws:
            #this forces characters to be drawn last, as well as calls their animate functions in a timely manner
            curDraw = currentMap.draws[index]
            curDraw.animate(frameTime)
            gameDisplay.blit(curDraw.image, (offX+int(curDraw.locX - curDraw.boundX / 2), offY+int(curDraw.locY - curDraw.boundY / 2)))

        # TODO draw ability UI here
        # for starters, just have first ability from testChar file selected, maybe use number keys to change which one is highlighted later
        # display icon should use animation specified by config (new line, can share with skill, does not need to)

        if testChar.alive:
            # life and mana regen, continous effects calculations
            if testChar.currentMana < testChar.getMaxMana():
                # regen 0.1% of missing mana per second per point in mana
                testChar.currentMana += frameTime * (testChar.getMaxMana()-testChar.currentMana) * 0.001 * (0+testChar.mana) #max(1, 0.01 * (testChar.getMaxMana()-testChar.currentMana) )
            if testChar.currentMana > testChar.getMaxMana():
                testChar.currentMana = testChar.getMaxMana()
            # life
            if testChar.currentLife < testChar.getMaxLife():
                testChar.currentLife += frameTime * (testChar.getMaxLife() - testChar.currentLife) * 0.001 * (0+testChar.life) #max(1, 0.01 * (testChar.getMaxLife() - testChar.currentLife))
            if testChar.currentLife > testChar.getMaxLife():
                testChar.currentLife = testChar.getMaxLife()
        else:
            # you are dead, dead, dead
            deadSurface, deadBox = font.render(str("YOU ARE DEAD"), (200, 50, 50))
            gameDisplay.blit(deadSurface, (display_width/2-50, display_height/2-25))
            #print("Final score:", int(aliveTime))
            #time.sleep(2)
            #menu = True

        # draw HUD  # TODO get HUD to scale with screen resolution (atm its all hard coded to fit 1920x1080)
        if testChar.getMaxMana() > 0.0:
            gameDisplay.blit(manaBarBase.image, (manaBarBase.locX, manaBarBase.locY))
            manaFillImage = pygame.transform.scale(manaBarFill.image, (int(160.0*max(0,testChar.currentMana)/(testChar.getMaxMana())), 40))  # TODO update for dynamic asset scaling
            gameDisplay.blit(manaFillImage, (manaBarBase.locX, manaBarBase.locY))
            manaTextSurface, manaTextBox = font.render(str(int(testChar.currentMana)), (0,0,0))   # current/max str(int(testChar.currentMana))+"/"+str(int(testChar.baseMana*1.1**testChar.mana))
            gameDisplay.blit(manaTextSurface, (0,70))

        gameDisplay.blit(lifeBarBase.image, (lifeBarBase.locX, lifeBarBase.locY))
        # fill in bars based on percent current
        lifeFillImage = pygame.transform.scale(lifeBarFill.image, (int(160.0 * max(0,testChar.currentLife) / (testChar.getMaxLife())), 40))
        gameDisplay.blit(lifeFillImage, (lifeBarBase.locX, lifeBarBase.locY))
        # numeric values for life and mana, just current values since the bar establishes percentage
        lifeTextSurface, lifeTextBox = font.render(str(int(testChar.currentLife)), (0, 0, 0))    # current/max str(int(testChar.currentHP)) + "/" + str(int(testChar.baseHP * 1.1 ** testChar.life)
        gameDisplay.blit(lifeTextSurface, (0, 30))
        # draw player
        #gameDisplay.blit(testChar.image, (testChar.locX, testChar.locY))
        aliveTime += frameTime
        frameRate = 1.0/frameTime
        aliveTimeSurface, aliveTimeBox = font.render(str(int(frameRate)), (45, 255, 0))    # current/max str(int(testChar.currentHP)) + "/" + str(int(testChar.baseHP * 1.1 ** testChar.life)
        gameDisplay.blit(aliveTimeSurface, (0, 590))

        # abilities list, use list of abilities found on testChar to populate, draw one box for each (try to evenly space, centered, 0-9 left-right)
        # take note of "active" ability, this one will use the selected UI variant
        # can change which one is highlighted via number keys (should display a number 1+ in box to suggest as much)
        # left mouse click will fire selected ability
        # somehow preview mana cost... draw in purple on mana bar based on amount, draw in orange if not enough
        #print("TestChar knows", testChar.abilities)
        boxWidth, boxHeight = abilityBox.get_size()
        numAbilities = len(list(testChar.abilities.keys()))
        curAbilityNum = 0
        while curAbilityNum < numAbilities:
            dispX = display_width/2-(boxWidth*numAbilities)/2+boxWidth*curAbilityNum
            dispY = display_height-2*boxHeight
            if curAbilityNum == highlightedAbility:
                gameDisplay.blit(highlightBox, (dispX, dispY))
            else:
                gameDisplay.blit(abilityBox, (dispX, dispY))
            abilityName = testChar.abilities[curAbilityNum]
            # TODO render ability icon here

            # check if ability is on cooldown, then draw cooldownBox scaled along height to match percentage of cooldown remaining
            if testChar.cooldowns[abilityName] > 0.0:
                # cooldown is active
                percentRemaining = testChar.cooldowns[abilityName] / abilityDictionary[abilityName].getMaxCooldown(testChar)
                actualHeight = int(percentRemaining * boxHeight) # TODO fix for edge case when cooldown exceeds normal max AKA cooldown changing dynamically
                newCooldownBox = pygame.transform.scale(cooldownBox, (boxWidth, actualHeight))
                gameDisplay.blit(newCooldownBox, (dispX, dispY+(boxHeight-actualHeight)))

            curAbilityNum += 1


        # frame cleanup section
        # reset old movements (only need to remember what moved during this frame)
        for draw in currentMap.draws:
            draw.oldX = draw.locX
            draw.oldY = draw.locY
            if draw.limit is not None:
                #print("Draw limit", draw.limit, "age", draw.age)
                if draw.age >= draw.limit:
                    # which list to remove from...
                    # got to be a cleaner way to do this than checking type again
                    currentMap.draws.remove(draw)

    pygame.display.update()

pygame.quit()
quit()
