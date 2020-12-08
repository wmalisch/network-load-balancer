import datetime
import time

now = datetime.datetime.now()
time.sleep(1.5)
later = datetime.datetime.now()
print(now)
print(later)
difference = later - now
print(difference)
m = str(difference.microseconds)
mint = int(m[0:3])
print(m)

epoch = datetime.datetime.utcfromtimestamp(0)

servs = { 'localhost:8080':15.029721, 'localhost:592903':34.290423, 'localhost:2893':-1 }
print(servs)
servs = dict(sorted(servs.items(), key=lambda item: item[1]))
print(servs)

# for key in list(servs):
#     if servs[key] == -1:
#         del servs[key]
# print(servs)