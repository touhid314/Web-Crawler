from tkinter import *
import pyperclip, webbrowser, os
import general
import threading
from urllib.parse import urlparse
from time import perf_counter

class main:
    def __init__(self):
        ##LOAD DATABASE AS A SET OF LINKS
        self.db_set = self.load_database()


        ##GUI STARTS
        #window
        window = Tk()
        window.title("Aluminium")
        window.resizable(False, False)

        #SEARCH FRAME
        search_frame = Frame(window)
        search_frame.pack()

        #entry box
        self.query  = StringVar()
        entry = Entry(search_frame, textvariable = self.query, width = 60)
        entry.grid(row = 1, column = 1)
        entry.focus()

        #search key; hit enter to search
        entry.bind("<Return>", self.show_search_result)

        #search button
        search_btn = Button(search_frame, text = "Search", command = self.show_search_result)
        search_btn.grid(row = 1, column = 2)

        


        #RESULT FRAME
        result_frame = Frame(window, height = 40)
        result_frame.pack()

        self.label_list = []
        self.dwnldbtn_list = []
        self.streambtn_list = []
        self.nextbutton = Button(result_frame, text = "Next", command = self.nextbtn_handler)

        for i in range(10):
            label = Message(result_frame, justify = LEFT, anchor = 'w', width = 500)
            btn = Button(result_frame, text = "Download", command = (lambda i=i: self.dld_from_search_res_list(i) ) )
            streambtn = Button(result_frame, text = "Stream", command = lambda i=i : self.stream_from_srch_res_list(i))
            self.label_list.append(label)
            self.dwnldbtn_list.append(btn)
            self.streambtn_list.append(streambtn)
        



        window.mainloop()


    def load_database(self):
        
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


        for current_path, _, files in  os.walk(FILES_DIR_NAME):

            for file in files:

                if file == "videos.txt":
                    db_filename = (current_path + '\\' + file)

                    video_db_files.append(db_filename)

        #IF SERVER OF THE VIDEODB IS NOT UP, REMOVE THAT VIDEO DB FROM VIDEODB LIST

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

        
        return db_set


#OTHER METHODS
    def pack_widgets(self, no_of_rows):
        i = 1

        for i in range(no_of_rows):
            self.label_list[i].grid(row = i, column = 1, sticky = 'w')
            self.dwnldbtn_list[i].grid(row = i, column = 3, sticky = 'e')
            self.streambtn_list[i].grid(row = i, column = 2, sticky = 'e')

        self.nextbutton.grid(row = i + 1, column = 4, sticky = 'e')

    def make_search_result(self, query):
        #THIS METHOD SEARCHES IN THE VIDEODB SET AND RETURNS SEARCH RESULT AS A SET
        
        query = self.query.get()


        #MAKE A SEARCH_RESULT LIST FOR STORING SEARCH RESULT
        search_result = []


        #GO THROUGH THE DB_SET AND SEARCH FOR SEARCH QUERY IN THE SET USING in 
        for url in self.db_set:

            #PROCESS THE URL FOR BETTER SEARCHING
            processed_name = general.url_to_filename(url)

            #PROCESS QUERY STRING FOR BETTER SEARCHING
            #remove extra white spaces
            query = " ".join(query.split())

            if query == '':
                self.search_result = search_result
                return

            #IF QUERY in SET_ELEMENT, ADD THE SET_ELEMENT TO THE SEARCH_RESULT LIST
            #make a case insensitive search
            if query.lower() in processed_name.lower():
                search_result.append(url)

        search_result.sort(key = general.url_to_filename)
        self.search_result = search_result


    def show_search_result(self, event = None):
        self.make_search_result(self.query)
        
        if len(self.search_result) == 0:
            return
        
        #KEEP A COUNT OF HOW MANY RESULTS HAVE BEEN SHOWN
        self.count = 0

        #FIRST FLUSH CLEAR ALL EXISTING ROWS
        for i in range(10):
            self.label_list[i].grid_forget()
            self.streambtn_list[i].grid_forget()
            self.dwnldbtn_list[i].grid_forget()
            

        #NOW SHOW ALL NEW ROWS
        if len(self.search_result) >= 10:
            r = 10
        else:
            r = len(self.search_result)
        
        #pack the required number of rows
        self.pack_widgets(r)
        
        #show text within the rows
        for i in range(r):
                name_to_show = str(i + 1) +'. ' + general.url_to_filename(self.search_result[self.count])
                          
                self.label_list[i]["text"] = name_to_show
                self.count += 1


    def nextbtn_handler(self):

        #FIRST FLUSH CLEAR ALL EXISTING ROWS
        for i in range(10):
            self.label_list[i].grid_forget()
            self.streambtn_list[i].grid_forget()
            self.dwnldbtn_list[i].grid_forget()
        

        #NOW SHOW ALL NEW ROWS
        if len(self.search_result) >= 10:
            r = 10
        else:
            r = len(self.search_result)
        
        #pack the required number of rows
        self.pack_widgets(r)
        
        #show text within the rows
        for i in range(r):
                print(self.count, len(self.search_result))
                if self.count + 1 > (len(self.search_result)):
                    return

                name_to_show = str(self.count + 1) +'. ' + general.url_to_filename(self.search_result[self.count])
                          
                self.label_list[i]["text"] = name_to_show
                self.count += 1


    def dld_from_search_res_list(self, i):
        print(i)
        webbrowser.open(self.search_result[i])

    def stream_from_srch_res_list(self, i):
        print("Starting stream in video player...")
        flag = general.playvideo(self.search_result[i])

        if flag == -1:    #playvideo returns -1 user inputs nothing for player loc
            print("couldn't find default app for the video extension")

        elif flag == -2:
            print("Video player's location not specified properly")


main()