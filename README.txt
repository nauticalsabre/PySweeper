Creation Date: 5-25-2020
Author: Tyler Hanson
Current Version 0.5

Version 0.1
	Features:
	- block clicking and flagging (unable to click flagged blocks)
	- expanding clicks (clicking on a blank block will click on nearby blocks)
	- Timer with ability to see best time achieved for current play session
	- 1 color blocks, no effects
	- 1 flag/bomb image
	- timer goes forever
	Controls:
	- Left-click    > reveal blocks contents
	- Right-click   > flag blocks so you can't click on them and mark bombs
	- Middle-click  > expanding clicks
	- Escape        > close game
	- Spacebar      > new game
	
Version 0.2
	Features:
	- same as v0.1
	Controls:
	- Left-click    > reveal blocks contents
	- Right-click   > flag blocks so you can't click on them and mark bombs
	- Middle-click  > expanding clicks
	- Escape        > close game
	- Spacebar      > new game
	Programming Features:
	- Implemented OS independant file lookups
	
Version 0.3
	Features:
	- same as v0.2
	- retart game button
	- change color of blocks using buttons 1-3 (Gray, Green, and Blue)
	- timer now shows tenths of a second
	- timer now only starts when the first block is clicked
	Controls:
	- Left-click    > reveal blocks contents
	- Right-click   > flag blocks so you can't click on them and mark bombs
	- Middle-click  > expanding clicks
	- Escape        > close game
	- 1-3           > changes color of blocks between 3 set colors
	Programming features:
	- Included Simple Button class to implement buttons (game now has restart button)
	- Switched block image handling from purely in click function to independant updateImage
	  function. Now allows blocks to change images based on state whenever called instead of
	  only from interacting with button
	- New block image handling now allows for color changing blocks. Even in the middle
	  of gameplay

Version 0.4
	Features:
	- same as v0.3
	- custom block colors, no longer stuck with the 3 presets
	- simple game options added, now has options button in top-left. When clicked brings up
	  panel with 3 sliders to adjust block color along with a preview of the color and
	  confirmation button
	- timer pauses when options menu open
	- blocks now have color gradient
	Controls:
	- Left-click    > reveal blocks contents
	- Right-click   > flag blocks so you can't click on them and mark bombs
	- Middle-click  > expanding clicks
	- Escape        > close game
	Programming features:
	- updated image handling with blocks for implementation of color gradient
	- removed unnecessary image updating code, no longer get block image files everytime image
	  updating happens
	- added a Panel class, extends from Sprite class, has lists for buttons and sliders you add
	  to the panel object, to handle killing any of them when the panel is closed. really only
	  used for options right now, until it no longer just draw a color block on it, very bare
	  class, just has a close function and arbitrary update for drawing a color square
	- added a Slider class, extends from Sprite class, used to adjust a value between 2 set values.
	  used in options for color selection of r,g,b values
	  
Version 0.5
	Features:
	- block clicking and flagging (unable to click flagged blocks)
	- expanding clicks (clicking on a blank block will click on nearby blocks)
	- restart/options buttons
	- blocks now have color gradient
	- Timer with ability to see best time achieved for current play session
	- timer now only starts when the first block is clicked
	- timer now shows tenths of a second
	- timer pauses when options menu open
	- custom block colors, no longer stuck with the 3 presets
	- custom image choices, now there are 3 types of images for flags, circle, flag, and star.
	  along with 2 types of images for bombs, a bomb, and a cross
	- 3 difficulties added, easy, medium, and hard. Each with there own highscore.
	Controls:
	- Left-click    > reveal blocks contents
	- Right-click   > flag blocks so you can't click on them and mark bombs
	- Middle-click  > expanding clicks
	- Escape        > close game
	Programming Features:
	- Changed image handling on Block class. Block's image is now assembled on click.
	  creates solid color background and layers on preset block outline/shade image
	- sliders knob now has padding. No longer does half the button disappear off the side
	  when at lowest or highest value.
	- Slider class can now take images for the rail and button. If none are provided it
	  draws the simple slider graphics
	- Buttons now have modern button graphics. Now you can tell when you are hovering
	  or pressing a button.
	- Buttons now do there action on mouse button released instead of on press
	
