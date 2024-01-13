import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import general
from requests.exceptions import ConnectionError
from time import perf_counter


class Spider:
    def __init__(self, start_page_url, boundary_url, downloader):
        self.start_page_url = start_page_url
        self.boundary_url = boundary_url
        self.downloader = downloader

        self.netloc = self.get_netloc(self.boundary_url)
        self.domain_name = self.get_domain_name(self.boundary_url)
        #filenames
        self.__queue_filename = 'files' + '/' + self.netloc + '/' + "queue.txt"
        self.__crawled_filename = 'files' + '/' + self.netloc + '/' + "crawled.txt"
        self.__couldntcrawl_filename = 'files' + '/' + self.netloc + '/' + "couldntcrawl.txt"
        #@ CHANGE TO VIDEOS.DB
        self.__videodb_filename = 'files' + '/' + self.netloc + '/' + "videos.txt"
       
        self.make_files()
        self.initialize_sets()

        #import downloader module as per argument
        #import selenium
        if self.downloader == "selenium":
            #import selenium
            from selenium import webdriver

            #start phantomjs
            print("launching headless browser\n")
            phantomjs_path = r"phantomjs-2.1.1-windows\bin\phantomjs.exe"
            self._driver = webdriver.PhantomJS(executable_path = phantomjs_path)
        #import requests
        elif self.downloader == "requests":
            import requests
        #if not specified properly exit
        else:
            print("\ndownloader not specified properly in spider argument\n")
            sys.exit()
        
        print('spider created\n')


    def get_domain_name(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme + '://' + parsed_url.netloc

    def get_netloc(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def make_files(self):
        #THIS METHOD MAKE SURE files/netloc/required_files  exist
        #make queue.txt if doesn't exist
        general.mkfile('files', self.netloc, 'queue.txt')
        #make crawled.txt if doesn't exist
        general.mkfile('files', self.netloc, 'crawled.txt')
        #make couldntcrawl.txt if doesn't exist
        general.mkfile('files', self.netloc, 'couldntcrawl.txt')
        #make videos.db if doesn't exist
        #@ CHANGE LATER TO VIDEOS.DB
        general.mkfile('files', self.netloc, 'videos.txt')  

    def initialize_sets(self):
        #queue set
        self.queue_set = general.txtfile_to_set(self.__queue_filename)
        #crawled set
        self.crawled_set = general.txtfile_to_set(self.__crawled_filename)
        #couldnt_crawl set
        self.couldnt_crawl_set = general.txtfile_to_set(self.__couldntcrawl_filename)
        #videobd set
        #@ VIDEODB SHOULD BE BINARY FILE; CHANGE LATER; use binaryfile_to_Set()
        self.videodb_set = general.txtfile_to_set(self.__videodb_filename)

        #if queue file was empty then the set will be empty and the start_page_url will be only there
        #but if queue file was not empty for some reason then, CRAWLING WON'T START FROM 
        #START_PAGE_URL
        if self.start_page_url not in self.crawled_set:
            self.queue_set.add(self.start_page_url)


    def crawl(self):

        video_count = 0
        crawled_count = 0

        while True:
##GET LINK_TO_CRAWL FROM QUEUESET
            if len(self.queue_set) > 0:     #get the first link of queue_set for crawling
                for i in self.queue_set:
                    link_to_crawl = i
                    break
            else:
                #if len(queue_set) is 0 then CRAWLING IS FINISHED

                #WRITE THE SETS TO FILE
                #write queue_set to queue.txt
                general.txtset_to_txtfile(self.queue_set, self.__queue_filename, 'w')
                #write crawled_set to crawled.txt
                general.txtset_to_txtfile(self.crawled_set, self.__crawled_filename, 'w')
                #write couldntcrawl_set to couldntcrawl.txt
                general.txtset_to_txtfile(self.couldnt_crawl_set, self.__couldntcrawl_filename, 'w')
                #write videodb_set to videos.db
                general.txtset_to_txtfile(self.videodb_set, self.__videodb_filename, 'w')


                #show message
                print('finished crawling the domain ' + self.domain_name + '\n')
                #break out of the crawling loop
                break             

            print('Now Crawling: ' + link_to_crawl + '\n')

##DOWNLOAD THE PAGEHTML

    #CHECK BEFORE DOWNLOADING
        #no need to check before downloading.
        #check is done, without sending request to server, before adding to queue
        #that should guarantee that the link returns text/html file

    #DOWNLOAD TEXT/HTML CONTENT

            if (self.downloader == "selenium"):
                try:
                    #@ add timeout
                    self._driver.get(link_to_crawl)
                    pagehtml = self._driver.page_source
                    
                ##@ PROBABLY CAN'T CATCH DOWNLOAD ERROR LIKE THIS IN SELENIUM
                except:
                    self.move_from_set_to_set(self.queue_set, self.couldnt_crawl_set, link_to_crawl)
                    print("couldn't crawl: " + str(len(self.couldnt_crawl_set)) + 'links\n')
                    
                    #write couldntcrawl_set to file
                    general.txtset_to_txtfile(self.couldnt_crawl_set, self.__couldntcrawl_filename, 'w')

                    continue

            #if not selenium then definitely requests because __init__ method veified
            #only one of these two has been specified in the class initializer
            else:
                r = general.get_response(link_to_crawl)

                if r == 0:
                    self.move_from_set_to_set(self.queue_set, self.couldnt_crawl_set, link_to_crawl)
                    print("couldn't crawl: " + str(len(self.couldnt_crawl_set)) + 'links\n')

                    #write couldntcrawl_set to file
                    general.txtset_to_txtfile(self.couldnt_crawl_set, self.__couldntcrawl_filename, 'w')

                    continue
                else:
                    pagehtml = r.text


##PARSE PAGEHTML TO FIND ALL A TAG'S HREF
            soup = BeautifulSoup(pagehtml, features="lxml")
            anchor_list = soup.select('a')
            
        #for loop starts
            for anchor in anchor_list:

                link = anchor.get('href')

            #convert link to absolute url
                link = urljoin(link_to_crawl, link)

            #DETERMINE WHETHER A LINK GOES TO QUEUESET, VIDEODBSET OR gets discarded
                if link == None:
                    continue

                elif (not general.in_boundary_url(link, self.boundary_url)) and (not general.is_video(link)):
                    continue

                elif general.is_video(link):
                    if (link not in self.videodb_set): #add only if link isn't already in videodb
                        self.videodb_set.add(link)

                        print('-->ADDED TO VIDEODB ' + link)
                        print('VIDEOS FOUND IN CURRENT SESSION: ' + str(video_count))
                        print('TOTAL NO. OF VIDEOS FOUND: ' + str(len(self.videodb_set)) + '\n')
                        video_count += 1

                elif general.is_webpage_link(link) and (link not in self.queue_set) and (link not in self.crawled_set):
                    self.queue_set.add(link)

                    print('added to queueset ' + link + '\n')
                    print(str(len(self.queue_set)) + ' links in queue \n')

                else:
                    #comes to this clause if not video file nor webpage, so discard
                    continue
        #for loop ends           
            
##MOVE CRAWLED LINK FROM QUEUESET TO CRAWLEDSET
            self.move_from_set_to_set(self.queue_set, self.crawled_set, link_to_crawl)

            #report crawling
            print('added to crawledset ' + link_to_crawl)
            crawled_count += 1
            print('crawled links in current session: '+ str(crawled_count))
            print('total crawled links: ' + str(len(self.crawled_set)) + '\n')

            #crawl speed report
            consumed_time = perf_counter()
            print('CRAWL SPEED: ' + str(crawled_count/consumed_time) + " pages per second\n")
            #video adding speed report
            print(f"{video_count} videos found in current session in {consumed_time} seconds")
            print(f"added {video_count/consumed_time} videos per second ")


#@ WRITING SETS TO THEIR FILES AFTER EVERY 400 DISCOVERY
#  SHOULD BE REMOVED LATER

            #write queue_set
            if len(self.queue_set)%400 == 0:
                general.txtset_to_txtfile(self.queue_set, self.__queue_filename, 'w')

            #write crawled_set
            if len(self.crawled_set)%400 == 0:
                general.txtset_to_txtfile(self.crawled_set, self.__crawled_filename, 'w')

            #write videodb_set to videos.txt
            if video_count != 0:
                if video_count%100 == 0:
                    #overwrite videodb_set to videos.db in write mode
                    general.txtset_to_txtfile(self.videodb_set, self.__videodb_filename, 'w')
                    
                    print('wrote 100 more videos to file')
                               
       
        #while loop ends

                
    def move_from_set_to_set(self, from_set, to_set, element):
        from_set.remove(element)
        to_set.add(element)



spider1 = Spider("http://ftp.timepassbd.live/timepassbd-data/","http://ftp.timepassbd.live/timepassbd-data/", "selenium")
spider1.crawl()

print('\nvideos found: ' + str(len(spider1.videodb_set)) + '\n')
