import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from selenium import webdriver
import time
from pathlib import Path
import csv
from os.path import join


# Get my linkedin username and password from different directory (user and pass variables)
userpass_dir = (Path(__file__).parent / "../../Password").resolve()
userpass_file =  'LinkedIn.csv'
userpass_loc = join(userpass_dir,userpass_file)

with open(userpass_loc) as file:
    userpass = csv.reader(file)
    for row in userpass:
        user = row[0]
        pw = row[1]

# Get csv data of names and previous job titles to search on linkedin
csv_to_import_dir = (Path(__file__).parent).resolve()
csv_to_import_file =  'example_info.csv'
csv_to_import = join(csv_to_import_dir,csv_to_import_file)
df = pd.read_csv(csv_to_import)

# function to login to LinkedIn

def login(user,pw, driver):
    driver.get("https://www.linkedin.com/login?trk=homepage-basic_conversion-modal-signin")
    time.sleep(5)
    username = driver.find_element_by_name('session_key')
    username.send_keys(user)
    password = driver.find_element_by_name('session_password')
    password.send_keys(pw)
    submit_btn = driver.find_element_by_class_name("btn__primary--large")
    submit_btn.click()

# function to extract html soup response from search on LinkedIn

def get_url_response(df,name,prev_employer,driver):
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


# function to get data i want (number of search results, job title, company, location)

def get_data(soup):
    soup_search_results = soup.find_all(class_='search-results__total')
    num_results = soup_search_results[0].contents[0].strip().strip(' ').split(' ')[1]

    soup_job_title = soup.find_all(class_='subline-level-1')
    job_results = soup_job_title[0].contents[0].strip().strip(' ').split(' at ')
    job_title = job_results[0]
    company = job_results[1]

    soup_location = soup.find_all(class_='subline-level-2')
    location = soup_location[0].contents[0].strip().strip(' ')
    return [num_results,job_title,company,location]

###########

# Login to LinkedIn
driver = webdriver.Chrome()
login(user,pw,driver)

# go through each csv and get data desired

for name,prev_employer in zip(df['Name'],df['Previous Employer']):
    soup = get_url_response(df,name,prev_employer,driver)
    data = get_data(soup)
    print(data)
# driver.close()