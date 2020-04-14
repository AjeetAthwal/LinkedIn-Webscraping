import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from selenium import webdriver
import time
from pathlib import Path
import csv

userpass_loc = (Path(__file__).parent / "../../Password/LinkedIn.csv").resolve()

with open(userpass_loc) as file:
    userpass = csv.reader(file)
    for row in userpass:
        user = row[0]
        pw = row[1]

driver = webdriver.Chrome()

driver.get("https://www.linkedin.com/login?trk=homepage-basic_conversion-modal-signin")
time.sleep(5)
username = driver.find_element_by_name('session_key')
username.send_keys(user)
password = driver.find_element_by_name('session_password')
password.send_keys(pw)
submit_btn = driver.find_element_by_class_name("btn__primary--large")
submit_btn.click()

csv_to_import = 'info.csv'
df = pd.read_csv(csv_to_import)

def get_url_response(df,name,prev_employer):


    name_splt = name.split(' ')
    prev_employer_splt = prev_employer.split(' ')

    search_items = []
    search_items.extend(name_splt)
    search_items.extend(prev_employer_splt)

    counter = 0
    for item in search_items:
        if counter == 0:
            search_items_str = item
        else:
            search_items_str += '%20' + item
        counter += 1

    url = 'https://www.linkedin.com/search/results/all/?keywords='+search_items_str+'=GLOBAL_SEARCH_HEADER'

    driver.get(url)
    time.sleep(5)
    response = driver.page_source

    return BeautifulSoup(response,'html.parser')


for name,prev_employer in zip(df['Name'],df['Previous Employer']):
    soup = get_url_response(df,name,prev_employer)
    soup_search_results = soup.find_all(class_='search-results__total')
    num_results = soup_search_results[0].contents[0].strip().strip(' ').split(' ')[1]

    soup_job_title = soup.find_all(class_='subline-level-1')
    job_results = soup_job_title[0].contents[0].strip().strip(' ').split(' at ')
    job_title = job_results[0]
    company = job_results[1]

driver.close()