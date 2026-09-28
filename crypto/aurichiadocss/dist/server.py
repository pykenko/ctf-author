#!/usr/bin/python3
from auric import secret_shift, kebaikan_auric, flag
import time

alphabets = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

user_create = False

def encrypt(yesyes):
    for shift in range(secret_shift):
        res = ''
        for i in range(len(yesyes)):
            if yesyes[i].isalnum():
                res += alphabets[(alphabets.index(yesyes[i]) + shift) % len(alphabets)]
            else:
                res += yesyes[i]
    return res

def register():
    name = input("name : ")
    password = input("password : ")
    if user_create == True:
        cipher = encrypt(password)
        with open("user.db", 'a') as a:
            a.write(f"{name},{cipher}\n")
            a.close()
        print(f"registered {name}")
    else:
        print("User account creation is not available")
        print("heres a gift from auric", kebaikan_auric)

def login():
    name = input("name : ")
    password = input("password : ")
    data = open("user.db", 'r')
    count = 0
    password = encrypt(password)
    for i in data:
        username, password = i.strip().split(',')
        # print(f"{count}",username, password)
        count += 1
        if name == 'fuwawa' and name == username and password == password:
            print(flag)
            return;
        elif name == username and password == password:
            print("Welcome back", name)
            return;
    print("Wrong Username or Password please recheck!")

def docs():
        print("best docs for tutorials")
        print("1. what are encodings?")
        print("2. what are encryptions")
        print("3. what is RSA?")
        pick = int(input("pick a docs : "))
        if pick > 3 or pick < 1:
            print("Not Found!")
        else:
            fname = "docs/"
            fname += str(pick)
            with open(fname, 'r') as a:
                for i in a:
                    print(i.strip())

def leak():
    with open("chat.txt", 'r') as a:
        for i in a:
            print(i.strip())
            time.sleep(0.7)

def main():
    while(True):
        print("aurichia docs")
        print("1. see docs")
        print("2. login")
        print("3. register")
        print("4. Exit")
        try:
            user = int(input("input : "))
            if user == 3:
                register()
            elif user == 2:
                login()
            elif user == 1:
                docs()
            elif user == 4:
                break;
            elif user == 69: # note for developer : dont forget to delete this!
                leak()
        except:
            print("invalid input!")

if __name__ == '__main__':
    main()