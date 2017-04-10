import sqlite3
import random
import copy

#params
rows = 5
columns = 5
epoch = 0
turn = 1
alpha = 0.2
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

    

    c.execute('CREATE TABLE IF NOT EXISTS red(board TEXT, row INT, col INT, prob REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS blue(board TEXT, row INT, col INT, prob REAL)')


def train():
    print("training..")
    global pmat, bmat, moves_red, moves_blue, turn, game_over
    for i in range(rows):
        for j in range(columns):

            pmat[i][j] = 0
            bmat[i][j] = 0

    moves_red = []
    moves_blue = []
    turn = 1
    game_over = False
    while not game_over:
        training()
    conn.commit()

def training():
    global turn,game_over,bmat, pmat
    query_r = "SELECT * FROM red WHERE board = '"
    query_b = "SELECT * FROM blue WHERE board = '"
    possible_moves = []
    board = encode(pmat,bmat)
    if turn == 1:
        c.execute(query_r+board+"'")
        data = c.fetchall()
    else:
        c.execute(query_b+board+"'")
        data = c.fetchall()
    if len(data) == 0:
        for i in range(rows):
            for j in range(columns):
                if pmat[i][j] == 0 or pmat[i][j] == turn:
                    move = make_move(i, j, turn)
                    if move == "exit":
                        game_over = True
                        if turn == 1:
                            moves_red.append((board, i, j, 0))
                            c.execute("INSERT INTO red(board, row, col, prob) VALUES(?,?,?,?)",(board,i,j,0))
                            print((board,i,j,0))
                            feed_reward_red(1)
                            feed_reward_blue(-1)
                            return
                        else:
                            moves_blue.append((board, i, j, 0))
                            c.execute("INSERT INTO blue(board, row, col, prob) VALUES(?,?,?,?)",(board,i,j,0))
                            print((board,i,j,0))
                            feed_reward_red(-1)
                            feed_reward_blue(1)
                            return
                            
                
                    if turn == 1:
                        c.execute("INSERT INTO red(board, row, col, prob) VALUES(?,?,?,?)",(board,i,j,0))
                        possible_moves.append((board,i,j,0))
                        
                    else:
                        c.execute("INSERT INTO blue(board, row, col, prob) VALUES(?,?,?,?)",(board,i,j,0))
                        possible_moves.append((board,i,j,0))
                
    else:
        for x in data:
            possible_moves.append(x)

    
    best_move = choose_best(possible_moves)
    number = random.random()
    print(possible_moves)
    if number < alpha:
        print("making random move...")
        move = random.randint(0,len(possible_moves)-1)
        best_move = possible_moves[move]
    print("making move...",turn,best_move)
    confirm_move(best_move)
    if turn == 1:
        moves_red.append(best_move)
    else:
        moves_blue.append(best_move)
    turn = turn%2 + 1
    
    #training()


def confirm_move(best_move):
    global pmat,bmat
    (u,x,y,z) = best_move
    pmat[x][y] = turn
    bmat[x][y] += 1
    while not check(bmat):
        update(pmat,bmat)
    print(bmat)
    print(pmat)
                
                
def choose_best(possible_moves):
    maximum = -2
    r = 0
    c = 0
    for (x,i,j,y) in possible_moves:
        if y > maximum:
            r = i
            c = j
            maximum = y
    return (x,r,c,maximum)
                
def make_move(i, j, t):
    #print("making move..",t)
    global pmat,bmat
    n_pmat = copy.deepcopy(pmat)
    n_bmat = copy.deepcopy(bmat)
    n_pmat[i][j] = turn
    n_bmat[i][j] += 1
    while not check(n_bmat) and win(n_pmat)==0:
        #print("updating")
        update(n_pmat, n_bmat)
    if win(n_pmat) == 1:
        #print(i,j)
        print("feeding reward red wins..")
        return "exit"
    if win(n_pmat) == 2:
        #print(i,j)
        print("feeding reward blue wins..")
        return "exit"
    return "no exit"

def feed_reward_blue(rew):
    if rew == 1:
        query = "UPDATE blue SET prob = prob + 0.1*(1 - prob) WHERE board = '"
    else:
        query = "UPDATE blue SET prob = prob + 0.1*(-1 - prob) WHERE board = '"
    for x in moves_blue:
        (u,v,y,z) = x
        c.execute(query+u+"' and row ="+str(v)+" and col ="+str(y))
    conn.commit()

def feed_reward_red(rew):
    if rew == 1:
        query = "UPDATE red SET prob = prob + 0.1*(1 - prob) WHERE board = '"
    else:
        query = "UPDATE red SET prob = prob + 0.1*(-1 - prob) WHERE board = '"
    for x in moves_red:
        (u,v,y,z) = x
        c.execute(query+u+"' and row ="+str(v)+" and col ="+str(y))
    conn.commit()
        
        
def encode(pmat, bmat):
    sev_coded = 0
    
    for i in range(rows):
        for j in range(columns):
            sev_coded = sev_coded*10 + bmat[i][j]
            if pmat[i][j] == 2:
                sev_coded+=3
    return str(sev_coded)

def update(pmat, bmat):
    for i in range(rows):
        for j in range(columns):
            if bmat[i][j] > mmat[i][j]:
                if win(pmat) != 0:
                    return

                bmat[i][j] = 0
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
    #print(r,b)
    if r == 1 and b == 0:
        return 0

    elif b == 0 and r > 0:
        return 1

    elif r == 0 and b > 0:
        return 2
    

    else:
        return 0

    
init()
epoch = int(input("Enter the number of epochs:"))
print("Training the Bot....");
fo = open("counter.txt","r")
present = int(fo.read())
fo.close()
for i in range(epoch):
    print("Epoch",i+1)
    train()
    fo = open("counter.txt","w")
    fo.write(str(present+i+1))
    fo.close()

print("Exiting...")
conn.close()



