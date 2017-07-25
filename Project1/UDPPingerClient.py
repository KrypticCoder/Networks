# UDPPingerClienty.py
# Dimitar Vasilev, Matt Quesada

from socket import *
import time
from time import gmtime, strftime
from datetime import datetime

dayOfWeek = {"1": "M", "2": "T", "3": "W", "4": "R", "5": "F", "6": "S", "7": "U"}


def getCurrentTime():
    DateTime = strftime("%Y-%m-%d %I:%M:%S %u", gmtime()).split(" ")
    curDate = DateTime[0]
    curTime = ":".join(DateTime[1].split(":")[:2])
    weekday = DateTime[2]
    day = dayOfWeek[str(weekday)]
    return {"curDate": curDate, "curTime": curTime, "weekDay": day}


totalPings = 0
serverName = "127.0.0.1"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = raw_input('Input lowercase sentence: ')
clientSocket.settimeout(1)


while(totalPings < 10):
    now = getCurrentTime()
    totalPings = totalPings + 1
    start = time.time()
    str_list = []
    str_list.append("Ping")
    str_list.append(" ")
    str_list.append(str(totalPings))
    str_list.append(" ")
    str_list.append(str(now['curDate']))
    str_list.append(" ")
    str_list.append(now["weekDay"])
    str_list.append(" ")
    str_list.append(str(now['curTime']))
    str_list.append(" UTC")
    dataOut = ' '.join(str_list)
    print(dataOut.strip())
    clientSocket.sendto(dataOut, (serverName, serverPort))
    try:
        dataIn, serverAddress = clientSocket.recvfrom(2048)
        print(dataIn.strip())
        elapsed = (time.time() - start) * 1000
        print("RTT:", elapsed)
        print('\n')
    except:
        print("Request timed out")
        break
clientSocket.close()





     



