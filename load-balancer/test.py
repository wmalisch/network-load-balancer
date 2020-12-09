import datetime
import time
import argparse
from urllib.parse import urlparse
import socket
TIMEOUT = 60*5

servs = { 'localhost:8080':15.029721, 'localhost:592903':34.290423, 'localhost:2893':-1 }
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("scket created succesfully")
print("Default socket timeout: "+ str(s.gettimeout()))
s.settimeout(TIMEOUT)
print("current socket timeout: "+ str(s.gettimeout()))