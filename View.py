import pygame
import pygame.freetype
import math
import random
import time
from Model import Ability, Character, Player, Item, Map, Drawable, Projectile, Effect, Loadable
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

#playerCharacter = Loadable("Assets/Characters/TestChar.txt")
#evilGrunt = Loadable("Assets/Characters/EnemyGrunt.txt")    # TODO replace hard-coded loadables with dynamic dictionary entries
#print("Loaded characters:", loadedCharacters)
testChar = Character(loadedCharacters["Jeff"], 80, 160) # TODO player control should be established via team or name matching player current character field TBD
#testChar.move(80, 160)
currentMap.addDraw(testChar)
manaBarBase = Drawable("Assets/ManaBarBase.png", 0, 40)
lifeBarBase = Drawable("Assets/LifeBarBase.png", 0, 0)
manaBarFill = Drawable("Assets/ManaBarFull.png", 0, 40)
lifeBarFill = Drawable("Assets/LifeBarFull.png", 0, 0)

# science values
#testChar.toughness += 5
#testChar.evasion += 5
#testChar.efficiency += 5
testChar.life += 20
testChar.mana += 20 # 20 seems like a pretty good cap for defensive stat totals, good to test extreme specialization vs distributed builds

menu=True
menuBackground = pygame.image.load("Assets/MenuBackground.png").convert_alpha()
continueButton = pygame.image.load("Assets/Continue.png").convert_alpha()
optionsButton = pygame.image.load("Assets/Options.png").convert_alpha()
exitButton = pygame.image.load("Assets/Exit.png").convert_alpha()
gameTitle = pygame.image.load("Assets/GameTitle.png").convert_alpha()

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
        frameTime = clock.tick(60)/1000.0  # get time since last frame, ALSO tell pygame to limit FPS at 60 TODO make configurable
        #print(frameTime)

        playerSpeed = testChar.getMoveSpeed()  #testChar.baseMove * (1.1 ** testChar.movement)
        boost = math.sqrt(playerSpeed*playerSpeed*2)-playerSpeed
        if keyW:
            testChar.locY -= playerSpeed * frameTime
            # bonus speed if only moving on a cardinal axis
            if not keyA and not keyD:
                testChar.locY -= boost * frameTime
        if keyA:
            testChar.locX -= playerSpeed * frameTime
            if not keyW and not keyS:
                testChar.locX -= boost * frameTime
        if keyS:
            testChar.locY += playerSpeed * frameTime
            if not keyA and not keyD:
                testChar.locY += boost * frameTime
        if keyD:
            testChar.locX += playerSpeed * frameTime
            if not keyW and not keyS:
                testChar.locX += boost * frameTime

        # test movement changes, Q slows, R speeds
        #if keyQ:
        #    testChar.application -= 1
        #if keyR:
        #    testChar.application += 1

        # MOVEMENT STAGE

        # boundary enforcement
        # for now just keep within the 800x600
        # trigger all projectiles on reaching a border
        for draw in currentMap.draws:
            border = False
            colRadius = 10
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
                draw.move(newX, newY)
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
                badGuyChar.baseHP = 150
                badGuyChar.currentHP = badGuyChar.getMaxLife()
                currentMap.addDraw(badGuyChar)
                badGuyTimer = random.uniform(2,8)



        # display all objects here
        # draw map objects
        offX = display_width/2 - testChar.locX
        offY = display_height/2 - testChar.locY
        gameDisplay.blit(currentMap.image, (offX, offY))  # draw map background

        # click based actions
        if click:
            targetX, targetY = pygame.mouse.get_pos()
            targetX -= offX
            targetY -= offY
            # newDraw = Drawable("Assets/FireBall.png", targetX, targetY)
            left, middle, right = pygame.mouse.get_pressed()
            if left:
                #newProjectile = acidPit.cast(testChar, targetX, targetY)
                newProjectile = testFireBall.cast(testChar, targetX, targetY)
                if not newProjectile:
                    print("Not enough mana", testChar.currentMana)
                else:
                    currentMap.addDraw(newProjectile)
            elif right:
                newProjectile = acidPit.cast(testChar, targetX, targetY)
                #newProjectile = testSword.cast(testChar, targetX, targetY)
                if not newProjectile:
                    print("Not enough mana", testChar.currentMana)
                    #print("Target out of range")
                else:   # TODO dynamic ability cooldown solution
                    if playerSwordTime > 0.0:
                        print("Attack on cooldown")
                    else:
                        currentMap.addDraw(newProjectile)
                        playerSwordTime = 1.0

        if playerSwordTime > 0.0:
            playerSwordTime -= frameTime

        characterDraws = []    # postpone drawing characters of team "player" until the end of the draw loop
        for draw in currentMap.draws:
            if isinstance(draw, Projectile):
                if draw.moveProj(frameTime):
                    # trigger ability, get ability by name from payload, then call trigger at projectile location
                    abilityName = draw.payload
                    targetX = draw.locX
                    targetY = draw.locY
                    newTrigger = None
                    # if ability is valid (atm just in the dictionary) trigger effects
                    if abilityName in abilityDictionary.keys():
                        newTrigger = abilityDictionary[abilityName].trigger(draw.caster, targetX, targetY, currentMap)
                    else:
                        raise Exception("Unknown ability triggered:"+abilityName)
                    # remove projectile, might not be safe to do mid-loop TODO investigate
                    if newTrigger is not None:
                        currentMap.addDraw(newTrigger)
                    currentMap.draws.remove(draw)
            if isinstance(draw, Effect):
                draw.tick(frameTime)
            if isinstance(draw, Character):
                characterDraws.append(draw)
                #if draw.team == "Player":
                #    continue   #TODO if reimplementing players drawn last, this needs uncommented
                #print("Character is not a player", draw.currentHP, "HP")
                if draw.team != "Player" and draw.alive:
                #elif draw.alive:
                    # npc behavior here
                    # TODO abstract damage functions, auto including toughness, evasion, life, etc. IE Character.damage(amount)
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
                            draw.locX += frameTime * speed * ratX
                            draw.locY += frameTime * speed * ratY

                        else:
                            currentMap.addDraw(newFire)
                            draw.age -= random.uniform(1, 5)
                #continue
            else:
                gameDisplay.blit(draw.image, (offX+int(draw.locX-draw.boundX/2), offY+int(draw.locY-draw.boundY/2)))
            #print("Draw age", draw.age)
            draw.age += frameTime
            #print("Frametime", frameTime, "total", draw.age)
            if draw.limit is not None:
                #print("Draw limit", draw.limit, "age", draw.age)
                if draw.age >= draw.limit:
                    currentMap.draws.remove(draw)
        for draw in characterDraws:
            #this forces characters to be drawn last, as well as calls their animate functions in a timely manner
            draw.animate(frameTime)
            gameDisplay.blit(draw.image, (offX+int(draw.locX - draw.boundX / 2), offY+int(draw.locY - draw.boundY / 2)))


        # life and mana regen, continous effects calculations
        if testChar.currentMana < testChar.getMaxMana():
            # regen 0.1% of missing mana per second per point in mana
            testChar.currentMana += frameTime * (testChar.getMaxMana()-testChar.currentMana) * 0.001 * testChar.mana #max(1, 0.01 * (testChar.getMaxMana()-testChar.currentMana) )
        if testChar.currentMana > testChar.getMaxMana():
            testChar.currentMana = testChar.getMaxMana()
        # life
        if testChar.currentLife < testChar.getMaxLife():
            testChar.currentLife += frameTime * (testChar.getMaxLife() - testChar.currentLife) * 0.001 * testChar.life #max(1, 0.01 * (testChar.getMaxLife() - testChar.currentLife))
        if testChar.currentLife > testChar.getMaxLife():
            testChar.currentLife = testChar.getMaxLife()
        if not testChar.alive:
            # you are dead, dead, dead
            deadSurface, deadBox = font.render(str("YOU ARE DEAD"), (200, 50, 50))
            gameDisplay.blit(deadSurface, (display_width/2-50, display_height/2-25))
            #print("Final score:", int(aliveTime))
            #time.sleep(2)
            #menu = True

        # draw HUD
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

        # frame cleanup section
        # reset old movements (only need to remember what moved during this frame)
        for draw in currentMap.draws:
            draw.oldX = draw.locX
            draw.oldY = draw.locY

    pygame.display.update()

pygame.quit()
quit()
