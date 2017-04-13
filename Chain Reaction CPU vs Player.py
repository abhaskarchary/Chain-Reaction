#################################################
# Developed for TCS remote Internship 2017      #
# By A Bhaskar Chary and Jyoti Sinha            #
# CHAIN REACTION V 5.0                          #
# Simple Game FrameWork (Dynamic)               #
# Added animations to the Orbs                  #
# graphics added                                #
# Main Screen added                             #
#################################################





import pygame, glob
import time
import sqlite3
import copy
import random

#colors
black = (0,0,0)
red = (255,0,0)
blue = (0,0,255)
white = (255, 255, 255)

#gameparam
quitGame = False
turn = 1
end = False
game_mode = "init"
screen_x = 250
screen_y = 100
play_x = 350
play_y = 350
button_over = False

#board param
rows = 5
columns = 5
xoff = 150
yoff = 50
bSize = 500/rows
winSize = ( 800, 600)
ballSize = bSize/5
r1 = 0
r2 = (1,20)
r3 = (21, 40)
b1 = 41
b2 = (42, 61)
b3 = (62, 81)

#artificial intelligence
possible_moves = []
bot_moves = []
alpha = 0.25

#arrangement
pmat = [[0 for x in range(rows)] for y in range(columns)]
bmat = [[0 for x in range(rows)] for y in range(columns)]
mmat = [[0 for x in range(rows)] for y in range(columns)]
orb = [[0 for x in range(rows)] for y in range(columns)]


bg = pygame.image.load("images/bg.jpg")

clock = pygame.time.Clock()
background = pygame.image.load("images/bg2.jpg")
orbs = glob.glob("Spins/Spin*.png")
orbs.sort()

conn = sqlite3.connect('optimal_strategy.db')
cur = conn.cursor()

back = pygame.Surface(winSize)
gameScreen = pygame.display.set_mode(winSize)
pygame.display.set_caption("Chain Reaction")
pygame.init()
pygame.font.init()

class ball:


    def __init__(self, i, j, n, c):

        self.x = xoff + i*bSize
        self.y = yoff + j*bSize
        
        if c == 1:
            if n == 1:
                self.start = r1
                self.end = r1
            elif n == 2:
                (self.start, self.end) = r2
            elif n == 3:
                (self.start, self.end) = r3
            else:
                self.start = -1
                
        else:
            if n == 1:
                self.start = b1
                self.end = b1
            elif n == 2:
                (self.start, self.end) = b2
            elif n == 3:
                (self.start, self.end) = b3
            else:
                self.start = -1

        if bmat[i][j] > mmat[i][j]:
            self.start = -1

        self.now = self.start

    def animate(self):
        if self.start != -1:
            image = pygame.image.load(orbs[self.now])
            gameScreen.blit( image, (self.x, self.y))
            self.now+=1
            if self.now>self.end:
                self.now = self.start




class circ:


    def __init__(self, x, y, t):
        if t == 1:
            image = pygame.image.load(orbs[r1])
        else:
            image = pygame.image.load(orbs[b1])
        
        gameScreen.blit( image, (x, y))



class main_screen:


    def __init__(self):
        self.now = 0
        self.x = screen_x
        self.y = screen_y
        self.all_image = glob.glob("images/ChainRN*.png")
        self.all_image.sort()
        #.update(self)

    def update(self):
        #print(self.now);
        image = pygame.image.load(self.all_image[self.now])
        
        

        gameScreen.blit(image, (self.x, self.y))
        
        self.now+=1
        if self.now>39:
            self.now = 0

class button:


    def __init__(self):
        self.now = 0
        self.x = play_x
        self.y = play_y
        self.all_image = glob.glob("Button/Button*.png")
        self.clicked = glob.glob("Button/ButtonClicked.png")
        self.all_image.sort()

    def update(self):
        image = pygame.image.load(self.all_image[self.now])
        gameScreen.blit(image, (self.x, self.y))
        if button_over:
            if self.now<12:
                self.now+=1

        else:
            self.now=0

    def button_clicked(self):
        image = pygame.image.load(self.clicked[0])
        gameScreen.blit(image, (self.x, self.y))
        
main = main_screen()
btn = button()


def start():
    init()
    gameloop()

def reset_game():
    global quitGame,quit_menu,turn,end,game_mode,button_over,bot_moves
    quitGame = False
    quit_menu = False
    turn = 1
    end = False
    game_mode = "start"
    button_over = False
    bot_moves = []
    
