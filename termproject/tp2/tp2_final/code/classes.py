import names, uuid, random, math, copy, decimal

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
        if(room==None): self.room=random.randint(0, 4)
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
        return f"Name: {self.name}\nInformation: {self.information}"

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
        if(distractedness==None): self.distractedness=random.choice(range(0, 70))/100
        else: self.distractedness=distractedness
        if(suspicion==None): self.suspicion=random.choice(range(0, 100))/100
        else: self.suspicion=suspicion
    
    def __repr__(self):
        return f"Talkativeness: {self.talkativeness}\nDistractedness: {self.distractedness}\nSuspicion: {self.suspicion}"

class Murder(object):
    def __init__(self, victim, peopleInRoom, room):
        self.victim=victim
        self.peopleInRoom=peopleInRoom
        self.room=room

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
    
    def __repr__(self):
        return f"({self.numMurder}, {self.personUid}, {self.room}, {self.innocent}, {self.givenBy})"
    
    def __eq__(self, other):
        if(other==None): return False
        return (self.numMurder==other.numMurder) and (self.personUid==other.personUid) and (self.innocent==other.innocent)