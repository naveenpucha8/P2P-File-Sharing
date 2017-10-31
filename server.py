import socket
import os
import random
import re
from datetime import datetime


def create_port(socket):
    cp = random.randint(0, 9999)
    try:
        socket.bind((host, cp))
    except:
        return create_port(socket)
    return cp


def longlist(s):
    files = os.popen("find . -not -path '*/\.*' -type f").read().split('\n')
    # print files
    if len(files) == 1:
        s.send("No Files Found")
        return
    val = len(files)
    s.send('val')
    try:
        for j in files:
            if j != "":
                j = '"' + j + '"'
                cmd = "stat --printf 'name= %n \tSize= %s bytes\t Type= %F\t Timestamp=%z\n' " + j
                res = os.popen(cmd).read()
                temp = res
                temp = temp.split("\t")
                temp[0]=temp[0].split("=")
                temp[3]=temp[3].split("=")
                # print temp[0][1],temp[3][1]

                # s.send(temp[0][1]),s.send(temp[3][1])
                s.send(res)
                if s.recv(1024) != "Received":
                    break
        s.send(" ")
        s.recv(1024)
        s.send("Done")
    except:
        print "Connection Error"
        return


def shortlist(s, inp):
    inp = inp.split()
    time1 = inp[2] + " " + inp[3]
    time2 = inp[4] + " " + inp[5]
    files = os.popen("find %s -newermt %s ! -newermt  %s -not -path '*/\.*' -type f" % (
        ".", str('"' + time1 + '"'), str('"' + time2 + '"'))).read().split('\n')
    if len(files) == 1:
        s.send("No Files Found")
        s.recv(1024)
        return
    try:
        for j in files:
            if j != "":
                j = '"' + j + '"'
                cmd = "stat --printf 'name= %n \tSize= %s bytes\t Type= %F\t Timestamp=%z\n' " + j
                res = os.popen(cmd).read()
                s.send(res)
                if s.recv(1024) != "Received":
                    break
        s.send(" ")
        s.recv(1024)
        s.send("Done")
    except:
        print "Connection Error"
        return

def regex(s, inp):
    reg = inp[2]
    fl = False
    files = os.popen("find . -not -path '*/\.*' -type f").read().split('\n')
    if len(files) == 1:
        s.send("No Files Found")
        return
    try:
        for j in files:
            if j != "" and re.search(reg, j) != None and re.search(reg, j).group(0) != '':
                j = '"' + j + '"'
                cmd = "stat --printf 'name= %n \tSize= %s bytes\t Type= %F\t Timestamp=%z\n' " + j
                res = os.popen(cmd).read()
                s.send(res)
                fl = True
                if s.recv(1024) != "Received":
                    break
        if not fl:
            s.send("No Files Found")
        s.send(" ")
        s.recv(1024)
        s.send("Done")
    except:
        print "Connection Error"
        return

def verify(s, file_name, fl=True):
    filename = '"' + file_name + '"'
    cmd = "stat --printf '%z\n' " + filename
    time_modified = os.popen(cmd).read().split('\n')[0]
    if time_modified == "":
        s.send("No Such File")

    elif time_modified != "":
        try:
            cmd = "cksum " + filename
            hash_value = os.popen(cmd).read().split('\n')[0].split()[0]
            hash_value = "CheckSum: " + hash_value + "\n"
            time_modified = "Last Modified: " + time_modified
            str = "File Name: " + file_name
            res = [str, time_modified, hash_value]
            for i in res:
                s.send(i)
                if s.recv(1024) != "Received":
                    break
        except:
            print "Connection Error"
            return

def checkall(s):
    files = os.popen("find . -not -path '*/\.*' -type f").read().split('\n')
    for i in files:
        if i != "":
            verify(s, i, False)
    s.send("Done")

