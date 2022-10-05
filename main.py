#800x600 resolution!
#0=unexp
#9=zero
#10=bomb


import pyautogui as gui
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import time
from time import sleep
from PIL import ImageGrab
from PIL import Image
from operator import add
import random
import mouse
import cv2 as cv

######################################################################################### Functions

#################################################################### Image processing

def pixsame(pix1,pix2,toler): # Tests if two pixels match based on a tolerance of maximum difference between R/G/B values
    dc = [abs(pix1[0] - pix2[0]), abs(pix1[1] - pix2[1]), abs(pix1[2] - pix2[2])]
    if max(dc) < toler:
        return True
    else:
        return False

def pixgrabmatch(ii,jj,pix,toler): # Gets pixel at certain coordinate in boardimg and tests if it matches other pixel
    return pixsame(boardimg.getpixel((ii,jj)), pix, toler)

def imagegrabprint(): # Adds black dots to each 'polling' square on boardimg, then prints it 
    for i in bx:
        for j in by:
            boardimg.putpixel((i,j),(0,0,0))
    boardimg.show()

def visionprint(): # Prints a grid of the code's vision of the board, with green = unexplored, blue = 1, yellow = 2, ... black = bomb.
    cmap = colors.ListedColormap(['green','blue','yellow','red','purple','orange','cyan','white','black'])
    bounds = [0,1,2,3,4,5,6,9,9.5,11]
    norm = colors.BoundaryNorm(bounds,cmap.N)
    fig, ax = plt.subplots()
    #board2 = np.flip(board,axis=0)
    #board2 = np.flip(board2,axis=1)
    board2 = np.swapaxes(board,0,1)
   
    ax.imshow(board2,cmap=cmap,norm=norm)
    ax.grid(which='major',axis='both',linestyle='-',color='k',linewidth=0.5)
    ax.set_xticks(np.arange(0,cols,1))
    ax.set_yticks(np.arange(0,rows,1))
    plt.show()

def boardprint(): # Prints boardimg and code's vision of board
   imagegrabprint()
   visionprint()

#################################################################### Game loop

def click(x,y): # Left clicks at coordinates on screen
    mouse.move(x,y, absolute=True)
    #time.sleep(0.001*slowdown)
    mouse.click(button='left')
    #time.sleep(0.001*slowdown)
def rclick(x,y): # Right clicks at coordinates on screen
    mouse.move(x,y, absolute=True)
    #time.sleep(0.001*slowdown)
    mouse.click(button='right')
    #time.sleep(0.001*slowdown)

def gclick(x,y): # Clicks at coordinates on game grid
    global clicks
    px = boardloc[0]+bx[x]
    py = boardloc[1]+by[y]
    click(px,py)
    clicks+=1

def boardscan(): # Scans the current board
    global success
    global boardimg
    boardimg = ImageGrab.grab(bbox=boardloc) # Screenshots board bounding box 
    for i in range(cols): 
        for j in range(rows): # For each game tile
            if board[i,j] == 0: # If it is unexplored
                pix = boardimg.getpixel((bx[i],by[j])) # Get its pixel
                if pixsame(pix,u1,tol) or pixsame(pix,u2,tol):
                    board[i,j] = 0 # If it is still green, set to unexplored
                elif pixsame(pix,b1,tol) or pixsame(pix,b2,tol):
                    board[i,j] = 9 # If it is tan, set to empty
                else: # If it is not unexplored or tan
                    w=1
                    for z in colorz:
                        if pixsame(pix,z,tol): # If it matches any number's color
                            board[i,j] = w # Set it to that number, and stop searching through colors
                            break
                        w+=1
                    if board[i,j] == 0: # If it is no longer unexplored, not empty, and does not match any number (no match found)
                        board[i,j] = 1 # Set it to number 1 (which is the tile with the highest rate of being misread, so it is the best assumption to make)

    

def bombscan(): # Updates which tiles are bombs based on currently available information
    for i in range(cols):
        for j in range(rows): # For each game tile
            num = board[i,j] 
            if 0 < num < 9: # If the tile is not a bomb and has bombs around it
                unexplored = 0
                for w in search: # For each tile bordering the tile
                    if ttile(i,j,w) == 0 or ttile(i,j,w) == 10: # If it is unexplored or a bomb
                        unexplored+=1
                if num == unexplored: # If the number of unexplored and bomb tiles around a tile is equal to its number
                    for w in search: # For each bordering tile 
                        if ttile(i,j,w) == 0: # If it is unexplored 
                            board[i+w[0],j+w[1]] = 10 # Actually it is a bomb
                            #click(button='right',x=boardloc[0]+bx[i+w[0]],y=boardloc[1]+by[j+w[1]])
                            #print('There is a bomb at %d,%d. I am looking at %d,%d, and it has %d unexplored neighbors.'%(i+w[0],j+w[1],i,j,unexplored))

