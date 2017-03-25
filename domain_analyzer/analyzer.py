import time
import re
import logging
import os
import json

from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException


# Main URL
DOMAINPUNCH_URL = 'https://domainpunch.com/tlds/daily.php'
# Loading time wait
DELAY = 1
# User defined regex list
REGEX_LIST = [re.compile('\d.*')]
# User defined domain whitelist
WHITELIST = ['google.com', '73ct.com', '73db.com']
RESULTS_DIR = 'results'
METAINFO_FILE = os.path.join(RESULTS_DIR, 'metainfo')

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    level=logging.INFO)


class UrlUnreachableException(Exception):
    pass


class DomainAnalyzer(object):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metainfo_retriever = MetainfoRetriever()
        self.main_driver = Chrome()
        self.main_driver.set_page_load_timeout(5)
        self.main_driver.get(DOMAINPUNCH_URL)
        # wait for the page to load
        time.sleep(DELAY)

    def get_domains_to_check(self, domains):
        domains_to_check = []
        for domain in domains:
            if any(regex.match(domain) for regex in REGEX_LIST):
                self.logger.debug("Domain %s matches regex", domain)
                if domain in WHITELIST:
                    self.logger.debug("Domain %s exists in whitelist", domain)
                else:
                    domains_to_check.append(domain)
        return domains_to_check

    def get_domains_from_page(self):
        # locate the table with domain info and extract its items
        table = self.main_driver.find_element_by_id('domtable')
        table_items = table.find_elements_by_css_selector('td')

        # extract domains as a list
        domains = [table_item.text for table_item in table_items if '.com' in table_item.text]
        return domains

    def move_to_next_page(self):
        pages = self.main_driver.find_elements_by_xpath('//*[@id="domtable_paginate"]/span/a')
        for page_element in pages:
            # if button is dimmed out
            if 'ui-state-disabled' in page_element.get_attribute('class'):
                # get next page element and click on it
                next_page_index = pages.index(page_element) + 1
                # On the last page this should give IndexError
                self.logger.info("Moving to page %s", pages[next_page_index].text)
                pages[next_page_index].click()
                break

    def run(self):
        while True:
            self.logger.info("Getting domain list from main page")
            retrieved_domains = self.get_domains_from_page()
            self.logger.info("Getting domains to check")
            to_check = self.get_domains_to_check(retrieved_domains)
            self.logger.info("Domains to check: %s", to_check)
            # Metainfo retrieved here
            for domain in to_check:
                try:
                    self.metainfo_retriever.retrieve_info(domain)
                except UrlUnreachableException:
                    self.logger.warning("Domain %s unreachable, cannot get metainfo", domain)
            self.logger.info("Moving on to the next page")
            try:
                self.move_to_next_page()
            except IndexError:
                self.logger.info("No more pages to crawl")
                break
            time.sleep(DELAY)


class MetainfoRetriever(object):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.chrome_driver = Chrome()
        # enable android browser emulator
        mobile_emulation = {"deviceName": "Google Nexus 5"}
        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        self.android_driver = Chrome(chrome_options=chrome_options)

    def retrieve_info(self, domain):
        url = ''.join(['http://', domain])
        self.get_screenshot(url, domain)
        metainfo = self.get_metainfo(url)
        with open(METAINFO_FILE, 'a') as metainfo_file:
            metainfo_file.write(''.join([json.dumps(metainfo), '\n']))

    def get_screenshot(self, url, domain):
        for driver in [self.chrome_driver, self.android_driver]:
            try:
                driver.get(url)
                time.sleep(DELAY)
                suffix = '_chrome' if driver == self.chrome_driver else '_android'
                driver.save_screenshot(os.path.join(RESULTS_DIR, ''.join([domain, suffix])))
            except TimeoutException:
                self.logger.info('Timeout reached for url %s', url)
                raise UrlUnreachableException

    def get_metainfo(self, url):
        metainfo = {'title': self.chrome_driver.title}
        for meta in ['description', 'keywords']:
            try:
                metainfo[meta] = self.chrome_driver.\
                    find_element_by_xpath("//meta[@name='{0}']".format(meta)).get_attribute('content')
            except NoSuchElementException:
                self.logger.info('Element %s not found for url %s', meta, url)
        return metainfo


def main():
    if not os.path.exists(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)
    domain_analyzer = DomainAnalyzer()
    domain_analyzer.run()


if __name__ == '__main__':
    main()
