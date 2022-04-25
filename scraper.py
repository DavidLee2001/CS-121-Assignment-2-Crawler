import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from simhash import Simhash,SimhashIndex

near_dup_threshold = 3

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


def scraper(url, resp):
    return extract_next_links(url, resp)

def extract_next_links(url, resp):
    
    if resp.status != 200 or url in crawled_links:
        bad_links.add(url)
        return list()
    
    if (resp.raw_response == None):     
        bad_links.add(url)
        return list()

    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    parsed = urlparse(url)
    
    words = tokenize(soup.get_text())
    hashVal = Simhash(words)
    

    # domain_path = parsed.scheme + '/' + parsed.netloc + '/' + parsed.hostname + parsed.path
    # print(domain_path)

    if is_exact_dup(hashVal):
        # domain + path
        domain_path = parsed.scheme + parsed.hostname + parsed.path
        bad_links.add(domain_path)
        return list()
    
    if is_near_dup(hashVal):
        domain_path = parsed.scheme + parsed.hostname + parsed.path
        bad_links.add(domain_path)
        return list()

    # A unique link --> add to simhash_set()
    simhash_set.add(hashVal.value)
    data[str(hashVal.value)] = hashVal

    if(soup.body != None):
        if (len(soup.get_text()) < 300): #filters out websites with low amount of text 
            print("Low text URL: ", )
            bad_links.add(url)
            # return list()
    else:
        bad_links.add(url)


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

    urls = set()

    if resp.raw_response.content != None:  # need testing
        for link in soup.find_all('a'):
            child = link.get('href')
            
            child = urldefrag(child)[0]


            if child != None and is_valid(child) and child not in crawled_links and child not in bad_links:                            
                urls.add(child)
                crawled_links.add(child)
            else:
                bad_links.add(child)

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
            elif domain == 'ics.uci.edu':
                if domain not in subdomains:
                    subdomains[domain] = set()
                subdomains[domain].add(url)
            
        if parsed.hostname == 'today.uci.edu' and parsed.path != '/department/information_computer_sciences':
            return False

        # if parsed.path in bad_paths:
        #     return False

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
def is_exact_dup(hashVal):
    if hashVal.value in simhash_set:
        return True

    return False


def is_near_dup(hashVal):
    # Need to store data in dict to use simhash index
    index = SimhashIndex([(k, v) for k, v in data.items()])
    # near_dup_threshold returns a list of keys in data that are near duplicates
    dups = index.get_near_dups(hashVal)
    if(len(dups) > near_dup_threshold):
        return True




# /ref/
# https://github.com/1e0ng/simhash
# https://leons.im/posts/a-python-implementation-of-simhash-algorithm/
# https://github.com/memosstilvi/simhash/blob/master/simhash.py
# https://support.archive-it.org/hc/en-us/articles/208332963-Modify-crawl-scope-with-a-Regular-Expression
