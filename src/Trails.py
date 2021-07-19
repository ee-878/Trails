import random
import arcade
#from arcade import gui
from string import ascii_uppercase
from PIL import Image

from arcade.arcade_types import RGB
from arcade.key import KEY_1, NUM_1, NUM_2

SPRITE_SCALING_PLAYER = 0.1
SPRITE_SCALING_BUBBLE = 0.2
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Trails"

#joystick constants
MOVEMENT_SPEED = 7
DEAD_ZONE = 0.25

class Player(arcade.Sprite):
    
    def __init__(self, filename: str, scale: float):
        super().__init__(filename, scale)

        self.trail_point_list = [] #stores the points for showing the trail of the player sprite

        self.joysticks = arcade.get_joysticks()

        if self.joysticks:
            arcade.draw_text("Joystick connected", SCREEN_WIDTH/2, SCREEN_WIDTH/2, arcade.color.BLACK, 20)
            self.joystick = self.joysticks[0]
            self.joystick.open()
            self.joystick.push_handlers(self) #makes this obejct a handler for the joystick events
        else:
            self.joystick=None

    def update(self):
        if self.joystick:
            #handles joystick movement
            self.change_x = self.joystick.x*MOVEMENT_SPEED
            #sets minimum movement of joystick to register movement
            if abs(self.change_x) < DEAD_ZONE:
                self.change_x = 0
            
            self.change_y = -self.joystick.y*MOVEMENT_SPEED
            if abs(self.change_y) < DEAD_ZONE:
                self.change_y = 0

            self.center_x += self.change_x
            self.center_y += self.change_y

            if (abs(self.change_x)>0) or (abs(self.change_y)>0):
                self.trail_point_list.append((self.center_x,self.center_y))
            #mouse movement handled by TrailsView


class Bubble(arcade.Sprite):

    def __init__(self, filename: str, scale: float, id: int):
        super().__init__(filename=filename, scale=scale)
        self.id = id

