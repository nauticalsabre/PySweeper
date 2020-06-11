#! C:\Program Files\Python37 python
"""
Author: Tyler Hanson
Last worked date: 6/4/2020
Last build  date: 5/25/2020 ver 0.5
version: 0.7
Project: Minesweeper using pygame

Summary:
    Learning project for pygame by creating a minesweeper clone.

    At the moment it all works. Need to figure out a way of organizing
the file. Maybe into modules like the block and such, or just keep it in a
big file format like this.

Features:
- Block clicking and flagging
- unable to click flagged blocks
- expanding clicks (clicking on a blank block will click on nearby blocks)
- middle-click revealed blocks to quick click nearby unflagged blocks if the amount
  of blocks flagged is equal to the amount of nearby bombs (can still end up clicking
  on bombs with this)
- new color changing abilities for the block class, setup a new color in the options menu
- adjust bomb amount in options
- 2 game modes [normal, rush]
- 3 flag image choices [circle, flag, star]
- 3 bomb image choices [bomb, cross, blank]
- board layouts, with ability to change .txt file for custom ones

Features to expand game:
"""

import pygame
import random
import os.path
import math
import json

path_game_images = os.path.join(os.getcwd(), 'Data')    # create base path string to game files

pygame.init()                                           # initialize pygame

screen = pygame.display.set_mode((750,625))             # setup game window with a given width and height


class Button(pygame.sprite.Sprite):
    def __init__(self, pos, image_paths, action_function, *args, parent_panel=None):
        pygame.sprite.Sprite.__init__(self,self.groups)       # MUST BE CALLED TO INITIALIZE PYGAME SPRITE CLASS
        self.button_images = []                               # list of 3 images: 1 > base image | 2 > hover image | 3 > pressed image
        self.is_hovered = False                               # this will tell if the mouse is hovering over the button or not
        self.is_pressed = False                               # this will tell if the mouse has pressed and held onto the button
        self.args = args                                      # store arguments you want to pass to function called from button clicked
        for i in image_paths:                                 # fill list with 3 images using file paths passed to button
            if type(i) == pygame.Surface:                     # if the image_paths passed are Class Surface type, just add the Surface
                temp_image = i
            elif type(i) == str:                              # if the type is a string, load image from file
                temp_image = pygame.image.load(i)
            self.button_images.append(temp_image)
        self.image = self.button_images[0]                    # set image to base image
        self.rect = self.button_images[0].get_rect()          # use base image to create collision rect
        self.rect.x = pos[0]                                  # set x and y position of button using passed pos coordinates
        self.rect.y = pos[1]
        self.action_function = action_function                # assign function to call on click

    def click(self, button):
        if self.is_pressed:                                   # make sure the button is still pressed to continue onto the click action
            if len(self.args) > 0:                            # if there are args passed, then continue the pass to the buttons function
                self.action_function(self.args[0])
            else:                                             # if no args, just call function
                self.action_function()

    def processEvent(self, event):
        mouse_pos = pygame.mouse.get_pos()                              # store mouse pos on event process
        if self.rect.collidepoint(mouse_pos):                           # check if mouse pos is inside the buttons bounds
            if event.type == pygame.MOUSEMOTION:                        # if mouse moved over button, set button to hover
                self.is_hovered = True
            if event.type == pygame.MOUSEBUTTONDOWN:                    # if mouse pressed on button, set button to pressed
                self.is_pressed = True
            if event.type == pygame.MOUSEBUTTONUP and self.is_pressed:  # if mouse released and button is pressed call click()
                self.click(1)
                self.is_pressed = False
        else:                                                           # check events if mouse is outside of button
            if event.type == pygame.MOUSEMOTION:                        # if mouse moved outside of button, set button to unhovered
                self.is_hovered = False
            if event.type == pygame.MOUSEBUTTONUP:                      # if mouse released outside of button, button no longer pressed
                self.is_pressed = False
        self.update()                                                   # call update() to set appropriate image for button state

    def update(self):
        if len(self.button_images) == 3:                      # make sure we have 3 images for the button
            if self.is_pressed:                               # if the button is pressed change image to the pressed version
                self.image = self.button_images[2]
            else:                                             # if the button is not pressed change the image based on whether the mouse is hovering
                if self.is_hovered:                           # over it or not
                    self.image = self.button_images[1]
                else:
                    self.image = self.button_images[0]
        else:                                                 # if button only has 1 image, just use the 1 image
            self.image = self.button_images[0]

