import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from general import is_video, get_response, get_header
from requests.exceptions import ConnectionError


class Spider:
    def __init__(self, start_page_url):
        self.start_page_url = start_page_url
        self.domain_name = self.get_domain_name(self.start_page_url)
        self.make_sets()
        print('spider created\n')

    def get_domain_name(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme + '://' + parsed_url. dir2

    def make_sets(self):
        self.queue_set = set()
        self.crawled_set = set()
        self.couldnt_crawl_set = set()
        self.videodb_set = set()

        self.queue_set.add(self.start_page_url)



    def crawl(self):
#while loop starts
        while True:

            ##GET LINK_TO_CRAWL FROM QUEUESET
            if len(self.queue_set) > 0:
                for i in self.queue_set:
                    link_to_crawl = i
                    break
            else:
                #if len(queue_set) is 0 then crawling is finished
                print('finished crawling the domain ' + self.domain_name + '\n')
                break                

            print('Now Crawling: ' + link_to_crawl + '\n')


            ##DOWNLOAD THE PAGEHTML

            #CHECK BEFORE DOWNLOADING
            #if content type is not html then go to next cycle, remove the link from queue
            #check whether the server responds
            #if the server respond check whether the response is 200
            header = get_header(link_to_crawl)

            if header == 0:      #return value equals 0 means error
                #couldn't connect to server or page not available
                self.move_from_set_to_set(self.queue_set, self.couldnt_crawl_set, link_to_crawl)
                print("couldn't crawl: " + str(len(self.couldnt_crawl_set)) + 'links\n')
                continue

            else:
                #server connects for link_to_crawl and server responds with content
                fullctype = header.get('content-type')

                #if contenttype is a nonetype object, remove it from queue, go to next cycle
                if (fullctype == None):      
                    self.queue_set.remove(link_to_crawl)
                    continue
                else:
                    #content type is not nonetype and can be parsed
                    ctype = fullctype.split(';')[0]

                    #if content type is not text/html, remove link_to_crawl from queue, go to next cycle 
                    if ctype != 'text/html':    
                        self.queue_set.remove(link_to_crawl)
                        continue



            #DOWNLOAD TEXT/HTML CONTENT
            r = get_response(link_to_crawl)

            if r == 0:
                self.move_from_set_to_set(self.queue_set, self.couldnt_crawl_set, link_to_crawl)
                print("couldn't crawl: " + str(len(self.couldnt_crawl_set)) + 'links\n')
                continue
            else:
                pagehtml = r.text


            ##PARSE PAGEHTML TO FIND ALL A TAG'S HREF
            soup = BeautifulSoup(pagehtml, features="lxml")
            anchor_list = soup.select('a')
#for loop starts
            for anchor in anchor_list:

                link = anchor.get('href')

                #if link is of nonetype discard it, go to next loop
                if link == None:
                    continue

                ##add the link to the desired set or discard it
                
                #if link is not of the same domain discard the link
                #but if link is a video then even if different domain keep it
                is_link_video = is_video(link)

                link_ dir2 = urlparse(link). dir2
                if not((link_ dir2 == urlparse(self.domain_name). dir2) or link_ dir2 == '') and not is_link_video:
                    continue

                #convert link to absolute url
                link = urljoin(self.domain_name, link)
                
                #add url to queueset or videodbset 
                if is_link_video:
                    self.videodb_set.add(link)
                    print('-->ADDED TO VIDEODB ' + link)
                    print('NO. OF VIDEOS FOUND: ' + str(len(self.videodb_set)) + '\n')
                else: 
                    if (link not in self.queue_set) and (link not in self.crawled_set):
                        self.queue_set.add(link)

                        print('added to queueset ' + link + '\n')
                        print(str(len(self.queue_set)) + ' links in queue \n')
#for loop ends           
            

            #MOVE CRAWLED LINK FROM QUEUESET TO CRAWLEDSET
            self.move_from_set_to_set(self.queue_set, self.crawled_set, link_to_crawl)

            print('added to crawledset ' + link_to_crawl)
            print('total crawled links: '+ str(len(self.crawled_set)) + '\n')
       
#while loop ends

                
    def move_from_set_to_set(self, from_set, to_set, element):
        from_set.remove(element)
        to_set.add(element)


spider1 = Spider("http://103.102.253.250/Data/")
spider1.crawl()

print('\nvideos found: ' + str(len(spider1.videodb_set)) + '\n')
for i in spider1.videodb_set:
    print(i)