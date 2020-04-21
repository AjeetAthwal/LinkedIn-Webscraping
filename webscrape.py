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
userpass_dir = (Path(__file__).parent / "../../Data/LinkedIn").resolve()
userpass_file =  'userpass.csv'
userpass_loc = join(userpass_dir,userpass_file)

with open(userpass_loc) as file:
    userpass = csv.reader(file)
    for row in userpass:
        user = row[0]
        pw = row[1]

# Get csv data of names and previous job titles to search on linkedin
csv_to_import_dir = userpass_dir
csv_to_import_file =  'info.csv'
csv_to_import = join(csv_to_import_dir,csv_to_import_file)
df = pd.read_csv(csv_to_import)
df = df.fillna('')

# function to login to LinkedIn

def login(user,pw, driver):
    driver.get("https://www.linkedin.com/login?trk=homepage-basic_conversion-modal-signin")
    username = driver.find_element_by_name('session_key')
    username.send_keys(user)
    password = driver.find_element_by_name('session_password')
    password.send_keys(pw)
    submit_btn = driver.find_element_by_class_name("btn__primary--large")
    submit_btn.click()
    time.sleep(5)

# function to extract html soup response from search on LinkedIn

def get_url_response(df,fname,lname,prev_employer,driver,num_words_to_remove = 0):
    if fname != '':
        fname_splt = fname.split(' ')
    else:
        fname_splt = []
    if lname != '':
        lname_splt = lname.split(' ')
    else:
        lname_splt = []
    if prev_employer != '':
        prev_employer_splt = prev_employer.split(' ')
    else:
        prev_employer_splt = []

    search_items = []
    search_items.extend(fname_splt)
    search_items.extend(lname_splt)
    search_items.extend(prev_employer_splt)
    if num_words_to_remove>0:
        search_items = search_items[:-num_words_to_remove]

    counter = 0
    for item in search_items:
        if counter == 0:
            search_items_str = item
        else:
            search_items_str += '%20' + item
        counter += 1

    url = 'https://www.linkedin.com/search/results/all/?keywords='+search_items_str+'=GLOBAL_SEARCH_HEADER'
    driver.get(url)
    response = driver.page_source

    return BeautifulSoup(response,'html.parser')


# function to get data i want (number of search results, job title, company, location) (if multiple results it only takes the top name)

def get_ind_data(soup):
    soup_search_results = soup.find_all(class_='search-results__total')

    try:
        soup_search_results[0].contents[0].strip().strip(' ').split(' ')[1]
    except IndexError:
        results_exist = False
    else:
        results_exist = True
    print(results_exist)

    if results_exist:
        num_results = soup_search_results[0].contents[0].strip().strip(' ').split(' ')[1]
        soup_job_title = soup.find_all(class_='subline-level-1')
        job_results = soup_job_title[0].contents[0].strip().strip(' ').split(' at ')

        if ' at ' not in soup_job_title[0].contents[0].strip().strip(' '):
            job_title = ''
            company = job_results[0]
        else:
            job_title = job_results[0]
            company = job_results[1]

        soup_location = soup.find_all(class_='subline-level-2')
        location = soup_location[0].contents[0].strip().strip(' ')
        return [num_results,job_title,company,location]
    return False

###########

# Login to LinkedIn
driver = webdriver.Chrome()
login(user,pw,driver)

# go through each csv and get data desired

df_head = ['First Name', 'Last Name', 'Last Name Adj', 'Account Name','Number of Search Attempts','Number of Search Results', 'Job Title', 'Current Company', 'Location']
print(df_head)
for fname,lname,prev_employer in zip(df['First Name'],df['Last Name'],df['Account Name']):
    if lname[-7:] == " (gone)":
        lname_adj = lname[:-7]
    elif lname[-18:] == ' (went to Celsius)':
        lname_adj = lname[:-18]
    else:
        lname_adj = lname

    data=False
    counter = 0
    while data == False:
        soup = get_url_response(df,fname,lname_adj,prev_employer,driver,counter)
        data = get_ind_data(soup)
        counter +=1
    print(data)
    row_data = [fname,lname,lname_adj,prev_employer,counter]
    row_data.extend(data)
    print(row_data)
    try: new_df
    except NameError:
        new_df = pd.DataFrame(columns=df_head)
        new_df = new_df.append(pd.Series(row_data,index=df_head), ignore_index = True)
    else:
        new_df = new_df.append(pd.Series(row_data,index=df_head), ignore_index = True)
    print(new_df)

# Get csv data of names and previous job titles to search on linkedin
csv_to_export_dir = csv_to_import_dir
csv_to_export_file =  'new_'+csv_to_import_file
csv_to_export = join(csv_to_export_dir,csv_to_export_file)

new_df.to_csv(csv_to_export, index=False)
driver.close()