class Block(pygame.sprite.Sprite):
    flag_style = "circle"      # style of flag to use
    bomb_style = "bomb"        # style of bomb to use

    # load in the starting images
    image_hidden_surface        = pygame.image.load(os.path.join(path_game_images, "blocks", "block_hidden.png")).convert_alpha()
    image_bomb_surface          = pygame.image.load(os.path.join(path_game_images, "blocks",  "block_bomb_" + bomb_style + ".png")).convert_alpha()
    image_flagged_surface       = pygame.image.load(os.path.join(path_game_images, "blocks",  "block_flag_" + flag_style + ".png")).convert_alpha()
    image_bomb_flagged_surface  = pygame.image.load(os.path.join(path_game_images, "blocks",  "block_bomb_flag_" + flag_style + ".png")).convert_alpha()

    image_revealed_surface = [] # this will hold all 9 revealed block images
    for i in range(9):
        image_revealed_surface.append(pygame.image.load(os.path.join(path_game_images, "blocks", ("block_" + str(i) + ".png"))).convert_alpha())

    # create background surface that gives blocks their color
    background_surface       = pygame.Surface((image_hidden_surface.get_width(),image_hidden_surface.get_height())).convert_alpha()
    block_color_raw         = (45,125,255)     # the raw unaltered color for the blocks
    background_surface.fill(block_color_raw)   # fill background surface with raw color

    bomb_clicked = False                       # store whether a bombs been clicked, will decide game over
    bombs_flagged = 0                          # amount of bombs flagged. value goes down for any block that is flagged, not just bombs

    first_game_click = True                    # whether it's the first click of a new game

    def __init__(self, pos, bl_color):
        pygame.sprite.Sprite.__init__(self,self.groups) # THIS MUST COME FIRST!

        Block.block_color_raw = bl_color      # store the raw color to use for the class

        self.is_bomb        = False           # whether the block is a bomb
        self.is_flagged     = False           # whether the block has been flagged
        self.been_revealed  = False           # whether the blocks already been clicked, used to stop infinite loops
        self.cant_be_bomb   = False           # whether the block can't be a bomb, used during replacement of bombs

        self.pos_x = pos[0]                   # x position of block
        self.pos_y = pos[1]                   # y position of block

        # store row and column of block, use for the gradual shade of color from top-left to bottom-right
        self.x = self.pos_x/Block.image_hidden_surface.get_width()
        self.y = self.pos_y/Block.image_hidden_surface.get_height()

        # the background surface of the instance block, will use this to give each individual block it's own color
        self.background_surface = pygame.Surface((Block.image_hidden_surface.get_width(),Block.image_hidden_surface.get_height()))
        # the amount to add to each r,g,b value of the blocks color to give it a gradually darker shade of the raw color
        # can shade the raw color by a max of 150 (from top-left to bottom-right | (255,255,255) > (105,105,105))
        self.gradient_trans = min(int(math.sqrt( math.pow((self.x*4) - 0, 2) + math.pow((self.y*4) - 0, 2)) - 50), 150)

        self.image  = None                 # define block image
        self.updateImage()                 # call updateImage to setup starting block image

        self.rect = self.image.get_rect()  # create collision rect for mouse interaction

        # create collision rect that will be used to get nearby blocks
        self.neighbor_detection_rect  = self.rect.inflate(self.rect.width,self.rect.height)

        self.rect.x = self.pos_x  # set x and y position of block using passed pos coordinates
        self.rect.y = self.pos_y

        self.neighbor_detection_rect.x = self.rect.x - self.rect.width/2 # set x and y position of neigh rect based on
        self.neighbor_detection_rect.y = self.rect.y - self.rect.width/2 # block collision rect

    def getNearbyNeighbors(self, sprite_group):
        self.group_neighbors = pygame.sprite.Group()
        self.neighbors_group_indices = self.neighbor_detection_rect.collidelistall(sprite_group.sprites())
        for i in self.neighbors_group_indices:
            self.group_neighbors.add(sprite_group.sprites()[i])
        self.group_neighbors.remove(self)
        return self.group_neighbors

    def nearbyBombs(self):
        self.neighbors = self.getNearbyNeighbors(self.groups)
        self.bomb_count = 0
        for n in self.neighbors.sprites():
            if n.isBomb():
                self.bomb_count+=1
        return self.bomb_count

    def nearbyFlags(self):
        self.neighbors = self.getNearbyNeighbors(self.groups)
        self.flag_count = 0
        for n in self.neighbors.sprites():
            if n.isFlagged():
                self.flag_count+=1
        return self.flag_count

    def click(self, button):
        if button == 1 and not self.is_flagged: # handle left-click calls
            self.been_revealed = True

            if Block.first_game_click:
                """ this will check if we should have the opening start click
                that expands a minimum of 3x3 spot"""
                total_blocks = len(self.groups)
                total_bombs = 0
                for block in self.groups:
                    if block.isBomb():
                        total_bombs += 1
                if total_bombs < (total_blocks - 9):

                    if self.isBomb() or self.nearbyBombs() > 0:

                        if self.isBomb():
                            self.bombs_to_replace = self.nearbyBombs() + 1
                        else:
                            self.bombs_to_replace = self.nearbyBombs()
                        self.cant_be_bomb = True
                        self.is_bomb = False
                        for block in self.getNearbyNeighbors(self.groups).sprites():
                            block.cant_be_bomb = True
                            block.is_bomb = False
                        self.replaceBomb(self.bombs_to_replace)

                Block.first_game_click = False
                self.click(1)
            else:
                if self.isBomb():
                    Block.bomb_clicked = True

                elif self.nearbyBombs() == 0:
                    for block in self.getNearbyNeighbors(self.groups).sprites():
                        if block.been_revealed == False:
                            block.click(1)
        elif button == 2 and self.been_revealed: # handle middle-click calls
            if self.nearbyBombs() == self.nearbyFlags():
                self.neighbors = self.getNearbyNeighbors(self.groups)
                if len(self.neighbors) > 0:
                    for block in self.neighbors.sprites():
                        if not block.is_flagged and not block.been_revealed:
                            block.click(1)

        elif button == 3 and not self.been_revealed: # handle right-click calls
            self.toggleFlag()

        self.updateImage()

    def toggleFlag(self):
        self.is_flagged = not self.is_flagged
        if self.is_flagged:
            Block.bombs_flagged -= 1
        else:
            Block.bombs_flagged += 1

    def isFlagged(self):
        return self.is_flagged

    def isBomb(self):
        return self.is_bomb

    def giveBomb(self):
        self.is_bomb = True

    def replaceBomb(self, amount_to_replace):
        while amount_to_replace > 0:
            randn = random.randrange(0,len(self.groups))
            if not self.groups.sprites()[randn].isBomb() and not self.groups.sprites()[randn].cant_be_bomb:
                amount_to_replace -= 1
                self.groups.sprites()[randn].is_bomb = True

    def revealBomb(self):
        if self.isBomb() and self.isFlagged():
            self.image = Block.image_bomb_flagged_surface
            self.been_revealed = True
        elif self.isBomb() and not self.isFlagged():
            self.image = Block.image_bomb_surface
            self.been_revealed = True

    def reveal(self):
        self.been_revealed = True
        self.updateImage()

    def updateImage(self):
        self.block_color = Block.block_color_raw
        red = min(max(self.block_color[0] - self.gradient_trans, 0), 255)
        green = min(max(self.block_color[1] - self.gradient_trans, 0), 255)
        blue = min(max(self.block_color[2] - self.gradient_trans, 0), 255)
        self.block_color = [red,green,blue]

        self.background_surface.fill(self.block_color)
        Block.background_surface.fill(Block.block_color_raw)

        if self.been_revealed:
            if self.isBomb() and Block.bomb_clicked and not self.isFlagged():
                self.image = Block.image_bomb_surface
            elif self.isBomb() and Block.bomb_clicked and self.isFlagged():
                self.image = Block.image_bomb_flagged_surface
            elif self.isBomb() and not Block.bomb_clicked:
                self.image = Block.image_bomb_flagged_surface
            else:
                temp_image = Block.background_surface.copy()
                temp_image.blit(Block.image_revealed_surface[self.nearbyBombs()], (0,0))
                self.image = temp_image.convert_alpha()
        else:
            if self.isFlagged():
                temp_image = self.background_surface.copy()
                temp_image.blit(Block.image_flagged_surface, (0,0))
                self.image = temp_image.convert_alpha()
            else:
                temp_image = self.background_surface.copy()
                temp_image.blit(Block.image_hidden_surface, (0,0))
                self.image = temp_image.convert_alpha()

    def setFlagStyle(new_style):
        Block.flag_style = new_style
        Block.image_flagged_surface = pygame.image.load(os.path.join(path_game_images, "blocks",  "block_flag_" + Block.flag_style + ".png")).convert_alpha()
        Block.image_bomb_flagged_surface = pygame.image.load(os.path.join(path_game_images, "blocks",  "block_bomb_flag_" + Block.flag_style + ".png")).convert_alpha()

    def setBombStyle(new_style):
        Block.bomb_style = new_style
        Block.image_bomb_surface = pygame.image.load(os.path.join(path_game_images, "blocks",  "block_bomb_" + Block.bomb_style + ".png")).convert_alpha()

    def setBlockColor(new_color):
        Block.block_color_raw = new_color

