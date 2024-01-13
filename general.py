#THIS FILE INCLUDES MANY FILES USED IN OTHER FILES WITH REFERENCE TO THE FILENAME general
#DON'T CHANGE THE FILENAME FROM general

import requests, subprocess, threading
from urllib.parse import urlparse
from time import perf_counter
import os.path
import shlex, winreg

FILES_DIR_NAME = 'files'

#@ SHOULD BE REMOVED LATER
NETLOC_T0_SERVERADDRESS_LIST = [['103.102.253.250', r'http://103.102.253.250/Data/'],

                                ['server1.ftpbd.net', r'http://server1.ftpbd.net/FTP-1/'],

                                ['server2.ftpbd.net', r'http://server2.ftpbd.net/FTP-2/'],

                                ['server4.ftpbd.net', r'http://server4.ftpbd.net/FTP-4/'],

                                ['cdn1.discoveryftp.net', r'http://cdn1.discoveryftp.net/'],

                                ['cdn2.discoveryftp.net', r'http://cdn2.discoveryftp.net/'],

                                ['103.114.39.39', r'http://103.114.39.39/'],

                                ['index.circleftp.net', r'http://index.circleftp.net/'],]


VIDEO_FILE_EXTENSION = ['webm', 'mkv', 'flv',
                        'vob', 'ogv', 'ogg',
                        'avi', 'wmv', 'yuv',
                        'rm', 'viv', 'asf',
                        'amv', 'mp4', 'm4p',
                        'm4v', 'mpg', 'mp2',
                        'mpeg', 'm2v', '3gp',
                        '3g2', 'f4v']

WEBPAGE_FILE_EXTENSION = ['html', 'htm', 'php',
                         'aspx', 'asp', 'xhtml', 
                         'srf', 'php3','php4', 'phtml' 'axd',
                         'asx', 'asmx', 'ashx',
                         'jhtml', 'jsp', 'jspx']


def is_video(string):
    if string.split('.')[-1] in VIDEO_FILE_EXTENSION:
        return True
    else:
        return False

def is_webpage_link(url):

    #URL MUST HAVE SCHEME INCLUDED OTHERWISE FUNCTION WON'T WORK PROPERLY
    #IT'S BECAUSE URLPARSE DON'T WORK PROPERLY WITHOUT SCHEME INCLUDED
    
    urlpath = urlparse(url).path

    if ''.join(urlpath.split('.')) == urlpath:
        #if there is no . in the urlpath then after split and before split is same
        #join is used to convert splitted list to string
        return True
    elif urlpath.split('.')[-1] in WEBPAGE_FILE_EXTENSION:
        return True
    else:
        return False


def get_response(url):
    try:
        r = requests.get(url, timeout = 1)
        
        try:
            r.raise_for_status()
        except:
            print('download error: ' + url + '\n')
            return 0

    except:
        print("couldn't connect to server or timedout\n")
        return 0

    return r

def get_header(url, timeout):
    try:
        h = requests.head(url, timeout = timeout)
        
        try:
            h.raise_for_status()
        except: #Exception as e:
            # print(e)
            return 0
        
    except:
        # print("couldn't connect to server or timedout\n")
        return 0

    return h.headers


def trim_scheme(url):
    return url.replace(urlparse(url).scheme + "://" , '')

def trim_last_slash(url):
    if url[-1] == '/':
        a = list(url)
        del a[-1]
        url = ''.join(a)
        return url
    else:
        return url


def in_boundary_url(url, boundary_url):
    processed_boundary_url = trim_scheme(trim_last_slash(boundary_url))
    processed_link = trim_scheme(trim_last_slash(url))

    if (processed_boundary_url not in processed_link):
        return False
    else:
        return True


def mkfile(dir1, dir2, filename):
    #THIS FUNCTION MAKES FILE IN dir1/dir2/
    #IF THE FILE ALREADY EXIST IT DOESN'T DO ANYTHING
    if not os.path.isfile(dir1 + '/' + dir2 + '/' + filename):
        #file dir doesn't exist
        if not os.path.isdir(dir1):
            os.mkdir(dir1)
        #file/ dir2 dir doesn't exist
        if not os.path.isdir(dir1 + '/' + dir2):
            os.mkdir(dir1 + '/' + dir2)
        #file/ dir2/queue dir doesn't exist
        f = open(dir1 + '/' + dir2 + '/' + filename, 'w')
        f.close()

def txtfile_to_set(filename):
    #CONVERTS TEXTFILE TO SET AND RETURN THE SET
    #IF TEXT FILE IS EMPTY RETURN AN EMPTY SET
    set_to_make = set()

    f = open(filename, 'r')
    for line in f:
        line = line.replace('\n', '')
        set_to_make.add(line)
    f.close()
    
    return set_to_make

def txtset_to_txtfile(fromset, tofilename, mode):
    f = open(tofilename, mode)

    for i in fromset:
        f.write(i + '\n')

    f.close()


