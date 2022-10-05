# minesweeper_bot
Bot that plays Google Minesweeper: https://www.google.com/fbx?fbx=minesweeper
Relatively easily configurable for different computers and modes, but is currently set to only play at the link above, in Hard mode, for a 4k screen, at 250% screen scaling on Windows (I believe?)

To modify to work on any computer, you'll need to modify all of the calls to click() that have hardcoded inputs. This tool is very helpful for getting the coordinates of the mouse: https://sourceforge.net/projects/mpos/

You'll also need to use a snipping tool to take a screenshot that includes the board (all of the green tiles) with a little buffer on the edges (as far to the left side of the screen as possible), and save it in the same file as this program as 'board.png'.

You'll need to get the coordinates of the browser refresh button, the tab of the minesweeper link, the mode select button, the mode you want to play, and a blank portion of the screen.

You'll also have to change the number of rows and columns for any mode other than hard.

Note: Even though it is most definitely possible with the above instructions, this program is currently NOT intended to be seamless to run on computers other than mine, and the code is presented more as something to learn from than something to use. If trying to actually use this problem, it is likely you will run into bugs or have to make modifications beyond those listed above. You'll also have to dig into the program to understand where to actually input the above recommended modifications because while they are commented, they are not separated from the functions they are in. 

Second note: The code is absolutely awful and if I were to rewrite it would look very different. It works, and not much more than that.