class Slider(pygame.sprite.Sprite):
    def __init__(self, start_value, min_value, max_value, size=[100,20], pos=[0,0], images=[], control_type=0, value_increment=1, parent_panel=None):
        pygame.sprite.Sprite.__init__(self,self.groups)    # must always call the Sprite class __init__ when inheriting from it
        self.min_value = min_value              # minimum value the slider value can be
        self.max_value = max_value              # maximum value the slider value can be
        self.cur_value = start_value            # the value the slider is currently
        self.size = size                        # this is the size of the slider, the first index represent the length of the
                                                # slider, while the second index represents the height. the second index is also
                                                # used for the dimension of the button. so with a height of 20, that means the
                                                # button is a 20 x 20 square.
        self.control_type = control_type        # whether the slider is controlled by using the button only, or clicking anywhere on the rail
                                                # (defaults to rail)

        self.value_increment = value_increment  # increment to use for cur_value (increment of 5 will only allow values divisible by 5)

        # this tells the program if the slider button should follow the mouse's x
        # it should be set to active when the slider has had a mouse button pressed down on it
        # and set to inactive when the mouse button is released
        self.active = False

        if len(images) == 0:
            self.default_image = pygame.surface.Surface((self.size[0],self.size[1]))                 # default surface that will be for the rail and button
            self.default_image.fill((255,255,255))                                                   # just fill it with white
            pygame.draw.rect(self.default_image, (0,0,0), [0,0,self.size[0],self.size[1]], 2)        # then add a black line border
        else:
            self.default_image = pygame.image.load(os.path.join(path_game_images, "sliders", images[0]))

        self.image = self.default_image                                                              # this is the base image for the slider
        self.image.convert_alpha()



        if len(images) == 0:
            self.button_surface = pygame.surface.Surface((self.size[1],self.size[1]))                # set up surface for button
            pygame.draw.rect(self.button_surface, (0,0,0), [0,0,self.size[1],self.size[1]],0)        # make the button just all black with a white line border
            pygame.draw.rect(self.button_surface, (255,255,255), [0,0,self.size[1],self.size[1]],1)
            self.button_surface.convert()
        else:
            self.button_surface = pygame.image.load(os.path.join(path_game_images, "sliders", images[1]))
            self.button_surface.convert()

        self.rect = self.image.get_rect()                                          # this is the base rect for the slider, used to place slider in the window
        self.rect.x = pos[0]                                                                     # and be the hitbox for clicking on the slider
        self.rect.y = pos[1]

        self.padding = self.button_surface.get_width()/2

        self.draw()                                                                              # this will setup image on creation of new slider

    """
    This will be for showing the state of the slider, where the button is mostly
    """
    def draw(self):
        temp_image = self.default_image.copy()                                                   # create copy of default image so we don't overrite it and ruin everything

        # this will convert the location of the button on the slider to a value between 0 and 1
        # such as a slider with values between 0 and 100 with a current value of 25 with return
        # .25 letter you know the button is a quarter of the way through the bar on the left
        normalized_value = ((self.cur_value - self.min_value) / (self.max_value - self.min_value))

        # this is the rect for the button
        self.button_rect = self.button_surface.get_rect()
        self.button_rect.move_ip((normalized_value * (self.rect.width - self.padding * 2) + self.rect.x, self.rect.y))

        # draw the button surface onto the slider surface
        temp_image.blit(self.button_surface, (self.button_rect.x - self.rect.x, 0))

        temp_image.convert()
        self.image = temp_image

    def update(self):
        if(self.active):                                                                                      # will only update slider value and button position if the slider is active
            self.slide_position = pygame.mouse.get_pos()[0] - (self.rect.x + self.padding)                    # button position using the left side of the slider and current mouse x position
            if(self.slide_position > self.rect.width - (self.padding * 2)):                                   # make sure the button doesn't go past the end of the slider
                self.slide_position = self.rect.width - (self.padding * 2)
            if(self.slide_position < 0):                                                                      # make sure the button doesn't go past the beginning of the slider
                self.slide_position = 0

            normalized_value = (self.slide_position - 0) / ((self.rect.width - (self.padding * 2)) - 0)       # get the normalized value of the buttons position on the slider
            # using the normalized value of the buttons position convert it to
            # the value the buttons position is suppose to represent
            #
            # so if you have a 300 pixel wide slider that represents values 0-100
            # if the button is is 150 pixels in from the left, the normalized value
            # is 0.5 so when you get the value of the slider using .5 you know the
            # buttons position represents the value 50
            self.cur_value = int( normalized_value * (self.max_value - self.min_value) + self.min_value  )
            if self.cur_value % self.value_increment != 0:
                self.cur_value = self.cur_value - (self.cur_value % self.value_increment)
            self.draw()

    def processEvent(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos) and self.control_type == 0 or self.button_rect.collidepoint(mouse_pos) and self.control_type == 1:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active = True

        if event.type == pygame.MOUSEBUTTONUP and self.active:
            self.active = False

        self.update()

    def get_value(self):
        return self.cur_value

class ImageSurface(pygame.sprite.Sprite):
    def __init__(self, image_path='', size=[100,100], pos=[0,0], parent_panel=None, **kwargs):
        pygame.sprite.Sprite.__init__(self,self.groups)    # must always call the Sprite class __init__ when inheriting from it

        self.image_path = image_path
        self.size = size

        self.kwargs = kwargs

        if self.image_path is not '':
            self.image = pygame.image.load(self.image_path)
            self.image.convert_alpha()
        else:
            self.image = pygame.surface.Surface((self.size[0],self.size[1]))
            self.image.fill((255,0,255))
            pygame.draw.rect(self.image, (0,0,0), [0,0,self.size[0],self.size[1]], 2)
            self.image.convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self):
        if self.image_path is '':
            if 'sliders' in self.kwargs:
                new_color = (self.kwargs["sliders"][0].cur_value, self.kwargs["sliders"][1].cur_value, self.kwargs["sliders"][2].cur_value)
                self.image.fill(new_color)

class Panel(pygame.sprite.Sprite):
    def __init__(self, size=[100,100], pos=[0,0], image_path=''):
        pygame.sprite.Sprite.__init__(self,self.groups)    # must always call the Sprite class __init__ when inheriting from it

        self.image_path = image_path

        if self.image_path is not '':
            self.panel_surf = pygame.image.load(self.image_path)
        else:
            self.panel_surf = pygame.surface.Surface((size[0],size[1]))
            self.panel_surf.fill((255,255,255))
        self.panel_surf.convert_alpha()

        self.image = self.panel_surf
        self.rect = self.panel_surf.get_rect()

        self.rect.x = pos[0]
        self.rect.y = pos[1]

        self.children_sprites = []

    """
    when removing the panel call closePanel() to delete all the buttons/sliders and the panel itself
    """
    def close(self):
        for child in self.children_sprites:
            child.kill()

        self.kill()

    """
    called every frame to display the color the value of the 3 sliders provide on the small color surface
    """
    def update(self):
        for child in self.children_sprites:
            if isinstance(child, ImageSurface) or isinstance(child, TextBox):
                child.update()

