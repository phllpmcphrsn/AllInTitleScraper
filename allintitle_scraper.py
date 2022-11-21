import time
import requests
import pandas as pd
import random

from bs4 import BeautifulSoup

def extract_keywords(filename) -> list:
# filename = 'resources\\input\\allintitle.xlsx'
    keyword_df = pd.DataFrame()
    
    # add logging?
    try:
        if '.csv' in filename:
            keyword_df = pd.read_csv(filename)
        elif '.xlsx' in filename:
            keyword_df = pd.read_excel(filename)
    except FileNotFoundError as f:
        print("File not found. Please check that the file exists in the resources/input directory :: ")
        return
    except:
        print('Unknown error occurred')

    try:
        keyword_df.columns = keyword_df.columns.str.lower()
    except KeyError:
        print('Column not found: "keyword"')
        return
    return keyword_df["keyword"].tolist() 
    


# main
# setup request
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
stats = []
keywords = extract_keywords('resources\\input\\allintitle.xlsx')
exported_df = pd.DataFrame()
exported_df.columns = ['Keyword', 'All In Title', 'Search Volume', 'KGR']

for i in keywords:
    search_phrase = 'allintitle:' + i
    params = {'q': search_phrase}
    url='https://www.google.com/search'

    # perform request
    response = requests.get(url, headers=headers, params=params)

    # parse response
    soup = BeautifulSoup(response.text, 'html.parser')
    result = soup.find("div", {"id":"result-stats"}).text

    # assuming Google keeps the number of results in the following format:
    # "About <number> results (<time>)"
    # have to remove commas from string to make int
    # should revert back to string for export
    num_of_results = result.split()[1].replace(',','')

    # adding a random number for volume
    volume = random.randrange(1,1000)
    kgr = round(num_of_results/volume, 2)
    exported_df.loc[len(exported_df.index)] = [i, num_of_results, volume, kgr]
    # stats[i] = [int(num_of_results.replace(',','')), ]
    time.sleep(1)
print(exported_df)

# conditional formatting of kgr column (Series)
green = [1 if kgr < 0.25 else 0 for kgr in kgrs ]
yellow = [2 if kgr >= 0.25 or kgr < 1 else 0 for kgr in kgrs ]
