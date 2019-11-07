#!/usr/bin/python

import socket 
from thread import *
import threading
from terminaltables import AsciiTable
from chat_module import *

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



host = ''
port = 8888

TR_num = []
clients_lists = []
TR_ip = []
TR_port = []




def Help():

    print """
                      +------------+
                      | Help: Menu |
                      +------------+

    clients                                 List all sessions
    clients -i <session number>             Interact with specific session
    kill client <session number>            Kill specific session
    exit                                    Exit the main room    

    """




            

def threaded(c, thread_num, conn_data):
    IP = conn_data['IP']
    PORT = conn_data['PORT']
    mydata = threading.local()

    mydata.x = thread_num
    TR_ip.append(str(IP))
    TR_port.append(str(PORT))
    TR_num.append(str(mydata.x))
    while 1:
        data = c.recv(1024)
        if not data or data.rstrip() == 'exit':
            clients_lists.remove(c)
            TR_num.pop(0)
            print "[+] Client closed connection"
            print "[+] Removing his nickname from data"
            if nicknames == []:
                print '[+] User %s hasn\'t chosen nickname yet. No need for removal' % (green + IP + reset)
                c.close()
                break
            else:
                print '[+] Removing User.'
                for name in nicknames:
                    for key, value in name.iteritems():
                        if value == c:
                            nicknames.remove(name)
                            print '[+] User %s has been removed' % (orange + key + reset)
                            c.close()
                break
            
        if "nickname" in data:
        
            if data.split(" ")[0] == "set" and data.split(" ")[1] == "nickname" and len(data.split(" ")) == 3:
                nickname = str(data.rstrip().split(" ")[2])
                if nicknames == []:
                    nicknames.append({nickname:c})
                    print '[+] Client %s nickname is now => %s' % (orange + IP + reset, orange + nickname + reset)
                    c.send('Nickname set -> ' + lblue + nickname + reset)
                else:
                    name = Admin(c, nickname=nickname)
                    nickname_result = name.check_nickname()
                    if nickname_result == 'already set':
                        c.send('You have chosen this nickname already.')
                        continue
                    elif nickname_result == 'different user':
                        c.send('This nickname has been chosen by a different User.')
                    elif 'changed' in nickname_result:
                        old_name = nickname_result.split(':')[1]
                        print '[+] Client %s changed nickname  %s <=> %s ' % (green + IP + reset, green + old_name + reset, green + nickname + reset)
                        c.send("Nickname has been changed -> " + nickname )
                        continue
                    elif nickname_result == 'added':
                        print '[+] Client %s nickname is now => %s' % (orange + IP + reset, orange + nickname + reset)
                        c.send('Nickname set -> ' + lblue + nickname + reset )

                        
                    
        elif  "create" in data or 'join' in data:
            check_name = Admin(c)
            nickname_value = check_name.check_nickname()
            if nickname_value == "not found":
                c.send("Choose nickname first before joining or creating rooms. Ex. set nickname <test1>")
                continue
            else:
                if data.split(" ")[0] == "create" and len(data.split(" ")) == 2:
                    room2create = str(data.rstrip().split(" ")[1])

                    roomData = Admin(c, nickname_value, room2create)
                    room_exist = roomData.check_room()
                    if room_exist == 'empty' or room_exist == 'nothing':
                        #print 'Room name doesnt exist'
                        roomData.create_Room()
                        user_status = roomData.inside_Room()
                        if user_status == 'kicked':
                            c.send( red + 'You have been kicked from the room' + reset)
                    elif room_exist == "exist":
                        c.send('The room %s already exist. Choose a different name' %(room2create))
                        continue
                elif data.split(" ")[0] == "join" and len(data.split(" ")) == 2:
                    room2join = str(data.rstrip().split(" ")[1])
                    roomData = Admin(c, nickname_value, room2join)
                    print '[+] User %s wants to join room %s'.format(white + nickname_value + reset, white + room2join + reset)
                    room_exist = roomData.check_room()
                    if room_exist == 'empty' or room_exist == 'nothing':
                        c.send('Room was not found')
                    else:

                        roomData.join_Room()
                        user_status = roomData.inside_Room()
                        if user_status == 'kicked':
                            c.send(red + 'You have been kicked from the room'+reset)
                


        else:
            if nicknames == []:
                print "[+] Client" + str(mydata.x) + " says: " + white + data + reset
                c.send("You must set a nickname first. Ex. set nickname <test1>")
            else:
                check_name = Admin(c)
                nickname_value = check_name.check_nickname()
                if nickname_value == "not found":
                    c.send("You must set a nickname first. Ex. set nickname <test1>")
                else:
                    c.send('Command not found')
                    

                

        
        


def check_sessions():
    if TR_num == []:
        print red + "No clients" + reset
    else:
        print "+--------------------------------------------+"
        for tr_num, IP, PORT in zip(TR_num, TR_ip, TR_port):
            print "Client : {}  IP : {}   Port {}".format(green + tr_num + reset, green + IP + reset, green + PORT + reset)
        print "+--------------------------------------------+"




def remove_session(conn):
    if conn in clients_lists:
        clients_lists.remove(conn)
        TR_num.pop(0)


def kill_session(s_number):
    for tr_num, session in zip(TR_num, clients_lists):
        if tr_num == s_number:
            print "[+] Client {} killed".format(red + s_number + reset)
            session.close()
            remove_session(session)



def CMD():

    while 1:
        cmd = raw_input(green +"> "+reset)
        if cmd == "":
            continue
        elif cmd == "exit":
            print red + "[Hit Control + C to switch to main menu]" + reset
            break
        elif cmd == "help":
            Help()
        elif "client" in cmd or "clients" in cmd:
            if cmd.split(" ")[0] == 'clients' and len(cmd.split(" ")) == 1:
                check_sessions()
            elif len(cmd.split(" ")) == 3 and cmd.split(" ")[0] == "kill":
                session = cmd.split(" ")[2]
                kill_session(session)
        elif cmd == 'list nicknames':
            all_names = Admin(client=None)
            all_names.list_nicknames()
        elif 'sendto' in cmd:
            if cmd.split(" ")[0] == 'sendto' and len(cmd.split(" ")) == 2:
                nickname = cmd.split(" ")[1]
                msg_to_send = Admin(client=None, nickname=nickname)
                check_name = msg_to_send.check_before_send()
                if check_name == 'found':
                    msg_to_send.admin_msg()
                elif check_name == 'not found':
                    print '[+] User {} not found'.format(red + nickname + reset)
                    continue

        elif cmd == 'list all users':
            admin = Admin(client=None)
            admin.list_users()
        elif 'kick' in cmd and cmd.split(" ")[0] == 'kick' and len(cmd.split(" ")) == 2:
            name_to_kick = cmd.split(" ")[1]
            admin = Admin(client=None, nickname=name_to_kick)
            admin.kick_user()        
        else:
            print "[+] {}".format(red + "Invalid command" + reset)






thread_num = 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind((host, port))

print "[+] Binded successfully."

s.listen(5)

print "[+] Listening on port {}".format(green + str(port) + reset)
start_new_thread(CMD, ())


while 1:

    try:
        c, addr = s.accept()
        
        clients_lists.append(c)
        thread_num += 1
        print "[+] Client%s connected.  IP : %s PORT : %s" % (red + str(thread_num) + reset, red + str(addr[0]) + reset, red + str(addr[1]) + reset)
        
        conn_data = {'IP':str(addr[0]), 'PORT':str(addr[1])}
        
        start_new_thread(threaded, (c,thread_num, conn_data))


    except KeyboardInterrupt:

        print "[+] Closing.."
        break

s.close()