class InstructionView(arcade.View):

    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.WHITE)
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        arcade.start_render()
        instructionText = "Touch each circle sequentially as quickly as possible.\n Move the cursor to circle 1 to begin."
        arcade.draw_text("Instructions:", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 75, arcade.color.BLACK, font_size=40, anchor_x="center")
        arcade.draw_text(f"{instructionText}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.BLACK, font_size=16, anchor_x="center")
        arcade.draw_text("Press A to start with layout A, or press B to start with layout B. \n \
            Press 1 or 2 for practice modes A or B respectively.", SCREEN_WIDTH/2, SCREEN_HEIGHT/2-100, arcade.color.BLACK, font_size=14, anchor_x="center")

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol==arcade.key.A or symbol==arcade.key.B \
            or symbol==arcade.key.NUM_1 or symbol==arcade.key.NUM_2 \
            or symbol==arcade.key.KEY_1 or symbol==arcade.key.KEY_2:
            game_view = TrailsView(symbol)
            game_view.setup()
            self.window.show_view(game_view)

class GameCompleteView(arcade.View):

    def __init__(self, timeOutput):
        super().__init__()
        self.timeOutput = timeOutput
        arcade.set_background_color(arcade.csscolor.GREEN)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Game Complete", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, font_size=40, anchor_x="center")
        arcade.draw_text(f"Time: {self.timeOutput}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, arcade.color.WHITE, font_size=40, anchor_x="center")
        arcade.draw_text(f"Press A to restart with layout A, or press B to restart with Layout B \n \
            Press 1 or 2 for practice modes A or B respectively.", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 130, arcade.color.WHITE, font_size=14, anchor_x="center")

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol==arcade.key.A or symbol==arcade.key.B \
           or symbol==arcade.key.KEY_1 or symbol==arcade.key.NUM_1 \
           or symbol==arcade.key.KEY_2 or symbol==arcade.key.NUM_2:
            game_view = TrailsView(symbol)
            game_view.setup()
            self.window.show_view(game_view)

class TrailsView(arcade.View):

    def __init__(self, layout_mode_key):
        """Initializer"""
        super().__init__()

        #self.window = window
        #self.uimanager = gui.UIManager(window)


        arcade.set_background_color(arcade.color.WHITE)

        if layout_mode_key==arcade.key.A:
            self.layout_mode="A"
        elif layout_mode_key==arcade.key.B:
            self.layout_mode="B"
        elif layout_mode_key==arcade.key.KEY_1 or layout_mode_key==arcade.key.NUM_1:
            self.layout_mode="A_practice"
        elif layout_mode_key==arcade.key.KEY_2 or layout_mode_key==arcade.key.NUM_2:
            self.layout_mode="B_practice"
        else:
            self.layout_mode=None


        #vars that hold lists of sprites
        self.player_list = None
        self.bubble_list = None

        self.gameStarted = False

        #vars that hold player info
        self.player_sprite = None
        self.nextBubble = 1
        
        self.bubbleCoordsX = []
        self.bubbleCoordsY = []

        if self.layout_mode=="A":
            #these were measured from top left
            self.xCoordsRaw = [553, 424, 633, 658, 409, 526, 367, 171, 218,  309,  
                416,  66,  121, 49,  50,  132, 295, 347, 573, 403, 467, 811, 838,  748, 710]
            self.yCoordsRaw = [797, 921, 920, 417, 546, 655, 721, 906, 1005, 905,
                1028, 1044, 582, 684, 132, 316, 55,  319, 227, 212, 42,  166, 1008, 569, 1027]
            self.basis = [879, 1097]
        elif self.layout_mode=="B":
                self.xCoordsRaw = [542, 388, 612, 757, 905, 575, 242, 129, 282, 989, 
                    988, 55,  758, 490, 757, 910, 839,  316,  158, 289, 667, 940, 80, 171] #all numbers, then all letters
                self.yCoordsRaw = [552, 915, 373, 174, 744, 1028, 551, 56, 140, 65, 
                    1169, 618, 958, 216, 661, 196, 1059, 1144, 718, 339, 38,  860, 1198, 949]
                self.basis = [1077, 1280]
        elif self.layout_mode=="A_practice":
            #corresponds to practice mode A
            self.xCoordsRaw = [706, 809, 1108, 932, 1026, 275, 124, 505]
            self.yCoordsRaw = [447, 172, 331, 417, 649, 598, 308, 294]
            self.basis = [1280, 753]
        elif self.layout_mode=="B_practice":
            #corresponds to practice mode B
            self.xCoordsRaw = [698, 1099, 1010, 127, 817, 930, 264, 504] #all numbers, then all letters
            self.yCoordsRaw = [456, 346, 667, 315, 175, 428, 597, 267]
            self.basis = [1280, 765]
        #else:
            #throw error

        #iterate through each of the raw coordinates and calculate the new coords for the game window
        j = 0
        for x in self.xCoordsRaw:
            self.bubbleCoordsX.append(x/self.basis[0])
            self.bubbleCoordsX[j] = self.bubbleCoordsX[j]*SCREEN_WIDTH
            j = j + 1
        jj = 0
        for y in self.yCoordsRaw:
            self.bubbleCoordsY.append((self.basis[1]-y)/self.basis[1]) #flips the y measurements
            self.bubbleCoordsY[jj] = self.bubbleCoordsY[jj]*SCREEN_HEIGHT
            jj = jj + 1

        self.bubble_count = len(self.bubbleCoordsY)

        self.window.set_mouse_visible(True) #keep mouse visible until game starts

        if self.layout_mode=="A" or self.layout_mode=="A_practice" or self.layout_mode=="B_practice":
            self.timerPos = [10, SCREEN_HEIGHT-20] #top left
        elif self.layout_mode=="B":
            self.timerPos = [SCREEN_WIDTH-85, 10] #bottom middle

        self.elapsedTime = 0.0
        self.timeOutput = "00:00:00"

    def setup(self):
        #set up game, inititialize vars

        #sprite lists
        self.player_list = arcade.SpriteList()
        self.bubble_list = arcade.SpriteList()

        #time
        self.elapsedTime = 0.0

        #set up the player
        self.player_sprite = Player("res/pointer.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = self.bubbleCoordsX[0]
        self.player_sprite.center_y = self.bubbleCoordsY[0]
        self.player_list.append(self.player_sprite)

        #set up the bubbles
        if self.layout_mode=="A" or self.layout_mode=="A_practice":
            for i in range(self.bubble_count):
                bubble = Bubble(f"res/bubble{i+1}.jpeg", SPRITE_SCALING_BUBBLE, id=i+1) #create bubble instance
                bubble.center_x = self.bubbleCoordsX[i] 
                bubble.center_y = self.bubbleCoordsY[i]
                self.bubble_list.append(bubble) 
        elif self.layout_mode=="B" or self.layout_mode=="B_practice":
            id_index = 1
            if self.layout_mode=="B":
                numBubblesCt = 12
            elif self.layout_mode=="B_practice":
                numBubblesCt = 4
            for i in range(numBubblesCt):
                bubble = Bubble(f"res/bubble{i+1}.jpeg", SPRITE_SCALING_BUBBLE, id=id_index) #create bubble instance
                bubble.center_x = self.bubbleCoordsX[i] 
                bubble.center_y = self.bubbleCoordsY[i]
                self.bubble_list.append(bubble) 
                id_index = id_index + 2
            id_index = 2 #id's should alternate between number vs letter bubbles
            for i in range(self.bubble_count-numBubblesCt):
                bubble = Bubble(f"res/bubble{ascii_uppercase[i]}.jpeg", SPRITE_SCALING_BUBBLE, id=id_index) #create bubble instance
                bubble.center_x = self.bubbleCoordsX[i+self.bubble_count-numBubblesCt] 
                bubble.center_y = self.bubbleCoordsY[i+self.bubble_count-numBubblesCt]
                self.bubble_list.append(bubble) 
                id_index = id_index + 2

    def on_draw(self):
        arcade.start_render()

        self.bubble_list.draw()
        self.player_list.draw()

        arcade.draw_text(self.timeOutput, self.timerPos[0], self.timerPos[1], arcade.color.BLACK, 14)
        arcade.draw_line_strip(self.player_sprite.trail_point_list, arcade.color.BLACK, 2)

    def on_mouse_motion(self, x, y, dx, dy):
        #joystick motion is handled in Player sprite class (and timer is handled in update for that case)
        if self.gameStarted == False:
            #starts the game if the player moves the mouse to circle 1 (mouse mode only)
            if ((x>self.bubbleCoordsX[0]-7) and (x<self.bubbleCoordsX[0]+7) and
                 y>self.bubbleCoordsY[0]-7) and (y<self.bubbleCoordsY[0]+7) and not self.player_sprite.joysticks:
                self.gameStarted = True
                self.window.set_mouse_visible(False)
        elif self.gameStarted == True and not self.player_sprite.joystick:
            self.player_sprite.center_x = x
            self.player_sprite.center_y = y
            self.player_sprite.trail_point_list.append((x,y))



    def update(self, delta_time):
        #movement and game logic

        if self.player_sprite.joysticks and \
            self.player_sprite.center_x!=self.bubbleCoordsX[0]\
            and self.player_sprite.center_y!=self.bubbleCoordsY[0]:
            self.gameStarted = True
            self.window.set_mouse_visible(False)

        #run timer if the game has started
        if self.gameStarted == True:
            self.elapsedTime += delta_time
            minutes = int(self.elapsedTime) // 60
            seconds = int(self.elapsedTime) % 60
            seconds_100th = int((self.elapsedTime - seconds) * 100)
            self.timeOutput = f"{minutes:02d}:{seconds:02d}:{seconds_100th:02d}" #print formatting


        self.bubble_list.update()
        self.player_sprite.update()
        
        #list of all sprites that collided with the player sprite
        bubble_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.bubble_list)
        
        for bubble in bubble_hit_list:
            if bubble.id == self.nextBubble:
                #bubble.alpha = 100 #lower opacity when hit
                self.nextBubble += 1
                if self.nextBubble > self.bubble_count:
                    #take screenshot
                    #img = arcade.draw_commands.get_image()
                    #if you get an error here, whitelist the program in Windows settings->controlled filesystem access
                    #img.save(f"./output/{self.subjectID}_{self.layout_mode}_screenshot.png","PNG")
                    complete_view = GameCompleteView(self.timeOutput)
                    self.window.show_view(complete_view)


def main():
    """main method"""
    global SCREEN_WIDTH, SCREEN_HEIGHT #bring these global variables into the context of main
    SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
    SCREEN_WIDTH = round(0.5*SCREEN_WIDTH)
    SCREEN_HEIGHT = SCREEN_WIDTH*(round(11/8.5))
    game_window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    game_window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()