def clickscan(): # Clicks on tiles
    global clicks 
    clicks = 0 # Counter
    for i in range(cols):
        for j in range(rows): # For each game tile
            bombs = 0
            num = board[i,j] 
            if 0 < num < 9: # If the tile is not a bomb and has bombs around it
                for w in search: # For each bordering tile
                    if ttile(i,j,w) == 10: # If the bordering tile is a bomb
                        bombs+=1 # Add bomb to counter
                        #print('bomb at= %d, %d' %(i+w[0],j+w[1]))
                if bombs == num: # If number of bordering bombs is equal to tile's number
                    for w in search: # For each bordering tile
                        if ttile(i,j,w) == 0: # If tile is unexplored
                            gclick(i+w[0],j+w[1]) # Click on tile
                            #board[i+w[0],j+w[1]] = -1
                            #time.sleep(0.01*slowdown)
                            #print('I want to click on %d,%d. %d, %d has %d bombs and is %d num.' % (i+w[0],j+w[1],i,j,bombs))
    if clicks == 0: # If there were no 100% safe clicks
        best = 10
        bclick = (0,0)
        #visionprint()
        #print('tryna click around',bestclick)
        for i in range(cols):
            if clicks == 0:
                for j in range(rows): # For each game tile
                    if clicks == 0:
                        num = board[i,j]
                        prox = 0
                        if num == 0: # If tile is unexplored
                            for w in search: # For each bordering tile
                                test = ttile(i,j,w)
                                if 0 < test < 9: # If bordering tile is not a bomb and has bombs around it
                                    prox+= test # Add number of bombs of bordering tile to counter
                            if prox == 1: # If tile has only one bordering bomb
                                gclick(i,j) # Click it
                                clicks +=1
                                break
                            if prox < best and prox != 0: # If there is a new lowest number of bordering bombs
                                best = prox # Save number
                                bclick = (i,j) # Save tile
        if clicks == 0: # If there were no tiles with only 1 bordering bomb
            gclick(bclick[0],bclick[1]) # Click on lowest number of bordering bombs tile
    if clicks == 0: # If still nothing was clicked on (all of bordering bombs was 0)
        for i in range(cols):
            for j in range(rows): # For each tile
                if board[i,j] == 0: # If it is unexplored
                    gclick(i,j) # Click it 
    
def istartup():
    click(200,150) # Refresh page
    time.sleep(0.4)
    click(134,323) # Click mode select
    time.sleep(0.1)
    click(150,480) # HARD remember to save new board and change rows/cols
    time.sleep(0.1)
    #click(150,380) # EASY remember to save new board and change rows/cols
    click(1500,400) # Click in empty area of window

def gstartup():
    click(1000,1500) # Clicks restart button (I think?)

global testtile
def ttile(i,j,w): # Gets number of tile, or says if tile being asked for is invalid
    try:
        if i+w[0] >= 0 and j+w[1] >= 0: # If both coordinates are positive
            testtile = board[i+w[0],j+w[1]] # Get number of tile
        else: # If a coordinate is negative
            testtile = 100
    except:
        testtile = 100
        #print (testtile)
    return testtile


########################################################################################## STARTUP
########################################################### Board acquisition

def findboard(): # Locates board on screen and saves its bounding box coordinates
    global boardimg
    global boardloc
    boardimg = ImageGrab.grab() # Grabs image of entire screen
    # boardimg = cv.cvtColor(np.array(boardimg), cv.COLOR_RGB2BGR)
    # boardpng = cv.imread('board.png',0)
    # gameloc = cv.matchTemplate(boardimg,boardpng,cv.TM_CCOEFF)
    try:
        gameloc = gui.locateOnScreen('board.png') # Looks for board image in full screenshot
        #print(gameloc) 
        boardimg = ImageGrab.grab(bbox=(gameloc[0],gameloc[1],gameloc[0]+gameloc[2],gameloc[1]+gameloc[3])) # Updates boardimg with actual board if it was found
        #print(gameloc)
        #gameloc = left, top, width, height
    except: # If board png was not found in full screenshot
        print("Board not found on screen")
        exit()
    print("Board found on screen")

    boardloc = [0,0,0,0] # 0 = left. 1 = top. 2 = width. 3 = height. Location of actual grid of green tiles. Boardimg above is just location of png. 
    boardloc[0] = 2 # Offsets left side 2 pixels off of side of screen
    y=0
    while pixgrabmatch(boardloc[0], y, u1, tol) == False: # Scans from top of png looking for green pixel
        y+=1
    boardloc[1] = y # Saves location of top side of green tiles
    y=gameloc[3]-1
    while pixgrabmatch(boardloc[0], y, u2, tol) == False: # Scans from bottom of png looking for green pixel
        y-=1
    boardloc[3] = y - boardloc[1] # Saves location of bottom side of green tiles
    x=gameloc[2]-1
    while pixgrabmatch(x, boardloc[1], u2, tol) == False: # Scans from right of png looking for green pixel
        x-=1
    boardloc[2] = x # Saves location of right side of green tiles
    boardloc[0] = boardloc[0] + gameloc[0]   # Offsets boardloc with actual pixel location on screen
    boardloc[1] = boardloc[1] + gameloc[1]   #
    boardloc[2] = boardloc[0] + boardloc[2]  #
    boardloc[3] = boardloc[1] + boardloc[3]  #
    boardimg = ImageGrab.grab(bbox=boardloc) #
    #boardimg.show()
