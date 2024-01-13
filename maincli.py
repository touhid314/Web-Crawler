#THIS IS A COMMAND LINE INTERFACE FOR THE PROGRAM

##@ UPDATE NETLOC_SERVERADDRESS_LIST IN GENERAL MODULE
# OTHERWISE DATABASE WON'T BE LOADED

import pyperclip, webbrowser, os, subprocess
import general
from msvcrt import getch
import threading
from urllib.parse import urlparse
from time import perf_counter


FILES_DIR_NAME = "files"

#@ KEEP A 2D LIST OF SERVER NETLOC AGAINST SERVER ADDRESS
#@ SHOULD BE REMOVED LATER; SERVERS SHOULD HAVE A LOG THAT WOULD LOG IT'S CRAWLING INFO
        #IT'S IN GENERAL.PY

#KEEP PATH OF ALL VIDEO DBs IN ONE LIST
video_db_files = []

#WALK IN THE files DIRECTORY AND FETCH PATH TO ALL VIDEO DB FILES AND STORE THE PATH IN THE LIST
# FETCH  ALL VIDEODB 
#the video_db_files will be like: ["files\ftpbd.net\videos.txt", "files\discovery.net\videos.txt"]

print("Checking all file's health...")


for current_path, folders, files in  os.walk(FILES_DIR_NAME):

    for file in files:

        if file == "videos.txt":
            db_filename = (current_path + '\\' + file)

            video_db_files.append(db_filename)


#IF SERVER OF THE VIDEODB IS NOT UP, REMOVE THAT VIDEO DB FROM VIDEODB LIST
#BUT IF THERE IS NO INTERNET THEN THE

#function for thread to execute
def threadfunc(server_address, lock):

    if not general.is_server_working(server_address, 3.5):
        print(f"{urlparse(server_address).netloc} not up")

        lock.acquire()
        video_db_files.remove(general.server_address_to_videodb_file(server_address))
        lock.release()


threads = []    #list for storing threads so that they can be joined later

lock = threading.Lock()

#start a thread for every videodb file in video_db_Files
for video_db_file in video_db_files: 
    
    server_netloc = video_db_file.split('\\')[-2]  #bcz video_db_file would be like files/ftpbd.net/videos.txt
    server_address = general.netloc_to_server_address(server_netloc)

    t = threading.Thread(target=threadfunc, args=[server_address, lock,])

    threads.append(t)
    t.start()

for thread in threads:
    thread.join()


print('startup time: ' + str( perf_counter() ) )

#MAKE ONE db_set FROM ALL THE VIDEOS.TXT FILE
db_set = set()
#go through the video_db_files list and open them and add them to db_set
for video_db_file in video_db_files:
    #open file
    f = open(video_db_file, 'r')
    #read lines from file and add to db_set
    for line in f:
        db_set.add(line.replace('\n', ''))

    #close file
    f.close()



while True:
    #INPUT SEARCH QUERY FROM USER
    print("\n________________________________________________________")
    query = input("Search Query (just hit enter to exit): ")

    if query == '':
        #DOUBLE CHECK USER'S DECSION
        key = input('exit?(y/n):  ')
        
        if key == 'y' or key =='Y':
            break
        if key == 'n' or key == "N":
            continue
        else:
            continue

        # break

    #MAKE A SEARCH_RESULT LIST FOR STORING SEARCH RESULT
    search_result = []


    #GO THROUGH THE DB_SET AND SEARCH FOR SEARCH QUERY IN THE SET USING in 
    for url in db_set:
        
        #PROCESS THE VIDEO NAME FOR BETTER SEARCHING
        processed_name = general.url_to_filename(url)

        #PROCESS QUERY STRING FOR BETTER SEARCHING
        #remove extra white spaces
        query = " ".join(query.split())

        #IF QUERY in SET_ELEMENT, ADD THE SET_ELEMENT TO THE SEARCH_RESULT LIST
        #make a case insensitive search
        if query.lower() in processed_name.lower():
            search_result.append(url)


    #PRINT SEARCH RESULT
    #IF SEARCH_LIST IS BIGGER THAN 10 PRINT ONLY FIRST 10 RESULT, OTHERWISE PRINT THE SEARCH RESULT LIST
    search_result.sort(key = general.url_to_filename) #it sorts the list based on the filename of the url
    
    print("\nSEARCH RESULT FOR " + query + '\n')

    if len(search_result) > 10:
        i = 1

        for url in search_result:
            name_to_show = general.url_to_filename(url)

            print(str(i) + '. ' + name_to_show)
            
            i += 1

            if (i-1)%10 == 0: #if i = 11, 21, 31 and so on then it should be checked
                if i < len(search_result):
                    print('\nPress N for NEXT/ Any other key to continue\n')
                    key = getch().decode()

                    if (key == 'N') or (key == 'n'):
                        continue
                    else:
                        break
                else:
                    break
        
    else:
        i = 1
        for url in search_result:
            name_to_show = general.url_to_filename(url)
            print(str(i) + '. ' + name_to_show)

            i += 1
    
    #LET USER BE ABLE TO:
    # DOWNLOAD/STREAM/COPY THE LINK FOR i th NUMBER RESULT AUTOMATICALLY
    #input what number of result needs to be downloaded

    if len(search_result) > 0: #if no result then don't show this dialog

        while True:
            #Stream: s <space> <number>     Download: d <space> <number>    Copy: c <space> <number>
            #Just hit enter to continue

            #TAKE COMMAND INPUT
            print("\nSTREAM: s <space> <number>     DOWNLOAD: d <space> <number>    COPY: c <space> <number>    SKIP: just hit enter ")

            cmd = input()
            
            if cmd == '':
                break

            #strip whitespace, make lowercase
            cmd = cmd.strip().lower()

            #PARSE COMMAND
            mode = cmd.split()[0]
            try:
                number = int(cmd.split()[1])
            except:
                print("invalid input")
                continue

            #TAKE ACTION ACCORDING TO COMMAND
            url = search_result[number - 1]

            if mode == 's':
                print("Starting stream in video player...")
                flag = general.playvideo(url)

                if flag == -1:    #playvideo returns -1 user inputs nothing for player loc
                    print("couldn't find default app for the video extension")
                    continue

                elif flag == -2:
                    print("Video player's location not specified properly")
                    continue

            if mode == 'd':
                webbrowser.open(url)
                print("opening browser to download file...")

            if mode == 'c':
                pyperclip.copy(url)
                print("url copied")



            # num = input("\nEnter result no. to download (just hit enter to skip):

            # try:
            #     if num == '':
            #         break
            #     else:
            #         
            # except:
            #     print('invalid input')
