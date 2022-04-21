import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup, Comment

crawled_links = set()
query = set()
bad_links = set()



def scraper(url, resp):
    links = extract_next_links(url, resp)
    for link in links:
        if is_valid(link):
            print(link)

    return [urldefrag(link)[0] for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    #transform relative url to absolute url 
    # -- using urljoin

    
    if resp.status != 200 and url in crawled_links:
        bad_links.add(url)
        return list()
    
    if (resp.raw_response == None):
        bad_links.add(url)
        return list()
    
    urls = set()

    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    for tag in soup(content = lambda content: isinstance(content, Comment)):
        tag.extract()
    
    for elem in soup.findAll(['script', 'style']):
        elem.extract()
    
    text = soup.get_text()
    text = re.sub('\s+', ' ', text)

    # tokenize it

    for link in soup.find_all('a'):
        child = link.get('href')
        if is_valid(child) and child not in crawled_links:
            if '#' in child:
                child = child.split('#')[0]
            urls.add(child)
            crawled_links.add(child)
    
    return list(urls)

    
    '''
    links = []

    #url = requests.get(absoluteurl)
    
    if(resp.status == 200): #if the URL has permission to be able to be scraped & has no other problems 
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser' )
    
        for link in soup.find_all('a'):
            #if(link != None):
            
            # if(resp.raw_response.content != None): #if there is content, might need to go in another place
            
            # still not crawling
            link = link.get('href')
            #if (link != '#'):
            newUrl = urljoin(url, link)
            crawled_links.add(newUrl)
            #print(url)
            # if url =='#':
            #     print('123')
            if newUrl not in crawled_links:
                links.append(url)
    
    return links
    '''


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
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # Added code
        if parsed.hostname not in set(["ics.uci.edu", "cs.uci.edu", 
        "informatics.uci.edu", "stat.uci.edu", "today.uci.edu"]):

            domain = '.'.join(parsed.hostname.split('.')[1:])
            if domain not in set(["ics.uci.edu", "cs.uci.edu", 
            "informatics.uci.edu", "stat.uci.edu", "today.uci.edu"]):
                return False
        
        if parsed.hostname == 'today.uci.edu' and parsed.path != '/department/information_computer_sciences':
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
