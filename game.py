# CS 107, Fall 2018
# Map Class for HaverQuest

#
# Main game file. This file loads all other classes and uses their
# implementations.
# 

import pygame, sys, os, json, time
from pygame.locals import *

# Classes we created
from players import *
from pqueue import *
from map import *
from gameboard import *

class Game:
    """This class ties all of the other classes together, and represents
    the entire game state. It tracks a few things:

    - The current level
    - The configuration of the game
    """
    def __init__(self):
        # Command-line configuration parameters
        self.startX = None
        self.startY = None
        self.endX = None
        self.endY = None

        # Load the configuration
        print("Loading configuration")
        self.loadJson()
    
        # Pull various elements from the configuration file
        height = self.cfg["tileSize"] * self.cfg["screenY"]
        width = self.cfg["tileSize"] * self.cfg["screenX"]
        self.screen = pygame.display.set_mode((height, width))
        self.height = self.cfg["screenY"]
        self.width = self.cfg["screenX"]
        self.tileSize = self.cfg["tileSize"]

        # Set up the observers
        self.observers = []
        self.tickObservers = []

        # Set up and populate the tile cache
        self.tileFactory = TileFactory(self.cfg)
        
        # Initialize PyGame
        pygame.init()

        # Load the first level
        self.loadLevel(1)

        # Have main character register for key events 
        self.registerForEvents(self.mainCharacter)

        # Register for events from clock ticks
        self.registerForClockTick(self.board)
        
        # Finally, set up the game clock time
        self.clock = pygame.time.Clock()

    # Constants for arrows: these must be the same as the map
    # characters from config.json. I.e., the right arrow picture must
    # be specified as 'R' there, etc..
    rightChar = 'r'
    leftChar  = 'l'
    upChar    = 'u'
    downChar  = 'd'

    # Load the JSON-based configuration and initialize the game state
    def loadJson(self):
        try:
            jsonData = open(os.path.join("./config.json")).read()
            self.cfg = json.loads(jsonData)
        except Exception as e:
            print("Could not load configuration file, possible JSON error")
            print(e)
            exit(1)

    # Load level numbered `n`
    def loadLevel(self,n):
        level = self.cfg["levels"][n - 1]
        mapfile = level["file"]
        width = level["width"]
        height = level["height"]
        self.board = GameBoard(self.cfg, level["width"], level["height"])
        # Load these if they aren't specified via the command line
        startX = self.startX or level["startX"]
        startY = self.startY or level["startY"]

        # Create the main character and place him on the screen
        self.mainCharacter = Squirrel((startX,startY), self.board)

        # Optionally load the start and end x values
        endX = self.endX or level["endX"]
        endY = self.endY or level["endY"]
        self.endX = endX
        self.endY = endY

        # Create the "end" tile (i.e., picture of a nut). Once the
        # character reaches this tile, they win the game.
        self.endTile = Exit((endX,endY), self.board)

        # Add the main tile to the board
        self.board.addTile(self.mainCharacter)

        # Add the main tile to the board
        self.board.addTile(self.endTile)

        # Add the enemies / healthpacks / etc...
        if 'characters' in level:
            self.board.setupCharacters(level["characters"])

        # Load a map in from a file
        levelMap = Map(self.tileFactory, mapfile, width, height)
        levelMap.loadMap()
        levelMap.loadToBoard(self.board)
    
    def registerForEvents(self,observer):
        self.observers.append(observer)
    
    def registerForClockTick(self,observer):
        self.tickObservers.append(observer)
    
    # Main Game Loop
    def gameLoop(self):
        ticks = 0
        running = True
        fps    = 10
        millis = int(round(time.time() * fps))
        while running:
            self.clock.tick_busy_loop(40)
            ticks += 1

            nmillis = int(round(time.time() * fps))
            
            # Is it time to tick the clock again yet..?
            if (nmillis > millis):
                # Process all the clock tick observers
                for observer in self.tickObservers:
                    observer.clockTick(fps,nmillis-millis)
            
            # Update clock
            millis = nmillis

            # Process events to happen in the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False

                for observer in self.observers:
                    observer.handleEvent(event)

            # Redraw the screen
            self.board.renderScreen(self.screen)
            pygame.display.update()

# Play the game
Game().gameLoop()
