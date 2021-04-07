"""
Program Name: Scraping CVS Locations
Author: Michael Macarthur
Date: 4/7/2021

Purpose: To scrape all CVS location addresses.
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import lxml.html
import re
import pandas as pd
import os
import time
import requests


chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--enable-automation")
#chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-browser-side-navigation")

#chrome_options.add_argument("--remote-debugging-port=9222")
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

print(url_list_state)

# STEP 2 - Get City level links --------------------------------------------------------------------------------------
url_list_cities = [] # sets up list for writing city urls to
tot_state = len(url_list_state) # count of states for loop counter
loop_count = 0 # init the loop count
for s in url_list_state:
# we create a new session of chome driver every loop to prevent the driver getting stale

    driver = webdriver.Chrome(r'INSERT PATH TO CHROMEDRIVER, options=chrome_options)
    driver.get(s)
    links = driver.find_elements_by_xpath("//a[@href]") # finds all href links. we will harvest these for later link creation

    city_links_step1 = [] #create step 1 lst

    for l in links:
        #loops through step1 list grabbing all href links and storing in step1 list
        href = l.get_attribute("href")
        city_links_step1.append(href)

    driver.close() # closes chromedriver

    city_links_step2 = [k for k in city_links_step1 if ';jsessionid=' in k]
# list comprehension filter to all strings containing a jsessionid. Do this because all city links have session ids

    city_links_step3 = [k for k in city_links_step2 if '/store-locator/cvs-pharmacy-locations/' in k]
# filters previous list to only ones with store-locator/cvs-pharmacy-locations/ in it

    city_links_step4 = []
    for link in city_links_step3:
        # removes unnecessary text from urls
        link_clean1 = str(link).split(';jsessionid=')
        city_links_step4.append(link_clean1[0])

    url_list_cities.append(city_links_step4) # appends cleaned links to larger list
    loop_count += 1 # increments counter
    print('Finished Loop '+str(loop_count)+' of '+str(tot_state)) # updates status


#STEP 3 - CHECK CITY LIST FOR ACCURACY --------------------------------------------------------------------------------
flat_city_list = []
for i in url_list_cities:
    # converts nested lists into single list
    flat_city_list.extend(i)

# puts list in dataframe for QCing
#df = pd.DataFrame(flat_city_list)
#df.to_csv('FLAT_CITY_LIST_FORCHECK.csv')

#STEP 4 - CREATE LIST OF FACILITY URLS ---------------------------------------------------------------------------------
pharm_url_dump = []
tot_city = len(flat_city_list)
loop_count=0
for l in flat_city_list:
    # loops through all city links and pulls out the pharmacy links for further scraping
    response = requests.get(l)
    time.sleep(2)
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.find_all('a', href=re.compile('/cvs-pharmacy-address/'))

    step1_list = []
    for l in links:
        step1 = str(l).split(';jessionid=')
        step1_list.append(step1)

    step2_list = []
    for l in step1_list:
        link_clean1 = str(l).split(';jsessionid=')
        step2_list.append(link_clean1[0])

    step3_list = []
    for l in step2_list:
        link_clean2 = str(l).split('href="')
        step3_list.append(link_clean2[1])

    base2 = 'cvs.com'
    step4_list = []
    for l in step3_list:
        fin_link = base2+l
        step4_list.append(fin_link)

    step4_list = set(step4_list)
    pharm_url_dump.append(step4_list)
    loop_count+=1
    response.close()
    print('Completed Loop '+str(loop_count)+' of '+str(tot_city))

flat_pharm_list = []
for i in pharm_url_dump:
    flat_pharm_list.extend(i)

# df = pd.DataFrame(flat_pharm_list)
# df.to_csv('FLAT_PHARM_LIST_FORCHECK.csv')

#STEP 5 - SCRAPE DATA  ------------------------------------------------------------------------------------------------

pharm_loc_list = []
url_base = 'http://www.'

flat_pharm_list2 = []
for u in flat_pharm_list:
    item = url_base+u
    flat_pharm_list2.append(item)

for u in flat_pharm_list2:

    response = requests.get(u)
    time.sleep(2)
    soup = BeautifulSoup(response.text, 'lmxl')
    pharm = soup.find('title')
    pharm_loc_list.append(pharm)
    response.close()

df = pd.DataFrame(pharm_loc_list)
df.to_csv('pharmacy_addresses.csv')
