import requests
import backoff
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

def read_usernames():
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1d0foz9yjxydkXHDHtdNFf0LQtnIuneowUnRYqUx6vzY/'
    conn = st.experimental_connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Input", usecols=list(range(9)), ttl=100)
    df.drop(how='all')
    return list(df['Username'].str.lower())

class ForbiddenError(Exception):
    pass

@backoff.on_exception(backoff.expo, ForbiddenError, max_tries=20)
def fetch(contestName,pageNumber):

    headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'cookies' : 'asdweaea',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    
    url = f"https://leetcode.com/contest/api/ranking/{contestName}/?pagination={pageNumber}&region=global"
    response = requests.get(url , headers=headers)

    if response.status_code == 200:
        return response
    elif response.status_code == 403:
        print('error raised')
        raise ForbiddenError('forbidden')
    else:
        return response


def contestfetch(contestName):
    pageNumber = 1
    completeData = {}
    
    usernames = read_usernames()

    while(True):
        
        response = fetch(contestName,pageNumber)

        if response.status_code == 200:
            json_data = response.json()

            completeData['found'] = True

            if len(json_data) == 0:
                
                break
            
            submissions = json_data['submissions']
            total = json_data['total_rank']



            if(len(submissions) == 0):
                break

            for i in range(len(submissions)):
                
                userName = total[i]['username'].lower()

                if userName in usernames:
                    rank = total[i]['rank']+1
                    score = total[i]['score']
                    problemsSolved = len(submissions[i])

                    completeData[userName] = {'rank':rank,"score":score, "problemsSolved" : problemsSolved}
            
            print(pageNumber)
            pageNumber += 1
        elif response.status_code == 404:
            return {'found' : 400} , False
        else:

            return {'found' : response.status_code} , False
        

    return completeData , True


    
