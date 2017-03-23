from selenium import webdriver


DOMAINPUNCH_URL = 'https://domainpunch.com/tlds/daily.php'

driver = webdriver.Chrome()
driver.get(DOMAINPUNCH_URL)
driver.implicitly_wait(2)

table = driver.find_element_by_id('domtable')
table_items = table.find_elements_by_css_selector('td')

domains = [x.text for x in table_items if '.com' in x.text]
print domains
