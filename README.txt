Creation Date: 5-25-2020
Author: Tyler Hanson
Current Version 0.7

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