def init():
    global pmat,bmat
    for i in range(rows):
        for j in range(columns):

            pmat[i][j] = 0
            bmat[i][j] = 0

            if i==0 or j == 0 or i == rows-1 or j == columns-1:
                mmat[i][j] = 2
            else:
                mmat[i][j] = 3

            orb[i][j] = ball(i, j, 0, 0)

    mmat[0][0] = 1
    mmat[0][columns-1] = 1
    mmat[rows-1][columns-1] = 1
    mmat[rows-1][0] = 1
    
        



def gameloop():
    global game_mode, turn
    while game_mode == "play":
        clock.tick(60)
        
        #c = circ(20,20,1);
        

        #print(win())
        handleEvents()
        while not check() and win() == 0:
            update()
        gameScreen.fill(white)
        gameScreen.blit(background, (0,0))
        displaytext()
        makeGrid()
        pygame.display.update()
        winner = win()
        if winner > 0:
            feed_reward(-1)
            win_message(winner)
            continue
            #print(quitGame)
        if turn == 2:
            
            cpu_make_move()
        winner = win()
        if winner > 0:
            win_message(winner)
            continue
            
        
    
def cpu_make_move():
    global pmat, bmat, turn
    possible_moves = []
    board_state = encode(pmat,bmat)
    cur.execute("SELECT * FROM blue WHERE board = '"+board_state+"'")
    data = cur.fetchall()
    turn = turn%2 + 1
    if len(data) == 0:
         for i in range(rows):
             for j in range(columns):
                 if pmat[i][j] == 0 or pmat[i][j] == 2:
                     cur.execute("INSERT INTO blue(board, row, col, prob) VALUES(?,?,?,?)",(board_state, i, j, 0))
                     possible_moves.append((board_state, i, j, 0))
    else :
        for x in data:
            possible_moves.append(x)

    best_move = choose_best(possible_moves)

    number = random.random()
    if number <= alpha:
        best_move = possible_moves[random.randint(0,len(possible_moves)-1)]
    bot_moves.append(best_move)
    confirm_move(best_move)
    print(bmat)
    print(pmat)
    gameScreen.fill(white)
    gameScreen.blit(background, (0,0))
    displaytext()
    makeGrid()
    pygame.display.update()


def confirm_move(best_move):
    #(x,i,j,p) = best_move
    global pmat,bmat,orb
    (u,x,y,z) = best_move
    pmat[x][y] = turn%2+1
    bmat[x][y] += 1
    while not check() and win() == 0:
        update()
    if win() == 2:
        feed_reward(1)

    orb[x][y] = ball(x,y,bmat[x][y],pmat[x][y])
    

        

def feed_reward(rew):
    if rew == 1:
        query = "UPDATE blue SET prob = prob + 0.1*(1 - prob) WHERE board = '"
    else:
        query = "UPDATE blue SET prob = prob + 0.1*(-1 - prob) WHERE board = '"
    for x in bot_moves:
        (u,v,y,z) = x
        cur.execute(query+u+"' and row ="+str(v)+" and col ="+str(y))
    conn.commit()
    
def choose_best(possible_moves):
    maximum = -2
    r = 0
    c = 0
    minimum = 2
    for (x,i,j,y) in possible_moves:
        if y > maximum:
            r = i
            c = j
            maximum = y
        if y < minimum:
            minimum = y

    if minimum == maximum:
            (x,r,c,maximum) = possible_moves[random.randint(0,len(possible_moves)-1)]
    return (x,r,c,maximum)


def encode(pmat, bmat):
    sev_coded = 0
    
    for i in range(rows):
        for j in range(columns):
            sev_coded = sev_coded*10 + bmat[i][j]
            if pmat[i][j] == 2:
                sev_coded+=3
    return str(sev_coded)


def handleEvents():
    global quitGame,turn,bmat,pmat,game_mode
    (mx, my) = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitGame = True
            game_mode = "end"
        if turn == 1:
            if event.type == pygame.MOUSEBUTTONUP:
                for i in range(rows):
                    for j in range(columns):
                        if mx > xoff + i*bSize and mx < xoff + (i+1)*bSize and my > yoff + j*bSize and my < yoff + (j+1)*bSize:
                            if turn == 1 and (pmat[i][j] == 1 or pmat[i][j] == 0):
                                bmat[i][j] += 1
                                pmat[i][j] = 1
                                turn = turn%2 + 1
                                orb[i][j] = ball(i,j,bmat[i][j],pmat[i][j])
                        
                            
                            
                
