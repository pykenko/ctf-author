import time
import random

luck = [1, -1, 1, 1, -10, 1, 1, 1]

def freeFlag():
    with open("flag.txt", 'r') as a:
        for i in a:
            print(i.strip())

def gameStart():
    flag = 60
    while flag > -1:
        print(f"you have {flag}s left")
        time.sleep(1)
        flag -= random.choice(luck)
        if flag == 0:
            freeFlag()
            exit(1)

if __name__ == '__main__':
    gameStart()