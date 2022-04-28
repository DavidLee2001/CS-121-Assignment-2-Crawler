import re
from urllib.parse import urlparse, urldefrag, urljoin
from bs4 import BeautifulSoup
from simhash import Simhash


near_dup_threshold = 10
crawled_links = set()
bad_links = set()
simhash_set = set()
# (id, simhash)
data = dict()


# Report - 2
longestPage = ''
longestPageWordCount = 0

# Report - 3
allWords = dict()
stopWords = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"}

# Report - 4
subdomains = dict()



def tokenize(text):
    tokens = []
    lines = text.split('\n')
    for line in lines:
        for word in re.split(r'\W+', line):
            if word.isalnum() and word.isascii() and word != '':
                tokens.append(word.lower())
    return tokens


# https://leons.im/posts/a-python-implementation-of-simhash-algorithm/
def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]


def scraper(url, resp):
    return extract_next_links(url, resp)


def extract_next_links(url, resp):
    if resp.status != 200 or resp.raw_response == None:  # url with status != 200 or no response is excluded
        bad_links.add(url)
        return list()       # return with an empty list() to not crawl this url
    
    if url in crawled_links:    # url is already crawled
        return list()



    soup = BeautifulSoup(resp.raw_response.content, 'lxml') 
    


    simhashObject = Simhash(get_features(soup.get_text()))            # for checking duplicated content
    
    if is_exact_dup(simhashObject):
        return list()
    
    if is_near_dup(simhashObject):
        # bad_links.add(url) # might make checking for bad links easier
        return list()

    # A unique link (content is not duplicated) --> add to simhash_set()
    simhash_set.add(simhashObject.value)
    data[str(simhashObject.value)] = simhashObject

    if(soup.body != None):
        if (len(soup.get_text()) < 300): # filters out websites with low amount of text 
            bad_links.add(url)
            # No scraping low content website
            return list()
    else:
        bad_links.add(url)
        return list()
    


    words = tokenize(soup.get_text())

    # Report - 2
    global longestPage, longestPageWordCount
    if len(words) > longestPageWordCount:
        longestPage = url
        longestPageWordCount = len(words)
    
    # Report - 3
    global allWords
    for word in words:
        if word not in stopWords:
            if word not in allWords:
                allWords[word] = 0
            allWords[word] = allWords[word] + 1
    


    print("\tMain URL:", url)

    urls = set()    # set of scraped links from this url

    if resp.raw_response.content != None:
        # num_links = 0
        for link in soup.find_all('a'):
            link = link.get('href')
            newLink = urljoin(url, link)        # Transform relative to absolute url
            newLink = urldefrag(newLink)[0]     # Defragment 

            # checking if the scraped link is valid, in crawled links/bad links
            if newLink != None and is_valid(newLink) and newLink not in crawled_links and newLink not in bad_links:                      
                urls.add(newLink)
                crawled_links.add(newLink)
            else:
                bad_links.add(newLink)
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

        # if subdomains not belong to these domains. The url is not valid
        if parsed.hostname == 'today.uci.edu':
            if re.match('/department\/information_computer_sciences(\/.*)?', parsed.path) == None:
                return False
        elif re.match('.*\.ics\.uci\.edu',  parsed.hostname) == None \
            and re.match('.*\.cs\.uci\.edu',  parsed.hostname) == None \
            and re.match('.*\.informatics\.uci\.edu',  parsed.hostname) == None \
            and re.match('.*\.stat\.uci\.edu',  parsed.hostname) == None:
            return False

        # Report - 4
        if re.match('.*\.ics\.uci\.edu', parsed.hostname):
            if parsed.hostname not in subdomains:
                subdomains[parsed.hostname] = 0
            subdomains[parsed.hostname] = subdomains[parsed.hostname] + 1


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
        pass


# check duplications
def is_exact_dup(simhashObject):
    return simhashObject.value in simhash_set


def is_near_dup(simhashObject):
    # Distance
    for value in data.values():
        if value.distance(simhashObject) < near_dup_threshold:
            return True
    return False


# /ref/
# https://github.com/1e0ng/simhash
# https://leons.im/posts/a-python-implementation-of-simhash-algorithm/
# https://github.com/memosstilvi/simhash/blob/master/simhash.py
# https://support.archive-it.org/hc/en-us/articles/208332963-Modify-crawl-scope-with-a-Regular-Expression