class TextBox(pygame.sprite.Sprite):
    def __init__(self, text='', text_size=14, text_font='Segoe UI', text_color=(255,255,255), pos=[0,0], linked_obj=None):
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.text = text
        self.text_size = text_size
        self.text_font = text_font
        self.text_color = text_color
        self.linked_obj = linked_obj

        self.text_font = pygame.font.SysFont(self.text_font, self.text_size)   # set our font and size
        # my_font = pygame.font.Font(".\fonts\example font.tff", 24) here's an example of importing your own font.
        if self.linked_obj == None:
            self.image = self.text_font.render(self.text, True, self.text_color)   # draw our given message, anti-aliased, with a gray color
        else:
            self.image = self.text_font.render(str(self.linked_obj.get_value()), True, self.text_color)

        self.image.convert_alpha()

        self.pos = pos

        self.rect = self.image.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def update(self):
        if self.linked_obj != None:
            self.image = self.text_font.render(str(self.linked_obj.get_value()), True, self.text_color)

background  = pygame.image.load(os.path.join(path_game_images, "Background.png"))  # create background image
background  = background.convert_alpha()                                           # convert background image for faster blitting                                                   # draw background image to screen

game_icon = pygame.image.load(os.path.join(path_game_images, "block_icon.png"))  # create game icon from .png file
pygame.display.set_icon(game_icon)                                               # set game icon

clock     = pygame.time.Clock()        # create pygame clock object
mainloop  = True                    # create var to control main loop
FPS       = 60                          # desired max. framerate
playtime  = 0                       # storing time played for a game, used for highscores

# this is the template for creating different shaped boards
# 0 represents where blocks go, change from 0 to any other number
# to remove the block
layouts = None
with open(os.path.join(path_game_images, "Boardlayouts.txt"), 'r') as file:
    layouts = json.load(file)

board_layout         = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

bomb_amount          = 90
game_type            = "normal"
game_type_rush_time  = 5

game_over         = False                  # used to determine if you can click on blocks
is_playing        = False                 # when to start the game clock. game is set as playing with first block click of game
first_game_click  = True            # used to make sure you can't click on bomb and help create area to start from

game_options_opened   = False
block_options_opened  = False
board_options_opened  = False
menu_opened           = False

status_message = None

group_all_blocks         = pygame.sprite.Group()   # group of all blocks
group_all_buttons        = pygame.sprite.Group()   # group of all buttons
group_all_sliders        = pygame.sprite.Group()   # group of all the sliders
group_all_panels         = pygame.sprite.Group()   # group of all the panels
group_all_imagesurfaces  = pygame.sprite.Group()
group_all_textboxs       = pygame.sprite.Group()

Block.groups         = group_all_blocks         # assign default group of Block class
Button.groups        = group_all_buttons        # assign default group of Button class
Slider.groups        = group_all_sliders        # assign default group of Slider class
Panel.groups         = group_all_panels         # assign default group of Panel class
ImageSurface.groups  = group_all_imagesurfaces
TextBox.groups       = group_all_textboxs


def setBoardLayout(layout):
    global board_layout, bomb_amount, status_message
    board_layout = layouts[layout]["grid"]
    bomb_amount = layouts[layout]["bomb_default"]
    setupBoard()

"""
call to wipe board of all blocks, reset game variables and setup game for a new game
"""
def setupBoard():
    global playtime, bomb_amount, game_over, is_playing, status_message    # this allows you to change value of global variables in this list
    # sets top window text, tells game version and displays current game sessions best time
    # pygame.display.set_caption("Pygame: MineSweep v0.5 - (Best Time Easy: " + str( (lambda best : best == 999999 and "--- |" or "{:.2f}".format(best_time_easy))(best_time_easy)) +
    #                                                     " Best Time Medium: " + str( (lambda best : best == 999999 and "--- |" or "{:.2f}".format(best_time_medium))(best_time_medium)) +
    #                                                     " Best Time Hard: " + str( (lambda best : best == 999999 and "---)" or "{:.2f}".format(best_time_hard))(best_time_hard)))
    pygame.display.set_caption("Pygame: MineSweep v0.7")
    Block.first_game_click = True   # reset games first click for new game
    game_over = False               # new game so game_over is no longer true
    is_playing = False              # set to False so game timer doesn't immediatly start
    if game_type == "rush":
        playtime = game_type_rush_time
    else:
        playtime = 0

    Block.bomb_clicked = False
    Block.bombs_flagged = 0

    block_color = Block.block_color_raw   # save block color before destroying all the blocks to assign the color to the new batch of blocks

    for block in group_all_blocks:  # go through all blocks calling kill() which should remove the blocks from all groups they are in
        block.kill()                # allowing them to be removed for garbage collection

    if isinstance(status_message, ImageSurface):
        status_message.kill()
        status_message = None

    # create grid of blocks using block dimensions and play fields dimensions
    # giving 1 block worth of space from the left and right, and 2 block worth of
    # space from top and 1 from bottom
    #
    # 22 x 28
    for x in range(1, int(screen.get_rect().width/25)-1):
        for y in range(2, int(screen.get_rect().height/25)-1):
            if board_layout[y-2][x-1] == 0:
                Block([x*25,y*25], block_color)

    list_of_all_blocks = group_all_blocks.sprites()

    if bomb_amount > len(list_of_all_blocks):
        bomb_amount = len(list_of_all_blocks) - 1
    # get amount of bombs to place using the percetage of bombs we want
    total_bombs = bomb_amount

    # cycle through all blocks checking if it is a bomb, if it is NOT a bomb make it one and
    # subtract 1 from total_bombs
    # if it IS a bomb just check another one
    while total_bombs > 0 and len(list_of_all_blocks) > 0:
        randn = int(random.uniform(0, len(list_of_all_blocks)))
        if not list_of_all_blocks[randn].isBomb():
            list_of_all_blocks[randn].giveBomb()
            total_bombs -= 1
            list_of_all_blocks.remove(list_of_all_blocks[randn])

    Block.bombs_flagged = bomb_amount             # let Block class know how many bombs there are in the game

"""
@parameter won_game
pass whether the game is over because we won or not

reveal all blocks that may have not been revealed before game was over
if we won the game check to see if our time is better then our best time
"""
def gameOver(won_game):
    global playtime, best_time_easy, best_time_medium, best_time_hard, game_over, is_playing, status_message

    game_over = True
    is_playing = False                        # we are no longer playing which will pause the game timer
    if game_type == "rush":
        playtime = 0
    for block in group_all_blocks.sprites():  # go through all the blocks and reveal them
        block.revealBomb()

    if won_game:
        status_message = ImageSurface(image_path=os.path.join(path_game_images, "win_message.png"), pos=[25,50])
    else:
        status_message = ImageSurface(image_path=os.path.join(path_game_images, "lost_message.png"), pos=[25,50])

