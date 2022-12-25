import time
import requests
import random
import xlsxwriter

import pandas as pd
import streamlit as st
import logging as log

from bs4 import BeautifulSoup
from io import BytesIO


def extract_keywords(file) -> list:
    keyword_df = pd.DataFrame()
    log.debug(f'Filename: {file.name}')
    # add logging?
    try:
        if '.csv' in file.name:
            keyword_df = pd.read_csv(file)
            log.debug(f'Keyword Dataframe: {keyword_df}')
        elif '.xlsx' in file.name:
            keyword_df = pd.read_excel(file)
            log.debug(f'Keyword Dataframe: {keyword_df}')
    except FileNotFoundError as f:
        print('File not found. Please check that the file exists ',
              'in the resources/input directory :: ', f)
        log.error('File not found. Please check that the file exists ',
                  'in the resources/input directory :: %s', f)
        return
    except Exception:
        print('Unknown error occurred')
        log.error('Unknown error occurred')
        return

    try:
        keyword_df.columns = keyword_df.columns.str.lower()
        return keyword_df["keyword"].tolist() 
    except KeyError:
        print('Column not found: "keyword"')
        log.error('Column not found: "keyword"')
        return


def format_cells(kgr) -> str:
    # conditional formatting of kgr column (Series)
    color = ''
    if kgr < 0.25:
        color = 'background-color: green'
    elif kgr >= 0.25 and kgr < 1:
        color = 'background-color: yellow'
    else:
        color = 'background-color: red'
    log.debug(f'Color chosen: {color}')
    return color


def create_df(keywords: list) -> pd.DataFrame:
    log.info(f'Keywords received: {keywords}')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
               'AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/74.0.3729.169 Safari/537.36'}
    # stats = []
    df = pd.DataFrame({'Keyword': [], 'All In Title': [], 'Search Volume': [], 'KGR': []})

    for i in keywords:
        search_phrase = 'allintitle:' + i
        params = {'q': search_phrase}
        url = 'https://www.google.com/search'

        # perform request
        response = requests.get(url, headers=headers, params=params)

        # parse response
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find("div", {"id": "result-stats"}).text

        # assuming Google keeps the number of results in the following format:
        # "About <number> results (<time>)"
        # have to remove commas from string to make int
        # should revert back to string for export
        num_of_results = result.split()[1].replace(',', '')

        # adding a random number for volume
        volume = random.randrange(1, 2)
        kgr = round(int(num_of_results)/volume, 2)
        df.loc[len(df.index)] = [i, num_of_results, volume, kgr]
        # stats[i] = [int(num_of_results.replace(',','')), ]
        time.sleep(1)

    return df


@st.cache
def convert_df(df: pd.DataFrame, filename: str) -> BytesIO:
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    # Write files to in-memory strings using BytesIO
    output = BytesIO()
    # writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    workbook.close()
    return output


with st.echo(code_location='below'):
    uploaded_file = st.file_uploader(
        "uploader",
        type=['xlsx', 'csv'],
        key="1",
        help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
        accept_multiple_files=False
    )
    if uploaded_file is not None:
        file_container = st.expander("Check your uploaded .csv or .xlsx")
        keywords = extract_keywords(uploaded_file)
        if keywords is None:
            log.error('Keywords are empty')
            st.stop()
           
        uploaded_file.seek(0)
        file_container.write(keywords)
    else:
        st.info("""👆 Upload a .csv or .xlsx file first.""")
        st.stop()
           
    df = create_df(keywords)
    output_file = 'allintitle_results.xlsx'
    # converted_df = convert_df(df, output_file)
    output = convert_df(df, output_file)

    st.download_button(
        label="Download as XLSX",
        data=output.getvalue(),
        file_name=output_file,
        mime='application/vnd.openxmlformatsofficedocument.spreadsheetml.sheet'
    )
    st.dataframe(df.style.applymap(format_cells, subset=['KGR']))
