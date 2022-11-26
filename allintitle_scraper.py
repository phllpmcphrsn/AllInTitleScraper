import time
import requests
import pandas as pd
import random
import streamlit as st

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

def format_cells(kgr):
    # conditional formatting of kgr column (Series)
    color = ''
    if kgr < 0.25:
        color = 'background-color: green'
    elif kgr >= 0.25 and kgr < 1:
        color = 'background-color: yellow'
    else:
        color = 'background-color: red'
    return color

# main
# setup request
with st.echo(code_location='below'):
    uploaded_file = st.file_uploader(
        "",
        key="1",
        help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
    )
    if uploaded_file is not None:
        file_container = st.expander("Check your uploaded .csv")
        keywords = extract_keywords(uploaded_file)
        uploaded_file.seek(0)
        file_container.write(keywords)
    else:
        st.info(f"""👆 Upload a .csv file first.""")
        st.stop()
        
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    stats = []
    exported_df = pd.DataFrame({'Keyword': [], 'All In Title': [], 'Search Volume': [], 'KGR': []})

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
        volume = random.randrange(1,2)
        kgr = round(int(num_of_results)/volume, 2)
        exported_df.loc[len(exported_df.index)] = [i, num_of_results, volume, kgr]
        # stats[i] = [int(num_of_results.replace(',','')), ]
        time.sleep(1)
        
    exported_df.style.applymap(format_cells, subset=['KGR']).to_excel('resources\\output\\allintitle.xlsx', index=False, engine='openpyxl')
    st.table(exported_df)