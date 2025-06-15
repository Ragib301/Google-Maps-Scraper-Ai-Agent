from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import streamlit as st
from time import sleep
import subprocess
import json


def scroll_window(driver, query, num_results):
    divSideBar = driver.find_element(
        By.CSS_SELECTOR, f"div[aria-label='Results for {query}']")
    for i in range(num_results // 3):
        divSideBar.send_keys(Keys.END)
        sleep(2)


def scrape_google_maps(query, location, num_results):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    st.write('Starting Name & URL Scrapping...')
    search_query = f"{query} in {location}"
    search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
    driver.get(search_url)
    sleep(5)

    scroll_window(driver, search_query, num_results)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listings = soup.find_all('div', class_='Nv2PK THOPZb CpccDe')

    local_info = []
    for listing in listings:
        a_tag = listing.find('a', class_='hfpxzc')
        name = a_tag.get('aria-label', '').strip()
        url = a_tag.get('href', '').strip()

        info_dict = {
            'name': name,
            'url': url,
        }
        local_info.append(info_dict)
    st.write('Starting Business Info Scrapping...')
    return scrape_business_details(driver, local_info)


def scrape_business_details(driver, local_info):
    progress_bar = st.progress(0, text="Scraping in Progress...")
    business_info = []
    for info_dict in local_info:
        name = info_dict['name']
        map_url = info_dict['url']

        driver.get(map_url)
        sleep(5)

        address, website = '', ''
        email_data = {'emails': []}
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        business_div = soup.find_all(
            'div', class_='Io6YTe fontBodyMedium kR99db fdkmkc')
        website_div = soup.find('a', class_='lcr4fd S9kvJb', href=True)
        address_div = soup.find('button', class_='CsEnBe')

        if business_div and website_div and address_div:
            website = website_div['href']
            address = address_div['aria-label'].strip('Address: ')
            rating = soup.find(
                'div', class_='fontDisplayLarge').get_text(strip=True)

        if website:
            ''' Just change the location and put the path where 
            you saved the Email Scraper's spiders folder '''
            email_scraper_path = r"D:\AI Automation\email_scraper\email_scraper\spiders"
            command = f"cd {email_scraper_path} && python email_scraper.py {website}"
            result = subprocess.run(command, shell=True,
                                    capture_output=True, text=True)
            if result.returncode == 0:
                #print('Output:', result.stdout)
                f = open(r'D:\AI Automation\email_scraper\email_scraper\spiders\emails.json')
                email_data = json.load(f)
            print(email_data)

        business_info_dict = {
            'name': name,
            'website': website,
            'addreess': address,
            'rating': rating,
            'emails': email_data['emails']
        }
        business_info.append(business_info_dict)
        sleep(5)
        progress_bar.progress((len(business_info)/len(local_info)),
                              text="Scraping in Progress...")

    progress_bar.empty()
    driver.close()
    return business_info


if __name__ == "__main__":
    print(scrape_google_maps("Coffee Shops", "London, UK", 15))
