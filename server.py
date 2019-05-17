'''
File: server.py
Name: Shaurya Chandhoke
UCID: sc855
Class: CS 356 102
'''
import sys
import re #used to split url via regex
from pathlib import Path #used to find file
from socket import *
import datetime, time
import os.path

def contentInfo(filename):
    contentLength = "Content-Length: "
    CONTENTTYPE= "Content-Type: text/html; charset=UTF-8\r\n\r\n"
    contentString = ""

    with open(filename, 'r') as file:
        for line in file:
            contentString += line

    contentLength += str(len(bytes(contentString, 'UTF-8')))
    contentLength += "\r\n"
    return contentLength + CONTENTTYPE + contentString

def dateReturn():
    currTime = datetime.datetime.utcnow()
    date = currTime.strftime("%a, %d %b %Y %H:%M:%S GMT")
    date += "\r\n"
    return "Date: " + date

def modDateReturn():
    secs = os.path.getmtime(filename)
    modTime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(secs))
    return modTime

def fileinfo(filename):
    date = dateReturn()
    modDate = "Last-Modified: " + modDateReturn() + '\r\n'
    content = contentInfo(filename)
    return (date + modDate) + content



# Start
argv = sys.argv
if(len(argv) < 3):
    print("Please enter cla <IP> <Port>")
    exit()

dataLen = 100000 #Change for TCP buffer size
serverIP = argv[1]
serverPort = int(argv[2])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen(1) #Listen for requests from clients

print("Server is listening")

while(True):
    mod_Flag = False
    connectionSocket, address = serverSocket.accept()
    data = connectionSocket.recv(dataLen).decode()

    if("If-Modified-Since: " in data):
        mod_Flag = True
        mod_Date = time.strptime(re.split("If-Modified-Since:", data)[1].strip(), "%a, %d %b %Y %H:%M:%S %Z")
        mod_Time = time.mktime(mod_Date)

    filename = re.split('/', data.split()[1])[1]

    config = Path('./' + filename)
    if(config.is_file()): #If requested HTML file exists and is available
        if(mod_Flag):

            trueMod_Date = time.strptime(modDateReturn(), "%a, %d %b %Y %H:%M:%S %Z")
            trueMod_Time = time.mktime(trueMod_Date)

            if(trueMod_Time == mod_Time):
                responseMSG = "HTTP/1.1 304 Not Modified\r\n" + dateReturn() + "\r\n"
            else:
                responseMSG = "HTTP/1.1 200 OK\r\n" + fileinfo(filename)
        else:
            responseMSG = "HTTP/1.1 200 OK\r\n" + fileinfo(filename)
    else:
        responseMSG = "HTTP/1.1 404 Not Found\r\n" + dateReturn() + "\r\n"

    connectionSocket.send(responseMSG.encode())

    connectionSocket.close()
