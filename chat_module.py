#!/usr/bin/python

import socket 
from thread import *
import threading
from terminaltables import AsciiTable
from chat_module import *
import copy

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



nicknames = []
rooms = {}
all_members = {}
kicked_users = []

class Admin:
    def __init__(self, client, nickname=None, room_Name=None):
        self.client = client
        self.nickname = nickname
        self.room_Name = room_Name





    def list_nicknames(self):
        for conn in nicknames:
            for name, sock in conn.iteritems():
                print '[+] Nickname: {}'.format(orange + name + reset)

            
    def check_nickname(self):
        if self.nickname != None:
            junk = 'nothing'
            junk2 = ''
            for elem, name in enumerate(nicknames):
                for key, value in name.iteritems():
                    if key == self.nickname and value == self.client:
                        return "already set"

            for elem, name in enumerate(nicknames):
                for key, value in name.iteritems():
                    if key == self.nickname and value != self.client:
                        return "different user"
            

            for elem, name in enumerate(nicknames):
                for key, value in name.iteritems():
                    if key != self.nickname and value == self.client:
                        name[self.nickname] = name.pop(key)
                        return "changed"+':'+key
                        

                    
            nicknames.append({self.nickname:self.client})
            return 'added'
            #print '[-] %s' % junk
            #if 'true' in junk:
            #    key = junk.split(":")[-1]
            #    element = int(junk.split(":")[1])
            #    nicknames[element][self.nickname] = nicknames[element].pop(key)
            #    return 'changed'+':'+key
            #elif junk == 'false':
            #    return "different user"
            #elif junk == 'nothing':
                

            #nicknames.append({self.nickname:self.client})
            
            #return 'added'
        else:
            for name in nicknames:
                for nickname_value, value in name.iteritems():
                    if value == self.client:
                        return nickname_value


        
            return "not found"



    def inside_Room(self):
        #print '[+] User %s is inside room %s' % (orange + self.nickname + reset, orange + self.room_Name + reset)
        while 1:

            try:
                
                data = self.client.recv(1024)
                nrooms = copy.deepcopy(rooms)
                
                for x in kicked_users:
                    if x == self.nickname:
                        kicked_users.remove(self.nickname)
                        for room in rooms.keys():
                            if rooms[room] == []:
                                del rooms[room]
                        
                        return "kicked"

                if data == '' or data.rstrip() == 'exit':
                    
                    
                    for room, members in nrooms.iteritems():
                        if room == self.room_Name:
                            for num, conn in enumerate(members):
                                for nickname, sock_conn in conn.iteritems():
                                    if nickname == self.nickname:

                                        print '[+] User {} left the room'.format(white + nickname + reset)
                                        del rooms[room][num]
                                        
                                    else:
                                        
                                        sock_conn.send('User %s left the room' %(white + self.nickname + green))
                    

                    for room in rooms.keys():
                        
                        if rooms[room] == []:
                            del rooms[room]

                    return

                
                if data.rstrip() == "list":
                    for room, members in rooms.iteritems():
                        if room == self.room_Name:
                            for num, conn in enumerate(members):
                                for nickname in conn:
                                    if nickname == self.nickname:
                                        continue
                                    else:
                                        self.client.send("Nickname: " + purple + nickname + reset)
                    continue
                
                else:
                    for room, members in rooms.iteritems():
                        if room == self.room_Name:
                            for conn in members:
                                for nickname, sock_conn in conn.iteritems():
                                    if nickname == self.nickname:
                                        
                                        sock_conn.send('yourself')
                                        continue
                                    else:
                                        #print "[+] User %s is sending data to %s" % (self.nickname, nickname)
                                        sock_conn.send(green + self.nickname + reset + ' : ' + white + data + reset)
                            



            except Exception:
                for room in rooms.keys():
                        if rooms[room] == []:
                            del rooms[room]
                

    def kick_user(self):
        for room, members in rooms.iteritems():
            for num, conn in enumerate(members):
                for nickname, sock_conn in conn.iteritems():
                    if nickname == self.nickname:
                        kicked_users.append(nickname)
                        #sock_conn.close()
                        del members[num]
                        
                        print "[+] User {} has been kicked".format(white + nickname + reset)

        



    def list_users(self):
        
        users_table = [['Room', 'User']]

        for room, members in rooms.iteritems():
            for conn in members:
                for nickname, sock_conn in conn.iteritems():
                    users_table.append([room, nickname])
        users_table_instance = AsciiTable(users_table)
        users_table_instance.inner_heading_row_border = True
        users_table_instance.inner_row_border = False
        users_table_instance.justify_columns = {0: 'left', 1: 'left'}
        print users_table_instance.table


                    #print 'Room: {}  User: {}'.format(room, nickname)


    def check_room(self):
        if rooms == {}:
            return 'empty'
        else:
            print '[+] Checking if room exists.'
            for room, members in rooms.iteritems():
                if room == self.room_Name:
                    print '[+] Found room'
                    return "exist"
                
            print '[+] Room name is not taken.'
            return "nothing"


    def check_before_send(self):
        for conn in nicknames:
            for name, sock in conn.iteritems():
                if name == self.nickname:
                    return "found"
        return "not found"


    def admin_msg(self):
                    
        while 1:
            msg = raw_input(white + 'Enter message: ' + reset)
            if msg == '':
                continue
            elif msg == 'exit' or msg == 'bg':
                return

            else:
                for conn in nicknames:
                    for name, sock in conn.iteritems():
                        if name == self.nickname:
                            sock.send('Admin: ' + purple + msg + reset)
                

                            
    def create_Room(self):
        print '[+] Room {} has been created by {}'.format(white + self.room_Name + reset, white + self.nickname + reset)
        rooms.update({self.room_Name:[{self.nickname:self.client}]})
        #all_members.update({self.room_Name:[self.client]})
        self.client.send('Room created -> '+ white + self.room_Name + reset)
        return

    def join_Room(self):
        print '[+] User %s joined room %s' % (white + self.nickname + reset, white + self.room_Name + reset)
        for key, value in rooms.iteritems():
            if key == self.room_Name:
                value.append({self.nickname:self.client})
        
        self.client.send('Room Joined -> '+ white + self.room_Name + reset)
        for room, members in rooms.iteritems():
            if room == self.room_Name:
                for conn in members:
                    for nickname, sock_conn in conn.iteritems():
                        if nickname == self.nickname:
                            #print "Found myself"
                            continue
                        else:
                            #print "[+] User %s joined the room " % (self.nickname)
                            sock_conn.send('User {} joined the room'.format(white + self.nickname + green))
                            #sock_conn.send('User %s joined the room' % white + (self.nickname)) 
        return
