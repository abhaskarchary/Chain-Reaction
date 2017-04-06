import sqlite3
import random

#params
rows = 5
columns = 5
epoch = 0
turn = 1
alpha = 0.3
gamma = 0.1
game_over = False

mmat = [[0 for x in range(rows)] for y in range(columns)]
bmat = [[0 for x in range(rows)] for y in range(columns)]
pmat = [[0 for x in range(rows)] for y in range(columns)]

moves_red = []
moves_blue = []

conn = sqlite3.connect('optimal_strategy.db')
c = conn.cursor()

def init():
    global pmat,bmat,mmat
    for i in range(rows):
        for j in range(columns):

            pmat[i][j] = 0
            bmat[i][j] = 0

            if i==0 or j == 0 or i == rows-1 or j == columns-1:
                mmat[i][j] = 2
            else:
                mmat[i][j] = 3

    mmat[0][0] = 1
    mmat[0][columns-1] = 1
    mmat[rows-1][columns-1] = 1
    mmat[rows-1][0] = 1

    moves_red = []
    moves_blue = []

    c.execute('CREATE TABLE IF NOT EXISTS red(board TEXT, prob REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS blue(board TEXT, prob REAL)')


def train():
    global pmat, bmat
    for i in range(rows):
        for j in range(columns):

            pmat[i][j] = 0
            bmat[i][j] = 0
    start_training()

def start_training():
    query_r = "SELECT * FROM red WHERE board = '"
    query_b = "SELECT * FROM blue WHERE board = '"
    possible_moves = []
    for i in range(rows):
        for j in range(columns):
            if pmat[i][j] == 0 or pmat[i][j] == turn:
                move = make_move(i, j, turn)
                if turn == 1:
                    c.execute(query_r+move+"'")
                    data = c.fetchall()
                    if len(data) == 0:
                        c.execute("INSERT INTO red(board, prob) VALUES(?,?)",(move,0))
                        possible_moves.append((move,0))
                    else:
                        [(x,y)] = data
                        possible_moves.append((x,y))
                        
                else:
                    c.execute(query_b+move+"'")
                    data = c.fetchall()
                    if len(data) == 0:
                        c.execute("INSERT INTO blue(board, prob) VALUES(?,?)",(move,0))
                    else:
                        [(x,y)] = data
                        possible_moves.append((x,y))

    best_move = choose_best(possible_moves)
    number = random.random()
    if number < alpha:
        move = random.randint(0,len(possible_moves)-1)
        (best_move,v) = possible_moves[move]
    confirm_move(best_move)
    if turn == 1:
        moves_red.append(best_move)
    else:
        moves_blue.append(best_move)


def confirm_move(best_move):
    global pmat,bmat
    filling = dec_to_sev(best_move)
    for i in range(rows-1,0,-1):
        for j in range(columns-1,0,-1):
            x = filling%10
            filling/=10
            if x > 3:
                pmat[i][j] = 2
                bmat[i][j] = x-3
            elif x == 0:
                pmat[i][j] = 0
                bmat[i][j] = 0
            else:
                pmat[i][j] = 1
                bmat[i][j] = x
                
                
def choose_best(possible_moves):
    (x,y) = sort(possible_moves, key = lambda x:x[1], reverse = True)[0]
    return x
                
def make_move(i, j, t):
    global pmat,bmat
    n_pmat = pmat
    n_bmat = bmat
    n_pmat[i][j] = turn
    n_bmat[i][j] += 1
    while not check(n_bmat) or win(n_pmat)!=0:
        update(n_pmat, n_bmat)

    board = encode(n_pmat, n_bmat)
    return board
    
def encode(pmat, bmat, t):
    sev_coded = 0
    for i in range(rows):
        for j in range(columns):
            sev_coded = sev_coded*10 + bmat[i][j]
            if pmat[i][j] == 2:
                sev_coded+=3
    encoded = sev_to_dec(sev_coded)
    return str(encoded)

def update(pmat, bmat):
    for i in range(rows):
        for j in range(columns):
            if bmat[i][j] > mmat[i][j]:
                if win(pmat) != 0:
                    return

                bmat[i][j] = 0
                animate(i,j)
                if i+1 < rows:
                    pmat[i+1][j] = pmat[i][j]
                    bmat[i+1][j] += 1

                if j+1 < columns:
                    pmat[i][j+1] = pmat[i][j]
                    bmat[i][j+1] += 1

                if i-1 >= 0:
                    pmat[i-1][j] = pmat[i][j]
                    bmat[i-1][j] += 1

                if j-1 >= 0:
                    pmat[i][j-1] = pmat[i][j]
                    bmat[i][j-1] += 1

                pmat[i][j] = 0

                

def check(bmat):
    for i in range(rows):
        for j in range(columns):
            if bmat[i][j] > mmat[i][j]:
                return False
    return True



def win(pmat):
    r,b = 0,0
    
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


    

def sev_to_dec(x):
    ans = 0
    c = 0
    while x>=1:
        ans = ans*10 + (x%10)*7**c
        x/=10
        c+=1
    return int(ans)

def dec_to_sev(y):
    x = int(y)
    ans = 0
    while x>=1:
        ans = (x%7) + ans*10
        x/=7
    return int(ans)
    
init()
train()
