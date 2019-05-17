'''
File: client.py
Name: Shaurya Chandhoke
Class: CS 356 102
'''
import sys
import re #used to split url via regex
from pathlib import Path #used to find file
from socket import *

def rewrite(CACHENAME, filename, lineIndex, msg):
    lines = open(CACHENAME).read().splitlines()
    lines[lineIndex] = msg
    string = '\n'.join(lines)
    open(CACHENAME, 'w').write(string + '\n')

# Start
argv = sys.argv
if(len(argv) < 2):
    print("Error, please include url\nex: \'localhost:12000/filename.html\'")
    exit()

CACHENAME = "cache.txt" #Change to rename cache file
DATALEN = 100000 #Change for TCP buffer size

url = argv[1]
requestHost = url.split("/")[0]

cacheFileFound = False

parser = re.split(':|/', url)
socketHost = parser[0]
socketPort = int(parser[1])
filename = parser[2]

config = Path('./' + CACHENAME)
cacheExists = config.is_file() #Checking if cache file exists

if(cacheExists):

    lineIndex = 0

    with open(CACHENAME, 'a+') as cache:
        cache.seek(0)
        for line in cache:
            csv = re.split(',', line, 1)
            if(csv[0].strip() == filename):
                cacheFileFound = True
                requestMod_Date = csv[1]
                break

            lineIndex += 1

        if(cacheFileFound): #CONDITIONAL HTTP GET
            GET_Request = "GET /" + filename + " HTTP/1.1\r\n"
            GET_Request += "Host: " + requestHost + "\r\n"
            GET_Request += "If-Modified-Since: " + requestMod_Date + "\r\n"

            GET_Request += "\r\n"

        else: #HTTP GET
            GET_Request = "GET /" + filename + " HTTP/1.1\r\n"
            GET_Request += "Host: " + requestHost + "\r\n"

            GET_Request += "\r\n"

else: #HTTP GET
    GET_Request = "GET /" + filename + " HTTP/1.1\r\n"
    GET_Request += "Host: " + requestHost + "\r\n"

    GET_Request += "\r\n"

print(GET_Request) #Send request to stdout
clientSocket = socket(AF_INET, SOCK_STREAM) #Create TCP socket

try:
    clientSocket.connect((socketHost,socketPort))
    clientSocket.send(GET_Request.encode())
    data = clientSocket.recv(DATALEN)
    response = data.decode()

    print(response) #Send response from server to stdout

    code = int(response[9:12]) #HTTP GET response header code

    #If file exists or if file has been previously modified, update cache
    if(code == 200):
        for element in response.split('\r\n'):
            if("Last-Modified: " in element):
                modDate = re.split("Last-Modified: ", response)[1].strip("\r\n").split()[0:6]
                modDate = " ".join(modDate)

        with open(CACHENAME, 'a+') as cache:
            if(cacheFileFound):
                rewrite(CACHENAME, filename, lineIndex, (filename + "," + modDate))
            else:
                cache.write(filename + "," + modDate + '\n')

except ConnectionRefusedError:
    print("Failed to connect -- Connection refused")
    exit()


clientSocket.close()
