# Written by: Katerina Bosko
# scraping data from
# "America's Best Large Employers 2021, Forbes",
# https://www.forbes.com/best-large-employers/


from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import requests
from bs4 import BeautifulSoup

# PLEASE DON'T RUN THIS PART
# 1. to run Selenium, you need Chrome and chromedriver installed on your computer
# 2. It takes ~5 hours to get full data and if interrupted earlier, it might corrupt
# the 'companies_final.json' file 
"""
def main():
    # Part 1 - scrapes javascript-generated content (data table and links) using Selenium
    driver = webdriver.Chrome()
    driver.get('https://www.forbes.com/best-large-employers/#77f4ac3ffb3e')
    select = Select(driver.find_element_by_xpath('//*[@id="fbs-table-dropdown"]'))
    select.select_by_visible_text('All')

    companies_json = []
    table = driver.find_element_by_xpath('//*[@id="row-3"]/div/ul/li/div/div/table')
    rows = table.find_elements_by_tag_name('tr')
    for row in rows:
        cols = row.find_elements_by_tag_name('td')
        if not cols: #skip empty cols at the beginning
            continue
        companies_json.append({"rank": cols[0].text, "name": cols[1].text, "industry": cols[2].text, "employees": cols[3].text, "year_founded": cols[4].text})


    urls = []
    for i in range(1, 501):
        for elem in driver.find_elements_by_xpath(f'//*[@id="row-3"]/div/ul/li/div/div/table/tbody/tr[{i}]/td[2]/a'):
            urls.append(elem.get_attribute("href"))


    urls_clean = [url.replace("?list=best-employers/", "") for url in urls]
    for i, url in enumerate(urls_clean):
        companies_json[i]['url'] = url

    # Part 2 - scrapes headquarters and description of each company by going into each url
    for i, company in enumerate(companies_json):
        page = requests.get(company['url'])
        soup = BeautifulSoup(page.content, "lxml")
        try:
            hq_elem = soup.find(text="Headquarters").findNext('span').contents[0]
            print(company['name'])
            companies_json[i]['headquarters'] = hq_elem
        except:
            print("skipped - ", company['name'])
            companies_json[i]['headquarters'] = "-1"
        try:
            desc_elem = soup.find('div', class_="profile-text").findNext('span')
            companies_json[i]['desc'] = desc_elem.text
        except:
            companies_json[i]['desc'] = "-1"
        time.sleep(30)


    with open('companies_final.json', 'w') as f:
        json.dump(companies_json, f, indent=3)


if __name__ == "__main__":
    main()
"""