########################################################### Row + Column dimension acquisition
def rowcolscan(): # Saves screen coordinates of each "target" pixel on each tile
    global colwidth, rowwidth
    colwidth = np.arange(cols)
    rowwidth = np.arange(rows)
    x = y = buffer = 0
    for i in np.arange(cols-1): # For each column
        if i%2 == 0: # If col number is even
            search = u2 # Search for dark green
        else: # If col number is odd
            search = u1 # Search for light green
        while pixgrabmatch(x,y,search,3) == False: # Scans until finds match to search
            x+=1
        colwidth[i] = x - buffer # Updates col width
        buffer = x # Saves previous position
    colwidth[cols-1]=(boardloc[2]-boardloc[0])-x # Saves width of last column for which there is no right-bordering green
    x = y = buffer = 0
    for i in np.arange(rows-1): # For each row
        if i%2 == 0: # If row number is even
            search = u2 # Search for dark green
        else: # If row number is odd
            search = u1 # Search for light green
        while pixgrabmatch(x,y,search,3) == False: # Scnans until finds match to search
            y+=1
        rowwidth[i] = y - buffer # Updates row width
        buffer = y # Saves previous position
    rowwidth[rows-1]=(boardloc[3]-boardloc[1])-y # Saves width of last row for which there is no bottom-bordering green

############################################################################### Board setup - game board and interface pixel coordinate arrays 
def boardwipe(): # Creates array the size of board with all zeros
    global board
    board = np.zeros((cols,rows),dtype=np.int8)

def boardinit(): # Initializes board array
    global bx, by
    global board
    boardwipe() # Creates array of zeros
    bix = range(cols) # Only used as iterator
    biy = range(rows) # Only used as iterator
    bx = np.arange(cols,dtype=np.int32)
    by = np.arange(rows,dtype=np.int32)
    bx[0] = 0
    by[0] = 0
    for i in range(cols-1): # For each column
        bx[i+1] = bx[i] + colwidth[i+1] # The next column is the width of this column away, plus the location of the right side of the column
    for i in range(rows-1): # For each row
        by[i+1] = by[i] + rowwidth[i+1] # The next row is the height of this row away, plus the location of the top side of the row
    for i in bix: 
        bx[i] = bx[i] + int(colwidth[i]*dotx) # Updates with the "target" pixel instead of the border of the tile
    for i in biy:
        by[i] = by[i] + int(rowwidth[i]*doty) # Updates with the "target" pixel instead of the border of the tile
    #print(bx,by)
    print("Board initialized, beginning game")

################################################################ Testing module

# click(boardloc[0] + bx[12], boardloc[1] + by[10])
# time.sleep(20)
# print('10s')
# time.sleep(10)
# start = time.time()
# boardscan()
# end = time.time()
# print('Scantime = %f'%(end-start))
# end = 0

def rowcoliter(): # Debug. Moves the mouse to each "target" pixel, does not click
 for i in bx:
     for j in by:
        mouse.move(boardloc[0]+i,boardloc[1]+j)
        time.sleep(0.1)


def xydb(dx,dy): # Debug. Makes new board array, scans board, identifies bombs, and prints vision
    global dotx
    global doty
    dotx = dx
    doty = dy
    boardinit()
    boardscan()
    bombscan()
    visionprint()

def timetest(t): # Debug. Wipes board, clicks randomly, sleeps, scans board, prints vision
    boardwipe()
    randclick()
    time.sleep(t)
    boardscan()
    visionprint()
    

##################################################################################Game initialization
def gameinitclicks(): # Clicks on game tiles to start game
    gclick(12,10)
   # gclick(0,0)
   # gclick(0,19)
   # gclick(23,0)
   # gclick(23,19)
   # gclick(12,10)
    #gclick(12,10)
    #gclick(12,10)