def url_to_filename(url):
    #CONVERTS AN URL LIKE: http://example.com/whiplash.%282015%29.brrip.mkv
    #TO whiplash (2015) brrip mkv
    filename = url.split('/')[-1]

    filename = filename.replace('.', ' ')
    filename = filename.replace('%20', ' ').replace('%28', '(').replace('%29', ')').replace('%21', '!').replace('%26', '&').replace('%27', '\'').replace('%2C', ',').replace('%2D', '-').replace('%3A', ':').replace('%3F', '?').replace('%5B', '[').replace('%5D', ']').replace('%2B', '+').replace('%23', '#')
    
    return filename

def get_default_windows_app(suffix):
    class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, suffix)
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)) as key:
        command = winreg.QueryValueEx(key, '')[0]
        return shlex.split(command)[0]


def playvideo_threadfunc(playerloc, filename):
    lst = [playerloc, filename]
    subprocess.call(lst)



def playvideo(filename):

# #TO PLAY VIDEO IN A PLAYER, FIRST PLAYER PROGRAM'S LOCATION HAS TO BE KNOWN.
    # #PLAYER LOCATION HAS TO BE LOADED FROM APPDATA.TXT FILE

    # ##MAKE SURE FILE APPDATA.TXT EXISTS
    # #if file doesn't exist make it, with proper value inside
    # if not os.path.isfile(FILES_DIR_NAME + '/' + 'appdata.txt'):
    #     #make the file
    #     f = open(FILES_DIR_NAME + '/' + 'appdata.txt', 'w')
    #     #take as input from user video player location    
    #     loc = input("\nSeems like video player's location has not been specified yet.\
    #                 \n Please enter video player's location. (example: C:/programs/vlc/vlc.exe)\
    #                 \n Video Player Location: ")

    #     if loc == '': #user didn't input anything
    #         return -1
    #     #write the player location to file
    #     f.write(loc)
    #     #close file
    #     f.close()

    # ##OPEN FILE. READ PLAYER LOC
    # #now it's sure the file exists. open it in read write mode to read player location
    # f = open(FILES_DIR_NAME + '/' + 'appdata.txt', 'r+')
    # playerloc = f.readline()
    # playerloc.replace('\n', '')
    
    # #file is empty. input location
    
    # if playerloc == '':
    #     playerloc = input("\nSeems like video player's location has not been specified yet.\
    #                 \n Please enter video player's location. (example: C:/programs/vlc/vlc.exe)\
    #                 \n Video Player Location: ")
    #     f.write(playerloc)

    # f.close()
    
##GET DEFAULT PLAYER'S LOCATION AUTOMATICALLY
    try:
        playerloc = get_default_windows_app('.' + filename.split('.')[-1])
    except:
        return -1

    ##PLAY FILE IN PLAYER WITH GIVEN FILENAME
    lst = [playerloc, filename]
    thread = threading.Thread(target=playvideo_threadfunc, args=lst)
    try:
        thread.start()
    except:
        return -2

def is_server_working(url, timeout):
    #GIVEN AN URL IT CHEKS WHETHER THE URL IS WORKING
    #THIS FUNCTION IS MADE FOR FTP SERVER SIDE, WHERE IF ONE PAGE IS WORKING USUALLY ALL OTHER
    # PAGES ARE WORKING TOO.AND THE SERVER IS UP 
    # THIS FUNCTION WON'T BE GOOD FOR SITES WHERE HOMEPAGE IS WORKING BUT MANY LINKS INSIDE
    #ARE NOT WORKING
    h = get_header(url, timeout)

    if h == 0:
        return False
    else:
        return True

def netloc_to_server_address(netloc):
    server_address = None

    for i,j in NETLOC_T0_SERVERADDRESS_LIST:
        if i == netloc:
            server_address = j

    return server_address


def server_address_to_videodb_file(addresss):
    #input: http://ftpbd.net    output: files/ftpbd.net/videos.txt
    videodb_file = ''

    for i, j in NETLOC_T0_SERVERADDRESS_LIST:
        if j == addresss:
            videodb_file = FILES_DIR_NAME + '\\' + i + '\\' + 'videos.txt'

    return videodb_file





# playvideo("http://cdn1.discoveryftp.net/Tutorial/Android%20Bootcamp%20Series-Video%20Tutorials%20%282012%29%20720p/03%20-%20Hello%2C%20World_%20Android%20Bootcamp%20Series%202012.mp4")

# sa =  netloc_to_server_address('103.102.253.250')

# if is_server_up(sa):
#     print("up")
# else:
#     print("down")


# st = {'hello.world i am here', 'my name is touhid.mkv', 'goodbye'}
# txtset_to_txtfile(st, "testtxt.txt", 'w')

# st = txtfile_to_set("testtxt.txt")
# print(len(st))
# print(st)

#get_response("http://cdn1.discoveryftp.net/Movies/Hindi/2020/Baaghi%203/Baaghi.3.2020.1080p.DSNP+.WEB-DL.AAC2.0.x264-Telly.mkv")

# url = "ftp://example.com"
# print(trim_scheme(url))

# url = "www.example.com/abc"
# print(trim_last_slash(url))

# url = "https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=13&ct=1597004811&rver=7.3.6963.0&wp=MBI_SSL&wreply=https%3a%2f%2fwww.microsoft.com%2fen-us%2fwindows%2f&lc=1033&id=74335&aadredir=1"
# print(is_webpage_link(url))
