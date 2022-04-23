import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from simhash import Simhash


crawled_links = set()
query = set()
bad_links = set()
content = []

simhash_set = set()


def tokenize(text):
    tokens = []
    lines = text.split('\n')
    for line in lines:
        for word in re.split(r'\W+', line):
            if word.isalnum() and word.isascii() and word != '':
                tokens.append(word.lower())
    return tokens


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return links

def extract_next_links(url, resp):
    if resp.status != 200 or url in crawled_links:
        bad_links.add(url)
        return list()
    
    if (resp.raw_response == None):     
        bad_links.add(url)
        return list()
    
    urls = set()

    soup = BeautifulSoup(resp.raw_response.content, 'lxml')

    if(soup.body != None):
        if(len(soup.get_text()) < 300 ): #filters out websites with low amount of text 
            bad_links.add(url)
    else:
        bad_links.add(url)

    #hash the current url's text -> commenting out to test calander trap
  #  url_hash = Simhash(soup.getText())
    #store the hash 
    
   # if( len(content) == 0): #add website to first position if there's no other website
   #     content[0] = url_hash
   # elif (len(content) == 1): #if there's already a website in "previous website", add it to the second position
   #     content[1] = url_hash
   # elif (len(content) == 2): #if there's two websites stored alr, move the second website to the "previous website" slot & put the current website in the "current websote" slot
   #     content[0] = content[1]
    #    content[1] = url_hash

    
    
    # duplicates function are below
    


    # /ref/
    # https://github.com/1e0ng/simhash
    # https://leons.im/posts/a-python-implementation-of-simhash-algorithm/
    # https://github.com/memosstilvi/simhash/blob/master/simhash.py
    # https://support.archive-it.org/hc/en-us/articles/208332963-Modify-crawl-scope-with-a-Regular-Expression



    print("Main URL:", url)
    
    if resp.raw_response.content != None:  # need testing
        for link in soup.find_all('a'):
            child = link.get('href')
            # might need change relative --> absolute url
            
            child = urldefrag(child)[0]

            # if dup shove it in bad_links            
            # hashValue = Simhash()               
            # if not is_Exact_Duplicate(hashValue):
            #     # check for near duplicate
            #     if is_Near_Duplicate(hashValue):
            #         return list()

            # --
                

            if child != None and is_valid(child) and child not in crawled_links and child not in bad_links:
                print("\tFound URL:", child)                            
                urls.add(child)
                crawled_links.add(child)

    print()

    return list(urls)



def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # *.ics.uci.edu/*
    # *.cs.uci.edu/*
    # *.informatics.uci.edu/*
    # *.stat.uci.edu/*
    # today.uci.edu/department/information_computer_sciences/*

    try:

        parsed = urlparse(url)
        if parsed is None or parsed.hostname is None:
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if parsed.hostname not in set(["ics.uci.edu", "cs.uci.edu", 
        "informatics.uci.edu", "stat.uci.edu", "today.uci.edu"]):

            domain = '.'.join(parsed.hostname.split('.')[1:])
            if domain not in set(["ics.uci.edu", "cs.uci.edu", 
            "informatics.uci.edu", "stat.uci.edu", "today.uci.edu"]):
                return False
        
        if parsed.hostname == 'today.uci.edu' and parsed.path != '/department/information_computer_sciences':
            return False

        #blocking URls with repeating directories & calanders
        if re.match("^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$",parsed.path.lower()) or re.match("^.*calendar.*$",parsed.path.lower()):
            return False

    
        

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        # print ("TypeError for ", parsed)
        # raise
        pass


# check duplications

def is_Exact_Duplicate(hashVal):
    if hashVal in simhash_set:
        return True

    simhash_set.add(hashVal)            


    return False


# ahh but then. we need to pass the set as well
# ohhhh. we can keep the set over there. 

# def is_Near_Duplicate(hashVal):
    
