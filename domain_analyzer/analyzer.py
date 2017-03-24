from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import time
import re

# Main URL
DOMAINPUNCH_URL = 'https://domainpunch.com/tlds/daily.php'
# Loading time wait
DELAY = 1
# User defined regex list
REGEX_LIST = [re.compile('\d.*')]
# User defined domain whitelist
WHITELIST = ['google.com', '73ct.com', '73db.com']


driver = Chrome()
driver.set_page_load_timeout(5)
driver.get(DOMAINPUNCH_URL)
time.sleep(DELAY)


def get_metainfo(url):
    try:
        driver.get(url)
    except TimeoutException:
        print 'Timeout reached for url', url
    # TODO: screenshot here?
    metainfo = {'title': driver.title}
    for meta in ['description', 'keywords']:
        try:
            metainfo[meta] = driver.find_element_by_xpath("//meta[@name='{0}']".format(meta)).get_attribute('content')
        except NoSuchElementException:
            print 'Element', meta, 'not found for url', url
            continue
    return metainfo


def get_domains_to_check(domains):
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


def get_domains_from_page():
    # locate the table with domain info and extract its items
    table = driver.find_element_by_id('domtable')
    table_items = table.find_elements_by_css_selector('td')

    # extract domains as a list
    domains = [table_item.text for table_item in table_items if '.com' in table_item.text]
    print domains
    return domains


def move_to_next_page():
    pages = driver.find_elements_by_xpath('//*[@id="domtable_paginate"]/span/a')
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


while True:
    print "Get domain list from main page"
    retrieved_domains = get_domains_from_page()
    print "Get domains to check"
    to_check = get_domains_to_check(retrieved_domains)
    print "To check:", to_check
    # ...Metainfo retrieved here...
    print "Moving to next page"
    move_to_next_page()
    time.sleep(DELAY)

