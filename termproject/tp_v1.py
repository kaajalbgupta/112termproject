import module_manager
module_manager.review()
from cmu_112_graphics import *
import names, uuid, random, math, copy, decimal
import nltk

#################################################
# classes
#################################################

class Person(object):

    people=[]

    @staticmethod
    def getRandomRGB():
        return Person.rgbString(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    
    # from https://www.cs.cmu.edu/~112/notes/notes-graphics.html
    @staticmethod
    def rgbString(r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

    def __init__(self, name, color, position, room, uid, highlight):
        if(name==None): self.name=names.get_first_name()
        else: self.name=name
        if (color==None): self.color=Person.getRandomRGB()
        else: self.color=color
        if(position==None): self.position=random.randint(55, 625)
        else: self.position=position
        if(room==None): self.room=random.randint(0, 8)
        else: self.room=room
        if(uid==None): self.uid=str(uuid.uuid1())
        else: self.uid=uid
        if(highlight==None): self.highlight=False
        else: self.highliight=highlight
        Person.people.append(self)
        self.information=[]
    
    def __repr__(self):
        return f"Name: {self.name}\nColor: {self.color}\nPosition: {self.position}\nRoom: {self.room}\nUID: {self.uid}\nHighlight: {self.highlight}"

class Protagonist(Person):
    # information should be in the form of a dictionary, with the keys as the num for the murder 
    # and the values a list of all information objects from that murder
    def __init__(self, name, color, position, room, uid, highlight):
        super().__init__(name, color, position, room, uid, highlight)
        self.position=300
        self.room=2
        self.name="Me"
        self.suspects=set()
        self.innocents=set()
        self.unknowns=set()
        self.information=dict()
        #update this after every murder
        self.currInfo=[]

class Player(Person):
    # information should be in the form of a dictionary, with the keys as the num for the murder 
    # and the values a list of all information objects from that murder
    def __init__(self, name, color, position, room, uid, highlight, friends, 
        characteristics, gravity, gravityRoom, stationary, currFriendIndex, direction):
        super().__init__(name, color, position, room, uid, highlight)

        if(friends==None): self.friends=[]
        else: self.friends=friends
        if(characteristics==None): self.characteristics=Characteristics(None, None, None)
        else: self.characteristics=characteristics
        self.information=dict()
        self.gravity=self.position
        self.gravityRoom=self.room
        if(stationary==None): self.stationary=False
        else: self.stationary=stationary
        if(currFriendIndex==None): self.currFriendIndex=-1
        else: self.currFriendIndex=currFriendIndex
        if(direction==None): self.direction=1
        else: self.direction=direction
        self.alive=True
        self.innocent=None
        self.questionsLeft=1
        self.eliminated=False
        self.smiling=False
        self.smilingTimeSoFar=0
        self.smileAfterMurderNumber=None
    
    def __repr__(self):
        return f"Name: {self.name}\nColor: {self.color}\nPosition: {self.position}\nRoom: {self.room}\nUID: {self.uid}\nFriends: {self.friends}\nCharacteristics: {self.characteristics}\nInfo: {self.information}\nHighlight: {self.highlight}\nGravity: {self.gravity}\nStationary: {self.stationary}"

class Villain(Player):
    def __init__(self, name, color, position, room, uid, highlight, friends, characteristics, 
        gravity, gravityRoom, stationary, currFriendIndex, direction, lastKillTimeSeconds):
        super().__init__(name, color, position, room, uid, highlight, friends, characteristics, gravity, gravityRoom, stationary, currFriendIndex, direction)
        if(lastKillTimeSeconds==None): self.lastKillTimeSeconds=random.randint(-110, -90)
        else: self.lastKillTimeSeconds=lastKillTimeSeconds
        self.murders=[]

class Characteristics(object):
    def __init__(self, talkativeness, distractedness, suspicion):
        if(talkativeness==None): self.talkativeness=random.choice(range(0, 100))/100
        else: self.talkativeness=talkativeness
        if(distractedness==None): self.distractedness=random.choice(range(0, 50))/100
        else: self.distractedness=distractedness
        if(suspicion==None): self.suspicion=random.choice(range(0, 100))/100
        else: self.suspicion=suspicion
    
    def __repr__(self):
        return f"Talkativeness: {self.talkativeness}\nDistractedness: {self.distractedness}\nSuspicion: {self.suspicion}"

class Murder(object):
    def __init__(self, victim, peopleInRoom, room):
        self.victim=victim
        self.peopleInRoom=peopleInRoom

class LogicPathObject(object):
    def __init__(self, personUid, information):
        self.personUid=personUid
        self.information=information

class Information(object):
    # innocent should be None if don't know, and true if know
    def __init__(self, numMurder, personUid, room, innocent, givenBy):
        self.numMurder=numMurder
        self.personUid=personUid
        self.room=room
        self.innocent=innocent
        self.givenBy=givenBy
    
    def getHashables(self):
        return (self.numMurder, self.personUid, self.room, self.innocent, self.givenBy)

    def __hash__(self):
        return hash(self.getHashables())
    
    def __eq__(self, other):
        if(other==None): return False
        return (self.numMurder==other.numMurder) and (self.personUid==other.personUid) and (self.innocent==other.innocent)

#################################################
# app, based from cmu_112_graphics.py
#################################################

rooms=["Foyer", "Kitchen", "Living Room", "Family Room", "Bedroom", "Study",  "Garage", "Conservatory"]

# from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html, added value parameter
def make2dList(rows, cols, value):
    return [ ([value] * cols) for row in range(rows) ]

# from https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
def roundHalfUp(d):
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

def appStarted(app):
    app.protag=Protagonist(None, None, None, None, None, None)
    app.numPlayers=9
    app.players=dict()

    for _ in range(app.numPlayers):
        player=Player(None, None, None, None, None, None, None, None, None, None, None, None, None)
        app.players[player.uid]=player

    for uid in app.players:
        app.protag.unknowns.add(uid)
        num=random.randint(0, len(app.players))
        app.players[uid].friends=random.sample(app.players.keys(), num)
        if(app.players[uid].uid in app.players[uid].friends):
            app.players[uid].friends.remove(app.players[uid].uid)

    app.playersToBeInnocent=random.sample(list(app.players.keys()), 2)
    print(app.players[app.playersToBeInnocent[0]].name)
    app.players[app.playersToBeInnocent[0]].smileAfterMurderNumber=0
    app.players[app.playersToBeInnocent[1]].smileAfterMurderNumber=0

    app.villain=Villain(None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    print(app.villain.name)
    app.protag.unknowns.add(app.villain.uid)

    app.radius=30
    app.border=30
    app.ground=app.height-app.border-100
    app.room=2
    app.pressed=False
    app.paused=False
    app.mouseX=-1
    app.mouseY=-1
    app.timerDelay=10
    app.deciseconds=0
    app.secondsPassed=0
    app.minUid=None
    app.showSettings=False
    app.showMap=False
    app.showReportMurderer=False
    app.showNewMurder=False
    app.showChat=False
    app.chatSelected=False
    app.chatString=""
    app.lastMessageTime=None
    app.protagMessage=None
    app.otherMessage=None
    app.gameOver=False
    app.triesLeft=2
    app.victory=False
    app.numMurder=0
    app.lastMurderTime=-1
    app.villainPos=random.randint(0, len(app.players))
    app.lightsOff=False
    app.lightsOffTime=0
    app.killTime=False

    app.settingsWidth=300
    app.settingsHeight=100

    app.chatWidth=500
    app.chatHeight=400

    app.deadImage=app.scaleImage(app.loadImage('https://i.ibb.co/wc13wHx/IMG-0342.png'), 1/10)

    # from https://material.io/resources/icons/
    app.settingsImage=app.scaleImage(app.loadImage('https://i.ibb.co/fDXjVPB/settings.png'), 1)
    app.mapImage=app.scaleImage(app.loadImage('https://i.ibb.co/hHfg4YD/baseline-room-black-18dp.png'), 1)
    app.reportImage=app.scaleImage(app.loadImage('https://i.ibb.co/mHr3Gv1/baseline-report-black-18dp.png'), 1)
    app.closeImage=app.scaleImage(app.loadImage('https://i.ibb.co/CHb1WgL/baseline-cancel-white-18dp.png'), 1)

# call this after every conversation with a person, and call this with newInformation=[] after the death of someone
# numMurder should be the index of the current murder in the villain's list
def updateProtagList(app, newInformation, numMurder, murderTime):
    if(numMurder>0):
        murder=app.villain.murders[numMurder-1]
        for player in app.players:
            if(not player.alive or player.eliminated):
                app.protag.innocents.add(player.uid)
    
    #the other people in the same room are innocent so adding them there
    if(murderTime):
        room=app.protag.room
        if(murder.room!=room):
            otherPeopleInRoom=getPeopleInRoom(app, room)
            for personUid in otherPeopleInRoom:
                app.protag.innocents.add(personUid)

    for info in newInformation:
        if(info.personUid in app.players): player=app.players[info.personUid]
        else: player=app.villain
        if(player.alive and not player.eliminated):
            if(info.innocent==True):
                app.protag.innocents.add(info.personUid)
            elif(info.room==murder.room and info.personUid not in app.protag.innocents):
                app.protag.suspects.add(info.personUid)
            elif(info.personUid not in app.protag.innocents and info.personUid not in app.protag.suspects):
                app.protag.unknowns.add(info.personUid)
    
    app.protag.suspects.difference(app.protag.innocents)
    app.protag.unknowns.difference(app.protag.innocents)
    app.protag.unknowns.difference(app.protag.suspects)

    print(len(app.protag.innocents), len(app.protag.suspects), len(app.protag.unknowns))

# knownInformation here should be a list with the protagonist's most recent information
# see if you can make ONE function from this and the above function?
def checkIfInfoRevealsMurderer(app, knownInformation, numMurder, players, murders):
    murder=murders[numMurder]
    innocents, suspects, unknowns=app.protag.innocents, app.protag.suspects, app.protag.unknowns

    for player in players:
        if(not player.alive or player.eliminated):
            innocents.add(player.uid)

    for info in knownInformation:
        if(info.personUid in app.players): player=app.players[info.personUid]
        else: player=app.villain
        if(player.alive and not player.eliminated):
            if(info.innocent==True):
                innocents.add(info.personUid)
            elif(info.room==murder.room and info.personUid not in innocents):
                suspects.add(info.personUid)
            elif(info.personUid not in innocents and info.personUid not in suspects):
                unknowns.add(info.personUid)
    
    suspects.difference(innocents)
    unknowns.difference(innocents)
    unknowns.difference(suspects)

    if(len(unknowns)==0 and len(suspects)==1 and suspects[0]==app.villain.uid): return True
    else: return False

def getAlivePlayersLeft(players):
    num=0
    for player in players:
        if(player.alive):
            num+=1
    return num

# currInfo's initial info should have the new info in a list
# playersDone should be a list of the players uid when gone through once in this path, initially []
# currMurder should be which murder we're currently on
def getPathsForPlayerToFindMurderer(app, currInfo, playersDone, currMurder, players, murders):
    #Base Case
    if(checkIfInfoRevealsMurderer(app, currInfo, currMurder, players, murders)):
        return playersDone
    elif(len(playersDone)==getAlivePlayersLeft(players)):
        return None
    #Recursive Case
    else:
        workingPaths=[]
        for uid in players:
            if(players[uid].alive and uid not in playersDone):
                newPlayersDone=playersDone+[uid]
                information=players[uid].information[len(players[uid].information)-1]
                for info in information:
                    newCurrInfo=currInfo+[info]
                    returned=getPathsForPlayerToFindMurderer(app, newCurrInfo, newPlayersDone, currMurder, players, murders)
                    if(returned!=None):
                        workingPaths+=[returned]
        return workingPaths

#kill each person in path and see the depth of figuring out that the person is the killer
#if same depth, choose the person with the path to figuring it out that is shortest
# if same length path, kill the least distracted person
def chooseVictimFromPath(app, minPath, players):
    for personUid in minPath:
        players[personUid].alive=False

# make this recursive
# after getting the shortest path for the protag to find, it should loop over each player 
# in the path and kill it and see how short the path would be from there (recursive)
# also see if you can add who else should be in the room, and what's optimal, which room, etc?
def decideTheNextKill(app):
    players=copy.deepcopy(app.players)
    # store min size and min size path
    minPath=None
    minPathSize=None
    uidToKill=None
    for uid in players:
        if(players[uid].alive):
            players[uid].alive=False
            newMurder=Murder(uid, [], players[uid].room)
            newMurders=app.villain.murders+[newMurder]
            paths=getPathsForPlayerToFindMurderer(app, [], 
                [], app.numMurder-1, players, newMurders)

            currMinPath=min(paths, key=len)
            currMinPathSize=len(minPath)
            if(minPathSize==None or currMinPathSize>=minPathSize):
                if(currMinPathSize==minPathSize):
                    if(players[uid].characteristics.distractedness<players[uidToKill].characteristics.distractedness):
                        minPathSize=currMinPathSize
                        minPath=currMinPath
                        uidToKill=uid
                    elif(players[uid].characteristics.distractedness==players[uidToKill].characteristics.distractedness):
                        if(len(players[uid].friends)>len(players[uidToKill].friends)):
                            minPathSize=currMinPathSize
                            minPath=currMinPath
                            uidToKill=uid
                else:    
                    minPathSize=currMinPathSize
                    minPath=currMinPath
                    uidToKill=uid
            print(uidToKill)
    return uidToKill   

def kill(app, personUid):
    # if protag is there, wait for them to leave, then go to the room, turn lights off, kill, 
    # turn light back on (MAKE SURE PROTAG IS NOT IN NEXT ROOM)

    #check if suspects are in room too, at least one
    roomToGo=app.players[personUid].room
    if(app.protag.room!=roomToGo):
        app.villain.gravityRoom=roomToGo
        movePlayerTowardsRoom(app,app.villain)
        app.lightsOff=True
        app.players[personUid].alive=False
        app.killTime=False
        app.numMurder+=1
        app.villain.lastKillTimeSeconds=app.secondsPassed
        app.lastMurderTime=app.secondsPassed
        updateProtagList(app, [], app.numMurder, True)
        app.villain.murders[app.numMurder]=Murder(personUid, getPeopleInRoom(app, roomToGo), roomToGo)
        app.villain.questionsLeft=1
        for uid in app.players:
            app.players[uid].questionsLeft=1
        app.lightsOffTime=0

def eventInBoundaries(x, y, x0, y0):
    return (x0-20<=x<=x0+20) and (y0-20<=y<=y0+20)

# add feature to slow player's movement when surrounded by more people
# WHY are players randomly stopping and piling on top of each other
def movePlayerTowardsRoom(app, player):
    if(player.room!=player.gravityRoom):
        if(player.position<=app.border+app.radius):
            if(player.room!=0):
                player.room-=1
                player.position=app.width-app.border-app.radius-1
        elif(player.position>=app.width-app.border-app.radius):
            if(player.room!=7):
                player.room+=1
                player.position=app.border+app.radius+1
        else:
            if(player.gravityRoom>player.room):
                player.position+=1
            else:
                player.position-=1
    elif(abs(player.gravity-player.position)>180):
        if(player.gravity>player.position):
            player.position+=1
        else:
            player.position-=1

# update the closest player to the protag
def updateClosestPlayer(app):
    if(not app.showChat):
        minUid=None
        minValue=None
        players=list(app.players.keys())+[app.villain.uid]
        for uid in players:
            player=None
            if(uid not in app.players): player=app.villain
            else: player=app.players[uid]
            if(player.room==app.room and player.alive):
                diff=abs(app.protag.position-player.position)
                if(diff<60):
                    if(minValue==None or diff<minValue):
                        minValue=diff
                        minUid=uid
        app.minUid=minUid

def getPeopleInRoom(app, room):
    players=list(app.players.values())+[app.villain]
    people=[]
    for player in players:
        if(player.room==room and player.alive):
            people+=[player.uid]
    return people

# call this when a murder happens
def playerCollectInformation(app, playerUid, isMurderTime):
    room=app.players[playerUid].room
    events=[]
    peopleInRoom=getPeopleInRoom(app, room)
    if(len(peopleInRoom)!=1):
        #check people in room and see if they're doing anything interesting
        for personUid in peopleInRoom:
            if(personUid!=playerUid):
                person=None
                if(personUid==app.villain.uid): person=app.villain
                else: person=app.players[personUid]
                if(isMurderTime):
                    if(person.smiling):
                        info=Information(app.numMurder, personUid, room, True, playerUid)
                        events+=[info]
                    elif(not person.smiling):
                        info=Information(app.numMurder, personUid, room, None, playerUid)
                        events+=[info]
                else:
                    if(person.smiling):
                        info=Information(app.numMurder, personUid, room, True, playerUid)
                        if(info not in app.players[playerUid].information[app.numMurder]):
                            events+=[info]

    #recording the number of events based on distractedness
    numEventsRecorded=len(events)
    eventsRecorded=random.sample(events, numEventsRecorded)

    if(app.numMurder in app.players[playerUid].information):
        app.players[playerUid].information[app.numMurder]+=eventsRecorded
    else:
        app.players[playerUid].information[app.numMurder]=eventsRecorded

def timerFired(app):
    if(not app.paused and app.pressed and not app.showChat):
        #move protag based on mouse movements
        difference=abs(app.mouseX-app.protag.position)
        if(app.mouseY>=app.border+100):
            if(app.mouseX>app.protag.position and 
                not app.protag.position>=app.width-app.border-app.radius):
                app.protag.position+=(difference/120)*10
            elif(app.mouseX<app.protag.position and 
                not app.protag.position<=app.border+app.radius):
                app.protag.position-=(difference/120)*10
                
        if(app.protag.position<=app.border+app.radius):
            if(app.room!=0):
                app.room-=1
                app.protag.position=app.width-app.border-app.radius
                app.pressed=False
        elif(app.protag.position>=app.width-app.border-app.radius):
            if(app.room!=7):
                app.room+=1
                app.protag.position=app.border+app.radius
                app.pressed=False

    if(not app.paused):
        updateClosestPlayer(app)
        players=list(app.players.keys())+[app.villain.uid]
        #move other players
        index=0
        for uid in players:
            index+=1
            if(uid not in app.players): player=app.villain
            else: player=app.players[uid]
            # CHECK THIS PART FOR VILLAIN VS NORMIE
            if(not player.stationary and player.alive):
                #if it's time to change direction
                if(app.secondsPassed%(20+(index*2))==0):
                    num=player.currFriendIndex
                    while(num==player.currFriendIndex):
                        num=random.randint(0, len(player.friends)+len(player.friends)//2+1)
                    #hanging out with friend
                    if(num<len(player.friends)):
                        friend=app.players[player.friends[num]]
                        diff=random.choice([50, -50])
                        if(uid in app.players):
                            app.players[uid].gravity=friend.position+diff
                            app.players[uid].gravityRoom=friend.room
                            app.players[uid].currFriendIndex=num
                        else:
                            app.villain.gravity=friend.position+diff
                            app.villain.gravityRoom=friend.room
                            app.villain.currFriendIndex=num
                    #hanging out at random place
                    elif(num>=len(player.friends)):
                        if(uid in app.players):
                            app.players[uid].gravity=random.randint(55, 625)
                            app.players[uid].gravityRoom=random.randint(0, 8)
                            app.players[uid].currFriendIndex=-1
                        else:
                            app.villain.gravity=random.randint(55, 625)
                            app.villain.gravityRoom=random.randint(0, 8)
                            app.villain.currFriendIndex=-1
                # move around 180 px near gravity
                else:
                    if(player.currFriendIndex!=-1):
                        friend=app.players[player.friends[player.currFriendIndex]]
                        diff=random.choice([50, -50])
                        if(uid in app.players):
                            app.players[uid].gravity=friend.position+diff
                            app.players[uid].gravityRoom=friend.room
                        else:
                            app.villain.gravity=friend.position+diff
                            app.villain.gravityRoom=friend.room
                    if(uid not in app.players): player=app.villain
                    else: player=app.players[uid]
                    if(abs(player.gravity-player.position)>180 or player.room!=player.gravityRoom):
                        movePlayerTowardsRoom(app, player)
                    else:
                        if(player.position-player.gravity>150 or player.position>=app.width-app.border-app.radius):
                            player.direction=-1
                        elif(player.gravity-player.position>150 or player.position<=app.border+app.radius):
                            player.direction=1
                        player.position+=player.direction
        
        #checking if it's time to switch message
        if(app.showChat and (app.lastMessageTime==None or app.secondsPassed-app.lastMessageTime==4)):
            if(app.protagMessage!=None):
                app.otherMessage=computeResponseToMessage(app, app.protagMessage, app.minUid)
                app.lastMessageTime=app.secondsPassed
                app.protagMessage=None

            elif(app.otherMessage!=None):
                app.otherMessage=None
        
        #smiling checking
        if(app.deciseconds%50==0):
            for uid in app.playersToBeInnocent:
                if(app.players[uid].alive):
                    if(app.players[uid].smileAfterMurderNumber==app.numMurder):
                        if(app.secondsPassed-app.lastMurderTime==10):
                            app.players[uid].smiling=True
                        if(app.players[uid].smiling):
                            app.players[uid].smilingTimeSoFar+=1
                        if(app.players[uid].smilingTimeSoFar==11):
                            app.players[uid].smiling=False
            
            if(app.lightsOff):
                app.lightsOffTime+=1
                if(app.lightsOffTime==5):
                    app.lightsOff=False
                    app.lightsOffTime=0
                    app.showNewMurder=True
            
            #checking if it's time to kill
            if(app.killTime or (app.secondsPassed-app.villain.lastKillTimeSeconds)%90==0):
                #app.killTime=True
                #victimUid=decideTheNextKill(app)
                #kill(app, victimUid)
                pass
        
        if(app.secondsPassed==app.lastMurderTime):
            for playerUid in app.players:
                if(app.players[playerUid].alive):
                    playerCollectInformation(app, playerUid, True)
        else:
            for playerUid in app.players:
                if(app.players[playerUid].alive):
                    playerCollectInformation(app, playerUid, False)
    
    app.deciseconds+=1
    if(app.deciseconds%50==0):
        app.secondsPassed+=1

def mouseMoved(app, event):
    if(not app.paused):
        players=list(app.players.keys())+[app.villain.uid]
        for uid in players:
            if(uid in app.players): player=app.players[uid]
            else: player=app.villain
            if(player.alive):
                if(player.position-app.radius<=event.x<=player.position+app.radius and
                    app.ground-(2*app.radius)-1<=event.y<=app.ground-1 and
                    player.room==app.room):
                    if(uid in app.players): app.players[uid].highlight=True
                    else: app.villain.highlight=True
                else:
                    if(uid in app.players): app.players[uid].highlight=False
                    else: app.villain.highlight=False

def getPlayerByName(app, name):
    players=list(app.players.keys())+[app.villain.uid]
    for uid in players:
        if(uid in app.players): player=app.players[uid]
        else: player=app.villain
        if(player.name.lower()==name.lower()):
            return player.uid
    return None

def mousePressed(app, event):
    # when game is over, restart game
    if(app.gameOver and (app.width/2)-(app.settingsWidth/2)<=event.x<=(app.width/2)+(app.settingsWidth/2) and
        (app.height/2)+(app.settingsHeight/2)-40<=event.y<=(app.height/2)+(app.settingsHeight/2)):
        appStarted(app)

    #check if clicked on settings
    if(not app.showChat and eventInBoundaries(event.x, event.y, app.width-app.border-25, app.border+25)):
        app.showSettings=not app.showSettings

    #checking if clicked on no restart game
    if(not app.showChat and app.showSettings and 
        (app.width/2)-(app.settingsWidth/2)<=event.x<=(app.width/2) and
        (app.height/2)+(app.settingsHeight/2)-40<=event.y<=(app.height/2)+(app.settingsHeight/2)):
        app.showSettings=False

    #checking if clicked on no restart game
    if(not app.showChat and app.showSettings and 
        (app.width/2)<=event.x<=(app.width/2)+(app.settingsWidth/2) and
        (app.height/2)+(app.settingsHeight/2)-40<=event.y<=(app.height/2)+(app.settingsHeight/2)):
        appStarted(app)

    #check if clicked on map
    if(not app.showChat and eventInBoundaries(event.x, event.y, app.border+25, app.border+25)):
        app.showMap=not app.showMap
    
    #check if clicked on report
    if(not app.showChat and eventInBoundaries(event.x, event.y, app.border+65, app.border+25)):
        app.showReportMurderer=not app.showReportMurderer

    #checking if clicked on another player
    if(not app.paused):

        '''
        #checking if say button is clicked
        if(app.showChat and (app.width/2)+(app.chatWidth/2)-90<=event.x<=(app.width/2)+(app.chatWidth/2)-10 and
            (app.height/2)+(app.chatHeight/2)-50<=event.y<=(app.height/2)+(app.chatHeight/2)-10):
            app.lastMessageTime=app.secondsPassed
            app.protagMessage=app.chatString
            app.chatString=""
            if(app.minUid in app.players): app.players[app.minUid].questionsLeft=0
            else: app.villain.questionsLeft=0

        #checking if chat box is selected
        if(app.showChat and (app.width/2)-(app.chatWidth/2)+10<=event.x<=(app.width/2)+(app.chatWidth/2)-90 and
            (app.height/2)+(app.chatHeight/2)-50<=event.y<=(app.height/2)+(app.chatHeight/2)-10):
            app.chatSelected=True
        else:
            app.chatSelected=False
        '''

        # checking if chat is open
        if(app.showChat):
            # checking if the innocence button was clicked
            if((app.width/2)-(app.chatWidth/2)+10<=event.x<=(app.width/2)+(app.chatWidth/2)-10 and 
                (app.height/2)+(app.chatHeight/2)-100<=event.y<=(app.height/2)+(app.chatHeight/2)-60):
                name = app.getUserInput('Enter the name of the person whose innocence you\'re checking.')
                if(name!=None):
                    playerUid=getPlayerByName(app, name)
                    app.protagMessage=Information(app.numMurder,playerUid, -1, True, None)
            
            #checking if other's button was cliicked
            if((app.width/2)-(app.chatWidth/2)+10<=event.x<=(app.width/2)+(app.chatWidth/2)-10 and 
                (app.height/2)+(app.chatHeight/2)-50<=event.y<=(app.height/2)+(app.chatHeight/2)-10):
                name = app.getUserInput('Enter the name of the person whose room you\'re checking at the time of the last murder.')
                if(name!=None):
                    playerUid=getPlayerByName(app, name)
                    app.protagMessage=Information(app.numMurder,playerUid, -1, None, None)

        #checking if clicked on talk button
        if(not app.showChat and app.border<=event.x<=app.width-app.border and 
            app.height-app.border-30<=event.y<=app.height-app.border and
            app.minUid!=None):
            app.showChat=True
            if(app.minUid in app.players): app.players[app.minUid].stationary=True
            else: app.villain.stationary=True
        
        #checking if clicked on close new murder alert
        if(app.showNewMurder and (app.width/2)-(app.settingsWidth/2)<=event.x<=(app.width/2)+(app.settingsWidth/2) and
            (app.height/2)+(app.settingsHeight/2)-40<=event.y<=(app.height/2)+(app.settingsHeight/2)):
            app.showNewMurder=False

        #checking if clicked on close talk button
        if(app.showChat and eventInBoundaries(event.x, event.y, 
            (app.width/2)-(app.chatWidth/2)+25, (app.height/2)-(app.chatHeight/2)+25)):
            app.showChat=False
            app.chatSelected=False
            app.chatString=""

        #checking if clicked on any player to talk
        players=list(app.players.keys())+[app.villain.uid]
        for uid in players:
            if(uid in app.players): player=app.players[uid]
            else: player=app.villain
            if(player.alive):
                if(player.position-app.radius<=event.x<=player.position+app.radius and
                    app.ground-(2*app.radius)-1<=event.y<=app.ground-1 and
                    player.room==app.room):
                    if(uid in app.players): app.players[uid].stationary=True
                    else: app.villain.stationary=True
                else:
                    if(not app.showChat or app.minUid!=uid):
                        if(uid in app.players): app.players[uid].stationary=False
                        else: app.villain.stationary=False

    if(not app.paused):
        app.mouseX=event.x
        app.mouseY=event.y
        app.pressed=True

    #checking if clicked on show report murderer button
    if(app.showReportMurderer):
        
        #checking if clicked on any person as murderer
        index=0
        ground1=(app.height/2)-50
        ground2=(app.height/2)+80
        positionX=(app.width/2)-(app.chatWidth/2)+90
        difference=80
        players=copy.deepcopy(list(app.players.values()))
        # from https://stackoverflow.com/questions/49597473/how-can-i-append-an-item-in-a-random-location-in-a-list-in-python
        players.insert(app.villainPos, app.villain)
        index=0
        clickedPlayerUid=None

        for player in players:
            if(index<5):
                if(positionX-app.radius+(difference*index)<=event.x<=positionX+app.radius+(difference*index) and
                    ground1-(2*app.radius)<=event.y<=ground1 and player.alive and not player.eliminated):
                    clickedPlayerUid=player.uid
                    break
            else:
                if(positionX-app.radius+(difference*(index-5))<=event.x<=positionX+app.radius+(difference*(index-5)) and
                    ground2-(2*app.radius)<=event.y<=ground2 and player.alive and not player.eliminated):
                    clickedPlayerUid=player.uid
                    break
            index+=1
    
        if(clickedPlayerUid!=None):
            if(clickedPlayerUid==app.villain.uid):
                app.victory=True
                app.gameOver=True
            else:
                app.triesLeft-=1
                app.players[clickedPlayerUid].eliminated=True
                if(app.triesLeft==0):
                    app.showReportMurderer=False
                    app.gameOver=True
                    app.paused=True

def showInnocence(app, playerUid):
    if(playerUid in app.playersToBeInnocent):
        app.players[playerUid].smiling=True

def mouseDragged(app, event):
    if(not app.paused):
        if(app.pressed):
            app.mouseX=event.x
            app.mouseY=event.y

#playerUid here is the person who the protag is talking to
def computeResponseToMessage(app, message, playerUid):
    # should return a string response
    message=app.protagMessage
    if(playerUid in app.players):
        players=copy.deepcopy(app.players)
        players[app.villain.uid]=app.villain
        informationCurrMurder=players[playerUid].information[message.numMurder]
        # from https://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
        info=next((x for x in informationCurrMurder if x.personUid == message.personUid and x.innocent==message.innocent), None)
        if(info!=None):
            if(info.innocent==True):
                text=f"Yes, {players[info.personUid].name} is innocent."
            else:
                text=f"{players[info.personUid].name} was in the {rooms[info.room]} at the time of the murder."
            updateProtagList(app, [info], app.numMurder, False)
            return text
        else:
            return "I do not have any information on that."
    else:
        # for villains, check about lying and whether or not information would confuse protag more or not
        pass

def keyPressed(app, event):
    if(app.chatSelected):
        if(len(event.key)==1 and len(app.chatString)<65):
            app.chatString+=event.key
        elif(event.key=="Backspace" or event.key=="Delete"):
            if(app.chatString!=""): 
                app.chatString=app.chatString[:len(app.chatString)-1]
        elif(event.key=="Space"):
            app.chatString+=" "

def drawPerson(app, canvas, person):
    positionX=person.position
    if(person.highlight):
        canvas.create_oval(positionX-app.radius, app.ground-(2*app.radius)-1, 
            positionX+app.radius, app.ground-1, fill=person.color, outline="black", width=2)
    else:
        canvas.create_oval(positionX-app.radius, app.ground-(2*app.radius)-1, 
            positionX+app.radius, app.ground-1, fill=person.color, outline=person.color)
    if(person.uid in app.players and person.smiling):
        canvas.create_arc(positionX-20, app.ground-(2*app.radius)-1+10, 
            positionX+20, app.ground-1-10, start=180, extent=180, fill="black")
    # draw death
    if(person.uid in app.players and not person.alive):
        canvas.create_image(positionX, app.ground-(app.radius)-1, image=ImageTk.PhotoImage(app.deadImage))
    canvas.create_text(positionX, app.ground-(2*app.radius)-11, text=person.name)

def drawTitle(app, canvas):
    canvas.create_text(app.width/2, 20+app.border, text=rooms[app.room], font="Helvetica 20 bold")

def drawBorder(app, canvas):
    canvas.create_rectangle(app.border, app.border, app.width-app.border, app.height-app.border)

def drawPlayers(app, canvas):
    for uid in app.players:
        player=app.players[uid]
        if(player.room==app.room):
            drawPerson(app, canvas, player)

def drawSettingsButton(app, canvas):
    canvas.create_image(app.width-app.border-25, app.border+25, 
        image=ImageTk.PhotoImage(app.settingsImage))

def drawMapButton(app, canvas):
    canvas.create_image(app.border+25, app.border+25, 
        image=ImageTk.PhotoImage(app.mapImage))

def drawReportButton(app, canvas):
    canvas.create_image(app.border+65, app.border+25, 
        image=ImageTk.PhotoImage(app.reportImage))

def drawTalkButton(app, canvas, person):
    canvas.create_text(app.width/2, app.height-app.border-15, text=f"TALK TO {person.name}".upper(), fill="white")

def drawChatBubbles(app, canvas):
    ground=(app.height/2)+(app.chatHeight/2)-150
    positionMe=(app.width/2)-(app.chatWidth/2)+80
    positionOther=(app.width/2)+(app.chatWidth/2)-80
    if(app.protagMessage!=None):
        canvas.create_line(positionMe, ground-(2*app.radius)-15, positionMe+5, ground-(2*app.radius)-50)
        canvas.create_line(positionMe, ground-(2*app.radius)-15, positionMe+20, ground-(2*app.radius)-35)
        canvas.create_line(positionMe+5, ground-(2*app.radius)-50, positionMe+5, ground-(2*app.radius)-125)
        canvas.create_line(positionMe+5, ground-(2*app.radius)-125, positionMe+305, ground-(2*app.radius)-125)
        canvas.create_line(positionMe+305, ground-(2*app.radius)-125, positionMe+305, ground-(2*app.radius)-35)
        canvas.create_line(positionMe+305, ground-(2*app.radius)-35, positionMe+20, ground-(2*app.radius)-35)
        text=""
        if(app.protagMessage.personUid in app.players): player=app.players[app.protagMessage.personUid]
        else: player=app.villain
        if(app.protagMessage.innocent==True):
            text=f"Do you know if {player.name} is innocent?"
        else:
            text=f"Where was {player.name} at the time of the murder"
        canvas.create_text(positionMe+(305/2), ground-(2*app.radius)-80, text=text)
    elif(app.otherMessage!=None):
        if(app.minUid in app.players): player=app.players[app.minUid]
        else: player=app.villain
        canvas.create_line(positionOther, ground-(2*app.radius)-15, positionOther-5, ground-(2*app.radius)-50)
        canvas.create_line(positionOther, ground-(2*app.radius)-15, positionOther-20, ground-(2*app.radius)-35)
        canvas.create_line(positionOther-5, ground-(2*app.radius)-50, positionOther-5, ground-(2*app.radius)-125)
        canvas.create_line(positionOther-5, ground-(2*app.radius)-125, positionOther-305, ground-(2*app.radius)-125)
        canvas.create_line(positionOther-305, ground-(2*app.radius)-125, positionOther-305, ground-(2*app.radius)-35)
        canvas.create_line(positionOther-305, ground-(2*app.radius)-35, positionOther-20, ground-(2*app.radius)-35)
        if(player.questionsLeft==0):
            canvas.create_text(positionOther-(305/2), ground-(2*app.radius)-80, text="That's enough questions for now.")
        else:
            canvas.create_text(positionOther-(305/2), ground-(2*app.radius)-80, text=app.otherMessage)

def drawChatInterface(app, canvas):
    canvas.create_rectangle((app.width/2)-(app.chatWidth/2), (app.height/2)-(app.chatHeight/2), 
        (app.width/2)+(app.chatWidth/2), (app.height/2)+(app.chatHeight/2), fill="white")
    canvas.create_rectangle((app.width/2)-(app.chatWidth/2), (app.height/2)-(app.chatHeight/2), 
        (app.width/2)+(app.chatWidth/2), (app.height/2)-(app.chatHeight/2)+50, fill="indigo")
    if(app.minUid in app.players): player=app.players[app.minUid]
    else: player=app.villain
    canvas.create_text(app.width/2, (app.height/2)-(app.chatHeight/2)+25, 
        text=f"TALK TO {player.name}".upper(), fill="white", font="Helvetica 15")
    canvas.create_image((app.width/2)-(app.chatWidth/2)+25, (app.height/2)-(app.chatHeight/2)+25, 
        image=ImageTk.PhotoImage(app.closeImage))

    ground=(app.height/2)+(app.chatHeight/2)-130
    canvas.create_line((app.width/2)-(app.chatWidth/2), ground, 
        (app.width/2)+(app.chatWidth/2), ground)

    positionMe=(app.width/2)-(app.chatWidth/2)+80
    canvas.create_oval(positionMe-app.radius, ground-(2*app.radius)-1, 
            positionMe+app.radius, ground-1, fill=app.protag.color, outline=app.protag.color)
    canvas.create_text(positionMe, ground+10, text=app.protag.name)

    positionOther=(app.width/2)+(app.chatWidth/2)-80
    canvas.create_oval(positionOther-app.radius, ground-(2*app.radius)-1, 
            positionOther+app.radius, ground-1, fill=player.color, outline=player.color)
    canvas.create_text(positionOther, ground+10, text=player.name)

    '''
    canvas.create_rectangle((app.width/2)-(app.chatWidth/2)+10, (app.height/2)+(app.chatHeight/2)-50, 
        (app.width/2)+(app.chatWidth/2)-90, (app.height/2)+(app.chatHeight/2)-10, outline="black" if app.chatSelected else "darkgrey")
    canvas.create_text((((app.width/2)-(app.chatWidth/2)+10)+((app.width/2)+(app.chatWidth/2)-90))/2, 
        (((app.height/2)+(app.chatHeight/2)-50)+((app.height/2)+(app.chatHeight/2)-10))/2, text=app.chatString, fill="black")
    if(len(app.chatString)==65):
        canvas.create_text((((app.width/2)-(app.chatWidth/2)+10)+((app.width/2)+(app.chatWidth/2)-90))/2, 
        (app.height/2)+(app.chatHeight/2)-70, text="Maximum message length met.", fill="black")

    canvas.create_rectangle((app.width/2)+(app.chatWidth/2)-90, (app.height/2)+(app.chatHeight/2)-50, 
        (app.width/2)+(app.chatWidth/2)-10, (app.height/2)+(app.chatHeight/2)-10, fill="indigo", outline="indigo")
    canvas.create_text((app.width/2)+(app.chatWidth/2)-50, (app.height/2)+(app.chatHeight/2)-30, text="SAY", fill="white")
    '''

    canvas.create_rectangle((app.width/2)-(app.chatWidth/2)+10, (app.height/2)+(app.chatHeight/2)-100, 
        (app.width/2)+(app.chatWidth/2)-10, (app.height/2)+(app.chatHeight/2)-60, fill="teal", outline="teal")
    canvas.create_text((app.width/2), (app.height/2)+(app.chatHeight/2)-80, 
        text="ASK ABOUT SOMEONE'S INNOCENCE", fill="white")
    canvas.create_rectangle((app.width/2)-(app.chatWidth/2)+10, (app.height/2)+(app.chatHeight/2)-50, 
        (app.width/2)+(app.chatWidth/2)-10, (app.height/2)+(app.chatHeight/2)-10, fill="indigo", outline="indigo")
    canvas.create_text((app.width/2), (app.height/2)+(app.chatHeight/2)-30, text="ASK ABOUT SOMEONE ELSE'S INNOCENCE DURING LAST MURDER", fill="white")

    drawChatBubbles(app, canvas)

def drawSettingsInterface(app, canvas):
    canvas.create_rectangle((app.width/2)-(app.settingsWidth/2), (app.height/2)-(app.settingsHeight/2), 
        (app.width/2)+(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2), fill="white")
    canvas.create_text(app.width/2, (app.height/2)-(app.settingsHeight/2)+30, text="Restart game?")
    canvas.create_rectangle((app.width/2)-(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2)-40, 
        (app.width/2), (app.height/2)+(app.settingsHeight/2), fill="indigo")
    canvas.create_text((app.width/2)-(app.settingsWidth/4), 
        (app.height/2)+(app.settingsHeight/2)-20, fill="white", text="NO")
    canvas.create_rectangle((app.width/2), (app.height/2)+(app.settingsHeight/2)-40, 
        (app.width/2)+(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2), fill="indigo")
    canvas.create_text((app.width/2)+(app.settingsWidth/4), 
        (app.height/2)+(app.settingsHeight/2)-20, fill="white", text="YES")

def drawWinLoseInterface(app, canvas):
    canvas.create_rectangle((app.width/2)-(app.settingsWidth/2), (app.height/2)-(app.settingsHeight/2), 
        (app.width/2)+(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2), fill="white")
    canvas.create_text(app.width/2, (app.height/2)-(app.settingsHeight/2)+30, text="You Won :)" if app.victory else f"You lost :( The murderer was {app.villain.name}")
    canvas.create_rectangle((app.width/2)-(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2)-40, 
        (app.width/2)+(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2), fill="indigo")
    canvas.create_text((app.width/2), 
        (app.height/2)+(app.settingsHeight/2)-20, fill="white", text="RESTART GAME")

def drawReportMurdererInterface(app, canvas):
    canvas.create_rectangle((app.width/2)-(app.chatWidth/2), (app.height/2)-(app.chatHeight/2), 
        (app.width/2)+(app.chatWidth/2), (app.height/2)+(app.chatHeight/2), fill="white")
    canvas.create_rectangle((app.width/2)-(app.chatWidth/2), (app.height/2)-(app.chatHeight/2), 
        (app.width/2)+(app.chatWidth/2), (app.height/2)-(app.chatHeight/2)+50, fill="indigo")
    canvas.create_text(app.width/2, (app.height/2)-(app.chatHeight/2)+25, 
        text=f"GUESS THE MURDERER", fill="white", font="Helvetica 15")
    canvas.create_image((app.width/2)-(app.chatWidth/2)+25, (app.height/2)-(app.chatHeight/2)+25, 
        image=ImageTk.PhotoImage(app.closeImage))
    ground1=(app.height/2)-50
    ground2=(app.height/2)+80
    positionX=(app.width/2)-(app.chatWidth/2)+90
    difference=80
    players=copy.deepcopy(list(app.players.values()))
    # from https://stackoverflow.com/questions/49597473/how-can-i-append-an-item-in-a-random-location-in-a-list-in-python
    players.insert(app.villainPos, app.villain)
    index=0
    for player in players:
        if(index<5):
            canvas.create_oval(positionX-app.radius+(difference*index), ground1-(2*app.radius), 
                positionX+app.radius+(difference*index), ground1, fill=player.color, outline=player.color)
            canvas.create_text(positionX+(difference*index), ground1+10, text=player.name)
            if(player.eliminated or not player.alive):
                canvas.create_image(positionX+(difference*index), ground1-app.radius, image=ImageTk.PhotoImage(app.deadImage))
        else:
            canvas.create_oval(positionX-app.radius+(difference*(index-5)), ground2-(2*app.radius), 
                positionX+app.radius+(difference*(index-5)), ground2, fill=player.color, outline=player.color)
            canvas.create_text(positionX+(difference*(index-5)), ground2+10, text=player.name)
            if(player.eliminated or not player.alive):
                canvas.create_image(positionX+(difference*(index-5)), ground2-app.radius, image=ImageTk.PhotoImage(app.deadImage))
        index+=1
    canvas.create_text((app.width/2), (app.height/2)+(app.chatHeight/2)-50, text=f"Tries Left: {app.triesLeft}")

def drawNewMurderInterface(app, canvas):
    canvas.create_rectangle((app.width/2)-(app.settingsWidth/2), (app.height/2)-(app.settingsHeight/2), 
        (app.width/2)+(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2), fill="white")
    canvas.create_text(app.width/2, (app.height/2)-(app.settingsHeight/2)+30, 
        text=f"{app.players[app.villain.murders[len(app.villain.murders)-1].victim].name} was killed in the {app.villain.murders[len(app.villain.murders)-1].room}")
    canvas.create_rectangle((app.width/2)-(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2)-40, 
        (app.width/2)+(app.settingsWidth/2), (app.height/2)+(app.settingsHeight/2), fill="indigo")
    canvas.create_text((app.width/2), 
        (app.height/2)+(app.settingsHeight/2)-20, fill="white", text="CONTINUE")

def redrawAll(app, canvas):
    canvas.create_line(app.border, app.ground, app.width-app.border, app.ground)
    drawPerson(app, canvas, app.protag)
    drawTitle(app, canvas)
    drawBorder(app, canvas)
    drawPlayers(app, canvas)
    # draw villain
    if(app.villain.room==app.room):
        drawPerson(app, canvas, app.villain)
    drawSettingsButton(app, canvas)
    drawMapButton(app, canvas)
    if(app.numMurder>0):
        drawReportButton(app, canvas)
    canvas.create_rectangle(app.border, app.height-app.border-30, app.width-app.border, app.height-app.border, fill="black")

    if(app.minUid!=None):
        if(app.minUid in app.players): drawTalkButton(app, canvas, app.players[app.minUid])
        else: drawTalkButton(app, canvas, app.villain)
    if(app.showChat):
        drawChatInterface(app, canvas)
    if(app.showSettings):
        drawSettingsInterface(app, canvas)
    if(app.showReportMurderer):
        drawReportMurdererInterface(app, canvas)
    if(app.showNewMurder):
        drawNewMurderInterface(app, canvas)
    if(app.gameOver):
        drawWinLoseInterface(app, canvas)
    if(app.lightsOff):
        canvas.create_rectangle(0, 0, app.width, app.height, fill="black")

#################################################
# main
#################################################

def main():
    runApp(width=680, height=480)

if __name__ == '__main__':
    main()