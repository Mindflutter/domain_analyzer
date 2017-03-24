from selenium.webdriver import Chrome, Android
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import time
import re
import logging

# Main URL
DOMAINPUNCH_URL = 'https://domainpunch.com/tlds/daily.php'
# Loading time wait
DELAY = 1
# User defined regex list
REGEX_LIST = [re.compile('\d.*')]
# User defined domain whitelist
WHITELIST = ['google.com', '73ct.com', '73db.com']

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    level=logging.INFO)


class DomainAnalyzer(object):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.main_driver = Chrome()
        self.main_driver.set_page_load_timeout(5)
        self.main_driver.get(DOMAINPUNCH_URL)
        time.sleep(DELAY)

    def get_domains_to_check(self, domains):
        domains_to_check = []
        # TODO: apply filter func?
        for domain in domains:
            if any(regex.match(domain) for regex in REGEX_LIST):
                print 'Domain', domain, 'matches regex'
                if domain in WHITELIST:
                    print 'Domain', domain, 'exists in whitelist'
                else:
                    domains_to_check.append(domain)
        return domains_to_check

    def get_domains_from_page(self):
        # locate the table with domain info and extract its items
        table = self.main_driver.find_element_by_id('domtable')
        table_items = table.find_elements_by_css_selector('td')

        # extract domains as a list
        domains = [table_item.text for table_item in table_items if '.com' in table_item.text]
        print domains
        return domains

    def move_to_next_page(self):
        pages = self.main_driver.find_elements_by_xpath('//*[@id="domtable_paginate"]/span/a')
        for page_element in pages:
            print page_element.text
            # if button is dimmed out
            if 'ui-state-disabled' in page_element.get_attribute('class'):
                # get next page element and click on it
                next_page_index = pages.index(page_element) + 1
                # On the last page this should give IndexError
                print 'Moving to page', pages[next_page_index].text
                pages[next_page_index].click()
                break

    def run(self):
        while True:
            self.logger.info("Getting domain list from main page")
            retrieved_domains = self.get_domains_from_page()
            self.logger.info("Getting domains to check")
            to_check = self.get_domains_to_check(retrieved_domains)
            self.logger.info("Domains to check: %s", to_check)
            # ...Metainfo retrieved here...
            # for domain in to_check:
            #     url = ''.join(['http://', domain])
            #     get_metainfo(url)
            self.logger.info("Moving to next page")
            try:
                self.move_to_next_page()
            except IndexError:
                self.logger.info("No more pages to crawl")
            time.sleep(DELAY)


class MetainfoRetriever(object):
    def __init__(self):
        self.chrome_driver = Chrome()
        self.android_driver = Android()

    def get_metainfo(self, url):
        try:
            driver.get(url)
        except TimeoutException:
            print 'Timeout reached for url', url
            return
        # TODO: screenshot here?
        metainfo = {'title': driver.title}
        for meta in ['description', 'keywords']:
            try:
                metainfo[meta] = driver.find_element_by_xpath("//meta[@name='{0}']".format(meta)).get_attribute('content')
            except NoSuchElementException:
                print 'Element', meta, 'not found for url', url
                continue
        print metainfo
        return metainfo


def main():
    domain_analyzer = DomainAnalyzer()
    domain_analyzer.run()


if __name__ == '__main__':
    main()