def update():
    global pmat,bmat
    for i in range(rows):
        for j in range(columns):
            if bmat[i][j] > mmat[i][j]:
                if win() != 0:
                    return

                bmat[i][j] = 0
                animate(i,j)
                if i+1 < rows:
                    pmat[i+1][j] = pmat[i][j]
                    bmat[i+1][j] += 1
                    orb[i+1][j] = ball(i+1,j,bmat[i+1][j],pmat[i+1][j])

                if j+1 < columns:
                    pmat[i][j+1] = pmat[i][j]
                    bmat[i][j+1] += 1
                    orb[i][j+1] = ball(i,j+1,bmat[i][j+1],pmat[i][j+1])

                if i-1 >= 0:
                    pmat[i-1][j] = pmat[i][j]
                    bmat[i-1][j] += 1
                    orb[i-1][j] = ball(i-1,j,bmat[i-1][j],pmat[i-1][j])

                if j-1 >= 0:
                    pmat[i][j-1] = pmat[i][j]
                    bmat[i][j-1] += 1
                    orb[i][j-1] = ball(i,j-1,bmat[i][j-1],pmat[i][j-1])

                pmat[i][j] = 0
                orb[i][j] = ball(i,j,bmat[i][j],pmat[i][j])

                
            
    


def animate(i,j):
    b = int(bSize)
    x = int(xoff + b*i)
    y = int(yoff + b*j)
    z = 5
    
    while(z<b):
        clock.tick(60)
        gameScreen.fill(white)
        gameScreen.blit(background, (0,0))
        displaytext()
        makeGrid()
        if i < rows-1:
            b1 = circ(int(x + z), y, turn%2+1)
        if j < columns-1:
            b2 = circ(x,int(y + z), turn%2+1)
        if i > 0:
            b3 = circ(int(x - z), y, turn%2+1)
        if j > 0:
            b4 = circ(x, int(y - z), turn%2+1)
        pygame.display.update()
        z+=5
        

    
def check():
    for i in range(rows):
        for j in range(columns):
            if bmat[i][j] > mmat[i][j]:
                return False
    return True
    

def displaytext():
    myfont = pygame.font.SysFont("monospace", 15)

    if turn == 1:
        label = myfont.render("Turn: Player", 1, red)
    else:
        label = myfont.render("Turn: CPU", 1, blue)
    
    gameScreen.blit(label, (350, 10))

def win_message(turn):
    global end,gameScreen,quitGame,game_mode
    end = True
    gameScreen.fill(white)
    gameScreen.blit(background, (0,0))
    myfont = pygame.font.SysFont("monospace", 30)

    if turn == 1:
        label = myfont.render("Player WINS!!", 1, red)
    else:
        label = myfont.render("CPU WINS!!", 1, blue)
    gameScreen.blit(label, (350, 270))
    pygame.display.update()
    game_mode = "init"
    time.sleep(2)
    
    


def win():
    r,b = 0,0
    global gameScreen,end,quitGame
    
    for i in range(rows):
        for j in range(columns):
            if pmat[i][j] == 1:
                r+=1
            elif pmat[i][j] == 2:
                b+=1
    
    if r == 1 and b == 0:
        return 0

    elif b == 0 and r > 0:
        return 1

    elif r == 0 and b > 0:
        return 2
    

    else:
        return 0
            
            
    
    


def makeGrid():

    for i in range(rows):
        for j in range(columns):
            pygame.draw.rect( gameScreen, black, ( xoff+i*bSize, yoff+j*bSize, bSize, bSize), 3)
            orb[i][j].animate()
            
            

def display_main_screen():
    
    gameScreen.fill(white)
    
    back.blit(bg, (0,50))
    back.set_alpha(200)
    animate_menu()


def animate_menu():
    global game_mode
    while game_mode == "start":
        clock.tick(24)
        handle_menu_events()
        gameScreen.blit(back, (0, 0))
        main.update()
        btn.update()
        pygame.display.update()


def handle_menu_events():
    global quitGame,button_over,game_mode
    (mx, my) = pygame.mouse.get_pos()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            game_mode = "end"
            quitGame = True
        if e.type == pygame.MOUSEBUTTONUP and play_x <= mx <= play_x+100 and play_y<= my <= play_y+60:
            btn.button_clicked()
            game_mode = "play"
            

    
    if play_x <= mx <= play_x+100 and play_y<= my <= play_y+60:
        button_over = True
    else:
        button_over = False
    
            


def menu():
    while not quitGame:
        if game_mode == "init":
            reset_game()
        elif game_mode == "start":
            display_main_screen()
        elif game_mode == "play":
            start()
    pygame.quit()
    quit()
        
    
menu()
