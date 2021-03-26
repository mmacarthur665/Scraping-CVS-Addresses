"""
Program Name: Scraping CVS Locations
Author: Michael Macartur
Date: 3/24/2021

Purpose: To scrape all CVS location addresses and flag all Health Hubs, Minute Clinics, etc.
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import lxml
import re
import pandas as pd
import os
import time


chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--remote-debugging-port=9222")
# Pandas preferences
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)
pd.set_option('display.width', 200)

# STEP 1 - Create State URLs

base = 'https://www.cvs.com/store-locator/cvs-pharmacy-locations/'

states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
          'District-of-Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
          'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
          'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New-Hampshire', 'New-Jersey', 'New-Mexico',
          'New-York', 'North-Carolina', 'North-Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto-Rico',
          'Rhode-Island', 'South-Carolina', 'South-Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
          'Washington', 'West-Virginia', 'Wisconsin', 'Wyoming']

# Use CreateStateList function to create the list of state urls that we'll grab the city links from

def CreateStateList(base, states):
    """
    :param base: base url
    :param state: state of USA that needs to be appended
    :return: list of urls
    """

    url_list_state = []

    for s in states:
        # creates list of state urls by appending state name to end of stock url
        url = base+s
        url_list_state.append(url)

    return url_list_state

url_list_state = CreateStateList(base=base, states=states) # for main later on

# STEP 2 - Get City level links ---------------------------------------------------------------------------------------
url_list_cities = []
tot_state = len(url_list_state)
loop_count = 0
for s in url_list_state:
    url = s
    driver = webdriver.Chrome(r'C:\Users\3183328\OneDrive - Fresenius Medical Care\Desktop\Python Script Stuff\chromedriver.exe', options=chrome_options)
    driver.get(s)
    links = driver.find_elements_by_xpath("//a[@href]")


    city_links_step1 = []

    for l in links:
        href = l.get_attribute("href")
        city_links_step1.append(href)

    driver.close()

    city_links_step2 = [k for k in city_links_step1 if ';jsessionid=' in k]

    city_links_step3 = [k for k in city_links_step2 if '/store-locator/cvs-pharmacy-locations/' in k]

    city_links_step4 = []
    for link in city_links_step3:
        link_clean1 = str(link).split(';jsessionid=')
        city_links_step4.append(link_clean1[0])

    url_list_cities.append(city_links_step4)
    loop_count += 1
    print('Finished Loop '+str(loop_count)+' of '+str(tot_state))
#
#
# # STEP 3 - CHECK CITY LIST FOR ACCURACY --------------------------------------------------------------------------------
# converts nested lists into single list
flat_city_list = []
for i in url_list_cities:
    flat_city_list.extend(i)

# puts list in dataframe for QCing
df = pd.DataFrame(flat_city_list)
df.to_csv('FLAT_CITY_LIST_FORCHECK.csv')

# STEP 4 - CREATE LIST OF FACILITY URLS --------------------------------------------------------------------------------
pharm_url_dump = []
tot_city = len(flat_city_list)
loop_count = 0

for c in flat_city_list:

    url = c
    driver = webdriver.Chrome(r'C:\Users\3183328\OneDrive - Fresenius Medical Care\Desktop\Python Script Stuff\chromedriver.exe', options=chrome_options)
    driver.get(c)
    links = driver.find_elements_by_xpath("//a[@href]")

    pharm_url_list_step1 = []

    for l in links:
        href = l.get_attribute("href")
        pharm_url_list_step1.append(href)

    driver.close()

    pharm_url_list_step2 = [k for k in pharm_url_list_step1 if '/cvs-pharmacy-address/' in k] # filters to list items containing '/cvs-pharmacy-address/'

    pharm_url_list_step3 = set(pharm_url_list_step2) # removes duplicates from list

    pharm_url_list_step4 = [] # creates list of urls without jsessionid
    for link in pharm_url_list_step3:
        link_clean1 = str(link).split(';jsessionid=')
        pharm_url_list_step4.append(link_clean1[0])

    pharm_url_dump.append(pharm_url_list_step4)
    loop_count +=1
    print('Completed Loop '+str(loop_count)+' of '+str(tot_city))


flat_pharm_list = []
for i in pharm_url_dump:
    flat_pharm_list.extend(i)

df = pd.DataFrame(flat_pharm_list)
df.to_csv('FLAT_PHARM_LIST_FORCHECK.csv')

# STEP 5 - SCRAPE DATA  ------------------------------------------------------------------------------------------------
