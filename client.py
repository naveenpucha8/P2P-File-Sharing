import socket
import os
from datetime import datetime
import hashlib

#function to write in the log file
def end_server():
    time_end = datetime.now().strftime("%I:%M%p %B %d, %Y")
    log.write("------- Connection Closed at " + time_end + " -------\n")
    log.close()
    s.close()
    exit(0)

def create_port(socket):
    cp = random.randint(0, 9999)
    try:
        socket.bind((host, cp))
    except:
        return create_port(socket)
    return cp

def recieve_data(inp):
    try:
        s.send(inp)
    except:
        print "Error in Connection"
        return
    while True:
        try:
            data = s.recv(1024)
        except:
            print "Error in Connection"
            end_server()
            break
        if data == "Done":
            break
        try:
            s.send("Received")
        except:
            print "Connection Error"
            end_server()
        print data
        print
    return

def func():
    print 'Updating directories'
    mtimein={}
    for i in os.listdir('.'):
        mtimein[i]=time.ctime(os.path.getmtime(i))

    s.send('Received')
    x=int(s.recv(1024))
    # s.send('continue')

    mtimethere={}
    namex={}
    for i in range(x):
        namex[i]=s.recv(1024)
        mtimethere[namex[i]]=s.recv(1024)

    for i in range(x):
        if (str(namex[i]) not in mtimein) or comp(mtimein[namex[i]],mtimethere[namex[i]])==0:
            s.send('Received')
            s.recv(1024)
            s.send(namex[i])
            s.recv(1024)
            s.send('hi')
            f= open(namex[i],'wb')


            while True:
              text=s.recv(1024)
              if text=='Done':
                break
              print('receiving data....')

              if not text:
                break
              f.write(text)
              s.send('Received')
            print 'Updated file:',namex[i]
            f.close()


#main Code
port = input("PORT: ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ""
down = raw_input("Download location of the folder: ")
if not os.path.exists(down):
    print "No Such Folder"
    exit(0)
elif not os.access(down, os.W_OK):
    print "No Permissions to access"
    exit(0)
else:
    os.chdir(down)
try:
    log = open("client_log.log", "a+")
except:
    print "Cannot Open Log file"
    exit(0)
try:
    s.connect((host, port))
except:
    print "No available server found on given port"
    s.close()
    exit(0)
temp_var = 0
print "Connection Established"
time = datetime.now().strftime("%I:%M%p %B %d, %Y")	
print "Connected to " ,"server on",time

log.write("Connected to " + host + " on " + time + " \nCommands Sent:\n")
while True:
    #before_prompt()
    temp_var += 1
    args = raw_input("prompt> ")
    inp = args.split()
    log.write(str(temp_var) + ". " + args + "\n")
    if len(inp) == 0 or inp[0] == "close":
        s.send(args)
        print "Logged out from server"
        end_server()
    elif inp[0] == "index" or inp[0] == "hash":
        recieve_data(args)
    elif inp[0] == "download":
#
        s.send(args)
        data = s.recv(1024)
        if inp[1] != "UDP" and inp[1] != "TCP":
            print "Error in the arguments"
            print "Format download <UDP/TCP> <file_name>"
            # return
        if data != "Received":
            print data
            # return
        if inp[1] == "TCP":
            try:
                f = open(" ".join(inp[2:]), "wb+")
            except:
                print "Insufficient Permissions or Space"
                # return
            while True:
                data = s.recv(1024)
                if data == "Done":
                    break
                f.write(data)
                s.send("Received")
            f.close()

        elif inp[1] == "UDP":
            nport = int(s.recv(1024))
            ncs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (host, nport)
            ncs.sendto("Received", addr)
            try:
                f = open(" ".join(inp[2:]), "wb+")
            except:
                print "Insufficient Permissions or Space"
                # return
            while True:
                data, addr = ncs.recvfrom(1024)
                if data == "Done":
                    break
                f.write(data)
                ncs.sendto("Received", addr)
            f.close()
            ncs.close()
            # UDP()
        hash_value = s.recv(1024)
        f = open(" ".join(inp[2:]), 'rb')
        original_hash = hashlib.md5(f.read()).hexdigest()

        if hash_value != original_hash:
            # print hash,original_hash
            print "File transfer Unsuccessful"
        else:
            s.send("sendme")
            data = s.recv(1024)
            print
            print data
            print "md5hash: ", hash_value
            print "Successfully Downloaded"
            #print hash_value,original_hash
    else:
        print "Invalid Command"
s.close()