def randclick(): # Clicks on a random tile
    click(boardloc[0] + bx[random.randint(0,cols-1)], boardloc[1] + by[random.randint(0,rows-1)])


############################################################# SUPER FUNCTIONS
def init(): # Clicks around to start game, locates board, scans rows and columns, creates board pixel array
    istartup()
    findboard()
    rowcolscan()
    boardinit()

def win(): # Called only if win is identified
    global wins
    global besttime
    gtime = time.time() - ttime # Saves how long the game took
    print('WIN!')
    print('Avg scan time= %.2f s' % (float(gtime)/lcount)) 
    print('Scans =',lcount)
    print('Total game time = %.2f s' % (gtime))
    if gtime < besttime: # If game time is a new record
        print('NEW RECORD!')
        besttime = gtime
        fp = 'wins\w' + '_' + str(wins) + '_t' + str(int(time.time()-ttime)) + 's' + '.png' # Filepath to save png
        print('Saved as %s'%fp)
        wproof = ImageGrab.grab(bbox = (550,260,750,500)) # Takes screenshot of board
        wproof.save(fp,'PNG')
    wins+=1
    restart() # Restarts game
    loop() # Restarts loop (very bad practice - after a few wins, program is in nested win loops)
    
def scanwinloss(): # Scans if the game has been won or lost
    p = boardimg.getpixel((727,1015)) # Gets "telltale" pixel
    if p == (229,194,159): # Loss color 1
        return False
    if p == (167,217,72): # Win color
        win()
    if p == (255,255,255): # Loss color 2
        return False
    return True

def restart(): # Restarts all counters and restarts game
    #boardprint()
    #exit()
    global attempts, tottotclicks, totclicks, clicks, ttime, lcount, lastround
    lcount = 0
    clicks = 0
    #imagegrabprint()
    boardwipe() # Resets board
    gstartup() # Clicks restart button
    time.sleep(0.3)
    ttime = time.time() # Start timer for next round
    gameinitclicks() # Sets mode, clicks start clicks
    time.sleep(startwaittime) # Sleeps to let flying green tiles fall away
    boardscan() # Scans board
    tottotclicks += totclicks
    totclicks = 0
    attempts+=1

def loopcore(t):
    #ltime = time.time()
    boardscan() # Scans new board
    #stime = time.time()-ltime
    bombscan() # Updates board locations
    #btime = time.time()-ltime
    clickscan() # Clicks on appropriate tiles
    #ctime = time.time()-ltime
    #print('SCAN= %3.2f BOMBS= %3.2f CLICKS= %3.2f'%(stime,btime,ctime))
    click(1500,400) # Holds mouse in empty part of screen while sleeping
    time.sleep(t)


############################################################# VARIABLES

#################################### Object colors
u1=(170,215,81) #LIGHTER green
u2=(162,209,73) #DARKER green
b1=(229,194,159) #LIGHTER tan
b2=(215,184,153) #DARKER tan
n1=(42,120,208)
n2=(68,147,73)
n3=(212,62,58)
n4=(130,50,160)
n5=(254,143,50)
n6=(175,184,161)
n7=(66,66,66)
n8=(0,0,0)
colorz = [n1,n2,n3,n4,n5,n6,n7,n8] # Each tile that has bombs around it and is not a bomb
white = (255,255,255)
###################################Others
rows = 20
cols = 24
dotx = 0.57 # Zero to one, left to right, location of "target" pixel in each tile
doty = 0.5 # Zero to one, bottom to top, location of "target" pixel in each tile
tol = 35 # Tolerance (out of 255)


search = [[1,1],[-1,-1],[1,-1],[-1,1],[1,0],[0,1],[-1,0],[0,-1]] # For a given tile, each bordering tile
clicks = 0 # Ctrl-F to find what they mean, I don't even know..
noclicks = 0
totclicks = 0
tottotclicks = 0
bestclicks = 0
attempts = 0
lcount = 0
clicks = 0
ttime = 0
lastround = 0
slowdown = 0
wins = 0
besttime = 100

looptime = 1
startwaittime = 0.8

global boardloc
global colwidth, rowwidth
global bx, by
global boardimg


################################################################################## Game loop

#initial setup:
init() # Gets everything ready
gameinitclicks() # Clicks on tiles

#loop:
ttime = time.time() # Initial round timer
def loop():
    global noclicks, lcount, totclicks, bestclicks
    while True: # Do forever
        if scanwinloss() == False: # If round has been lost
            restart() # Restart
            print('Restarting')
        loopcore(looptime) # Scan, identify bombs, clicks
        lcount += 1.0 # Add one loop to loop counter
        if (time.time() - ttime) > 50: # If it has been longer than 50 seconds since start of round
            restart()
loop()
    
            
