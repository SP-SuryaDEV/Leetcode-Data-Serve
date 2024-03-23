import streamlit as st
import json
import pandas as pd
from Fetcher import contestfetch
from streamlit_gsheets import GSheetsConnection

def fetch_input_data():
    conn = st.experimental_connection('gsheets', type=GSheetsConnection)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1d0foz9yjxydkXHDHtdNFf0LQtnIuneowUnRYqUx6vzY/'
    
    df = conn.read(worksheet="Input", usecols=list(range(9)), ttl=1000000)
    df.dropna(how='all', inplace=True)

    st.write(df)

    return df

st.title("Contest Data Fetch")

data = None

def LeetcodeContestInstantFetch(contest_name):
    try:
        data = contestfetch(contest_name)
        
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid JSON file.")
    csv = None

    if data is not None:
        csv = fetch_input_data()

        csv['Rank'] = ''
        csv['ProbCount'] = ''
        csv['Score'] = ''

        for ind , row in csv.iterrows():
            username = row['Username'].lower()

            if username in data:
                csv.loc[ind,'Rank'] = data[username]['rank']
                csv.loc[ind,'ProbCount'] = data[username]['problemsSolved']
                csv.loc[ind,'Score'] = data[username]['score']
            else:
                csv.loc[ind,'Rank'] = 0
                csv.loc[ind,'ProbCount'] = 0
                csv.loc[ind,'Score'] = 0

    conn = st.experimental_connection('gsheets', type=GSheetsConnection)
    
    conn.create(worksheet=f"{contest_name.title()}", data=csv)

    st.sucess('Data Fetched...')

            

LeetcodeContestInstantFetch('weekly-contest-389')
