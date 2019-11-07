#!/usr/bin/python

import socket 
from thread import *
import threading
from terminaltables import AsciiTable
from time import sleep
import pyfiglet
import sys

reset="\033[0;0m"
red="\033[38;5;9m"
byellow="\033[38;5;3m"
yellowb="\033[38;5;11m"
blue="\033[38;5;27m"
purple="\033[1;33;35m"
cyan="\033[38;5;6m"
white="\033[38;5;7m"
orange="\033[38;5;202m"
lblue="\033[38;5;117m"
green="\033[38;5;2m"

host = '127.0.0.1'
port = 8888



kicked = []
nickname = []
taken_rooms = []
room_status = []
nickname_set = []

def inside_room(conn, room=None, nickName=None):
    while 1:
        if kicked == []:
            cmd = raw_input('[+] %s [%s] ' % (orange + room + reset, blue + nickName + reset))
            if cmd == 'exit':
                conn.send(cmd)
                return
            elif cmd == '':
                continue
            else:
                conn.send(cmd)
                sleep(0.2)
        else:
            print '[+] Going back to Lobby..'
            kicked.remove('back')
            return
            




def threaded(c, data):
    if data == 'yourself':
        pass
    elif 'kicked' in data:
        print '{} {}'.format(white + '[+]' + reset, green + data + reset)
        kicked.append('back')
    elif 'room' in data and 'exist' in data:
        print '{} {}'.format(white + '[+]' + reset, green + data + reset)
        taken_name = data.split(" ")[2]
        taken_rooms.append(taken_name)
    elif 'Room' in data and 'not found' in data:
        print '{} {}'.format(white + '[+]' + reset, green + data + reset)
        room_status.append('unfound')
    elif 'Nickname' in data and 'set' in data:
        
        if nickname_set == []:
            nickname_set.append('true')
        else:
            nickname_set[0] = 'true'
        print '{} {}'.format(white + '[+]' + reset, green + data + reset)
    elif 'different' in data and 'User' in data:
        if nickname_set == []:
            nickname_set.append('false')
        else:
            nickname_set[0] = 'false'
        print '{} {}'.format(white + '[+]' + reset, green + data + reset)
    elif 'Room' in data and 'Joined' in data:
        print '{} {}'.format(white + '[+]' + reset, green + data + reset)
        if room_status != []:
            room_status[0] = 'found'
            
        

    elif 'Room created' in data:
        room_to_remove = data.split(" ")[-1]
        for x in taken_rooms:
            if x == room_to_remove:
                taken_rooms.remove(x)
        print '{} {}'.format(white + '[+]' + reset, green + data + reset)
    else:

        print '\n{} {}'.format(white + '[+]' + reset, green + data + reset)
        
        
    



def check_room(room_to_check):
    for x in taken_rooms:
        
        if x == room_to_check:
            
            return "taken"
     
    return "nothing"


def CMD(c):
    
    while 1:
        if nickname == []:
            nick_name = 'Client'

        else:
            for x in nickname:
                
                nick_name = x


        cmd = raw_input('[+] %s > ' % (orange + nick_name + reset))
        if cmd == '':
            continue
        elif cmd == 'exit':
        #    s.send(cmd)
            print 'Exiting'
            c.send(cmd)
            break
            
        elif 'join' in cmd or 'create' in cmd:
            if (cmd.split(" ")[0] == 'join' or cmd.split(" ")[0] == 'create') and len(cmd.split(" ")) == 2:
                roomName = cmd.split(" ")[1]
                c.send(cmd)
                if nickname_set == []:
                    sleep(0.2)
                    continue
                else:
                    if cmd.split(" ")[0] == 'create':
                        sleep(0.3)
                        if taken_rooms == []:
                            
                            inside_room(s, roomName, nick_name)
                        else:
                            check = check_room(roomName)
                            if check == 'taken':
                                
                                continue
                            elif check == 'nothing':
                        
                                inside_room(s, roomName, nick_name)
                    elif cmd.split(" ")[0] == 'join':
                        
                        sleep(0.2)
                        if room_status == [] or room_status == 'found':
                            inside_room(s, roomName, nick_name)
                        else:
                            continue

        elif 'nickname' in cmd:

                if cmd.split(" ")[0] == 'set' and cmd.split(" ")[1] == 'nickname' and len(cmd.split(" ")) == 3:
                    user_name = cmd.split(" ")[2]
                    c.send(cmd)
                    sleep(0.2)

                    
                    if nickname_set == []:
                        continue
                    else :
                        
                        if nickname_set[0] == 'true':
                            nickname.append(user_name)
                        else:
                            continue

                    

                    
                    
                    

        else:
            c.send(cmd)
            sleep(0.2)
        
banner = pyfiglet.figlet_format('Terminal')
               
print green + banner + reset

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((host, port))
    print '[+] %s' %(white + 'Connected!' + reset)
except socket.error:
    print '[-] Could not connect to server. Make sure the server is running'


start_new_thread(CMD, (s,))

while 1:
    try:
        data = s.recv(1024)
        if not data:
            break
        else:
            start_new_thread(threaded, (s,data))
    except KeyboardInterrupt:
        break