def file_send(s, args):
    inp = args.split()
    flag = inp[1]
    filename = " ".join(inp[2:])
    err = os.popen('ls -l"' + filename + '"').read().split('\n')[0]
    if err == "":
        s.send("No Such File or Directory")
        return
    s.send("Received")

    if flag == "TCP":
        try:
            f = open(filename, "rb")
            byte = f.read(1024)
            while byte:
                s.send(byte)
                if s.recv(1024) != "Received":
                    break
                byte = f.read(1024)
            s.send("Done")
        except:
            print "Connection Error"
            return
    elif flag == "UDP":
        ncs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        nport = create_port(ncs)
        s.send(str(nport))
        data, addr = ncs.recvfrom(1024)
        if data == "Received":
            try:
                f = open(filename, "rb")
                byte = f.read(1024)
                while byte:
                    ncs.sendto(byte, addr)
                    data, addr = ncs.recvfrom(1024)
                    if data != "Received":
                        break
                    byte = f.read(1024)
                ncs.sendto("Done", addr)
            except:
                print "Connection Error"
                return

    else:
        print "Wrong Arguments"
        return
    hash = os.popen('md5sum "' + filename + '"').read().split()[0]
    s.send(hash)
    cmd = "stat --printf 'name= %n \tSize= %s bytes\t Timestamp=%z\n' " + filename
    res = os.popen(cmd).read()
    if s.recv(1024) == 'sendme':
        s.send(res)
        print "Done"

# Main Code

port = input("PORT: ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ""
try:
    s.bind((host, port))
except:
    print "Socket creation Error"
    exit(0)
s.listen(5)
shared = raw_input("Full Path of the folder to be shared: ")

try:
    log = open("server_log.log", "a+")
except:
    print "Cannot Open Log file"
    exit(0)

if not os.path.exists(shared):
    print "No Such Folder"
    exit(0)
elif not os.access(shared, os.R_OK):
    print "No Permissions to access"
    exit(0)
else:
    os.chdir(shared)

print "Directory changed"
print "Server is Up and Listening"
times = datetime.now().strftime("%I:%M%p %B %d, %Y")
log.write("Server Started at " + times + " \n\n")
while True:
    try:
        cs, addr = s.accept()
    except:
        s.close()
        print
        time_end = datetime.now().strftime("%I:%M%p %B %d, %Y")
        log.write("\nServer Closed at " + time_end + " \n\n")
        log.close()
        exit(0)
    temp_var = 0
    time = datetime.now().strftime("%I:%M%p %B %d, %Y")
    print("Got a connection from %s" % str(addr))
    log.write("Got a connection from " + str(addr) + "at " + time + " \n Commands Executed:\n")
    while True:
        temp_var = temp_var + 1
        try:
            args = cs.recv(1024)
            log.write(str(temp_var) + ". " + args + "\n")
        except:
            print "Connection closed to client"
            time_end = datetime.now().strftime("%I:%M%p %B %d, %Y")
            log.write("Connection Closed at " + time_end + " \n")
            break
        # p = raw_input()
        p = args.split(" ")
        if len(p) == 0 or p[0] == "close":
            cs.close()
            print "Connection closed to client"
            time_end = datetime.now().strftime("%I:%M%p %B %d, %Y")
            log.write(" Connection Closed at " + time_end + " \n")
            break
        elif p[0] == "index":
            if p[1] == "longlist":
                # long list
                longlist(cs)
            elif len(p) == 6:
                shortlist(cs, args)
                print args
            elif len(p) == 4 or len(p) == 5:
                print "Insufficient number of arguments passed"
            elif len(p) > 6:
                print "More than 6 arguments have been passed"
            elif p[1] == "shortlist":
                try:
                    cs.send("Syntax error")
                    cs.send("Input Format => prompt> index shortlist date1 time1 date2 time2")
                    cs.send("Done")
                except:
                    print "Connection Error"
                    break
            elif p[1] == "regex" and len(p) == 3:
                # regex
                regex(cs, p)
                # print p[1]
            # elif p[1] == "regex":
            #     regex(cs,p)
            #
        elif p[0] == "hash":
            if p[1] == "verify":
                verify(cs, p[2])
            elif p[1] == "checkall" and len(p) == 2:
                checkall(cs)
            else:
                try:
                    cs.send("Invalid Arguments")
                    cs.send("Done")
                except:
                    print "Connection Error"
                    break
        elif p[0] == "download":
            file_send(cs, args)
        else:
            cs.send("Invalid Command")
            cs.send("Done")
    cs.close()