"""
called after interacting with blocks to check win condition

checks if we have clicked on a bomb if so game over, if not it just goes through all the blocks,
sees how many blocks are revealed, how many bomb blocks are flagged, and how many non bomb blocks
are flagged and sees if we meet the conditions to win

"""
def checkWin():
    global game_over

    if Block.bomb_clicked:               # check Blocks bomb clicked var to see if we have lost
        gameOver(False)
    else:                                # if we have not clicked on bomb check winning conditions
        total_blocks_revealed = 0        # used to count how many blocks have been revealed
        total_flagged_blocks = 0         # used to count how many non bomb blocks are flagged
        total_flagged_bombs = 0          # used to count how many bombs are flagged

        for block in group_all_blocks.sprites():    # go through all the blocks counting how many are flagged and clicked
            if block.isBomb() and block.is_flagged:
                total_flagged_bombs += 1
            if not block.isBomb() and block.is_flagged:
                total_flagged_blocks += 1
            if not block.isBomb() and block.been_revealed:
                total_blocks_revealed += 1

        # check whether the counters say we have won the game or not
        # 2 win conditions
        # -> we have flagged all the bombs and none of the other blocks
        # -> we have revealed all the blocks that aren't bombs
        if (total_flagged_bombs == bomb_amount and total_flagged_blocks == 0) or total_blocks_revealed == (len(group_all_blocks.sprites()) - bomb_amount):
            gameOver(True)

rush_time_background = pygame.image.load(os.path.join(path_game_images, "rush_time_background.png")).convert_alpha()
"""
return a surface with a render text of a given size
"""
def write(message="blank message", text_size=26, color=(50,50,50), cfont="Segoe UI", backgrounded=False, background_color=(0,0,0)):
    new_font = pygame.font.SysFont(cfont, text_size)   # set our font and size
    # my_font = pygame.font.Font(".\fonts\example font.tff", 24) here's an example of importing your own font.
    new_text = new_font.render(message, True, color)   # draw our given message, anti-aliased, with a gray color
    if backgrounded:
        temp_surf = rush_time_background.copy()
        temp_surf.blit(new_text, (3,2))
        return temp_surf
    else:
        new_text = new_text.convert_alpha()                     # convert our surface for faster blitting
        return new_text                                         # return our new surface with text written on it
def writeToSurface(message="default", text_size=26, color=(50,50,50), cfont="Segoe UI", write_surface=None, pos=[0,0]):
    if write_surface != None:
        new_font = pygame.font.SysFont(cfont, text_size)   # set our font and size
        # my_font = pygame.font.Font(".\fonts\example font.tff", 24) here's an example of importing your own font.
        new_text = new_font.render(message, True, color)   # draw our given message, anti-aliased, with a gray color
        temp_surf = pygame.Surface((new_text.get_width() + 4, new_text.get_height()))
        temp_surf.fill((255,255,255))
        temp_surf.blit(new_text, (2,0))
        write_surface.blit(temp_surf, pos)

def openMenu():
    global screen, menu_opened
    if menu_opened == False and game_options_opened == False and block_options_opened == False and board_options_opened == False:
        menu_opened = True
        panel_menu = Panel(pos=[300,200],image_path=os.path.join(path_game_images, "menu_background.png"))

        def closeMenu():
            global menu_opened
            menu_opened = False
            panel_menu.close()
        button_close = Button([panel_menu.rect.x + 127,panel_menu.rect.y + 3], [os.path.join(path_game_images, "buttons", "exit", "button_exit.png"),
                                                                                os.path.join(path_game_images, "buttons", "exit", "button_exit_hover.png"),
                                                                                os.path.join(path_game_images, "buttons", "exit", "button_exit_pressed.png")],
                                                                                closeMenu)
        panel_menu.children_sprites.append(button_close)

        def openBlockOptionsFromMenu():
            global menu_opened
            menu_opened = False
            openBlockOptions()
            panel_menu.close()
        button_open_block_options = Button( [panel_menu.rect.x + 21,panel_menu.rect.y + 55], [os.path.join(path_game_images, "buttons", "block_options", "button_block_options.png"),
                                                                                              os.path.join(path_game_images, "buttons", "block_options", "button_block_options_hover.png"),
                                                                                              os.path.join(path_game_images, "buttons", "block_options", "button_block_options_pressed.png")],
                                                                                              openBlockOptionsFromMenu)
        panel_menu.children_sprites.append(button_open_block_options)

        def openGameOptionsFromMenu():
            global menu_opened
            menu_opened = False
            openGameOptions()
            panel_menu.close()
        button_open_game_options = Button( [panel_menu.rect.x + 21,panel_menu.rect.y + 90], [os.path.join(path_game_images, "buttons", "game_options", "button_game_options.png"),
                                                                                             os.path.join(path_game_images, "buttons", "game_options", "button_game_options_hover.png"),
                                                                                             os.path.join(path_game_images, "buttons", "game_options", "button_game_options_pressed.png")],
                                                                                             openGameOptionsFromMenu)
        panel_menu.children_sprites.append(button_open_game_options)

        def openBoardOptionsFromMenu():
            global menu_opened
            menu_opened = False
            openBoardOptions()
            panel_menu.close()
        button_open_board_options = Button( [panel_menu.rect.x + 21,panel_menu.rect.y + 124], [os.path.join(path_game_images, "buttons", "board_options", "button_board_options.png"),
                                                                                               os.path.join(path_game_images, "buttons", "board_options", "button_board_options_hover.png"),
                                                                                               os.path.join(path_game_images, "buttons", "board_options", "button_board_options_pressed.png")],
                                                                                               openBoardOptionsFromMenu)
        panel_menu.children_sprites.append(button_open_board_options)