Version 0.6
	Features:
	- block clicking and flagging (unable to click flagged blocks)
	- expanding clicks (middle-clicking on a blank block will click on nearby blocks)
	- restart/options buttons
	- blocks have color gradient
	- timer
	- timer only starts when the first block is clicked
	- timer shows tenths of a second
	- timer pauses when menu's are opened
	- custom block colors
	- custom image choices, 3 types of images for flags, circle, flag, and star.
	  along with 2 types of images for bombs, a bomb, and a cross
	- slider to adjust amount of bombs, from 15-150, in increments of 5
	- 2 game types
		> normal: standard minesweeper, reveal all block or flag all bombs, no time limit
		> rush:   fast-paced mode, 5 seconds to reveal a block, time refreshes on block reveal
	Controls:
	- Left-click    > reveal blocks contents
	- Right-click   > flag blocks so you can't click on them and mark bombs
	- Middle-click  > expanding clicks
	- Escape        > close game
	Programming Features:
	- board layouts implemented, just no setup to use custom board layouts yet
	- highscores removed, since new difficulty adjustment added
	- slider class:
		> sliders button now has padding. No longer does half the button disappear off the side
		  when at lowest or highest value.
		> sliders can now have value increments
		> sliders can now be controlled by either only clicking on the button or the rail, option on creation
	- (new) imagesurface class:
		> imagesurface class to have a sprite that is either a solid color or an image
		> can pass a keyword arg 'sliders' with 3 slider tuple to adjust color of solid color
		  imagesurface object
	- (new) textbox class:
		> textbox class to have sprite that is just a text, or a value
		> can pass an object to textbox that has a get_value function to have the textbox
		  display an objects value (ex. the amount of bombs in the game options menu)
	- button class:
		> can now pass 1 argument to button's parameters that will be used for the passed function
	- panel class:
		> panels will now call update() to any imagesurfaces and textboxs in panel's children_sprites list
	
Version 0.7
	Features:
	- block clicking and flagging (unable to click flagged blocks)
	- expanding clicks (middle-clicking on a blank block will click on nearby blocks)
	- restart/options buttons
	- blocks have color gradient
	- timer
	- timer only starts when the first block is clicked
	- timer shows tenths of a second
	- timer pauses when menu's are opened
	- custom block colors
	- custom image choices, 3 types of images for flags, circle, flag, and star.
	  along with 3 types of images for bombs, a bomb, cross, and blank
	- slider to adjust amount of bombs, from 1-200, in increments of 1
	- 2 game types
		> normal: standard minesweeper, reveal all block or flag all bombs, no time limit
		> rush:   fast-paced mode, 5 seconds to reveal a block, time refreshes on block reveal
	- board layouts
	Controls:
	- Left-click    > reveal blocks contents
	- Right-click   > flag blocks so you can't click on them and mark bombs
	- Middle-click  > expanding clicks
	- Escape        > quick close menus
	Programming Features:
	- set board layouts and allow custom ones
	- max bomb count of 200 unless there are less then 200 blocks, then it's 1 less than total blocks
	- if the amount of bombs is more then the total amount of blocks - 9, you get no start block expand on first click
	- slider class:
		> sliders button now has padding. No longer does half the button disappear off the side
		  when at lowest or highest value.
		> sliders can now have value increments
		> sliders can now be controlled by either only clicking on the button or the rail, option on creation
	- imagesurface class:
		> imagesurface class to have a sprite that is either a solid color or an image
		> can pass a keyword arg 'sliders' with 3 slider tuple to adjust color of solid color
		  imagesurface object
	- textbox class:
		> textbox class to have sprite that is just a text, or a value
		> can pass an object to textbox that has a get_value function to have the textbox
		  display an objects value (ex. the amount of bombs in the game options menu)
	- button class:
		> can now pass 1 argument to button's parameters that will be used for the passed function
	- panel class:
		> panels will now call update() to any imagesurfaces and textboxs in panel's children_sprites list
