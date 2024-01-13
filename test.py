import requests, pyperclip, os.path
from urllib.parse import urlparse, urljoin
# import general
from time import sleep, perf_counter
import signal, threading
from msvcrt import getch
import subprocess, sys

# video = r"http://103.102.253.250/Data/Data/Movies/Animation/2019/A%20Shaun%20the%20Sheep%20Movie%20Farmageddon%20%282019%29/A.Shaun.the.Sheep.Movie.Farmageddon.2019.720p.BluRay.H264.AAC-RARBG.mp4"
# playerloc = r"C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe"

# lst = [playerloc, video]

# subprocess.call(lst)

# search = "IDMan.exe"

# def func(fileslist):
#     out = ''
#     for file in fileslist:
#         if file == search:
#             out =  os.path.abspath(file)

#     return out

# for root, dirs, files in os.walk(r"C:/"):
#     loc = func(files)
#     if loc != '' :
#         print(loc)
#         break

FILES_DIR_NAME = 'files'

f = open(FILES_DIR_NAME + '/' + 'appdata.txt', 'r+')
    #file is empty. input location
a = f.readline()
a = a.replace('\n', '')
print(a)

if a == '':
    playerloc = input("\nSeems like video player's location has not been specified yet.\
                    \n Please enter video player's location. (example: C:/programs/vlc/vlc.exe)\
                    \n Video Player Location: ")
    f.write(playerloc)
else:
    #read player's location
    print(a)

f.close()
print(a)
    