def openBlockOptions():
    global screen, block_options_opened
    if block_options_opened == False:                                # make sure we don't have another panel open
        block_options_opened = True
        panel_block_options = Panel(pos=[175,175], image_path=os.path.join(path_game_images, "block_options_background.png"))       # create a panel object with a size of 400x300 pixels in position 175, 150 from top-left

        red_slider = Slider(Block.block_color_raw[0],0,255, [200,12], [panel_block_options.rect.x + 41,panel_block_options.rect.y + 66])     # create slider for adjusting red value of block color
        gre_slider = Slider(Block.block_color_raw[1],0,255,[200,12],[panel_block_options.rect.x + 41,panel_block_options.rect.y + 91])    # create slider for adjusting green value of block color
        blu_slider = Slider(Block.block_color_raw[2],0,255,[200,12],[panel_block_options.rect.x + 41,panel_block_options.rect.y + 116])    # create slider for adjusting blue value of block color
        panel_block_options.children_sprites.extend([red_slider, gre_slider, blu_slider])                                                      # add them to panel objects list of sliders

        # create close button to close the options panel
        def closeBlockOptions():
            global block_options_opened
            block_options_opened = False
            panel_block_options.close()
        button_close = Button([panel_block_options.rect.x + 377,panel_block_options.rect.y + 3], [os.path.join(path_game_images, "buttons", "exit", "button_exit.png"),
                                                                                      os.path.join(path_game_images, "buttons", "exit", "button_exit_hover.png"),
                                                                                      os.path.join(path_game_images, "buttons", "exit", "button_exit_pressed.png")],
                                                                                      closeBlockOptions)
        panel_block_options.children_sprites.append(button_close)  # add close button to panel objects list of buttons

        # function that confirm color button using to pass new block color to all the blocks
        def confirmColor():
            Block.setBlockColor((red_slider.cur_value, gre_slider.cur_value, blu_slider.cur_value))
            for blo in group_all_blocks:                                                                 # go through all the blocks in the game
                blo.updateImage()

        # create confirm button for confirming new color choice
        button_confirm_color = Button([panel_block_options.rect.x + 209, panel_block_options.rect.y + 159], [os.path.join(path_game_images, "buttons", "confirm", "button_confirm.png"),
                                                                                                 os.path.join(path_game_images, "buttons", "confirm", "button_confirm_hover.png"),
                                                                                                 os.path.join(path_game_images, "buttons", "confirm", "button_confirm_pressed.png")],
                                                                                                 confirmColor)
        panel_block_options.children_sprites.append(button_confirm_color)  # add confirm button to panel objects list of buttons

        def newFlagStyle():
            style = ""
            if Block.flag_style is "circle":
                style = "flag"
            elif Block.flag_style is "flag":
                style = "star"
            elif Block.flag_style is "star":
                style = "circle"
            Block.setFlagStyle(style)
            for blo in group_all_blocks:                                                                 # go through all the blocks in the game
                blo.updateImage()
            button_switch_flag_style.button_images[0] = Block.image_flagged_surface
        button_switch_flag_style = Button([panel_block_options.rect.x + 316, panel_block_options.rect.y + 65], [Block.image_flagged_surface], newFlagStyle)
        panel_block_options.children_sprites.append(button_switch_flag_style)

        def newBombStyle():
            style = ""
            if Block.bomb_style is "bomb":
                style = "cross"
            elif Block.bomb_style is "cross":
                style = "blank"
            elif Block.bomb_style is "blank":
                style = "bomb"
            Block.setBombStyle(style)
            for blo in group_all_blocks:                                                                 # go through all the blocks in the game
                blo.updateImage()
            button_switch_bomb_style.button_images[0] = Block.image_bomb_surface
        button_switch_bomb_style = Button([panel_block_options.rect.x + 316, panel_block_options.rect.y + 133], [Block.image_bomb_surface], newBombStyle)
        panel_block_options.children_sprites.append(button_switch_bomb_style)

        def returnToMenu():
            global block_options_opened
            block_options_opened = False
            openMenu()
            panel_block_options.close()
        button_return_to_menu = Button([panel_block_options.rect.x + 285, panel_block_options.rect.y + 180], [os.path.join(path_game_images, "buttons", "return", "button_return.png"),
                                                                                                              os.path.join(path_game_images, "buttons", "return", "button_return_hover.png"),
                                                                                                              os.path.join(path_game_images, "buttons", "return", "button_return_pressed.png")],
                                                                                                              returnToMenu)
        panel_block_options.children_sprites.append(button_return_to_menu)

        image_color_preview = ImageSurface(size=[160,30], pos=[panel_block_options.rect.x + 42,panel_block_options.rect.y + 160], sliders=(red_slider, gre_slider, blu_slider))
        image_color_preview_flag = ImageSurface(size=[25,25], pos=[panel_block_options.rect.x + 316,panel_block_options.rect.y + 65], sliders=(red_slider, gre_slider, blu_slider))
        panel_block_options.children_sprites.append(image_color_preview)
        panel_block_options.children_sprites.append(image_color_preview_flag)
        panel_block_options.children_sprites.append(image_color_preview)

def openGameOptions():
    global screen, game_options_opened
    if game_options_opened == False:
        game_options_opened = True
        panel_game_options = Panel(pos=[175,175], image_path=os.path.join(path_game_images, "game_options_background.png"))

        image_gametype_desc = ImageSurface(pos=[panel_game_options.rect.x + 157, panel_game_options.rect.y + 102], image_path=os.path.join(path_game_images, "image_" + game_type + "_desc.png"))
        panel_game_options.children_sprites.append(image_gametype_desc)

        if bomb_amount > 1:
            slider_bomb = Slider(bomb_amount, 1, min(200, len(group_all_blocks) - 1), [265,12], [panel_game_options.rect.x + 39,panel_game_options.rect.y + 64])     # create slider for adjusting red value of block color
            panel_game_options.children_sprites.append(slider_bomb)

            textbox_bomb_amount = TextBox(text_size=18, text_color=(0,0,0), pos=[panel_game_options.rect.x + 312,panel_game_options.rect.y + 56], linked_obj=slider_bomb)
            panel_game_options.children_sprites.append(textbox_bomb_amount)

            def setNewBombAmount():
                global bomb_amount
                bomb_amount = slider_bomb.get_value()
                setupBoard()
            button_confirm_bomb_amount = Button([panel_game_options.rect.x + 345,panel_game_options.rect.y + 59], [os.path.join(path_game_images, "buttons", "confirm", "button_confirm_small.png"),
                                                                                                                   os.path.join(path_game_images, "buttons", "confirm", "button_confirm_small_hover.png"),
                                                                                                                   os.path.join(path_game_images, "buttons", "confirm", "button_confirm_small_pressed.png")],
                                                                                                                   setNewBombAmount)
            panel_game_options.children_sprites.append(button_confirm_bomb_amount)  # add close button to panel objects list of buttons

        # create close button to close the options panel
        def closeGameOptions():
            global game_options_opened
            game_options_opened = False
            panel_game_options.close()
        button_close = Button([panel_game_options.rect.x + 377,panel_game_options.rect.y + 3], [os.path.join(path_game_images, "buttons", "exit", "button_exit.png"),
                                                                                                os.path.join(path_game_images, "buttons", "exit", "button_exit_hover.png"),
                                                                                                os.path.join(path_game_images, "buttons", "exit", "button_exit_pressed.png")],
                                                                                                closeGameOptions)
        panel_game_options.children_sprites.append(button_close)  # add close button to panel objects list of buttons

        def setGameType(gamet):
            global game_type
            game_type = gamet
            setupBoard()
            image_gametype_desc.image = pygame.image.load(os.path.join(path_game_images, "image_" + game_type + "_desc.png"))
            # closeGameOptions()
        button_game_mode_norm = Button([panel_game_options.rect.x + 39,panel_game_options.rect.y + 117], [os.path.join(path_game_images, "buttons", "gametype_normal", "button_gametype_normal.png"),
                                                                                                          os.path.join(path_game_images, "buttons", "gametype_normal", "button_gametype_normal_hover.png"),
                                                                                                          os.path.join(path_game_images, "buttons", "gametype_normal", "button_gametype_normal_pressed.png")],
                                                                                                          setGameType, 'normal')
        panel_game_options.children_sprites.append(button_game_mode_norm)  # add close button to panel objects list of buttons

        button_game_mode_rush = Button([panel_game_options.rect.x + 39,panel_game_options.rect.y + 151], [os.path.join(path_game_images, "buttons", "gametype_rush", "button_gametype_rush.png"),
                                                                                                          os.path.join(path_game_images, "buttons", "gametype_rush", "button_gametype_rush_hover.png"),
                                                                                                          os.path.join(path_game_images, "buttons", "gametype_rush", "button_gametype_rush_pressed.png")],
                                                                                                          setGameType, 'rush')
        panel_game_options.children_sprites.append(button_game_mode_rush)

        def returnToMenu():
            global game_options_opened
            game_options_opened = False
            openMenu()
            panel_game_options.close()
        button_return_to_menu = Button([panel_game_options.rect.x + 285, panel_game_options.rect.y + 195], [os.path.join(path_game_images, "buttons", "return", "button_return.png"),
                                                                                                            os.path.join(path_game_images, "buttons", "return", "button_return_hover.png"),
                                                                                                            os.path.join(path_game_images, "buttons", "return", "button_return_pressed.png")],
                                                                                                            returnToMenu)
        panel_game_options.children_sprites.append(button_return_to_menu)

