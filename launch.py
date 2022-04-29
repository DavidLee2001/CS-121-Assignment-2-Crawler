from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler


# Report
import scraper


def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)

    
    # Report - 1
    print(f'\n\n\nNumber of unique pages found: {len(scraper.crawled_links)}\n\n')

    # Report - 2
    print(f'Longest page: {scraper.longestPage}\nWord count: {scraper.longestPageWordCount}\n')
    for key, value in scraper.longest.items():
        print(f'{key}: {value}\n')
    print('\n')
    
    # Report - 3
    print('50 most common words')
    counter = 0
    for word, count in sorted(scraper.allWords.items(), key=lambda item: -item[1]):
        if counter >= 50:
            break
        counter += 1
        print(f'{word} - {count}')
    print('\n\n')

    # Report - 4
    print(f"A total number of subdomains in the 'ics.uci.edu domain': {len(scraper.subdomains)}")
    for domain, urls in sorted(scraper.subdomains.items(), key=lambda item: item[0]):
        print(f'\t{domain}, {len(urls)}')



    with open('report.txt', 'w') as file:
        # Report - 1
        file.write(f'Number of unique pages found: {len(scraper.crawled_links)}\n\n')
    
        # Report - 2
        file.write(f'Longest page: {scraper.longestPage}\nWord count: {scraper.longestPageWordCount}\n')
        for key, value in scraper.longest.items():
            file.write(f'{key}: {value}\n')
        file.write('\n')
    
        # Report - 3
        file.write('50 most common words\n')
        counter = 0
        for word, count in sorted(scraper.allWords.items(), key=lambda item: -item[1]):
            if counter >= 50:
                break
            counter += 1
            file.write(f'\t{word} - {count}\n')
        file.write('\n')
    
        # Report - 4
        file.write(f"A total number of subdomains in the 'ics.uci.edu domain': {len(scraper.subdomains)}\n")
        for domain, urls in sorted(scraper.subdomains.items(), key=lambda item: item[0]):
            file.write(f'\t{domain}, {(urls)}\n')