def openBoardOptions():
    global screen, board_options_opened
    if board_options_opened == False:
        board_options_opened = True

        panel_board_options = Panel(pos=[75,125], image_path=os.path.join(path_game_images, "board_options_background.png"))

        # create close button to close the options panel
        def closeGameOptions():
            global board_options_opened
            board_options_opened = False
            panel_board_options.close()
        button_close = Button([panel_board_options.rect.x + 577,panel_board_options.rect.y + 3], [os.path.join(path_game_images, "buttons", "exit", "button_exit.png"),
                                                                                                  os.path.join(path_game_images, "buttons", "exit", "button_exit_hover.png"),
                                                                                                  os.path.join(path_game_images, "buttons", "exit", "button_exit_pressed.png")],
                                                                                                  closeGameOptions)
        panel_board_options.children_sprites.append(button_close)  # add close button to panel objects list of buttons

        def returnToMenu():
            global board_options_opened
            board_options_opened = False
            openMenu()
            panel_board_options.close()
        button_return_to_menu = Button([panel_board_options.rect.x + 487, panel_board_options.rect.y + 374], [os.path.join(path_game_images, "buttons", "return", "button_return.png"),
                                                                                                              os.path.join(path_game_images, "buttons", "return", "button_return_hover.png"),
                                                                                                              os.path.join(path_game_images, "buttons", "return", "button_return_pressed.png")],
                                                                                                              returnToMenu)
        panel_board_options.children_sprites.append(button_return_to_menu)

        def setBoardLayoutCloseBoardOptions(lay):
            global board_options_opened
            board_options_opened = False
            setBoardLayout(lay)
            panel_board_options.close()

        button_layout_1 = Button([panel_board_options.rect.x + 26, panel_board_options.rect.y + 49], [os.path.join(path_game_images, "buttons", "board_layout", "standard", "button_board_layout_standard.png"),
                                                                                                      os.path.join(path_game_images, "buttons", "board_layout", "standard", "button_board_layout_standard_hover.png"),
                                                                                                      os.path.join(path_game_images, "buttons", "board_layout", "standard", "button_board_layout_standard_pressed.png")],
                                                                                                      setBoardLayoutCloseBoardOptions, 'standard')
        panel_board_options.children_sprites.append(button_layout_1)

        button_layout_2 = Button([panel_board_options.rect.x + 141, panel_board_options.rect.y + 49], [os.path.join(path_game_images, "buttons", "board_layout", "cross", "button_board_layout_cross.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "cross", "button_board_layout_cross_hover.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "cross", "button_board_layout_cross_pressed.png")],
                                                                                                       setBoardLayoutCloseBoardOptions, 'cross')
        panel_board_options.children_sprites.append(button_layout_2)

        button_layout_3 = Button([panel_board_options.rect.x + 256, panel_board_options.rect.y + 49], [os.path.join(path_game_images, "buttons", "board_layout", "four_holes", "button_board_layout_four_holes.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "four_holes", "button_board_layout_four_holes_hover.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "four_holes", "button_board_layout_four_holes_pressed.png")],
                                                                                                       setBoardLayoutCloseBoardOptions, 'four_holes')
        panel_board_options.children_sprites.append(button_layout_3)

        button_layout_4 = Button([panel_board_options.rect.x + 371, panel_board_options.rect.y + 49], [os.path.join(path_game_images, "buttons", "board_layout", "circle", "button_board_layout_circle.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "circle", "button_board_layout_circle_hover.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "circle", "button_board_layout_circle_pressed.png")],
                                                                                                       setBoardLayoutCloseBoardOptions, 'circle')
        panel_board_options.children_sprites.append(button_layout_4)

        button_layout_5 = Button([panel_board_options.rect.x + 486, panel_board_options.rect.y + 49], [os.path.join(path_game_images, "buttons", "board_layout", "skull", "button_board_layout_skull.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "skull", "button_board_layout_skull_hover.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "skull", "button_board_layout_skull_pressed.png")],
                                                                                                       setBoardLayoutCloseBoardOptions, 'skull')
        panel_board_options.children_sprites.append(button_layout_5)

        button_layout_6 = Button([panel_board_options.rect.x + 26, panel_board_options.rect.y + 164], [os.path.join(path_game_images, "buttons", "board_layout", "two_hooks", "button_board_layout_two_hooks.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "two_hooks", "button_board_layout_two_hooks_hover.png"),
                                                                                                       os.path.join(path_game_images, "buttons", "board_layout", "two_hooks", "button_board_layout_two_hooks_pressed.png")],
                                                                                                       setBoardLayoutCloseBoardOptions, 'two_hooks')
        panel_board_options.children_sprites.append(button_layout_6)

        button_layout_7 = Button([panel_board_options.rect.x + 141, panel_board_options.rect.y + 164], [os.path.join(path_game_images, "buttons", "board_layout", "channel", "button_board_layout_channel.png"),
                                                                                                        os.path.join(path_game_images, "buttons", "board_layout", "channel", "button_board_layout_channel_hover.png"),
                                                                                                        os.path.join(path_game_images, "buttons", "board_layout", "channel", "button_board_layout_channel_pressed.png")],
                                                                                                        setBoardLayoutCloseBoardOptions, 'channel')
        panel_board_options.children_sprites.append(button_layout_7)

        button_layout_8 = Button([panel_board_options.rect.x + 256, panel_board_options.rect.y + 164], [os.path.join(path_game_images, "buttons", "board_layout", "python", "button_board_layout_python.png"),
                                                                                                        os.path.join(path_game_images, "buttons", "board_layout", "python", "button_board_layout_python_hover.png"),
                                                                                                        os.path.join(path_game_images, "buttons", "board_layout", "python", "button_board_layout_python_pressed.png")],
                                                                                                        setBoardLayoutCloseBoardOptions, 'python')
        panel_board_options.children_sprites.append(button_layout_8)

        button_layout_9 = Button([panel_board_options.rect.x + 371, panel_board_options.rect.y + 164], [os.path.join(path_game_images, "buttons", "board_layout", "hole", "button_board_layout_hole.png"),
                                                                                                        os.path.join(path_game_images, "buttons", "board_layout", "hole", "button_board_layout_hole_hover.png"),
                                                                                                        os.path.join(path_game_images, "buttons", "board_layout", "hole", "button_board_layout_hole_pressed.png")],
                                                                                                        setBoardLayoutCloseBoardOptions, 'hole')
        panel_board_options.children_sprites.append(button_layout_9)

        button_layout_10 = Button([panel_board_options.rect.x + 486, panel_board_options.rect.y + 164], [os.path.join(path_game_images, "buttons", "board_layout", "zipper", "button_board_layout_zipper.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "zipper", "button_board_layout_zipper_hover.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "zipper", "button_board_layout_zipper_pressed.png")],
                                                                                                         setBoardLayoutCloseBoardOptions, 'zipper')
        panel_board_options.children_sprites.append(button_layout_10)

        button_layout_11 = Button([panel_board_options.rect.x + 26, panel_board_options.rect.y + 279], [os.path.join(path_game_images, "buttons", "board_layout", "custom_one", "button_board_layout_custom_one.png"),
                                                                                                        os.path.join(path_game_images, "buttons", "board_layout", "custom_one", "button_board_layout_custom_one_hover.png"),
                                                                                                        os.path.join(path_game_images, "buttons", "board_layout", "custom_one", "button_board_layout_custom_one_pressed.png")],
                                                                                                        setBoardLayoutCloseBoardOptions, 'custom_one')
        panel_board_options.children_sprites.append(button_layout_11)

        button_layout_12 = Button([panel_board_options.rect.x + 141, panel_board_options.rect.y + 279], [os.path.join(path_game_images, "buttons", "board_layout", "custom_two", "button_board_layout_custom_two.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "custom_two", "button_board_layout_custom_two_hover.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "custom_two", "button_board_layout_custom_two_pressed.png")],
                                                                                                         setBoardLayoutCloseBoardOptions, 'custom_two')
        panel_board_options.children_sprites.append(button_layout_12)

        button_layout_13 = Button([panel_board_options.rect.x + 256, panel_board_options.rect.y + 279], [os.path.join(path_game_images, "buttons", "board_layout", "custom_three", "button_board_layout_custom_three.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "custom_three", "button_board_layout_custom_three_hover.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "custom_three", "button_board_layout_custom_three_pressed.png")],
                                                                                                         setBoardLayoutCloseBoardOptions, 'custom_three')
        panel_board_options.children_sprites.append(button_layout_13)

        button_layout_14 = Button([panel_board_options.rect.x + 371, panel_board_options.rect.y + 279], [os.path.join(path_game_images, "buttons", "board_layout", "custom_four", "button_board_layout_custom_four.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "custom_four", "button_board_layout_custom_four_hover.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "custom_four", "button_board_layout_custom_four_pressed.png")],
                                                                                                         setBoardLayoutCloseBoardOptions, 'custom_four')
        panel_board_options.children_sprites.append(button_layout_14)

        button_layout_15 = Button([panel_board_options.rect.x + 486, panel_board_options.rect.y + 279], [os.path.join(path_game_images, "buttons", "board_layout", "custom_five", "button_board_layout_custom_five.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "custom_five", "button_board_layout_custom_five_hover.png"),
                                                                                                         os.path.join(path_game_images, "buttons", "board_layout", "custom_five", "button_board_layout_custom_five_pressed.png")],
                                                                                                         setBoardLayoutCloseBoardOptions, 'custom_five')
        panel_board_options.children_sprites.append(button_layout_15)



setupBoard()  # setup the board for our first game

restart_button = Button( [354,1], [os.path.join(path_game_images, "buttons", "restart", "button_restart.png"),
                                   os.path.join(path_game_images, "buttons", "restart", "button_restart_hover.png"),
                                   os.path.join(path_game_images, "buttons", "restart", "button_restart_pressed.png")],
                                   setupBoard)  # create restart button with given images, action, and location to appear
menu_button    = Button( [10,10], [os.path.join(path_game_images, "buttons", "options", "button_options.png"),
                                   os.path.join(path_game_images, "buttons", "options", "button_options_hover.png"),
                                   os.path.join(path_game_images, "buttons", "options", "button_options_pressed.png")],
                                   openMenu)


while mainloop:
    milliseconds = clock.tick(FPS)          # milliseconds passed since last frame
    delta_time = milliseconds / 1000.0      # seconds passed since last frame (float)

    if is_playing and len(group_all_panels) == 0:
        if game_type == "rush":
            playtime -= delta_time
        else:
            playtime += delta_time

    if playtime < 0 and game_type == "rush":
        gameOver(False)

    screen.blit(background, (0,0))          # draw our background every frame

    screen.blit(write( str((lambda time : time >= 999.9 and "999.9" or "{:.1f}".format(playtime))(playtime)) ), (135,5))   # draw our game time to screen, if time is above 999 seconds just keep drawing 999
    screen.blit(write("{:.0f}".format(Block.bombs_flagged)), (558,5))                                                  # draw the amount of blocks flagged, used to give rough estimate of bombs left

    mouse_pos = pygame.mouse.get_pos()                  # store mouse position every frame

    for event in pygame.event.get():                    # handle events generated every frame

        for button in group_all_buttons:
                button.processEvent(event)

        for slide in group_all_sliders:
            slide.processEvent(event)

        if event.type == pygame.QUIT:                   # if the windows close button is pressed break out of main loop
            mainloop = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                if len(group_all_panels) > 0:
                    for panel in group_all_panels:
                        panel.close()
                    menu_opened = game_options_opened =  block_options_opened = board_options_opened = False

        if event.type == pygame.MOUSEBUTTONDOWN:        # handle mouse button pressed events
            """
            This will check whether any of the blocks were clicked on.
            It works by using the mouses x and y and checking if any of the blocks rects have
            that coordinate in them.
            If a block says "yes that mouse x and y is within my rect's bounds" then we know
            we clicked on a block.
            """
            for block in group_all_blocks:                            # check all block in our blocks group
                if block.rect.collidepoint(mouse_pos):                # check if the mouses position was in our block when mouse pressed
                    if not game_over and len(group_all_panels) == 0:  # check if the game is over, stops you from clicking blocks when game over, and check if there are no panels open, like options panel
                        if Block.first_game_click:                    # check if it the first click of the game, if so say we are now playing which will start the timer
                            is_playing = True
                        if game_type == "rush" and block.been_revealed == False and event.button == 1:
                            playtime = game_type_rush_time
                        block.click(event.button)                     # call block's click function and pass which mouse button was used

                        checkWin()                                    # check if we have won the game
                        break

    group_all_blocks.draw(screen)              # draw block's image on screen

    group_all_panels.update()                  # call update() on all panels, just the option panel right now, just updates the color preview box
    group_all_panels.draw(screen)              # draw panel's image on screen

    group_all_sliders.draw(screen)             # draw slider's image on the screen

    group_all_imagesurfaces.draw(screen)

    group_all_buttons.draw(screen)             # draw button's image on the screen

    group_all_textboxs.draw(screen)

    if game_type == "rush" and len(group_all_panels) == 0:
        if 25 < mouse_pos[0] < 725 and 50 < mouse_pos[1] < 600:
            screen.blit(write("{:.1f}".format(playtime), text_size=22, color=(255,255,255), cfont="Arial", backgrounded=True), (mouse_pos[0] + 12,mouse_pos[1] + 12))

    # this is equivalent to flip() except with update() you can pass
    # surface rects to only update passed rects.
    # if no rects are passed it works the same way as flip()
    pygame.display.update()
